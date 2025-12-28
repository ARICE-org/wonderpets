"""
Soil Analysis API Router

Endpoints for soil health scoring and forecasting.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from app.schemas.soil import (
    SoilAnalysisRequest,
    SoilHealthResponse,
    SoilForecastRequest,
    SoilForecastResponse
)
from app.services.soil_analysis_service import SoilAnalysisService

router = APIRouter()

# Service instance
soil_service = SoilAnalysisService()


@router.post("/analyze", response_model=SoilHealthResponse)
async def analyze_soil_health(request: SoilAnalysisRequest):
    """
    Analyze soil health and generate overall health score.
    
    Args:
        request: Soil analysis request with sensor data
    
    Returns:
        Overall health score (0-100) with parameter breakdown
    """
    try:
        response = await soil_service.analyze_health(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.post("/health-score")
async def get_detailed_health_score(request: SoilAnalysisRequest):
    """
    Get detailed health scoring with parameter breakdown and explanations.
    
    Args:
        request: Soil analysis request with sensor data
    
    Returns:
        Detailed scoring with interpretations for each parameter
    """
    try:
        response = await soil_service.get_detailed_score(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health score error: {str(e)}")


@router.post("/forecast", response_model=SoilForecastResponse)
async def get_soil_forecast(request: SoilForecastRequest):
    """
    Get 3-month soil condition forecast for rice planting season.
    
    Args:
        request: Forecast request with historical data and planting date
    
    Returns:
        Seasonal forecast with weekly summaries and growth stage alignment
    """
    try:
        response = await soil_service.forecast_season(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")


@router.post("/seasonal-forecast")
async def get_seasonal_soil_forecast(request: SoilForecastRequest):
    """
    Get soil forecast aligned with rice growth stages.
    
    Args:
        request: Forecast request with planting date
    
    Returns:
        Forecast with growth stage timeline and stage-specific alerts
    """
    try:
        response = await soil_service.get_seasonal_forecast(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seasonal forecast error: {str(e)}")


@router.post("/recommendations")
async def get_soil_recommendations(request: SoilAnalysisRequest):
    """
    Get soil improvement recommendations based on current conditions.
    
    Args:
        request: Soil analysis request
    
    Returns:
        Prioritized recommendations with expected improvements
    """
    try:
        response = await soil_service.get_recommendations(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations error: {str(e)}")


@router.get("/status")
async def get_soil_service_status():
    """
    Check soil analysis service status.
    
    Returns:
        Service status and model information
    """
    return {
        "service": "soil_analysis",
        "ready": soil_service.is_ready(),
        "health_model_loaded": soil_service.health_model is not None if hasattr(soil_service, 'health_model') else False,
        "forecast_model_loaded": soil_service.forecast_model is not None if hasattr(soil_service, 'forecast_model') else False
    }
