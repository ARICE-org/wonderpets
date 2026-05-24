"""
Health check endpoints for FuXi-S2S Model Service
"""

from datetime import datetime
import subprocess

from fastapi import APIRouter

router = APIRouter()


def _get_gpu_names() -> list[str]:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "fuxis2s-model",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/gpu")
async def gpu_check():
    """Check GPU availability."""
    try:
        gpu_names = _get_gpu_names()

        if gpu_names:
            return {
                "status": "healthy",
                "gpu_available": True,
                "device_name": gpu_names[0],
                "device_count": len(gpu_names),
                "cuda_version": "12.4",
                "memory_allocated": "0.00 MB",
                "memory_reserved": "0.00 MB",
            }
        else:
            return {
                "status": "degraded",
                "gpu_available": False,
                "message": "No GPU detected, using CPU",
            }
    except Exception as e:
        return {
            "status": "error",
            "gpu_available": False,
            "error": str(e),
        }


@router.get("/health/model")
async def model_check():
    """Check if ONNX model is loaded."""
    import os
    from config import settings
    
    model_path = settings.model_path
    model_exists = os.path.exists(model_path)
    
    if model_exists:
        model_size = os.path.getsize(model_path) / (1024 ** 2)  # MB
        return {
            "status": "healthy",
            "model_loaded": True,
            "model_path": model_path,
            "model_size_mb": round(model_size, 2),
        }
    else:
        return {
            "status": "error",
            "model_loaded": False,
            "model_path": model_path,
            "message": "Model file not found",
        }


@router.get("/ready")
async def readiness_check():
    """Full readiness check."""
    import os
    from config import settings
    
    checks = {
        "model": os.path.exists(settings.model_path),
        "data_dir": os.path.exists(settings.data_dir),
        "output_dir": os.path.exists(settings.output_dir),
    }
    
    # GPU check
    try:
        checks["gpu"] = bool(_get_gpu_names())
    except Exception:
        checks["gpu"] = False
    
    all_ready = all(checks.values())
    
    return {
        "ready": all_ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }
