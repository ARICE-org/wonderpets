"""
Recommendation service API dependencies.
"""

from functools import lru_cache

from apps.recommendation_service.services.recommendation_service import RecommendationService


@lru_cache()
def get_recommendation_service() -> RecommendationService:
    """Get or create recommendation service singleton."""
    return RecommendationService()
