"""
FuXi-S2S Weather Forecast Inference

Core module for running subseasonal-to-seasonal weather forecasts.
Adapted for Docker microservice architecture.
"""

import os
import time
from copy import deepcopy
from typing import Optional
from datetime import datetime

import numpy as np
import pandas as pd
import xarray as xr

from fuxis2s_model.config import settings
from .data_util import make_input, print_dataarray


# =============================================================================
# MODEL LOADING
# =============================================================================

def load_model(model_path: str, device: str = "cuda"):
    """
    Load ONNX model with specified device (CUDA or CPU).
    
    Parameters:
    -----------
    model_path : str
        Path to the ONNX model file
    device : str
        Device to use: 'cuda' or 'cpu'
    
    Returns:
    --------
    ort.InferenceSession
        ONNX Runtime inference session
    """
    import onnxruntime as ort
    
    ort.set_default_logger_severity(3)
    options = ort.SessionOptions()
    options.enable_cpu_mem_arena = False
    options.enable_mem_pattern = False
    options.enable_mem_reuse = False
    
    if device == "cuda":
        providers = [('CUDAExecutionProvider', {'arena_extend_strategy': 'kSameAsRequested'})]
    elif device == "cpu":
        providers = ['CPUExecutionProvider']
        options.intra_op_num_threads = 24
    else:
        raise ValueError("device must be cpu or cuda!")

    session = ort.InferenceSession(
        model_path,
        sess_options=options,
        providers=providers
    )
    return session


# =============================================================================
# DATA LOADING
# =============================================================================

def load_input_data(input_path: str) -> xr.DataArray:
    """
    Load input data from a file or directory.
    
    Args:
        input_path: Path to a .nc file or directory containing .nc files
        
    Returns:
        xr.DataArray: Combined input data in proper format
    """
    print(f"📂 Loading input data from: {input_path}")
    
    if os.path.isdir(input_path):
        print(f"  Combining variable files using make_input()...")
        input_data = make_input(input_path)
    else:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        input_data = xr.open_dataarray(input_path)
    
    print(f"  ✓ Loaded data shape: {input_data.shape}")
    return input_data


# =============================================================================
# INFERENCE FUNCTIONS
# =============================================================================

def save_forecast(output, input_data, member, lead_time, save_dir,
                  crop_lat=None, crop_lon=None, crop_radius=10.0,
                  print_fn=None):
    """Save forecast output to NetCDF file."""
    init_time = pd.to_datetime(input_data.time.values[-1])
    valid_time = init_time + pd.Timedelta(days=lead_time)
    
    output_data = xr.DataArray(
        data=output[0, 0],
        dims=['channel', 'lat', 'lon'],
        coords={
            'channel': input_data.channel.values,
            'lat': input_data.lat.values,
            'lon': input_data.lon.values,
        },
        attrs={
            'init_time': str(init_time),
            'valid_time': str(valid_time),
            'lead_time': lead_time,
            'member': member,
        }
    )
    
    # Apply regional crop if specified
    if crop_lat is not None and crop_lon is not None:
        lat_min = crop_lat - crop_radius
        lat_max = crop_lat + crop_radius
        lon_min = crop_lon - crop_radius
        lon_max = crop_lon + crop_radius
        
        output_data = output_data.sel(
            lat=slice(lat_max, lat_min),
            lon=slice(lon_min, lon_max)
        )
    
    # Create output directory
    year = init_time.strftime("%Y")
    date_str = init_time.strftime("%Y%m%d")
    member_dir = os.path.join(save_dir, year, date_str, "member")
    os.makedirs(member_dir, exist_ok=True)
    
    # Save file
    output_file = os.path.join(member_dir, f"member{member:02d}_lead{lead_time:02d}.nc")
    output_data.to_netcdf(output_file)
    
    if print_fn:
        print_fn(output_data)


