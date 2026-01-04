"""
ARICE ML Service - Custom Exceptions

Defines error types and their corresponding HTTP status codes
for consistent error handling across the ML service.
"""

from enum import Enum
from typing import Optional, Dict, Any


class ErrorCode(str, Enum):
    """
    Error codes for ML Service.
    
    Format: CATEGORY_SPECIFIC_ERROR
    Categories:
        - VAL: Validation errors (400)
        - AUTH: Authentication errors (401)
        - PERM: Permission errors (403)
        - NFD: Not Found errors (404)
        - CONF: Conflict errors (409)
        - PROC: Processing errors (422)
        - SRV: Server/Internal errors (500)
        - EXT: External service errors (502/503)
    """
    
    # Validation Errors (400)
    VAL_INVALID_INPUT = "VAL_001"
    VAL_MISSING_FIELD = "VAL_002"
    VAL_INVALID_RANGE = "VAL_003"
    VAL_INVALID_DATE = "VAL_004"
    VAL_INVALID_FORMAT = "VAL_005"
    VAL_EMPTY_DATA = "VAL_006"
    
    # Not Found Errors (404)
    NFD_MODEL_NOT_FOUND = "NFD_001"
    NFD_FORECAST_NOT_FOUND = "NFD_002"
    NFD_DATA_NOT_FOUND = "NFD_003"
    
    # Processing Errors (422)
    PROC_INSUFFICIENT_DATA = "PROC_001"
    PROC_FORECAST_FAILED = "PROC_002"
    PROC_ANALYSIS_FAILED = "PROC_003"
    PROC_REALIGNMENT_FAILED = "PROC_004"
    PROC_HEALTH_SCORE_FAILED = "PROC_005"
    
    # Server Errors (500)
    SRV_INTERNAL_ERROR = "SRV_001"
    SRV_MODEL_LOAD_ERROR = "SRV_002"
    SRV_PREDICTION_ERROR = "SRV_003"
    SRV_DATABASE_ERROR = "SRV_004"
    
    # External Service Errors (502/503)
    EXT_SERVICE_UNAVAILABLE = "EXT_001"
    EXT_TIMEOUT = "EXT_002"
    EXT_CONNECTION_FAILED = "EXT_003"


# Error code to HTTP status code mapping
ERROR_STATUS_CODES: Dict[str, int] = {
    # Validation (400)
    ErrorCode.VAL_INVALID_INPUT: 400,
    ErrorCode.VAL_MISSING_FIELD: 400,
    ErrorCode.VAL_INVALID_RANGE: 400,
    ErrorCode.VAL_INVALID_DATE: 400,
    ErrorCode.VAL_INVALID_FORMAT: 400,
    ErrorCode.VAL_EMPTY_DATA: 400,
    
    # Not Found (404)
    ErrorCode.NFD_MODEL_NOT_FOUND: 404,
    ErrorCode.NFD_FORECAST_NOT_FOUND: 404,
    ErrorCode.NFD_DATA_NOT_FOUND: 404,
    
    # Processing (422)
    ErrorCode.PROC_INSUFFICIENT_DATA: 422,
    ErrorCode.PROC_FORECAST_FAILED: 422,
    ErrorCode.PROC_ANALYSIS_FAILED: 422,
    ErrorCode.PROC_REALIGNMENT_FAILED: 422,
    ErrorCode.PROC_HEALTH_SCORE_FAILED: 422,
    
    # Server (500)
    ErrorCode.SRV_INTERNAL_ERROR: 500,
    ErrorCode.SRV_MODEL_LOAD_ERROR: 500,
    ErrorCode.SRV_PREDICTION_ERROR: 500,
    ErrorCode.SRV_DATABASE_ERROR: 500,
    
    # External (502/503)
    ErrorCode.EXT_SERVICE_UNAVAILABLE: 503,
    ErrorCode.EXT_TIMEOUT: 504,
    ErrorCode.EXT_CONNECTION_FAILED: 502,
}


class MLServiceError(Exception):
    """
    Base exception for ML Service errors.
    
    Attributes:
        error_code: The specific error code from ErrorCode enum
        message: Human-readable error message
        details: Additional error details (optional)
        status_code: HTTP status code to return
    """
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = ERROR_STATUS_CODES.get(error_code, 500)
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response."""
        return {
            "error": True,
            "error_code": self.error_code.value,
            "error_type": self.error_code.name,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }


class ValidationError(MLServiceError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        error_code = ErrorCode.VAL_INVALID_INPUT
        if field:
            details = details or {}
            details["field"] = field
        super().__init__(error_code, message, details)


class ModelNotFoundError(MLServiceError):
    """Raised when a required ML model is not loaded."""
    
    def __init__(self, model_name: str, details: Optional[Dict] = None):
        message = f"ML model '{model_name}' not found or not loaded"
        details = details or {}
        details["model_name"] = model_name
        super().__init__(ErrorCode.NFD_MODEL_NOT_FOUND, message, details)


class ForecastError(MLServiceError):
    """Raised when forecast generation fails."""
    
    def __init__(self, message: str, forecast_type: str = "unknown", details: Optional[Dict] = None):
        details = details or {}
        details["forecast_type"] = forecast_type
        super().__init__(ErrorCode.PROC_FORECAST_FAILED, message, details)


class AnalysisError(MLServiceError):
    """Raised when soil analysis fails."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(ErrorCode.PROC_ANALYSIS_FAILED, message, details)


class RealignmentError(MLServiceError):
    """Raised when forecast realignment fails."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(ErrorCode.PROC_REALIGNMENT_FAILED, message, details)


class HealthScoreError(MLServiceError):
    """Raised when health score calculation fails."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(ErrorCode.PROC_HEALTH_SCORE_FAILED, message, details)


class InsufficientDataError(MLServiceError):
    """Raised when there's not enough data for analysis."""
    
    def __init__(self, message: str, required: int = 0, provided: int = 0, details: Optional[Dict] = None):
        details = details or {}
        details["required_count"] = required
        details["provided_count"] = provided
        super().__init__(ErrorCode.PROC_INSUFFICIENT_DATA, message, details)


class ExternalServiceError(MLServiceError):
    """Raised when an external service call fails."""
    
    def __init__(self, service_name: str, message: str, details: Optional[Dict] = None):
        details = details or {}
        details["service_name"] = service_name
        super().__init__(ErrorCode.EXT_SERVICE_UNAVAILABLE, message, details)


# Error messages for common scenarios
ERROR_MESSAGES = {
    "invalid_ph": "pH value must be between 0 and 14",
    "invalid_nitrogen": "Nitrogen (ppm) must be a positive value",
    "invalid_phosphorus": "Phosphorus (ppm) must be a positive value",
    "invalid_potassium": "Potassium (meq) must be a positive value",
    "invalid_moisture": "Soil moisture must be between 0 and 100 percent",
    "invalid_organic_matter": "Organic matter must be between 0 and 100 percent",
    "invalid_date_format": "Date must be in ISO format (YYYY-MM-DD)",
    "invalid_date_range": "Planting date must be in the future or within current season",
    "empty_readings": "At least one sensor reading is required",
    "model_not_ready": "ML model is not ready. Please wait for initialization.",
    "forecast_horizon_invalid": "Forecast horizon must be between 7 and 180 days",
    "insufficient_history": "At least 7 days of historical data required for accurate forecasting",
}
