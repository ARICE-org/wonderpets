from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.middleware.rate_limiter import RateLimitMiddleware, FixedWindowRateLimiter
from app.routers.ping import router as ping_router
from app.routers.farmer import router as farmer_router
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.soil_sensor_device import router as soil_sensor_router
from app.routers.soil_data import router as soil_data_router
from app.routers.weather import router as weather_router
from app.routers.soil_forecast import router as soil_forecast_router
from app.db import Base, engine
import logging
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger("uvicorn")

logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(logs_dir, exist_ok=True)

log_file = os.path.join(logs_dir, f"backend_requests_{datetime.now().strftime('%Y%m%d')}.log")
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Custom formatter: DateTime - Endpoint - Client - Response
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

logging.getLogger("uvicorn.access").addHandler(file_handler)
logger.addHandler(file_handler)

# OpenAPI/Swagger configuration
tags_metadata = [
    {
        "name": "Auth",
        "description": "Endpoints for JWT OAuth operations.",
    },
    {
        "name": "Users",
        "description": "Endpoints for User operations.",
    },
    {
        "name": "Farmers",
        "description": "Endpoints for farmer operations.",
    },
    {
        "name": "Weather",
        "description": "Endpoints for weather data operations.",
    },
    {
        "name": "Sensors",
        "description": "Endpoints for sensors data operations.",
    },
    {
        "name": "Soil Data",
        "description": "Endpoints for soil data operations.",
    },
    {
        "name": "Soil Forecast",
        "description": "Endpoints for soil forecast and analysis.",
    }
]

app = FastAPI(
    title="ARICE API",
    description="REST API for the ARICE backend. Swagger UI is available at /docs and ReDoc at /redoc.",
    version="0.0.1",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
if settings.CORS_ORIGINS:
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
else:
    # Allow all origins in development if not specified
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Rate Limiter Middleware (Fixed Window Algorithm - uses ENV config)
rate_limiter = FixedWindowRateLimiter(
    requests_per_window=settings.RATE_LIMIT_STANDARD_REQUESTS,
    window_size_seconds=settings.RATE_LIMIT_STANDARD_WINDOW
)
app.add_middleware(
    RateLimitMiddleware,
    limiter=rate_limiter,
    exclude_paths=["/health", "/docs", "/redoc", "/openapi.json"]
)

@app.on_event("startup")
def on_startup():
    # Create tables if they do not exist. Wrap in try/except to avoid hard crash
    # when the DB host is not reachable (common during local development when
    # Postgres runs in Docker and the backend runs on the host).
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("-------------------------------")
        logger.info("✅ ARICE API is up and running! 🚀")
        logger.info("📚 Swagger UI available at /docs")
        logger.info("📘 ReDoc available at /redoc")
        logger.info(f"Connected to: postgresql://{settings.POSTGRES_USER}:@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
        logger.info("-------------------------------")
    except Exception as exc:  # pragma: no cover - operational startup error
        # Log a helpful message and continue. This makes it easier to run the
        # backend locally without a reachable DB while preserving visibility
        # to the error for debugging.
        logger.error("Failed to connect to the database during startup.")
        logger.error("Ensure POSTGRES_HOST is reachable from this process (check .env and docker-compose).")
        logger.error(f"DB connect info: host={settings.POSTGRES_HOST} port={settings.POSTGRES_PORT} db={settings.POSTGRES_DB} user={settings.POSTGRES_USER}")
        logger.exception(exc)


# Routers - All endpoints prefixed with /api
# app.include_router(ping_router, prefix="/api")
app.include_router(farmer_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(soil_sensor_router, prefix="/api")
app.include_router(soil_data_router, prefix="/api")
app.include_router(weather_router, prefix="/api")
app.include_router(soil_forecast_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}