"""FastAPI service to serve forecasts from MongoDB."""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from app.utils.mongo_store import MongoForecastStore as MongoStore

router = APIRouter()


def get_store():
    return MongoStore.from_env()


def _station_query(station_name: str) -> dict:
    # Current storage format: station is an object with station.name
    # Back-compat: allow older docs that stored station as a plain string.
    return {"$or": [{"station.name": station_name}, {"station": station_name}]}


def _nearest_run_for_lat_lon(store: MongoStore, latitude: float, longitude: float) -> dict | None:
    # Map lat/lon to the closest stored station point.
    # This is the same idea as weather apps: user location -> nearest model/grid point.
    pipeline = [
        {"$match": {"station.lat": {"$type": "number"}, "station.lon": {"$type": "number"}}},
        {
            "$addFields": {
                "_dist2": {
                    "$add": [
                        {"$pow": [{"$subtract": ["$station.lat", latitude]}, 2]},
                        {"$pow": [{"$subtract": ["$station.lon", longitude]}, 2]},
                    ]
                }
            }
        },
        {"$sort": {"_dist2": 1, "created_at": -1}},
        {"$limit": 1},
        {"$project": {"_dist2": 0}},
    ]
    docs = list(store.db.forecast_runs.aggregate(pipeline))
    return docs[0] if docs else None


@router.get("/health")
def health():
    """Health check endpoint."""
    store = None
    try:
        store = get_store()
        store.db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
    finally:
        if store is not None:
            store.close()


@router.get("/forecast/latest")
def get_latest_forecast(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    days: int = Query(7, ge=1, le=42, description="Number of forecast days")
):
    """
    Get latest forecast for a station.
    Returns ensemble mean + bias-corrected values.
    """
    store = None
    try:
        store = get_store()

        # Find nearest run based on lat/lon
        latest_run = _nearest_run_for_lat_lon(store, latitude=latitude, longitude=longitude)

        if not latest_run:
            raise HTTPException(404, "No forecasts found for the provided coordinates")

        run_id = latest_run.get("run_id") or latest_run.get("_id")
        if not run_id:
            raise HTTPException(500, "Malformed run document: missing run identifier")

        # Get forecasts
        forecasts = list(
            store.db.station_forecasts_final.find(
                {"run_id": run_id, "lead_time_days": {"$lte": days}},
                {"_id": 0},
            ).sort("lead_time_days", 1)
        )

        station_obj = latest_run.get("station")
        station_name = None
        if isinstance(station_obj, dict):
            station_name = station_obj.get("name")

        return {
            "run_id": run_id,
            "init_time": latest_run.get("init_time"),
            "created_at": latest_run.get("created_at"),
            "station": station_name,
            "station_details": station_obj if isinstance(station_obj, dict) else None,
            "requested_location": {"lat": latitude, "lon": longitude},
            "forecast_days": len(forecasts),
            "forecasts": forecasts,
        }
    finally:
        if store is not None:
            store.close()


@router.get("/forecast/by-date")
def get_forecast_by_date(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """
    Get forecasts for a specific date range.
    Finds the best available run that covers the requested dates.
    """
    store = None
    try:
        store = get_store()

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # Resolve nearest stored station/grid point via runs collection
        nearest_run = _nearest_run_for_lat_lon(store, latitude=latitude, longitude=longitude)
        if not nearest_run:
            raise HTTPException(404, "No forecasts found for the provided coordinates")

        station_obj = nearest_run.get("station")
        station_name = station_obj.get("name") if isinstance(station_obj, dict) else None
        if not station_name:
            raise HTTPException(500, "Malformed run document: missing station metadata")

        # Find forecasts in date range for the resolved point
        forecasts = list(
            store.db.station_forecasts_final.find(
                {
                    **_station_query(station_name),
                    "valid_time": {"$gte": start, "$lte": end},
                },
                {"_id": 0},
            ).sort("valid_time", 1)
        )

        if not forecasts:
            raise HTTPException(404, f"No forecasts found between {start_date} and {end_date} for the resolved location")

        return {
            "station": station_name,
            "station_details": station_obj,
            "requested_location": {"lat": latitude, "lon": longitude},
            "date_range": {"start": start_date, "end": end_date},
            "forecast_count": len(forecasts),
            "forecasts": forecasts,
        }
    finally:
        if store is not None:
            store.close()


@router.get("/runs")
def list_runs(
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Latitude coordinate"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Longitude coordinate"),
    station: Optional[str] = Query(None, description="(Deprecated) Filter by station name"),
    limit: int = Query(10, ge=1, le=100)
):
    """List recent forecast runs."""
    store = None
    try:
        store = get_store()

        query: dict = {}

        # Prefer lat/lon (new behavior). If not provided, fall back to station filter.
        if latitude is not None or longitude is not None:
            if latitude is None or longitude is None:
                raise HTTPException(400, "Provide both latitude and longitude")
            nearest = _nearest_run_for_lat_lon(store, latitude=latitude, longitude=longitude)
            if not nearest:
                return {"runs": []}
            station_obj = nearest.get("station")
            station_name = station_obj.get("name") if isinstance(station_obj, dict) else None
            if station_name:
                query = _station_query(station_name)
        elif station:
            query = _station_query(station)

        runs = list(
            store.db.forecast_runs.find(
                query,
                {"_id": 1, "init_time": 1, "created_at": 1, "station": 1, "members": 1, "run_id": 1},
            )
            .sort("created_at", -1)
            .limit(limit)
        )

        payload: dict[str, Any] = {"runs": runs}
        if latitude is not None and longitude is not None:
            payload["requested_location"] = {"lat": latitude, "lon": longitude}
        return payload
    finally:
        if store is not None:
            store.close()