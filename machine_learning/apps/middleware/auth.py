"""
Authentication middleware (placeholder for future use).
"""

from typing import Callable, Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for API key validation.
    
    Currently a placeholder - implement as needed.
    """
    
    def __init__(
        self,
        app,
        api_key: Optional[str] = None,
        exclude_paths: Optional[list] = None,
    ):
        super().__init__(app)
        self.api_key = api_key
        self.exclude_paths = set(exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"])
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip if no API key configured or path is excluded
        if not self.api_key or request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Check API key
        provided_key = request.headers.get("X-API-Key")
        
        if not provided_key:
            return HTTPException(
                status_code=401,
                detail={"error": "Missing API key", "error_code": "AUTH_001"}
            )
        
        if provided_key != self.api_key:
            logger.warning(f"Invalid API key attempt from {request.client.host}")
            return HTTPException(
                status_code=401,
                detail={"error": "Invalid API key", "error_code": "AUTH_002"}
            )
        
        return await call_next(request)
