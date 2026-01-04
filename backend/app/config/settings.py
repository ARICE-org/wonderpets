from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    CORS_ORIGINS: str
    
    # ML Service Configuration
    ML_SERVICE_URL: str = "http://localhost:8001"  # Default for local development
    ML_SERVICE_TIMEOUT: int = 30  # Timeout in seconds

    class Config:
        env_file = "../.env"
        extra = "ignore"  # ignore extra env vars

settings = Settings()

DATABASE_URL = (
    f"postgresql+psycopg2://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)
