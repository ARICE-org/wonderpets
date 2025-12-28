"""
Configuration settings for the ML service
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """ML Service configuration settings"""
    
    # Application
    APP_NAME: str = "ARICE ML Service"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/arice"
    )
    
    # Model paths
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./trained_models")
    RECOMMENDATION_MODEL_PATH: str = ""
    WEATHER_MODEL_PATH: str = ""
    SOIL_HEALTH_MODEL_PATH: str = ""
    SOIL_FORECAST_MODEL_PATH: str = ""
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:8081", "http://localhost:3000"]
    
    # External APIs
    WEATHER_API_KEY: str = ""
    WEATHER_API_URL: str = ""
    
    # Model parameters
    SOIL_FORECAST_HORIZON_DAYS: int = 90  # 3-month forecast for rice planting season
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set default model paths based on MODEL_PATH
        if not self.RECOMMENDATION_MODEL_PATH:
            self.RECOMMENDATION_MODEL_PATH = f"{self.MODEL_PATH}/recommendation"
        if not self.WEATHER_MODEL_PATH:
            self.WEATHER_MODEL_PATH = f"{self.MODEL_PATH}/weather"
        if not self.SOIL_HEALTH_MODEL_PATH:
            self.SOIL_HEALTH_MODEL_PATH = f"{self.MODEL_PATH}/soil"
        if not self.SOIL_FORECAST_MODEL_PATH:
            self.SOIL_FORECAST_MODEL_PATH = f"{self.MODEL_PATH}/soil"


settings = Settings()
