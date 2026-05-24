"""
Data Utilities for FuXi-S2S

Functions for preparing input data from ERA5 downloads.
"""

import os
import numpy as np
import xarray as xr

__all__ = ["make_input", "print_dataarray"]

LEVELS = [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000]

S2S_NAMES = [
    # Pressure level variables
    ('geopotential', 'z'),
    ('temperature', 't'),
    ('u_component_of_wind', 'u'),
    ('v_component_of_wind', 'v'),
    ('specific_humidity', 'q'),
    # Surface variables
    ('2m_temperature', 't2m'),
    ('2m_dewpoint_temperature', 'd2m'),
    ('sea_surface_temperature', 'sst'),
    ('top_net_thermal_radiation', 'ttr'),
    ('10m_u_component_of_wind', '10u'),
    ('10m_v_component_of_wind', '10v'),
    ('100m_u_component_of_wind', '100u'),
    ('100m_v_component_of_wind', '100v'),
    ('mean_sea_level_pressure', 'msl'),
    ('total_column_water_vapour', 'tcwv'),
    ('total_precipitation', 'tp'),
]


def print_dataarray(ds, msg='', n=10):
    """Print summary of xarray DataArray."""
    tid = np.arange(0, ds.shape[0])
    tid = np.append(tid[:n], tid[-n:])
    v = ds.isel(time=tid) if 'time' in ds.dims else ds
    
    msg += f"short_name: {ds.name}, shape: {ds.shape}"
    
    if hasattr(v, 'values'):
        msg += f", value: {v.values.min():.3f} ~ {v.values.max():.3f}"
    
    if 'lat' in ds.dims:
        lat = ds.lat.values
        msg += f", lat: {lat[0]:.3f} ~ {lat[-1]:.3f}"
    if 'lon' in ds.dims:
        lon = ds.lon.values
        msg += f", lon: {lon[0]:.3f} ~ {lon[-1]:.3f}"
    
    print(msg)


def _open_and_normalize(file_path: str) -> xr.DataArray:
    """
    Open a variable file and normalize CDS/sample formats to FuXi dims.
    
    Supports:
    - Sample files that already have dims like (time, level, lat, lon)
    - CDS ERA5 files with dims like (valid_time, pressure_level, latitude, longitude)
    """
    ds = xr.open_dataset(file_path)
    
    if len(ds.data_vars) == 1:
        var_name = next(iter(ds.data_vars))
    else:
        var_name = sorted(ds.data_vars.keys())[0]
    da = ds[var_name]

    # Drop ensemble dimension if present
    if "number" in da.dims:
        da = da.isel(number=0, drop=True)

    # Rename dimensions to standard names
    rename_map = {}
    if "valid_time" in da.dims:
        rename_map["valid_time"] = "time"
    if "pressure_level" in da.dims:
        rename_map["pressure_level"] = "level"
    if "latitude" in da.dims:
        rename_map["latitude"] = "lat"
    if "longitude" in da.dims:
        rename_map["longitude"] = "lon"
    if rename_map:
        da = da.rename(rename_map)

    # Validate required dimensions
    for required in ("time", "lat", "lon"):
        if required not in da.dims:
            raise ValueError(
                f"Unexpected dims in {os.path.basename(file_path)}: {list(da.dims)}"
            )

    # Regrid to the model grid if needed
    # The FuXi-S2S model expects 1.5° global grid: (lat=121, lon=240)
    # CDS ERA5 is typically 0.25° global grid: (lat=721, lon=1440)
    lat_n = int(da.sizes.get("lat"))
    lon_n = int(da.sizes.get("lon"))
    
    if lat_n == 721 and lon_n == 1440:
        # Exact stride from 0.25° -> 1.5° (factor 6)
        da = da.isel(lat=slice(0, None, 6), lon=slice(0, None, 6))
    elif lat_n == 121 and lon_n == 240:
        pass  # Already in model grid
    else:
        raise RuntimeError(
            f"Unsupported grid size for {os.path.basename(file_path)}: "
            f"lat={lat_n}, lon={lon_n}. Expected 721x1440 or 121x240."
        )

    return da


def make_input(data_dir: str) -> xr.DataArray:
    """
    Combine individual variable NetCDF files into a single input array
    for FuXi-S2S inference.
    
    Args:
        data_dir: Directory containing individual variable .nc files
        
    Returns:
        xr.DataArray with dims (time, channel, lat, lon)
    """
    ds = []
    channel = []
    
    for (long_name, short_name) in S2S_NAMES:
        file_name = os.path.join(data_dir, f"{long_name}.nc")
        
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"Missing variable file: {file_name}")
            
        v = _open_and_normalize(file_name)

        # Apply transformations
        if short_name == "tp":
            v = np.clip(v * 1000, 0, 1000)  # Convert to mm
        elif short_name == "ttr":
            v = v / 3600  # Convert to hourly rate

        if "level" in v.dims:
            # Ensure level order is 1000 -> 50 (descending)
            if v.level.values[0] != 1000:
                v = v.reindex(level=v.level[::-1])

            level_labels = [f"{short_name}{int(l)}" for l in v.level.values]
        else:
            # Surface vars: add a dummy level dimension
            v = v.expand_dims(level=[short_name])
            level_labels = [short_name]

        v.name = "data"
        v.attrs = {}
        v = v.assign_coords(level=level_labels)
        ds.append(v)
        channel += level_labels

    # Combine all variables
    combined = xr.concat(ds, "level").rename({"level": "channel"})
    combined = combined.assign_coords(channel=channel)
    combined = combined.transpose("time", "channel", "lat", "lon")
    
    return combined
