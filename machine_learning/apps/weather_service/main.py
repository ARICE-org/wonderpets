"""
Weather Service - Main FastAPI Application

Isolated ML service for weather forecasting.
Port: 8002
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
from apps.weather_service.api.endpoints import router as weather_router
from apps.weather_service.api.dependencies import get_weather_service
from apps.common.utils.logging_utils import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Weather Forecast Service...")
    
    try:
        service = get_weather_service()
        model_path = os.getenv("MODEL_PATH", "./trained_models/weather")
        await service.initialize(model_path)
        logger.info("Weather service initialized successfully")
    except Exception as e:
        logger.warning(f"Weather service initialization warning: {e}")
    
    yield
    
    logger.info("Shutting down Weather Forecast Service...")


app = FastAPI(
    title="ARICE Weather Forecast Service",
    description="Weather forecasting for agricultural planning",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
app.add_middleware(LoggingMiddleware)

register_exception_handlers(app)

app.include_router(weather_router, prefix="/api/v1/weather", tags=["weather"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "weather-forecast",
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "ARICE Weather Forecast Service",
        "version": "2.0.0",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "apps.weather_service.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
