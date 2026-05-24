"""
PAGASA Comparison Utilities

Functions for comparing FuXi-S2S forecasts with observations.
"""

import os
import glob
from typing import List, Dict, Optional, Any, cast

import pandas as pd
import xarray as xr
import numpy as np


# Station locations
STATIONS = {
    'Pili, Camarines Sur': {'lat': 13.58, 'lon': 123.28},
    'Naga City': {'lat': 13.62, 'lon': 123.19},
    'Pacol, Naga City': {'lat': 13.657096, 'lon': 123.224535},
    'CBSUA Pili': {'lat': 13.58, 'lon': 123.28},
}

# Variable mapping
VARIABLE_MAPPING = {
    'tp': 'total_precipitation',
    't2m': '2m_temperature',
    'd2m': '2m_dewpoint_temperature',
    'msl': 'mean_sea_level_pressure',
    '10u': '10m_u_wind',
    '10v': '10m_v_wind',
}


def load_fuxi_output(output_dir: str, init_date: str, member: int = 0) -> Optional[xr.DataArray]:
    """
    Load FuXi-S2S output from multiple lead time files.
    
    Args:
        output_dir: Base output directory
        init_date: Initialization date (YYYYMMDD)
        member: Ensemble member number
        
    Returns:
        xr.DataArray with forecast data
    """
    date_str = init_date.replace('/', '').replace('-', '')
    year_str = date_str[:4]
    
    # Check for flat structure first: member/memberXX_leadYY.nc
    member_dir = os.path.join(output_dir, year_str, date_str, "member")
    pattern = os.path.join(member_dir, f"member{member:02d}_lead*.nc")
    nc_files = sorted(glob.glob(pattern))
    
    # Fallback to subdirectory structure: member/XX/*.nc
    if not nc_files:
        member_subdir = os.path.join(member_dir, f"{member:02d}")
        if os.path.exists(member_subdir):
            nc_files = sorted(glob.glob(os.path.join(member_subdir, "*.nc")))
    
    if not nc_files:
        raise FileNotFoundError(f"Member directory not found: {member_dir}")
    
    def _as_dataarray(obj: Any) -> xr.DataArray:
        # xarray may return Dataset or DataTree for some NetCDF layouts; normalize to DataArray.
        if isinstance(obj, xr.DataArray):
            return obj

        # DataTree-like: try to extract a Dataset from the root node.
        if hasattr(obj, "to_dataset"):
            obj = obj.to_dataset()  # type: ignore[assignment]

        if isinstance(obj, xr.Dataset):
            if len(obj.data_vars) == 1:
                var_name = next(iter(obj.data_vars))
                return cast(xr.DataArray, obj[var_name])
            raise ValueError(f"Expected a single data variable in {nc_file}, found: {list(obj.data_vars)}")

        raise TypeError(f"Unsupported xarray object type: {type(obj)!r}")

    datasets: List[xr.DataArray] = []
    for nc_file in nc_files:
        opened = xr.open_dataset(nc_file, engine="netcdf4")
        ds = _as_dataarray(opened)
        # Extract lead_time from filename if not in data
        if 'lead_time' not in ds.dims:
            # Parse lead time from filename like member00_lead01.nc
            fname = os.path.basename(nc_file)
            try:
                lead_str = fname.split('_lead')[1].replace('.nc', '')
                lead_time = int(lead_str)
                ds = ds.expand_dims({'lead_time': [lead_time]})
            except (IndexError, ValueError):
                pass
        datasets.append(ds)
    
    combined: xr.DataArray = xr.concat(datasets, dim='lead_time')
    return combined


def extract_station_forecast(
    fuxi_data: xr.DataArray,
    lat: float,
    lon: float,
    init_date: str,
    variables: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Extract forecast data for a specific station location.
    
    Args:
        fuxi_data: FuXi-S2S output DataArray
        lat: Station latitude
        lon: Station longitude
        init_date: Initialization date
        variables: List of variables to extract
        
    Returns:
        DataFrame with forecast values
    """
    if variables is None:
        variables = ['tp', 't2m', 'd2m', 'msl', '10u', '10v']
    
    # Select nearest grid point
    station_data = fuxi_data.sel(lat=lat, lon=lon, method='nearest')
    
    # Get init time from data or parse from init_date
    if 'time' in station_data.coords:
        init_time = pd.to_datetime(station_data.time.values[0])
    else:
        init_time = pd.to_datetime(init_date)
    
    results = []
    
    for lead_time in station_data.lead_time.values:
        valid_time = init_time + pd.Timedelta(days=int(lead_time))
        row = {
            'init_time': init_time,
            'lead_time_days': int(lead_time),
            'valid_time': valid_time,
        }
        
        for var in variables:
            if var in station_data.channel.values:
                arr = station_data.sel(lead_time=lead_time, channel=var).values
                # Ensure we extract a scalar value
                value = float(arr.item() if arr.size == 1 else arr.flat[0])
                row[var] = value
        
        # Calculate derived values
        if '10u' in row and '10v' in row:
            u10 = row['10u']
            v10 = row['10v']
            row['wind_speed'] = np.sqrt(u10**2 + v10**2)
            wind_dir = np.degrees(np.arctan2(u10, v10)) + 180
            row['wind_direction'] = wind_dir % 360
        
        # Convert temperatures to Celsius
        if 't2m' in row:
            row['t2m_celsius'] = row['t2m'] - 273.15
        if 'd2m' in row:
            row['d2m_celsius'] = row['d2m'] - 273.15
        
        results.append(row)
    
    return pd.DataFrame(results)
