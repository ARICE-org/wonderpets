"""
ARICE ML Service - Common Utilities

Shared exceptions, logging, and utility classes.
"""

from app.common.exceptions import (
    ErrorCode,
    ERROR_STATUS_CODES,
    ERROR_MESSAGES,
    MLServiceError,
    ValidationError,
    ModelNotFoundError,
    ForecastError,
    AnalysisError,
    RealignmentError,
    HealthScoreError,
    InsufficientDataError,
    ExternalServiceError,
)
from app.common.logger import logger, log_error, log_request, log_response, log_ml_prediction

__all__ = [
    # Error codes
    "ErrorCode",
    "ERROR_STATUS_CODES",
    "ERROR_MESSAGES",
    # Exceptions
    "MLServiceError",
    "ValidationError",
    "ModelNotFoundError",
    "ForecastError",
    "AnalysisError",
    "RealignmentError",
    "HealthScoreError",
    "InsufficientDataError",
    "ExternalServiceError",
    # Logging
    "logger",
    "log_error",
    "log_request",
    "log_response",
    "log_ml_prediction",
]
