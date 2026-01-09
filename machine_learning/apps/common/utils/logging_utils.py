"""
Logging utilities for ML services.

Provides structured logging with colored console output and detailed error tracking.
"""

import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps


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
        color = self.LEVEL_COLORS.get(record.levelno, Colors.WHITE)
        record.levelname = f"{color}{record.levelname}{Colors.RESET}"
        record.asctime = f"{Colors.BLUE}{self.formatTime(record, self.datefmt)}{Colors.RESET}"
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
        context: Additional context for the error
        include_traceback: Whether to include traceback
        
    Returns:
        Error information dictionary
    """
    error_info = {
        "error_type": type(error).__name__,
        "message": str(error),
        "timestamp": datetime.now().isoformat(),
        "context": context or {},
    }
    
    # Add error code if available
    if hasattr(error, "error_code"):
        error_info["error_code"] = str(error.error_code.value) if hasattr(error.error_code, "value") else str(error.error_code)
    
    if include_traceback:
        error_info["traceback"] = traceback.format_exc()
    
    logger.error(
        f"{error_info['error_type']}: {error_info['message']} | Context: {context}"
    )
    
    return error_info


def log_request(
    endpoint: str,
    method: str,
    params: Optional[Dict[str, Any]] = None
) -> None:
    """Log an incoming API request."""
    logger.info(f"REQUEST | {method} {endpoint} | Params: {params or {}}")


def log_response(
    endpoint: str,
    status_code: int,
    duration_ms: Optional[float] = None
) -> None:
    """Log an API response."""
    duration_str = f" | Duration: {duration_ms:.2f}ms" if duration_ms else ""
    logger.info(f"RESPONSE | {endpoint} | Status: {status_code}{duration_str}")


def log_ml_prediction(
    model_name: str,
    input_summary: str,
    prediction_summary: str,
    duration_ms: Optional[float] = None
) -> None:
    """Log an ML prediction."""
    duration_str = f" | Duration: {duration_ms:.2f}ms" if duration_ms else ""
    logger.info(
        f"PREDICTION | {model_name} | Input: {input_summary} | "
        f"Output: {prediction_summary}{duration_str}"
    )
