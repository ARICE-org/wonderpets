from pydantic_settings import BaseSettings
from pathlib import Path

# Path to the root project folder (where .env lives)
BASE_DIR = Path(__file__).resolve().parents[3]  # backend/app/config -> backend/app -> backend -> wonderpets
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    CORS_ORIGINS: str

    class Config:
        env_file_encoding = "utf-8"  # optional

settings = Settings()

DATABASE_URL = (
    f"postgresql+psycopg2://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)
