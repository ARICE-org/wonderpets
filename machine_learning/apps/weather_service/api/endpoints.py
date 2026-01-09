"""
Weather Service API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from apps.weather_service.api.dependencies import get_weather_service
from apps.weather_service.api.schemas.requests import (
    WeatherForecastRequest,
    HistoricalAnalysisRequest,
    LocationInput,
)
from apps.weather_service.api.schemas.responses import (
    WeatherForecastResponse,
    HistoricalAnalysisResponse,
    DailyForecast,
)
from apps.weather_service.services.weather_service import WeatherService
from apps.common.utils.logging_utils import logger


router = APIRouter()


@router.post("/forecast", response_model=WeatherForecastResponse)
async def get_weather_forecast(
    request: WeatherForecastRequest,
    service: WeatherService = Depends(get_weather_service)
):
    """
    Get weather forecast for specified location and horizon.
    
    Args:
        request: Forecast request with location and horizon days
        
    Returns:
        Weather forecast response with daily predictions
    """
    try:
        result = await service.get_forecast(
            location=request.location.model_dump() if request.location else None,
            horizon_days=request.horizon_days,
            start_date=request.start_date
        )
        
        return WeatherForecastResponse(
            location=result.get("location"),
            forecast_start=result.get("forecast_start"),
            forecast_end=result.get("forecast_end"),
            horizon_days=result.get("horizon_days"),
            daily_forecasts=[
                DailyForecast(**forecast) 
                for forecast in result.get("daily_forecasts", [])
            ],
            summary=result.get("summary"),
            generated_at=result.get("generated_at")
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in weather forecast: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating weather forecast: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate forecast")


@router.post("/historical", response_model=HistoricalAnalysisResponse)
async def get_historical_analysis(
    request: HistoricalAnalysisRequest,
    service: WeatherService = Depends(get_weather_service)
):
    """
    Get historical weather analysis for a location and date range.
    """
    try:
        result = await service.get_historical_analysis(
            location=request.location.model_dump() if request.location else None,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return HistoricalAnalysisResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in historical analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze historical data")


@router.get("/current/{latitude}/{longitude}")
async def get_current_weather(
    latitude: float,
    longitude: float,
    service: WeatherService = Depends(get_weather_service)
):
    """
    Get current weather for a specific location.
    """
    try:
        result = await service.get_current_weather(
            latitude=latitude,
            longitude=longitude
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching current weather: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch current weather")


@router.get("/status")
async def get_service_status(
    service: WeatherService = Depends(get_weather_service)
):
    """Get weather service status and model information."""
    return {
        "service": "weather",
        "status": "ready" if service.is_ready() else "initializing",
        "model_info": service.get_model_info()
    }
