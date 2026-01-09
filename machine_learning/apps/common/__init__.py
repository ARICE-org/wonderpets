"""
Common utilities shared across all ML services.

This module contains:
- Base classes for models, services, and trainers
- Shared constants and configuration
- Exception classes and error codes
- Utility functions (logging, metrics, model I/O)
- Input validators
"""

from apps.common.base.base_model import BaseMLModel
from apps.common.base.base_service import BaseMLService
from apps.common.base.base_trainer import BaseTrainer
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
from apps.common.exceptions.error_codes import ErrorCode, ERROR_STATUS_CODES
from apps.common.utils.logging_utils import (
    logger,
    setup_logger,
    log_error,
    log_request,
    log_response,
    log_ml_prediction,
)
from apps.common.utils.metrics import ModelMetrics
from apps.common.utils.model_io import ModelIO
from apps.common.validators.input_validators import InputValidator

__all__ = [
    # Base classes
    "BaseMLModel",
    "BaseMLService",
    "BaseTrainer",
    # Exceptions
    "MLServiceError",
    "ModelNotFoundError",
    "ModelLoadError",
    "PredictionError",
    "ValidationError",
    "ForecastError",
    "AnalysisError",
    "RealignmentError",
    "HealthScoreError",
    "ErrorCode",
    "ERROR_STATUS_CODES",
    # Utils
    "logger",
    "setup_logger",
    "log_error",
    "log_request",
    "log_response",
    "log_ml_prediction",
    "ModelMetrics",
    "ModelIO",
    # Validators
    "InputValidator",
]
