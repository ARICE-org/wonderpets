"""
ARICE Machine Learning Service

FastAPI application for serving ML predictions:
- Rice variety recommendations
- Weather forecasting
- Soil health analysis and forecasting
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from datetime import datetime

from app.config.settings import settings
from app.middleware.rate_limiter import RateLimitMiddleware, FixedWindowRateLimiter
from app.routers import recommendation, weather, soil

logger = logging.getLogger("uvicorn")

logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(logs_dir, exist_ok=True)

log_file = os.path.join(logs_dir, f"ml_service_requests_{datetime.now().strftime('%Y%m%d')}.log")
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Custom formatter: DateTime - Endpoint - Client - Response
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

logging.getLogger("uvicorn.access").addHandler(file_handler)
logger.addHandler(file_handler)

app = FastAPI(
    title="ARICE ML Service",
    description="Machine Learning API for rice farming recommendations, weather forecasting, and soil analysis",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter Middleware (Fixed Window Algorithm - uses ENV config)
rate_limiter = FixedWindowRateLimiter(
    requests_per_window=settings.RATE_LIMIT_STANDARD_REQUESTS,
    window_size_seconds=settings.RATE_LIMIT_STANDARD_WINDOW
)
app.add_middleware(
    RateLimitMiddleware,
    limiter=rate_limiter,
    exclude_paths=["/health", "/docs", "/redoc", "/openapi.json", "/models/status"]
)

# Include routers
app.include_router(recommendation.router, prefix="/api/recommend", tags=["Recommendation"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(soil.router, prefix="/api/soil", tags=["Soil Analysis"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ml-service"}


@app.get("/models/status", tags=["Health"])
async def models_status():
    """Check status of loaded ML models"""
    return {
        "recommendation_model": {"loaded": False, "version": None},
        "weather_model": {"loaded": False, "version": None},
        "soil_health_model": {"loaded": False, "version": None},
        "soil_forecast_model": {"loaded": False, "version": None},
        "hybrid_soil_forecast_model": {
            "loaded": False,
            "version": None,
            "description": "Hybrid model combining Rule-Based + ML for soil forecasting"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
