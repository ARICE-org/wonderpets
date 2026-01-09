"""Forecast endpoints for Weather Service."""

import requests
from fastapi import APIRouter, HTTPException, Query

from app.utils.weather import process_forecast

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/forecast/latest")
async def get_latest_forecast(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    days: int = Query(7, ge=1, le=42, description="Number of forecast days"),
):
    """
    Get latest forecast for a location.
    Returns ensemble mean + bias-corrected values.
    Calls external API on port 5002.
    """
    try:
        response = requests.get(
            "http://localhost:5002/api/v1/forecast/latest",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "days": days,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return process_forecast(data)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"External weather service error: {e}")


@router.get("/forecast/by-date")
async def get_forecast_by_date(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
):
    """
    Get forecasts for a specific date range.
    Finds the best available run that covers the requested dates.
    Calls external API on port 5002.
    """
    try:
        response = requests.get(
            "http://localhost:5002/api/v1/forecast/by-date",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": end_date,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return process_forecast(data)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"External weather service error: {e}")

