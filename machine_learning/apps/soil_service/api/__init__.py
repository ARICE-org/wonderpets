"""
Soil service API module.
"""

from apps.soil_service.api.endpoints import router
from apps.soil_service.api.dependencies import get_soil_service

__all__ = ["router", "get_soil_service"]
