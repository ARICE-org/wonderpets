"""
ERA5 Data Download Module

Downloads ERA5 reanalysis data from the Copernicus Climate Data Store (CDS).
Adapted for Docker microservice architecture.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

import numpy as np
import xarray as xr

from config import settings


# Pressure level variables (13 levels each)
PRESSURE_VARS = [
    'geopotential', 'temperature', 'u_component_of_wind',
    'v_component_of_wind', 'specific_humidity'
]
PRESSURE_LEVELS = [
    '50', '100', '150', '200', '250', '300', '400',
    '500', '600', '700', '850', '925', '1000'
]

# Surface variables
SURFACE_VARS = [
    '2m_temperature', '2m_dewpoint_temperature', 'sea_surface_temperature',
    'top_net_thermal_radiation', '10m_u_component_of_wind', '10m_v_component_of_wind',
    '100m_u_component_of_wind', '100m_v_component_of_wind', 'mean_sea_level_pressure',
    'total_column_water_vapour', 'total_precipitation'
]


def get_cds_client():
    """Create CDS API client."""
    import cdsapi
    
    # Check for local .cdsapirc first
    local_rc = Path("/root/.cdsapirc")
    if local_rc.exists():
        config = {}
        with open(local_rc) as f:
            for line in f:
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    key, value = line.split(":", 1)
                    config[key.strip()] = value.strip()
        return cdsapi.Client(url=config.get("url"), key=config.get("key"))
    
    # Check environment variables
    cds_url = os.environ.get("CDS_API_URL", "https://cds.climate.copernicus.eu/api")
    cds_key = os.environ.get("CDS_API_KEY")
    
    if cds_key:
        return cdsapi.Client(url=cds_url, key=cds_key)
    
    # Fallback to default
    return cdsapi.Client()


def _requested_dates(target_date: datetime) -> List[str]:
    """Get the two dates needed for model input."""
    return [
        (target_date - timedelta(days=1)).strftime("%Y-%m-%d"),
        target_date.strftime("%Y-%m-%d"),
    ]


def _probe_has_two_consecutive_days(nc_path: str) -> bool:
    """Check if downloaded file contains 2 consecutive days."""
    ds = xr.open_dataset(nc_path)
    time_coord = None
    
    if "valid_time" in ds.coords:
        time_coord = ds["valid_time"].values
    elif "time" in ds.coords:
        time_coord = ds["time"].values
    else:
        return False

    if len(time_coord) < 2:
        return False

    t0 = np.datetime64(time_coord[-2])
    t1 = np.datetime64(time_coord[-1])
    return (t1 - t0) == np.timedelta64(1, "D")


def download_era5_for_date(target_date: datetime, output_dir: str = None, client=None):
    """
    Download ERA5 data for a specific initialization date.
    Requires 2 consecutive days (yesterday + today) for model input.
    """
    output_dir = output_dir or os.path.join(settings.data_dir, "realtime")
    os.makedirs(output_dir, exist_ok=True)
    
    client = client or get_cds_client()
    dates = _requested_dates(target_date)

    print(f"📥 Downloading ERA5 data for dates: {dates[0]} to {dates[1]}")

    # Probe with geopotential first
    probe_path = os.path.join(output_dir, "geopotential.nc")
    print(f"  Probing ERA5 availability...")
    
    client.retrieve('reanalysis-era5-pressure-levels', {
        'product_type': 'reanalysis',
        'variable': 'geopotential',
        'pressure_level': PRESSURE_LEVELS,
        'date': dates,
        'time': '00:00',
        'format': 'netcdf',
    }, probe_path)

    if not _probe_has_two_consecutive_days(probe_path):
        raise RuntimeError(
            "ERA5 download does not contain 2 consecutive timesteps. "
            "The latest day may not be available yet."
        )
    
    # Download remaining pressure level data
    for var in [v for v in PRESSURE_VARS if v != 'geopotential']:
        output_file = os.path.join(output_dir, f"{var}.nc")
        print(f"  Downloading {var}...")
        
        client.retrieve('reanalysis-era5-pressure-levels', {
            'product_type': 'reanalysis',
            'variable': var,
            'pressure_level': PRESSURE_LEVELS,
            'date': dates,
            'time': '00:00',
            'format': 'netcdf',
        }, output_file)
    
    # Download surface data
    for var in SURFACE_VARS:
        output_file = os.path.join(output_dir, f"{var}.nc")
        print(f"  Downloading {var}...")
        
        client.retrieve('reanalysis-era5-single-levels', {
            'product_type': 'reanalysis',
            'variable': var,
            'date': dates,
            'time': '00:00',
            'format': 'netcdf',
        }, output_file)
    
    # Save init date used
    init_date_file = os.path.join(output_dir, "init_date_used.txt")
    with open(init_date_file, "w", encoding="utf-8") as f:
        f.write(target_date.strftime("%Y%m%d") + "\n")
    
    print(f"✅ Downloaded all ERA5 data to {output_dir}")
    return output_dir


async def download_era5_data(
    init_date: Optional[str] = None,
    variables: Optional[List[str]] = None,
    lag_days: int = 5,
    max_lookback: int = 14
):
    """
    Async wrapper for downloading ERA5 data - called from API endpoints.
    
    Args:
        init_date: Date string YYYYMMDD (optional, auto-selects if not provided)
        variables: List of variables to download (optional)
        lag_days: Days to look back from today
        max_lookback: Max days to search backwards
    """
    import asyncio
    
    if init_date:
        target_date = datetime.strptime(init_date, "%Y%m%d")
    else:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        target_date = today - timedelta(days=lag_days)
    
    def _download():
        client = get_cds_client()
        last_error = None
        
        for offset in range(max_lookback + 1):
            candidate = target_date - timedelta(days=offset)
            print(f"Trying init_date={candidate.strftime('%Y%m%d')}...")
            
            try:
                download_era5_for_date(candidate, client=client)
                return candidate.strftime("%Y%m%d")
            except Exception as e:
                last_error = e
                print(f"  Not usable: {e}")
        
        raise RuntimeError(f"Failed to download ERA5 data: {last_error}")
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _download)
    return result


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download ERA5 data for FuXi-S2S")
    parser.add_argument("--date", type=str, default="",
                        help="Initialization date YYYYMMDD")
    parser.add_argument("--output", type=str, default="data/realtime",
                        help="Output directory")
    parser.add_argument("--lag_days", type=int, default=5,
                        help="Days back from today to start")
    parser.add_argument("--max_lookback_days", type=int, default=14,
                        help="Max days to search backwards")
    args = parser.parse_args()

    if args.date:
        start_date = datetime.strptime(args.date, "%Y%m%d")
    else:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today - timedelta(days=args.lag_days)

    client = get_cds_client()
    
    for offset in range(args.max_lookback_days + 1):
        candidate = start_date - timedelta(days=offset)
        print(f"\nTrying init_date={candidate.strftime('%Y%m%d')}...")
        try:
            download_era5_for_date(candidate, args.output, client=client)
            print(f"\n✅ INIT_DATE_USED={candidate.strftime('%Y%m%d')}")
            break
        except Exception as e:
            print(f"  Not usable: {e}")
