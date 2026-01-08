"""
Fixed Window Rate Limiter Middleware for ML Service

An in-memory rate limiter implementation using the Fixed Window algorithm.
No external dependencies (Redis, Lua) required.

Algorithm:
- Divides time into fixed windows (e.g., 60-second windows)
- Counts requests per client within each window
- Resets count when a new window starts
- Returns 429 Too Many Requests if limit exceeded
"""

import time
import threading
from typing import Optional, Dict, Callable
from fastapi import Request, HTTPException, status
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
        _storage: Dict mapping client_key -> {"count": int, "window_start": float}
        _lock: Threading lock for thread-safe operations
    """
    
    def __init__(
        self,
        requests_per_window: int = 100,
        window_size_seconds: int = 60,
        cleanup_interval: int = 300,  # Clean old entries every 5 minutes
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
    
    def is_allowed(self, client_key: str) -> tuple[bool, Dict]:
        """
        Check if a request from the client is allowed.
        
        Args:
            client_key: Unique identifier for the client (e.g., IP address, user ID)
        
        Returns:
            Tuple of (is_allowed: bool, info: dict with rate limit details)
        """
        current_time = time.time()
        current_window = self._get_window_start(current_time)
        
        with self._lock:
            # Periodic cleanup
            self._cleanup_old_entries(current_time)
            
            # Get or create entry for this client
            if client_key not in self._storage:
                self._storage[client_key] = {
                    "count": 0,
                    "window_start": current_window
                }
            
            entry = self._storage[client_key]
            
            # Reset if we're in a new window
            if entry["window_start"] < current_window:
                entry["count"] = 0
                entry["window_start"] = current_window
            
            # Calculate remaining time in current window
            window_reset = entry["window_start"] + self.window_size_seconds
            remaining_seconds = max(0, int(window_reset - current_time))
            
            # Check if request is allowed
            remaining_requests = max(0, self.requests_per_window - entry["count"])
            
            info = {
                "limit": self.requests_per_window,
                "remaining": remaining_requests,
                "reset": remaining_seconds,
                "window_size": self.window_size_seconds
            }
            
            if entry["count"] >= self.requests_per_window:
                return False, info
            
            # Increment counter
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
    """
    
    def __init__(
        self,
        app,
        limiter: FixedWindowRateLimiter,
        key_func: Optional[Callable[[Request], str]] = None,
        exclude_paths: Optional[list[str]] = None,
    ):
        super().__init__(app)
        self.limiter = limiter
        self.key_func = key_func or self._default_key_func
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]
    
    def _default_key_func(self, request: Request) -> str:
        """
        Default function to extract client identifier.
        Uses X-Forwarded-For header if behind a proxy, otherwise client host.
        """
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def dispatch(self, request: Request, call_next):
        # Check if path should be excluded from rate limiting
        # Use exact match for root "/" and startswith for other paths
        path = request.url.path
        should_exclude = any(
            (excluded == "/" and path == "/") or 
            (excluded != "/" and path.startswith(excluded))
            for excluded in self.exclude_paths
        )
        
        if should_exclude:
            return await call_next(request)
        
        # Get client identifier
        client_key = self.key_func(request)
        client_host = client_key if client_key != "unknown" else "Unknown"
        
        # Check rate limit
        is_allowed, info = self.limiter.is_allowed(client_key)
        
        if not is_allowed:
            # Log rate limit exceeded
            logger.warning(
                f"{request.method} {path} - Client: {client_host} - "
                f"Response: 429 Too Many Requests - Rate limit exceeded "
                f"(Limit: {info['limit']}, Reset in: {info['reset']}s)"
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": info["reset"]
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["reset"])
                }
            )
        
        # Process request and add rate limit headers to response
        try:
            response = await call_next(request)
            
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(info["reset"])
            
            # Log successful request
            status_code = response.status_code
            status_text = "OK" if 200 <= status_code < 300 else f"Error {status_code}"
            logger.info(
                f"{request.method} {path} - Client: {client_host} - "
                f"Response: {status_code} {status_text} - "
                f"Rate Limit: {info['remaining']}/{info['limit']}"
            )
            
            return response
        except Exception as e:
            # Log errors during request processing
            logger.error(
                f"{request.method} {path} - Client: {client_host} - "
                f"Response: 500 Internal Server Error - Error: {str(e)}"
            )
            raise
        
        return response


def create_rate_limit_dependency(
    limiter: FixedWindowRateLimiter,
    key_func: Optional[Callable[[Request], str]] = None
):
    """
    Create a FastAPI dependency for rate limiting specific endpoints.
    """
    def _default_key(request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"
    
    _key_func = key_func or _default_key
    
    async def rate_limit_dependency(request: Request):
        client_key = _key_func(request)
        is_allowed, info = limiter.is_allowed(client_key)
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded. Please try again later.",
                    "retry_after": info["reset"]
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["reset"])
                }
            )
        
        return None
    
    return rate_limit_dependency


# Pre-configured rate limiters for ML service
# Import settings lazily to avoid circular imports
def _get_settings():
    from app.config.settings import settings
    return settings


class RateLimiters:
    """Pre-configured rate limiters for ML service endpoints. Uses environment variables."""
    
    _instances: Dict[str, FixedWindowRateLimiter] = {}
    
    @classmethod
    def standard(cls) -> FixedWindowRateLimiter:
        """Standard API rate limit (default: 60 requests per 60 seconds)"""
        if "standard" not in cls._instances:
            settings = _get_settings()
            cls._instances["standard"] = FixedWindowRateLimiter(
                requests_per_window=settings.RATE_LIMIT_STANDARD_REQUESTS,
                window_size_seconds=settings.RATE_LIMIT_STANDARD_WINDOW
            )
        return cls._instances["standard"]
    
    @classmethod
    def prediction(cls) -> FixedWindowRateLimiter:
        """Prediction endpoints rate limit (default: 30 requests per 60 seconds)"""
        if "prediction" not in cls._instances:
            settings = _get_settings()
            cls._instances["prediction"] = FixedWindowRateLimiter(
                requests_per_window=settings.RATE_LIMIT_PREDICTION_REQUESTS,
                window_size_seconds=settings.RATE_LIMIT_PREDICTION_WINDOW
            )
        return cls._instances["prediction"]
    
    @classmethod
    def batch(cls) -> FixedWindowRateLimiter:
        """Batch operations rate limit (default: 10 requests per 60 seconds)"""
        if "batch" not in cls._instances:
            settings = _get_settings()
            cls._instances["batch"] = FixedWindowRateLimiter(
                requests_per_window=settings.RATE_LIMIT_BATCH_REQUESTS,
                window_size_seconds=settings.RATE_LIMIT_BATCH_WINDOW
            )
        return cls._instances["batch"]
