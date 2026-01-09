"""
Recommendation service API schemas.
"""

from apps.recommendation_service.api.schemas.requests import (
    RecommendationRequest,
    PlantingScheduleRequest,
    SoilDataInput,
    WeatherDataInput,
    LocationInput,
)
from apps.recommendation_service.api.schemas.responses import (
    RecommendationResponse,
    PlantingScheduleResponse,
    RiceVarietyRecommendation,
)

__all__ = [
    "RecommendationRequest",
    "PlantingScheduleRequest",
    "SoilDataInput",
    "WeatherDataInput",
    "LocationInput",
    "RecommendationResponse",
    "PlantingScheduleResponse",
    "RiceVarietyRecommendation",
]
