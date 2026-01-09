"""
Soil service core module.
"""

from apps.soil_service.core.config import soil_config, SoilServiceConfig
from apps.soil_service.core.constants import (
    SOIL_OPTIMAL_RANGES,
    SOIL_PARAMETER_WEIGHTS,
    GROWTH_STAGES,
)

__all__ = [
    "soil_config",
    "SoilServiceConfig",
    "SOIL_OPTIMAL_RANGES",
    "SOIL_PARAMETER_WEIGHTS",
    "GROWTH_STAGES",
]
