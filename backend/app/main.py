from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routers.ping import router as ping_router
from app.routers.farmer import router as farmer_router
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.db import Base, engine
import logging

logger = logging.getLogger("uvicorn")

# OpenAPI/Swagger configuration
tags_metadata = [
    {
        "name": "Health",
        "description": "Endpoints for health checks and service liveness.",
    },
    {
        "name": "Farmers",
        "description": "Endpoints for farmer operations.",
    },
    {
        "name": "Users",
        "description": "Endpoints for User operations.",
    },
    {
        "name": "Auth",
        "description": "Endpoints for JWT OAuth operations.",
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

@app.on_event("startup")
def on_startup():
    # Create tables if they do not exist
    Base.metadata.create_all(bind=engine)
    logger.info("-------------------------------")
    logger.info("✅ ARICE API is up and running! 🚀")
    logger.info("📚 Swagger UI available at /docs")
    logger.info("📘 ReDoc available at /redoc")
    logger.info(f"Connected to: postgresql://{settings.POSTGRES_USER}:@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    logger.info("-------------------------------")

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

# Routers
app.include_router(ping_router)
app.include_router(farmer_router)
app.include_router(user_router)
app.include_router(auth_router)
