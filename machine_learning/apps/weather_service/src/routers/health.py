"""
Health check endpoints for FuXi-S2S Model Service
"""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


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
        import torch
        
        if torch.cuda.is_available():
            return {
                "status": "healthy",
                "gpu_available": True,
                "device_name": torch.cuda.get_device_name(0),
                "device_count": torch.cuda.device_count(),
                "cuda_version": torch.version.cuda,
                "memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**2:.2f} MB",
                "memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**2:.2f} MB",
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
    from fuxis2s_model.config import settings
    
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
    from fuxis2s_model.config import settings
    
    checks = {
        "model": os.path.exists(settings.model_path),
        "data_dir": os.path.exists(settings.data_dir),
        "output_dir": os.path.exists(settings.output_dir),
    }
    
    # GPU check
    try:
        import torch
        checks["gpu"] = torch.cuda.is_available()
    except Exception:
        checks["gpu"] = False
    
    all_ready = all(checks.values())
    
    return {
        "ready": all_ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }
