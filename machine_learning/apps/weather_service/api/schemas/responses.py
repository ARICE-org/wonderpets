"""
Weather service response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class DailyForecast(BaseModel):
    """Daily weather forecast."""
    
    date: str = Field(..., description="Forecast date")
    temperature_max: Optional[float] = Field(None, description="Maximum temperature (°C)")
    temperature_min: Optional[float] = Field(None, description="Minimum temperature (°C)")
    temperature_avg: Optional[float] = Field(None, description="Average temperature (°C)")
    rainfall: Optional[float] = Field(None, description="Rainfall amount (mm)")
    rainfall_probability: Optional[float] = Field(None, description="Probability of rain (%)")
    humidity: Optional[float] = Field(None, description="Relative humidity (%)")
    wind_speed: Optional[float] = Field(None, description="Wind speed (km/h)")
    wind_direction: Optional[str] = Field(None, description="Wind direction")
    condition: Optional[str] = Field(None, description="Weather condition description")
    uv_index: Optional[int] = Field(None, description="UV index")
    
    # Agricultural relevance
    rice_suitability: Optional[str] = Field(None, description="Rice farming suitability")
    alerts: Optional[List[str]] = Field(default_factory=list, description="Weather alerts")


class WeatherSummary(BaseModel):
    """Weather summary statistics."""
    
    avg_temperature: Optional[float] = None
    total_rainfall: Optional[float] = None
    avg_humidity: Optional[float] = None
    rainy_days: Optional[int] = None
    hot_days: Optional[int] = None
    favorable_days: Optional[int] = None


class WeatherForecastResponse(BaseModel):
    """Weather forecast response."""
    
    location: Optional[Dict[str, Any]] = Field(None, description="Location info")
    forecast_start: str = Field(..., description="Forecast start date")
    forecast_end: str = Field(..., description="Forecast end date")
    horizon_days: int = Field(..., description="Number of forecast days")
    daily_forecasts: List[DailyForecast] = Field(
        default_factory=list,
        description="Daily forecast data"
    )
    summary: Optional[WeatherSummary] = Field(None, description="Forecast summary")
    generated_at: Optional[str] = Field(None, description="Generation timestamp")


class HistoricalAnalysisResponse(BaseModel):
    """Historical weather analysis response."""
    
    location: Optional[Dict[str, Any]] = None
    period: Dict[str, str] = Field(..., description="Analysis period")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Summary statistics")
    monthly_breakdown: Optional[List[Dict[str, Any]]] = None
    trends: Optional[List[Dict[str, Any]]] = None
    anomalies: Optional[List[Dict[str, Any]]] = None
