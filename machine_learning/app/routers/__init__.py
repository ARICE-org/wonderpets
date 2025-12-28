from .recommendation import router as recommendation_router
from .weather import router as weather_router
from .soil import router as soil_router

__all__ = [
    "recommendation_router",
    "weather_router",
    "soil_router"
]
