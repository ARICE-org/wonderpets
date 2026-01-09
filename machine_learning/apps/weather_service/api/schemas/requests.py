"""
Weather service request schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class LocationInput(BaseModel):
    """Location input for weather requests."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    name: Optional[str] = Field(None, description="Location name")
    region: Optional[str] = Field(None, description="Region/Province")


class WeatherForecastRequest(BaseModel):
    """Request for weather forecast."""
    
    location: LocationInput = Field(..., description="Location for forecast")
    horizon_days: int = Field(
        default=30,
        ge=1,
        le=90,
        description="Number of days to forecast"
    )
    start_date: Optional[str] = Field(
        None,
        description="Forecast start date (YYYY-MM-DD). Defaults to today."
    )
    include_hourly: bool = Field(
        default=False,
        description="Include hourly breakdown"
    )


class HistoricalAnalysisRequest(BaseModel):
    """Request for historical weather analysis."""
    
    location: LocationInput = Field(..., description="Location for analysis")
    start_date: str = Field(..., description="Analysis start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Analysis end date (YYYY-MM-DD)")
    parameters: Optional[list] = Field(
        default=None,
        description="Specific parameters to analyze"
    )
