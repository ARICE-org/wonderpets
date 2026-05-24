"""
Pipeline API endpoints for FuXi-S2S Model Service
Full workflow: download -> inference -> store
"""

import os
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from src.config import settings

router = APIRouter(prefix="/pipeline")


class PipelineRequest(BaseModel):
    """Request model for running full pipeline."""
    init_date: Optional[str] = Field(
        default=datetime.utcnow().strftime("%Y%m%d"),
        description="Initial date (YYYYMMDD). Defaults to today."
    )
    members: int = Field(default=11, ge=1, le=51)
    total_step: int = Field(default=42, ge=1, le=100)
    station: str = Field(default="Pacol, Naga City")
    skip_download: bool = Field(
        default=False,
        description="Skip ERA5 download if data exists"
    )
    skip_store: bool = Field(
        default=False,
        description="Skip storing to MongoDB"
    )


class PipelineResponse(BaseModel):
    """Response for pipeline execution."""
    status: str
    message: str
    job_id: Optional[str] = None
    init_date: Optional[str] = None
    steps: Optional[List[str]] = None


class DownloadRequest(BaseModel):
    """Request model for ERA5 download."""
    init_date: Optional[str] = Field(
        default=datetime.utcnow().strftime("%Y%m%d"),
        description="Initial date (YYYYMMDD). Defaults to today."
    )
    variables: Optional[List[str]] = None


class StoreRequest(BaseModel):
    """Request model for storing forecasts."""
    init_date: str = Field(
        default=datetime.utcnow().strftime("%Y%m%d"),
        description="Initial date (YYYYMMDD). Defaults to today."
    )
    station: str = Field(
        default="Pacol, Naga City",
        description="Station name. Defaults to Pacol, Naga City."
    )


# Job tracking
_pipeline_jobs: dict = {}


@router.post("/run", response_model=PipelineResponse)
async def run_pipeline(
    request: PipelineRequest,
    background_tasks: BackgroundTasks
):
    """
    Run the complete forecast pipeline:
    1. Download ERA5 data (optional)
    2. Run model inference
    3. Store results to MongoDB (optional)
    """
    job_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    init_date = request.init_date or datetime.utcnow().strftime("%Y%m%d")
    
    steps = []
    if not request.skip_download:
        steps.append("download")
    steps.append("inference")
    if not request.skip_store:
        steps.append("store")
    
    _pipeline_jobs[job_id] = {
        "status": "queued",
        "init_date": init_date,
        "steps": steps,
        "current_step": None,
        "progress": 0,
    }
    
    background_tasks.add_task(
        _run_pipeline_task,
        job_id,
        init_date,
        request.members,
        request.total_step,
        request.station,
        request.skip_download,
        request.skip_store,
    )
    
    return PipelineResponse(
        status="accepted",
        message="Pipeline job queued",
        job_id=job_id,
        init_date=init_date,
        steps=steps,
    )


@router.get("/status/{job_id}")
async def get_pipeline_status(job_id: str):
    """Get status of a pipeline job."""
    if job_id not in _pipeline_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _pipeline_jobs[job_id]


@router.post("/download")
async def download_era5(
    request: DownloadRequest,
    background_tasks: BackgroundTasks
):
    """Download ERA5 data."""
    init_date = request.init_date or datetime.utcnow().strftime("%Y%m%d")
    
    background_tasks.add_task(_download_era5_task, init_date, request.variables)
    
    return {
        "status": "accepted",
        "message": f"Download queued for {init_date}",
    }


@router.post("/store")
async def store_forecasts(request: StoreRequest):
    """Store forecast results to MongoDB."""
    try:
        from core.store_forecasts import store_forecast_data
        
        result = await store_forecast_data(
            init_date=request.init_date,
            station=request.station,
        )
        
        return {
            "status": "success",
            "message": "Forecasts stored",
            "records_stored": result.get("count", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/input")
async def check_input_data():
    """Check available input data."""
    data_dir = settings.data_dir
    realtime_dir = os.path.join(data_dir, "realtime")
    
    files = {}
    if os.path.exists(realtime_dir):
        for f in os.listdir(realtime_dir):
            if f.endswith(".nc"):
                path = os.path.join(realtime_dir, f)
                files[f] = {
                    "size_mb": round(os.path.getsize(path) / (1024**2), 2),
                    "modified": datetime.fromtimestamp(
                        os.path.getmtime(path)
                    ).isoformat(),
                }
    
    return {
        "data_dir": data_dir,
        "realtime_dir": realtime_dir,
        "files": files,
        "count": len(files),
    }


@router.get("/data/output")
async def check_output_data():
    """Check available output data."""
    output_dir = settings.output_dir
    
    runs = []
    if os.path.exists(output_dir):
        for year in os.listdir(output_dir):
            year_path = os.path.join(output_dir, year)
            if os.path.isdir(year_path):
                for run in os.listdir(year_path):
                    run_path = os.path.join(year_path, run)
                    if os.path.isdir(run_path):
                        runs.append({
                            "date": run,
                            "path": run_path,
                        })
    
    return {
        "output_dir": output_dir,
        "runs": sorted(runs, key=lambda x: x["date"], reverse=True),
        "count": len(runs),
    }


async def _run_pipeline_task(
    job_id: str,
    init_date: str,
    members: int,
    total_step: int,
    station: str,
    skip_download: bool,
    skip_store: bool,
):
    """Run the complete pipeline."""
    try:
        _pipeline_jobs[job_id]["status"] = "running"
        
        # Step 1: Download
        if not skip_download:
            _pipeline_jobs[job_id]["current_step"] = "download"
            _pipeline_jobs[job_id]["progress"] = 10
            from core.download_era5 import download_era5_data
            await download_era5_data(init_date)
        
        # Step 2: Inference
        _pipeline_jobs[job_id]["current_step"] = "inference"
        _pipeline_jobs[job_id]["progress"] = 40
        from core.inference import run_inference
        output_path = await run_inference(
            init_date=init_date,
            members=members,
            total_step=total_step,
            station=station,
        )
        
        # Step 3: Store
        if not skip_store:
            _pipeline_jobs[job_id]["current_step"] = "store"
            _pipeline_jobs[job_id]["progress"] = 80
            from core.store_forecasts import store_forecast_data
            await store_forecast_data(init_date, station)
        
        _pipeline_jobs[job_id]["status"] = "completed"
        _pipeline_jobs[job_id]["progress"] = 100
        _pipeline_jobs[job_id]["output_path"] = output_path
        
    except Exception as e:
        _pipeline_jobs[job_id]["status"] = "failed"
        _pipeline_jobs[job_id]["error"] = str(e)


async def _download_era5_task(init_date: str, variables: Optional[List[str]]):
    """Download ERA5 data task."""
    from core.download_era5 import download_era5_data
    await download_era5_data(init_date, variables)
