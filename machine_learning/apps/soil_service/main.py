"""
Soil Service - Main FastAPI Application

Isolated ML service for soil health analysis and forecasting.
Port: 8001
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from apps.middleware.rate_limiter import RateLimitMiddleware
from apps.middleware.error_handler import register_exception_handlers
from apps.middleware.logging_middleware import LoggingMiddleware
from apps.soil_service.api.endpoints import router as soil_router
from apps.soil_service.api.dependencies import get_soil_service
from apps.common.utils.logging_utils import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Soil Analysis Service...")
    
    # Initialize soil service
    try:
        service = get_soil_service()
        model_path = os.getenv("MODEL_PATH", "./trained_models/soil")
        await service.initialize(model_path)
        logger.info("Soil service initialized successfully")
    except Exception as e:
        logger.warning(f"Soil service initialization warning: {e}")
    
    yield
    
    logger.info("Shutting down Soil Analysis Service...")


# Create FastAPI application
app = FastAPI(
    title="ARICE Soil Analysis Service",
    description="Soil health scoring and forecasting using hybrid ML approach",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
app.add_middleware(LoggingMiddleware)

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(soil_router, prefix="/api/v1/soil", tags=["soil"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "soil-analysis",
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "ARICE Soil Analysis Service",
        "version": "2.0.0",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "apps.soil_service.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
