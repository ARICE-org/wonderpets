"""
Inference API endpoints for FuXi-S2S Model Service
"""

import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/inference")


class InferenceRequest(BaseModel):
    """Request model for running inference."""
    init_date: Optional[str] = Field(
        None, 
        description="Initial date for forecast (YYYYMMDD). Defaults to latest."
    )
    members: int = Field(
        default=11,
        ge=1,
        le=51,
        description="Number of ensemble members"
    )
    total_step: int = Field(
        default=42,
        ge=1,
        le=100,
        description="Total forecast steps (1 step = ~1 day)"
    )
    station: str = Field(
        default="Pacol, Naga City",
        description="Station name for localized forecast"
    )
    use_gpu: bool = Field(
        default=True,
        description="Whether to use GPU acceleration"
    )


class InferenceResponse(BaseModel):
    """Response model for inference."""
    status: str
    message: str
    job_id: Optional[str] = None
    init_date: Optional[str] = None
    output_path: Optional[str] = None


class InferenceStatus(BaseModel):
    """Status of an inference job."""
    job_id: str
    status: str  # queued, running, completed, failed
    progress: Optional[int] = None
    init_date: Optional[str] = None
    error: Optional[str] = None


# Simple job tracking (in production use Redis or similar)
_jobs: dict = {}


@router.post("/run", response_model=InferenceResponse)
async def run_inference(
    request: InferenceRequest,
    background_tasks: BackgroundTasks
):
    """
    Run FuXi-S2S model inference.
    
    This endpoint triggers the inference process which may take several minutes.
    """
    # Check if model exists
    if not os.path.exists(settings.model_path):
        raise HTTPException(
            status_code=503,
            detail=f"Model not found at {settings.model_path}"
        )
    
    # Generate job ID
    job_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    init_date = request.init_date or datetime.utcnow().strftime("%Y%m%d")
    
    # Store job
    _jobs[job_id] = {
        "status": "queued",
        "init_date": init_date,
        "members": request.members,
        "total_step": request.total_step,
        "station": request.station,
        "progress": 0,
    }
    
    # Add to background tasks
    background_tasks.add_task(
        _run_inference_task,
        job_id,
        init_date,
        request.members,
        request.total_step,
        request.station,
        request.use_gpu,
    )
    
    return InferenceResponse(
        status="accepted",
        message="Inference job queued",
        job_id=job_id,
        init_date=init_date,
    )


@router.get("/status/{job_id}", response_model=InferenceStatus)
async def get_inference_status(job_id: str):
    """Get status of an inference job."""
    if job_id not in _jobs:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    job = _jobs[job_id]
    return InferenceStatus(
        job_id=job_id,
        status=job.get("status", "unknown"),
        progress=job.get("progress"),
        init_date=job.get("init_date"),
        error=job.get("error"),
    )


@router.get("/jobs")
async def list_jobs():
    """List all inference jobs."""
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job.get("status"),
                "init_date": job.get("init_date"),
            }
            for job_id, job in _jobs.items()
        ]
    }


async def _run_inference_task(
    job_id: str,
    init_date: str,
    members: int,
    total_step: int,
    station: str,
    use_gpu: bool
):
    """Background task for running inference."""
    try:
        _jobs[job_id]["status"] = "running"
        _jobs[job_id]["progress"] = 10
        
        # Import inference module
        from core.inference import run_inference as do_inference
        
        _jobs[job_id]["progress"] = 20
        
        # Run inference
        output_path = await do_inference(
            init_date=init_date,
            members=members,
            total_step=total_step,
            station=station,
            use_gpu=use_gpu,
        )
        
        _jobs[job_id]["status"] = "completed"
        _jobs[job_id]["progress"] = 100
        _jobs[job_id]["output_path"] = output_path
        
    except Exception as e:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(e)
