"""
Recommendation service configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class RecommendationServiceConfig(BaseSettings):
    """Configuration specific to recommendation service."""
    
    # Model paths
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./trained_models/recommendation")
    VARIETY_MODEL_FILE: str = "rice_variety_model.pkl"
    
    # Recommendation settings
    DEFAULT_TOP_K: int = 5
    MAX_TOP_K: int = 20
    CONFIDENCE_THRESHOLD: float = 0.3
    
    # Feature settings
    USE_WEATHER_FEATURES: bool = True
    USE_SOIL_FEATURES: bool = True
    USE_LOCATION_FEATURES: bool = True
    
    class Config:
        env_prefix = "RECOMMENDATION_"
        case_sensitive = True


recommendation_config = RecommendationServiceConfig()
