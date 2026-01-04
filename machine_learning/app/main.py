"""
ARICE Machine Learning Service

FastAPI application for serving ML predictions:
- Rice variety recommendations
- Weather forecasting
- Soil health analysis and forecasting
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routers import recommendation, weather, soil

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
    # TODO: Implement actual model status checking
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
