"""
Weather service configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class WeatherServiceConfig(BaseSettings):
    """Configuration specific to weather service."""
    
    # Model paths
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./trained_models/weather")
    FORECAST_MODEL_FILE: str = "weather_forecast_model.pkl"
    
    # Forecast settings
    DEFAULT_FORECAST_HORIZON_DAYS: int = 30
    MAX_FORECAST_HORIZON_DAYS: int = 90
    MIN_FORECAST_HORIZON_DAYS: int = 7
    
    # Data sources
    WEATHER_API_URL: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None
    
    # Cache settings
    CACHE_TTL_HOURS: int = 6
    
    class Config:
        env_prefix = "WEATHER_"
        case_sensitive = True


weather_config = WeatherServiceConfig()
