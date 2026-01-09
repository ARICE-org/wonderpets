"""
Exception classes and error codes for ML services.
"""

from apps.common.exceptions.error_codes import ErrorCode, ERROR_STATUS_CODES
from apps.common.exceptions.model_exceptions import (
    MLServiceError,
    ModelNotFoundError,
    ModelLoadError,
    PredictionError,
)
from apps.common.exceptions.validation_exceptions import (
    ValidationError,
    ForecastError,
    AnalysisError,
    RealignmentError,
    HealthScoreError,
)

__all__ = [
    "ErrorCode",
    "ERROR_STATUS_CODES",
    "MLServiceError",
    "ModelNotFoundError",
    "ModelLoadError",
    "PredictionError",
    "ValidationError",
    "ForecastError",
    "AnalysisError",
    "RealignmentError",
    "HealthScoreError",
]
