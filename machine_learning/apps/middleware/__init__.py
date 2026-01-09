"""
Global middleware for ML services.

Includes:
- Rate limiting
- Error handling
- Request/response logging
- Authentication (if needed)
"""

from apps.middleware.rate_limiter import (
    RateLimitMiddleware,
    FixedWindowRateLimiter,
)
from apps.middleware.error_handler import (
    error_handler_middleware,
    register_exception_handlers,
)
from apps.middleware.logging_middleware import LoggingMiddleware

__all__ = [
    "RateLimitMiddleware",
    "FixedWindowRateLimiter",
    "error_handler_middleware",
    "register_exception_handlers",
    "LoggingMiddleware",
]
