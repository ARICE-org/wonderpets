"""
Full Pipeline Module

Combines download, inference, and store steps.
"""

import os
from datetime import datetime
from typing import Optional

from fuxis2s_model.config import settings


async def run_full_pipeline(
    init_date: Optional[str] = None,
    members: int = 11,
    total_step: int = 42,
    station: str = "Pacol, Naga City",
    skip_download: bool = False,
    skip_store: bool = False
) -> dict:
    """
    Run the full forecast pipeline:
    1. Download ERA5 data
    2. Run model inference
    3. Store results to MongoDB
    
    Args:
        init_date: Initialization date (YYYYMMDD)
        members: Number of ensemble members
        total_step: Forecast days
        station: Station name
        skip_download: Skip download step
        skip_store: Skip store step
        
    Returns:
        Dict with pipeline results
    """
    results = {
        "download": None,
        "inference": None,
        "store": None,
        "init_date": init_date,
    }
    
    # Step 1: Download ERA5 data
    if not skip_download:
        print("\n" + "=" * 60)
        print("STEP 1: DOWNLOAD ERA5 DATA")
        print("=" * 60)
        
        from .download_era5 import download_era5_data
        init_date = await download_era5_data(init_date)
        results["download"] = "success"
        results["init_date"] = init_date
        print(f"✅ Download complete. Init date: {init_date}")
    else:
        print("\n⏭️  Skipping download step")
        if not init_date:
            # Try to read from existing data
            init_file = os.path.join(settings.data_dir, "realtime", "init_date_used.txt")
            if os.path.exists(init_file):
                with open(init_file) as f:
                    init_date = f.read().strip()
                results["init_date"] = init_date
    
    # Step 2: Run inference
    print("\n" + "=" * 60)
    print("STEP 2: RUN MODEL INFERENCE")
    print("=" * 60)
    
    from .inference import run_inference
    output_path = await run_inference(
        init_date=init_date,
        members=members,
        total_step=total_step,
        station=station,
    )
    results["inference"] = "success"
    results["output_path"] = output_path
    print(f"✅ Inference complete. Output: {output_path}")
    
    # Step 3: Store to MongoDB
    if not skip_store:
        print("\n" + "=" * 60)
        print("STEP 3: STORE TO MONGODB")
        print("=" * 60)
        
        from .store_forecasts import store_forecast_data
        store_result = await store_forecast_data(
            init_date=init_date,
            station=station,
            members=members,
        )
        results["store"] = store_result
        print(f"✅ Stored {store_result['count']} documents")
    else:
        print("\n⏭️  Skipping store step")
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    
    return results


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description="Run FuXi-S2S full pipeline")
    parser.add_argument("--init_date", type=str, default=None)
    parser.add_argument("--members", type=int, default=11)
    parser.add_argument("--total_step", type=int, default=42)
    parser.add_argument("--station", type=str, default="Pacol, Naga City")
    parser.add_argument("--skip_download", action="store_true")
    parser.add_argument("--skip_store", action="store_true")
    
    args = parser.parse_args()
    
    result = asyncio.run(run_full_pipeline(
        init_date=args.init_date,
        members=args.members,
        total_step=args.total_step,
        station=args.station,
        skip_download=args.skip_download,
        skip_store=args.skip_store,
    ))
    
    print(f"\n📊 Results: {result}")
