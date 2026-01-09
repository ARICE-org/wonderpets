"""
Recommendation Service - Main FastAPI Application

Isolated ML service for rice variety recommendations.
Port: 8003
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
from apps.recommendation_service.api.endpoints import router as recommendation_router
from apps.recommendation_service.api.dependencies import get_recommendation_service
from apps.common.utils.logging_utils import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Recommendation Service...")
    
    try:
        service = get_recommendation_service()
        model_path = os.getenv("MODEL_PATH", "./trained_models/recommendation")
        await service.initialize(model_path)
        logger.info("Recommendation service initialized successfully")
    except Exception as e:
        logger.warning(f"Recommendation service initialization warning: {e}")
    
    yield
    
    logger.info("Shutting down Recommendation Service...")


app = FastAPI(
    title="ARICE Recommendation Service",
    description="Rice variety recommendations for optimal yield",
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

app.include_router(
    recommendation_router, 
    prefix="/api/v1/recommendation", 
    tags=["recommendation"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "recommendation",
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "ARICE Recommendation Service",
        "version": "2.0.0",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "apps.recommendation_service.main:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )
