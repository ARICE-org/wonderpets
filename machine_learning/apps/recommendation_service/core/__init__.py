"""
Recommendation service core module.
"""

from apps.recommendation_service.core.config import recommendation_config, RecommendationServiceConfig
from apps.recommendation_service.core.constants import (
    RICE_VARIETIES,
    VARIETY_REQUIREMENTS,
    PLANTING_SEASONS,
)

__all__ = [
    "recommendation_config",
    "RecommendationServiceConfig",
    "RICE_VARIETIES",
    "VARIETY_REQUIREMENTS",
    "PLANTING_SEASONS",
]
