"""
FuXi-S2S Model Service - FastAPI Application
Model inference and data pipeline
Port: 8002
"""

import os
import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import inference, pipeline, health


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("🤖 FuXi-S2S Model Service starting up...")
    print("   Checking GPU availability...")
    try:
        gpu_names = _get_gpu_names()
        if gpu_names:
            print(f"   ✓ GPU detected: {gpu_names[0]}")
        else:
            print("   ⚠ No GPU detected, using CPU")
    except Exception as e:
        print(f"   ⚠ GPU check failed: {e}")
    yield
    print("🤖 FuXi-S2S Model Service shutting down...")


app = FastAPI(
    title="FuXi-S2S Model Service",
    description="API for running FuXi-S2S weather forecast inference",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(inference.router, prefix="/api/v1", tags=["Inference"])
app.include_router(pipeline.router, prefix="/api/v1", tags=["Pipeline"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "FuXi-S2S Model Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
