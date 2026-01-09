"""
Global error handling middleware.
"""

from typing import Callable
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback

from apps.common.exceptions import (
    MLServiceError,
    ValidationError,
    ForecastError,
    AnalysisError,
)

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch and handle exceptions globally.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            return await call_next(request)
        except Exception as e:
            return handle_exception(request, e)


def handle_exception(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle an exception and return appropriate JSON response.
    """
    # Log the error
    logger.error(
        f"Error processing request {request.method} {request.url.path}: "
        f"{type(exc).__name__}: {str(exc)}"
    )
    logger.debug(traceback.format_exc())
    
    # MLServiceError and subclasses
    if isinstance(exc, MLServiceError):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )
    
    # ValidationError
    if isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.to_dict()
        )
    
    # ForecastError
    if isinstance(exc, ForecastError):
        return JSONResponse(
            status_code=422,
            content=exc.to_dict()
        )
    
    # AnalysisError
    if isinstance(exc, AnalysisError):
        return JSONResponse(
            status_code=422,
            content=exc.to_dict()
        )
    
    # Generic ValueError
    if isinstance(exc, ValueError):
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "error_code": "VAL_001",
                "message": str(exc)
            }
        )
    
    # Generic exception
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "error_code": "SRV_001",
            "message": "Internal server error",
            "details": str(exc) if logger.level <= logging.DEBUG else None
        }
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers with a FastAPI application.
    """
    
    @app.exception_handler(MLServiceError)
    async def ml_service_error_handler(request: Request, exc: MLServiceError):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content=exc.to_dict()
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "error_code": "VAL_001",
                "message": str(exc)
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "error_code": "SRV_001",
                "message": "Internal server error"
            }
        )


# Convenience function for use with app.middleware
async def error_handler_middleware(request: Request, call_next: Callable):
    """Error handler as a middleware function."""
    try:
        return await call_next(request)
    except Exception as e:
        return handle_exception(request, e)
