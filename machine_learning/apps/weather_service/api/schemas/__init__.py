"""
Weather service API schemas.
"""

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

__all__ = [
    "WeatherForecastRequest",
    "HistoricalAnalysisRequest",
    "LocationInput",
    "WeatherForecastResponse",
    "HistoricalAnalysisResponse",
    "DailyForecast",
]
