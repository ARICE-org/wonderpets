"""
Soil service schemas.
"""

from apps.soil_service.api.schemas.requests import (
    SoilAnalysisRequest,
    SoilSensorData,
    HybridForecastRequest,
    RealignForecastRequest,
    LocationInput,
)
from apps.soil_service.api.schemas.responses import (
    SoilHealthResponse,
    HybridForecastResponse,
    RealignForecastResponse,
    ParameterScore,
)

__all__ = [
    "SoilAnalysisRequest",
    "SoilSensorData",
    "HybridForecastRequest",
    "RealignForecastRequest",
    "LocationInput",
    "SoilHealthResponse",
    "HybridForecastResponse",
    "RealignForecastResponse",
    "ParameterScore",
]
