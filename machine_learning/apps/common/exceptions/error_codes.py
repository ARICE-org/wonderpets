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

from enum import Enum
from typing import Dict


class ErrorCode(str, Enum):
    """Error codes for ML Service."""
    
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
