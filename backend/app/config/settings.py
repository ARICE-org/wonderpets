from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
from pathlib import Path


ENV_FILE = Path(__file__).resolve().parents[3] / ".env"

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    CORS_ORIGINS: str
    MONGO_DB: str = "arice"
    MONGO_DB_URI: Optional[str] = None
    MONGO_URI: Optional[str] = None
    
    # Server Configuration
    PORT: int = 8000  # Backend server port for internal API calls
    
    # ML Service Configuration (Legacy - single URL for backward compatibility)
    ML_SERVICE_URL: str = "http://localhost:8001"  
    ML_SERVICE_TIMEOUT: int = 30  
    
    # Per-domain ML Service URLs (new architecture)
    SOIL_ML_URL: Optional[str] = None  # Falls back to ML_SERVICE_URL if not set
    WEATHER_ML_URL: Optional[str] = None  # Falls back to ML_SERVICE_URL if not set
    RECOMMENDATION_ML_URL: Optional[str] = None  # Falls back to ML_SERVICE_URL if not set
    
    # Rate Limiting Configuration
    RATE_LIMIT_STANDARD_REQUESTS: int = 100  
    RATE_LIMIT_STANDARD_WINDOW: int = 60     
    RATE_LIMIT_AUTH_REQUESTS: int = 10       
    RATE_LIMIT_AUTH_WINDOW: int = 60         
    RATE_LIMIT_RELAXED_REQUESTS: int = 1000  
    RATE_LIMIT_RELAXED_WINDOW: int = 60      
    RATE_LIMIT_STRICT_REQUESTS: int = 5      
    RATE_LIMIT_STRICT_WINDOW: int = 60       

    class Config:
        env_file = str(ENV_FILE)
        extra = "ignore"  # ignore extra env vars

    @property
    def mongo_db(self) -> str:
        return self.MONGO_DB

    @property
    def mongo_uri(self) -> str:
        return self.MONGO_DB_URI or self.MONGO_URI or "mongodb://mongodb:27017"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

DATABASE_URL = (
    f"postgresql+psycopg2://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)
