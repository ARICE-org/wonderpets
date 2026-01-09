"""
Soil service configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class SoilServiceConfig(BaseSettings):
    """Configuration specific to soil service."""
    
    # Model paths
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./trained_models/soil")
    HEALTH_MODEL_FILE: str = "soil_health_model.pkl"
    FORECAST_MODEL_FILE: str = "soil_forecast_model.pkl"
    HYBRID_MODEL_FILE: str = "hybrid_soil_forecast.joblib"
    
    # Forecast settings
    DEFAULT_FORECAST_HORIZON_DAYS: int = 90
    DEFAULT_FORECAST_INTERVAL_DAYS: int = 7
    MIN_FORECAST_HORIZON: int = 30
    MAX_FORECAST_HORIZON: int = 120
    
    # Health scoring settings
    HEALTH_SCORE_WEIGHTS: dict = {
        "ph": 0.20,
        "nitrogen": 0.20,
        "phosphorus": 0.15,
        "potassium": 0.15,
        "organic_matter": 0.15,
        "moisture": 0.15
    }
    
    class Config:
        env_prefix = "SOIL_"
        case_sensitive = True


soil_config = SoilServiceConfig()
