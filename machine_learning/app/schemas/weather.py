"""
Weather Schemas

Pydantic models for weather API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class LocationInput(BaseModel):
    """Location for weather queries."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    name: Optional[str] = Field(None, description="Location name")


class WeatherForecastRequest(BaseModel):
    """Request for weather forecast."""
    location: LocationInput = Field(..., description="Location for forecast")
    horizon_days: int = Field(
        default=30, 
        ge=1, 
        le=90, 
        description="Number of days to forecast (1-90)"
    )
    include_hourly: bool = Field(
        default=False, 
        description="Include hourly forecasts"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": {
                    "latitude": 14.5995,
                    "longitude": 120.9842,
                    "name": "Manila"
                },
                "horizon_days": 30,
                "include_hourly": False
            }
        }


class DailyWeatherForecast(BaseModel):
    """Daily weather forecast data."""
    date: str = Field(..., description="Forecast date (YYYY-MM-DD)")
    temperature_max: Optional[float] = Field(None, description="Maximum temperature (°C)")
    temperature_min: Optional[float] = Field(None, description="Minimum temperature (°C)")
    temperature_avg: Optional[float] = Field(None, description="Average temperature (°C)")
    rainfall: Optional[float] = Field(None, ge=0, description="Predicted rainfall (mm)")
    rainfall_probability: Optional[float] = Field(
        None, ge=0, le=100, description="Probability of rain (%)"
    )
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Humidity (%)")
    wind_speed: Optional[float] = Field(None, ge=0, description="Wind speed (km/h)")
    wind_direction: Optional[str] = Field(None, description="Wind direction")
    uv_index: Optional[float] = Field(None, ge=0, description="UV index")
    condition: Optional[str] = Field(None, description="Weather condition description")
    confidence: Optional[float] = Field(
        None, ge=0, le=1, description="Forecast confidence (0-1)"
    )


class HourlyWeatherForecast(BaseModel):
    """Hourly weather forecast data."""
    datetime: str = Field(..., description="Forecast datetime (ISO format)")
    temperature: Optional[float] = Field(None, description="Temperature (°C)")
    rainfall: Optional[float] = Field(None, ge=0, description="Rainfall (mm)")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Humidity (%)")
    wind_speed: Optional[float] = Field(None, ge=0, description="Wind speed (km/h)")
    condition: Optional[str] = Field(None, description="Weather condition")


class WeatherForecastResponse(BaseModel):
    """Response containing weather forecast."""
    location: LocationInput = Field(..., description="Forecast location")
    forecast_start: Optional[str] = Field(None, description="Forecast start date")
    forecast_end: Optional[str] = Field(None, description="Forecast end date")
    horizon_days: int = Field(..., description="Number of days forecasted")
    daily_forecasts: List[DailyWeatherForecast] = Field(
        ..., description="Daily forecast data"
    )
    hourly_forecasts: Optional[List[HourlyWeatherForecast]] = Field(
        None, description="Hourly forecast data (if requested)"
    )
    summary: Optional[Dict[str, Any]] = Field(None, description="Forecast summary")
    agricultural_advisory: Optional[str] = Field(
        None, description="Advisory for agricultural activities"
    )
    model_version: Optional[str] = Field(None, description="Model version used")
    generated_at: Optional[str] = Field(None, description="Timestamp of generation")


class HistoricalWeatherRequest(BaseModel):
    """Request for historical weather data."""
    location: LocationInput = Field(..., description="Location")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    parameters: Optional[List[str]] = Field(
        None, 
        description="Specific parameters to retrieve"
    )


class HistoricalWeatherResponse(BaseModel):
    """Response containing historical weather analysis."""
    location: LocationInput = Field(..., description="Location")
    period: Dict[str, str] = Field(..., description="Analysis period")
    summary: Dict[str, Any] = Field(..., description="Statistical summary")
    trends: Optional[List[Dict[str, Any]]] = Field(None, description="Trend analysis")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Raw data points")
