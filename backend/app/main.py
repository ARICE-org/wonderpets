from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.routers.ping import router as ping_router
from app.db import Base, engine

app = FastAPI()

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

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

# Routers
app.include_router(ping_router)
