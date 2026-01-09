"""
Global Settings Configuration

Centralized settings for all ARICE ML services.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Global settings for ML services."""
    
    # Application settings
    APP_NAME: str = "ARICE ML Services"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    
    # Model paths
    MODELS_BASE_PATH: str = "./trained_models"
    SOIL_MODEL_PATH: str = "./trained_models/soil"
    WEATHER_MODEL_PATH: str = "./trained_models/weather"
    RECOMMENDATION_MODEL_PATH: str = "./trained_models/recommendation"
    
    # Data paths
    DATA_BASE_PATH: str = "./data"
    
    # Service ports
    SOIL_SERVICE_PORT: int = 8001
    WEATHER_SERVICE_PORT: int = 8002
    RECOMMENDATION_SERVICE_PORT: int = 8003
    
    # API settings
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "*"
    
    # Rate limiting (uses ML-specific env vars with fallback)
    ML_RATE_LIMIT_STANDARD_REQUESTS: int = 60
    ML_RATE_LIMIT_STANDARD_WINDOW: int = 60
    ML_RATE_LIMIT_PREDICTION_REQUESTS: int = 30
    ML_RATE_LIMIT_PREDICTION_WINDOW: int = 60
    ML_RATE_LIMIT_BATCH_REQUESTS: int = 10
    ML_RATE_LIMIT_BATCH_WINDOW: int = 60
    RATE_LIMIT_ENABLED: bool = True
    
    # Legacy alias for backwards compatibility
    @property
    def RATE_LIMIT_REQUESTS_PER_MINUTE(self) -> int:
        return self.ML_RATE_LIMIT_STANDARD_REQUESTS
    
    # Cache settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600
    
    # External services
    BACKEND_URL: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
