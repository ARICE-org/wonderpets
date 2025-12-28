"""
Weather API Router

Endpoints for weather forecasting.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.schemas.weather import (
    WeatherForecastRequest,
    WeatherForecastResponse,
    LocationInput
)
from app.services.weather_service import WeatherService

router = APIRouter()

# Service instance
weather_service = WeatherService()


@router.post("/forecast", response_model=WeatherForecastResponse)
async def get_weather_forecast(request: WeatherForecastRequest):
    """
    Get weather forecast for a location.
    
    Args:
        request: Forecast request with location and horizon days
    
    Returns:
        Weather forecast with daily predictions
    """
    try:
        response = await weather_service.get_forecast(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")


@router.get("/historical")
async def get_historical_weather(
    latitude: float = Query(..., description="Location latitude"),
    longitude: float = Query(..., description="Location longitude"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """
    Get historical weather analysis for a location.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        start_date: Analysis start date
        end_date: Analysis end date
    
    Returns:
        Historical weather summary and trends
    """
    try:
        location = {"latitude": latitude, "longitude": longitude}
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start > end:
            raise ValueError("start_date must be before end_date")
        
        response = await weather_service.get_historical_analysis(location, start, end)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Historical analysis error: {str(e)}")


@router.get("/status")
async def get_weather_status():
    """
    Check weather service status.
    
    Returns:
        Service status and model information
    """
    return {
        "service": "weather",
        "ready": weather_service.is_ready(),
        "model_loaded": weather_service.model is not None if hasattr(weather_service, 'model') else False
    }