def _run_model_inference(model, input_data, total_step, total_member,
                         save_dir="", crop_lat=None, crop_lon=None,
                         crop_radius=10.0, print_fn=None):
    """
    Run FuXi-S2S inference for multiple ensemble members.
    """
    input_names = [inp.name for inp in model.get_inputs()]
    
    hist_time = pd.to_datetime(input_data.time.values[-2])
    init_time = pd.to_datetime(input_data.time.values[-1])
    assert init_time - hist_time == pd.Timedelta(days=1)
    
    lat = input_data.lat.values
    lon = input_data.lon.values
    batch = input_data.values[None]
    
    assert lat[0] == 90 and lat[-1] == -90
    print(f"\n🌍 Starting inference for {total_member} ensemble member(s)")
    print(f"   Init time: {init_time}")
    print(f"   Total steps: {total_step}")

    for member in range(total_member):
        print(f'\n🎲 ENSEMBLE MEMBER {member+1}/{total_member}')
        new_input = deepcopy(batch)

        start = time.perf_counter()
        for step in range(total_step):
            lead_time = (step + 1)

            inputs = {'input': new_input}

            if "step" in input_names:
                inputs['step'] = np.array([step], dtype=np.float32)

            if "doy" in input_names:
                valid_time = init_time + pd.Timedelta(days=step)
                doy = min(365, valid_time.day_of_year) / 365
                inputs['doy'] = np.array([doy], dtype=np.float32)

            istart = time.perf_counter()
            new_input, = model.run(None, inputs)
            output = deepcopy(new_input[:, -1:])
            step_time = time.perf_counter() - istart

            forecast_date = init_time + pd.Timedelta(days=lead_time)
            print(f"   ✓ Day {lead_time:2d} ({forecast_date.strftime('%b %d, %Y')}) - {step_time:.2f}s")
            
            save_forecast(
                output, input_data, member, lead_time, save_dir,
                crop_lat=crop_lat, crop_lon=crop_lon, crop_radius=crop_radius,
                print_fn=print_fn
            )

        run_time = time.perf_counter() - start
        print(f'   ✅ Member {member+1} complete! Time: {run_time:.1f}s')


# =============================================================================
# ASYNC API FUNCTION
# =============================================================================

async def run_inference(
    init_date: Optional[str] = None,
    members: int = 11,
    total_step: int = 42,
    station: str = "Pacol, Naga City",
    use_gpu: bool = True,
) -> str:
    """
    Async wrapper for running inference - called from API endpoints.
    
    Returns:
        str: Output directory path
    """
    import asyncio
    
    # Determine device
    device = "cuda" if use_gpu else "cpu"
    
    # Determine input directory
    if init_date:
        # Use specific date data
        year = init_date[:4]
        input_dir = os.path.join(settings.data_dir, "realtime")
    else:
        input_dir = os.path.join(settings.data_dir, "realtime")
    
    # Check input data exists
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input data not found: {input_dir}")
    
    # Load model
    print(f"🤖 Loading model from {settings.model_path}")
    model = load_model(settings.model_path, device)
    
    # Load input data
    input_data = load_input_data(input_dir)
    
    # Determine init_date from data if not provided
    if not init_date:
        init_time = pd.to_datetime(input_data.time.values[-1])
        init_date = init_time.strftime("%Y%m%d")
    
    # Run inference in thread pool to not block
    def _run():
        _run_model_inference(
            model=model,
            input_data=input_data,
            total_step=total_step,
            total_member=members,
            save_dir=settings.output_dir,
            crop_lat=settings.crop_lat,
            crop_lon=settings.crop_lon,
            crop_radius=settings.crop_radius,
            print_fn=print_dataarray,
        )
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _run)
    
    year = init_date[:4]
    output_path = os.path.join(settings.output_dir, year, init_date)
    return output_path


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FuXi-S2S Weather Forecast Inference")
    parser.add_argument('--model', type=str, default="model/fuxi_s2s.onnx")
    parser.add_argument('--input', type=str, default="data/realtime")
    parser.add_argument('--device', type=str, default="cuda", choices=['cuda', 'cpu'])
    parser.add_argument('--save_dir', type=str, default="output")
    parser.add_argument('--total_step', type=int, default=42)
    parser.add_argument('--total_member', type=int, default=11)
    parser.add_argument('--crop_lat', type=float, default=13.58)
    parser.add_argument('--crop_lon', type=float, default=123.28)
    parser.add_argument('--crop_radius', type=float, default=10.0)
    
    args = parser.parse_args()
    
    model = load_model(args.model, args.device)
    input_data = load_input_data(args.input)
    
    _run_model_inference(
        model=model,
        input_data=input_data,
        total_step=args.total_step,
        total_member=args.total_member,
        save_dir=args.save_dir,
        crop_lat=args.crop_lat,
        crop_lon=args.crop_lon,
        crop_radius=args.crop_radius,
        print_fn=print_dataarray,
    )
