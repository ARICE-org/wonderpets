"""
Validation and processing exceptions for ML services.
"""

from typing import Optional, Dict, Any, List
from apps.common.exceptions.error_codes import ErrorCode, ERROR_STATUS_CODES


class ValidationError(Exception):
    """
    Raised when input validation fails.
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        errors: Optional[List[str]] = None
    ):
        self.message = message
        self.field = field
        self.errors = errors or []
        self.error_code = ErrorCode.VAL_INVALID_INPUT
        self.status_code = 400
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "error": True,
            "error_code": self.error_code.value,
            "message": self.message,
            "field": self.field,
            "validation_errors": self.errors
        }


class ForecastError(Exception):
    """
    Raised when forecast generation fails.
    """
    
    def __init__(
        self,
        message: str,
        forecast_type: str = "unknown",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.forecast_type = forecast_type
        self.details = details or {}
        self.error_code = ErrorCode.PROC_FORECAST_FAILED
        self.status_code = 422
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "error": True,
            "error_code": self.error_code.value,
            "message": self.message,
            "forecast_type": self.forecast_type,
            "details": self.details
        }


class AnalysisError(Exception):
    """
    Raised when analysis processing fails.
    """
    
    def __init__(
        self,
        message: str,
        analysis_type: str = "unknown",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.analysis_type = analysis_type
        self.details = details or {}
        self.error_code = ErrorCode.PROC_ANALYSIS_FAILED
        self.status_code = 422
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "error": True,
            "error_code": self.error_code.value,
            "message": self.message,
            "analysis_type": self.analysis_type,
            "details": self.details
        }


class RealignmentError(Exception):
    """
    Raised when forecast realignment fails.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.details = details or {}
        self.error_code = ErrorCode.PROC_REALIGNMENT_FAILED
        self.status_code = 422
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "error": True,
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }


class HealthScoreError(Exception):
    """
    Raised when health score calculation fails.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.details = details or {}
        self.error_code = ErrorCode.PROC_HEALTH_SCORE_FAILED
        self.status_code = 422
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "error": True,
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }
