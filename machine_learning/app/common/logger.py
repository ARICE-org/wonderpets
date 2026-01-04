"""
ARICE ML Service - Logging Configuration

Provides structured logging for the ML service with colored console output
and detailed error tracking.
"""

import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps

from app.common.exceptions import MLServiceError, ErrorCode


# ANSI color codes for console output
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    LEVEL_COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.RED + Colors.BOLD,
    }
    
    def format(self, record):
        # Add color to level name
        color = self.LEVEL_COLORS.get(record.levelno, Colors.WHITE)
        record.levelname = f"{color}{record.levelname}{Colors.RESET}"
        
        # Add timestamp color
        record.asctime = f"{Colors.BLUE}{self.formatTime(record, self.datefmt)}{Colors.RESET}"
        
        # Format the message
        formatted = super().format(record)
        return formatted


def setup_logger(name: str = "ml-service") -> logging.Logger:
    """
    Set up and configure the ML service logger.
    
    Args:
        name: Logger name
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Format: [TIMESTAMP] LEVEL | module:line | message
    formatter = ColoredFormatter(
        fmt="[%(asctime)s] %(levelname)s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger()


def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    include_traceback: bool = True
) -> Dict[str, Any]:
    """
    Log an error with detailed information.
    
    Args:
        error: The exception that occurred
        context: Additional context information
        include_traceback: Whether to include the full traceback
    
    Returns:
        Dictionary with error details for API response
    """
    context = context or {}
    timestamp = datetime.utcnow().isoformat()
    
    # Determine error type and code
    if isinstance(error, MLServiceError):
        error_code = error.error_code.value
        error_type = error.error_code.name
        status_code = error.status_code
        message = error.message
        details = error.details
    else:
        error_code = ErrorCode.SRV_INTERNAL_ERROR.value
        error_type = ErrorCode.SRV_INTERNAL_ERROR.name
        status_code = 500
        message = str(error)
        details = {}
    
    # Build error log message
    log_message = f"""
{'='*60}
{Colors.RED}ERROR OCCURRED{Colors.RESET}
{'='*60}
Timestamp:   {timestamp}
Error Code:  {error_code}
Error Type:  {error_type}
Status Code: {status_code}
Message:     {message}
"""
    
    if details:
        log_message += f"Details:     {details}\n"
    
    if context:
        log_message += f"Context:     {context}\n"
    
    if include_traceback:
        tb = traceback.format_exc()
        if tb and tb.strip() != "NoneType: None":
            log_message += f"\nTraceback:\n{tb}"
    
    log_message += f"{'='*60}"
    
    # Log to console
    logger.error(log_message)
    
    # Return structured error for API response
    return {
        "error": True,
        "error_code": error_code,
        "error_type": error_type,
        "message": message,
        "details": details,
        "timestamp": timestamp,
        "status_code": status_code
    }


def log_request(
    endpoint: str,
    method: str,
    request_data: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
):
    """
    Log an incoming API request.
    
    Args:
        endpoint: The API endpoint being called
        method: HTTP method (GET, POST, etc.)
        request_data: Request body/parameters (will be sanitized)
        request_id: Optional request identifier
    """
    # Sanitize sensitive data
    safe_data = _sanitize_log_data(request_data) if request_data else {}
    
    log_message = f"{Colors.CYAN}→ REQUEST{Colors.RESET} [{method}] {endpoint}"
    
    if request_id:
        log_message += f" (ID: {request_id})"
    
    if safe_data:
        # Truncate large data
        data_str = str(safe_data)
        if len(data_str) > 500:
            data_str = data_str[:500] + "..."
        log_message += f"\n  Data: {data_str}"
    
    logger.info(log_message)


def log_response(
    endpoint: str,
    status_code: int,
    response_data: Optional[Dict[str, Any]] = None,
    duration_ms: Optional[float] = None
):
    """
    Log an API response.
    
    Args:
        endpoint: The API endpoint
        status_code: HTTP status code
        response_data: Response body (will be truncated)
        duration_ms: Request duration in milliseconds
    """
    # Choose color based on status code
    if status_code < 300:
        status_color = Colors.GREEN
    elif status_code < 400:
        status_color = Colors.YELLOW
    else:
        status_color = Colors.RED
    
    log_message = f"{Colors.MAGENTA}← RESPONSE{Colors.RESET} {status_color}{status_code}{Colors.RESET} {endpoint}"
    
    if duration_ms:
        log_message += f" ({duration_ms:.2f}ms)"
    
    if response_data and status_code >= 400:
        # Log error response details
        data_str = str(response_data)
        if len(data_str) > 300:
            data_str = data_str[:300] + "..."
        log_message += f"\n  Error: {data_str}"
    
    if status_code < 400:
        logger.info(log_message)
    else:
        logger.warning(log_message)


def _sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove sensitive fields from log data.
    
    Args:
        data: Original data dictionary
    
    Returns:
        Sanitized copy of the data
    """
    sensitive_fields = {"password", "token", "api_key", "secret", "authorization"}
    
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_fields:
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_log_data(value)
        elif isinstance(value, list) and len(value) > 10:
            sanitized[key] = f"[List with {len(value)} items]"
        else:
            sanitized[key] = value
    
    return sanitized


def log_ml_prediction(
    model_name: str,
    input_summary: str,
    prediction_summary: str,
    confidence: Optional[float] = None,
    duration_ms: Optional[float] = None
):
    """
    Log an ML prediction event.
    
    Args:
        model_name: Name of the ML model used
        input_summary: Brief description of input
        prediction_summary: Brief description of output
        confidence: Model confidence score (if applicable)
        duration_ms: Prediction duration in milliseconds
    """
    log_message = f"{Colors.CYAN}🤖 ML PREDICTION{Colors.RESET} [{model_name}]"
    log_message += f"\n  Input: {input_summary}"
    log_message += f"\n  Output: {prediction_summary}"
    
    if confidence is not None:
        log_message += f"\n  Confidence: {confidence:.2%}"
    
    if duration_ms:
        log_message += f"\n  Duration: {duration_ms:.2f}ms"
    
    logger.info(log_message)
