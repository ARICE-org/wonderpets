from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load .env from the same directory or parent
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv()  # fallback to cwd

class Settings(BaseModel):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "appuser")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "apppassword")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "appdb")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        # Default to local SQLite for dev without Docker; Docker will override with Postgres
        "sqlite:///./app.db",
    )
    CORS_ORIGINS: str | None = os.getenv("CORS_ORIGINS")

settings = Settings()
