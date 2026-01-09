"""
Dependency injection for soil service.
"""

from functools import lru_cache
from apps.soil_service.services.soil_analysis_service import SoilAnalysisService


@lru_cache()
def get_soil_service() -> SoilAnalysisService:
    """
    Get soil analysis service instance (singleton).
    """
    service = SoilAnalysisService()
    return service
