"""
Model-related exceptions for ML services.
"""

from typing import Optional, Dict, Any
from apps.common.exceptions.error_codes import ErrorCode, ERROR_STATUS_CODES


class MLServiceError(Exception):
    """
    Base exception for ML Service errors.
    
    Attributes:
        error_code: The specific error code from ErrorCode enum
        message: Human-readable error message
        details: Additional error context
        status_code: HTTP status code
    """
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.SRV_INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = ERROR_STATUS_CODES.get(error_code, 500)
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response."""
        return {
            "error": True,
            "error_code": self.error_code.value if isinstance(self.error_code, ErrorCode) else self.error_code,
            "message": self.message,
            "details": self.details
        }


class ModelNotFoundError(MLServiceError):
    """Raised when a required model is not found."""
    
    def __init__(self, model_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Model not found: {model_name}",
            error_code=ErrorCode.NFD_MODEL_NOT_FOUND,
            details=details
        )


class ModelLoadError(MLServiceError):
    """Raised when a model fails to load."""
    
    def __init__(self, model_name: str, reason: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to load model '{model_name}': {reason}",
            error_code=ErrorCode.SRV_MODEL_LOAD_ERROR,
            details=details
        )


class PredictionError(MLServiceError):
    """Raised when model prediction fails."""
    
    def __init__(self, model_name: str, reason: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Prediction failed for '{model_name}': {reason}",
            error_code=ErrorCode.SRV_PREDICTION_ERROR,
            details=details
        )
