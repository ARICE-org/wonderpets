"""
Fixed Window Rate Limiter Middleware for ML Service

An in-memory rate limiter implementation using the Fixed Window algorithm.
No external dependencies (Redis, Lua) required.
"""

import time
import threading
from typing import Optional, Dict, Callable, List
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class FixedWindowRateLimiter:
    """
    Thread-safe Fixed Window Rate Limiter using in-memory storage.
    
    Attributes:
        requests_per_window: Maximum requests allowed per window
        window_size_seconds: Duration of each window in seconds
    """
    
    def __init__(
        self,
        requests_per_window: int = 100,
        window_size_seconds: int = 60,
        cleanup_interval: int = 300,
    ):
        self.requests_per_window = requests_per_window
        self.window_size_seconds = window_size_seconds
        self.cleanup_interval = cleanup_interval
        self._storage: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.time()
    
    def _get_window_start(self, current_time: float) -> float:
        """Calculate the start of the current fixed window."""
        return (current_time // self.window_size_seconds) * self.window_size_seconds
    
    def _cleanup_old_entries(self, current_time: float) -> None:
        """Remove entries from previous windows to prevent memory bloat."""
        if current_time - self._last_cleanup < self.cleanup_interval:
            return
        
        current_window = self._get_window_start(current_time)
        keys_to_delete = [
            key for key, data in self._storage.items()
            if data["window_start"] < current_window
        ]
        
        for key in keys_to_delete:
            del self._storage[key]
        
        self._last_cleanup = current_time
        
        if keys_to_delete:
            logger.debug(f"Rate limiter cleanup: removed {len(keys_to_delete)} old entries")
    
    def is_allowed(self, client_key: str) -> tuple:
        """
        Check if a request from the client is allowed.
        
        Args:
            client_key: Unique identifier for the client
        
        Returns:
            Tuple of (is_allowed: bool, info: dict with rate limit details)
        """
        current_time = time.time()
        current_window = self._get_window_start(current_time)
        
        with self._lock:
            self._cleanup_old_entries(current_time)
            
            if client_key not in self._storage:
                self._storage[client_key] = {
                    "count": 0,
                    "window_start": current_window
                }
            
            entry = self._storage[client_key]
            
            if entry["window_start"] < current_window:
                entry["count"] = 0
                entry["window_start"] = current_window
            
            window_reset = entry["window_start"] + self.window_size_seconds
            remaining_seconds = max(0, int(window_reset - current_time))
            
            remaining_requests = max(0, self.requests_per_window - entry["count"])
            
            info = {
                "limit": self.requests_per_window,
                "remaining": remaining_requests,
                "reset": remaining_seconds,
                "window_size": self.window_size_seconds
            }
            
            if entry["count"] >= self.requests_per_window:
                return False, info
            
            entry["count"] += 1
            info["remaining"] = max(0, self.requests_per_window - entry["count"])
            
            return True, info
    
    def get_stats(self) -> Dict:
        """Get current rate limiter statistics."""
        with self._lock:
            return {
                "active_clients": len(self._storage),
                "requests_per_window": self.requests_per_window,
                "window_size_seconds": self.window_size_seconds
            }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting using Fixed Window algorithm.
    
    Can be initialized with either:
    - A FixedWindowRateLimiter instance via `limiter` parameter
    - Or directly with `requests_per_minute` / `requests_per_window` to auto-create a limiter
    """
    
    def __init__(
        self,
        app,
        limiter: Optional[FixedWindowRateLimiter] = None,
        key_func: Optional[Callable[[Request], str]] = None,
        exclude_paths: Optional[List[str]] = None,
        # Convenience parameters to auto-create limiter
        requests_per_minute: Optional[int] = None,
        requests_per_window: int = 100,
        window_size_seconds: int = 60,
    ):
        super().__init__(app)
        
        # Support both ways of initialization
        if limiter is not None:
            self.limiter = limiter
        elif requests_per_minute is not None:
            # Convenience: create limiter from requests_per_minute
            self.limiter = FixedWindowRateLimiter(
                requests_per_window=requests_per_minute,
                window_size_seconds=60
            )
        else:
            # Default: create limiter with provided or default params
            self.limiter = FixedWindowRateLimiter(
                requests_per_window=requests_per_window,
                window_size_seconds=window_size_seconds
            )
        
        self.key_func = key_func or self._default_key_func
        self.exclude_paths = set(exclude_paths or [])
    
    def _default_key_func(self, request: Request) -> str:
        """Default: use client IP as rate limit key."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        client = request.client
        return client.host if client else "unknown"
    
    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiter."""
        path = request.url.path
        
        # Skip excluded paths
        if path in self.exclude_paths:
            return await call_next(request)
        
        # Check rate limit
        client_key = self.key_func(request)
        is_allowed, info = self.limiter.is_allowed(client_key)
        
        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": info["reset"]
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["reset"])
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        
        return response
