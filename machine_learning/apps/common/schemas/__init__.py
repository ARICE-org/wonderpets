"""
Shared schemas for ML services.
"""

from apps.common.schemas.health_check import HealthCheckResponse, ModelStatusResponse
from apps.common.schemas.pagination import PaginatedResponse, PaginationParams

__all__ = [
    "HealthCheckResponse",
    "ModelStatusResponse",
    "PaginatedResponse",
    "PaginationParams",
]
