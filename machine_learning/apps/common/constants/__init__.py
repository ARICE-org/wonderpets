"""
Shared constants for ML services.
"""

from apps.common.constants.model_config import (
    DEFAULT_HYPERPARAMETERS,
    MODEL_VERSIONS,
)
from apps.common.constants.thresholds import (
    HEALTH_SCORE_THRESHOLDS,
    SOIL_PARAMETER_RANGES,
    WEATHER_PARAMETER_RANGES,
)

__all__ = [
    "DEFAULT_HYPERPARAMETERS",
    "MODEL_VERSIONS",
    "HEALTH_SCORE_THRESHOLDS",
    "SOIL_PARAMETER_RANGES",
    "WEATHER_PARAMETER_RANGES",
]
