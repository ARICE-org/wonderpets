"""
Store Forecasts to MongoDB

Writes FuXi-S2S station-level forecasts to MongoDB.
Adapted for Docker microservice architecture.
"""

import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

import pandas as pd
import numpy as np

from fuxis2s_model.config import settings


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _safe_float(value) -> Optional[float]:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        return None


def _safe_int(value) -> Optional[int]:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    try:
        return int(value)
    except Exception:
        return None


def get_mongo_client():
    """Get MongoDB client."""
    from pymongo import MongoClient
    return MongoClient(settings.mongo_uri)


def _build_run_id(
    init_date: str,
    station_name: str,
    num_members: int,
    use_ensemble: bool,
    apply_bias_correction: bool
) -> str:
    """Build a unique run_id."""
    station_safe = "".join(ch if ch.isalnum() else "_" for ch in station_name)
    ver = _utc_now().strftime("%Y%m%dT%H%M%S")
    return f"{init_date}_{station_safe}_m{num_members}_e{int(use_ensemble)}_b{int(apply_bias_correction)}_{ver}"


def _df_row_to_doc(
    row: pd.Series,
    run_id: str,
    station_name: str,
    station_lat: float,
    station_lon: float,
    member: Optional[int] = None,
    is_ensemble_mean: bool = False,
    bias_corrected: bool = False
) -> Dict[str, Any]:
    """Convert a DataFrame row to a MongoDB document."""
    valid_time = pd.to_datetime(row["valid_time"])
    init_time = pd.to_datetime(row["init_time"])

    # Temperature conversion
    t2m_c = row.get("t2m_celsius")
    if t2m_c is None or pd.isna(t2m_c):
        t2m_k = _safe_float(row.get("t2m"))
        t2m_c = None if t2m_k is None else (t2m_k - 273.15)

    d2m_c = row.get("d2m_celsius")
    if d2m_c is None or pd.isna(d2m_c):
        d2m_k = _safe_float(row.get("d2m"))
        d2m_c = None if d2m_k is None else (d2m_k - 273.15)

    doc = {
        "run_id": run_id,
        "station": {
            "name": station_name,
            "lat": float(station_lat),
            "lon": float(station_lon)
        },
        "init_time": init_time.to_pydatetime(),
        "lead_time_days": int(_safe_int(row.get("lead_time_days")) or 0),
        "valid_time": valid_time.to_pydatetime(),
        "variables": {
            "tp_mm": _safe_float(row.get("tp")),
            "t2m_c": _safe_float(t2m_c),
            "d2m_c": _safe_float(d2m_c),
            "msl_pa": _safe_float(row.get("msl")),
            "u10": _safe_float(row.get("10u")),
            "v10": _safe_float(row.get("10v")),
            "wind_speed": _safe_float(row.get("wind_speed")),
            "wind_direction_deg": _safe_float(row.get("wind_direction")),
        },
        "quality": {
            "kind": "ensemble_mean" if is_ensemble_mean else "member",
            "ensemble_mean": is_ensemble_mean,
            "bias_corrected": bias_corrected,
        },
        "created_at": _utc_now(),
    }
    
    if member is not None:
        doc["member"] = int(member)
    
    return doc


async def store_forecast_data(
    init_date: str,
    station: str = "Pacol, Naga City",
    members: int = 11,
    apply_bias_correction: bool = False
) -> Dict[str, Any]:
    """
    Store forecast data to MongoDB.
    
    Args:
        init_date: Initialization date YYYYMMDD
        station: Station name
        members: Number of ensemble members
        apply_bias_correction: Whether to apply bias correction
        
    Returns:
        Dict with operation result
    """
    import asyncio
    
    def _store():
        from .compare import load_fuxi_output, extract_station_forecast, STATIONS
        import os
        # BiasCorrector import
        corrector = None
        if apply_bias_correction:
            try:
                from train_fuxi.bias_correction import BiasCorrector
                corrector = BiasCorrector.load(os.path.join(os.path.dirname(__file__), '../../train_fuxi/artifacts/bias_correction_params.pkl'))
                print("Loaded bias correction model.")
            except Exception as e:
                print(f"Warning: Could not load bias correction model: {e}")
                corrector = None

        # Get station info
        station_info = STATIONS.get(station, {"lat": 13.58, "lon": 123.28})
        station_lat = station_info.get("lat", 13.58)
        station_lon = station_info.get("lon", 123.28)

        # Load forecast data
        output_dir = settings.output_dir
        year = init_date[:4]
        run_dir = os.path.join(output_dir, year, init_date)

        if not os.path.exists(run_dir):
            raise FileNotFoundError(f"Forecast output not found: {run_dir}")

        # Connect to MongoDB
        client = get_mongo_client()
        db = client[settings.mongo_db]

        run_id = _build_run_id(
            init_date, station, members,
            use_ensemble=True,
            apply_bias_correction=apply_bias_correction
        )

        docs = []
        count = 0

        # Load and store each member's data
        all_member_dfs = []
        for member in range(members):
            try:
                ds = load_fuxi_output(output_dir, init_date, member)
                df = extract_station_forecast(ds, station_lat, station_lon, init_date)
                df["member"] = member
                # Apply bias correction if requested and model is loaded
                if apply_bias_correction and corrector is not None:
                    df = corrector.transform(df)
                    bias_flag = True
                else:
                    bias_flag = False
                all_member_dfs.append(df)

                for _, row in df.iterrows():
                    doc = _df_row_to_doc(
                        row, run_id, station, station_lat, station_lon,
                        member=member, is_ensemble_mean=False, bias_corrected=bias_flag
                    )
                    docs.append(doc)
                    count += 1

            except Exception as e:
                print(f"Warning: Failed to process member {member}: {e}")

        # Insert member documents
        if docs:
            db["fuxi_member_forecasts"].insert_many(docs)

        # Calculate and store ensemble mean (final forecast)
        final_docs = []
        final_count = 0
        if all_member_dfs:
            combined = pd.concat(all_member_dfs, ignore_index=True)

            # Numeric columns to average
            numeric_cols = ["tp", "t2m", "d2m", "msl", "10u", "10v", "wind_speed", "wind_direction"]
            available_cols = [c for c in numeric_cols if c in combined.columns]

            # Group by lead_time_days and compute mean
            group_cols = ["lead_time_days", "valid_time", "init_time"]
            ensemble_mean = combined.groupby(group_cols, as_index=False)[available_cols].mean()

            # Apply bias correction to ensemble mean if requested
            if apply_bias_correction and corrector is not None:
                ensemble_mean = corrector.transform(ensemble_mean)
                bias_flag = True
            else:
                bias_flag = False

            for _, row in ensemble_mean.iterrows():
                doc = _df_row_to_doc(
                    row, run_id, station, station_lat, station_lon,
                    member=None, is_ensemble_mean=True, bias_corrected=bias_flag
                )
                final_docs.append(doc)
                final_count += 1

            if final_docs:
                db["fuxi_final_forecasts"].insert_many(final_docs)
                print(f"✅ Stored {final_count} ensemble mean documents to fuxi_final_forecasts")

        client.close()

        return {"count": count, "final_count": final_count, "run_id": run_id}
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _store)
    return result


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description="Store forecasts to MongoDB")
    parser.add_argument("--init_date", type=str, required=True)
    parser.add_argument("--station", type=str, default="Pacol, Naga City")
    parser.add_argument("--members", type=int, default=11)
    
    args = parser.parse_args()
    
    result = asyncio.run(store_forecast_data(
        args.init_date,
        args.station,
        args.members
    ))
    
    print(f"✅ Stored {result['count']} documents with run_id={result['run_id']}")
