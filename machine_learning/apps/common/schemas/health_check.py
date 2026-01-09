"""
Health check response schemas.
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional, Any


class HealthCheckResponse(BaseModel):
    """Standard health check response."""
    status: str = Field(..., description="Service status (healthy/unhealthy)")
    service: str = Field(..., description="Service name")
    version: Optional[str] = Field(None, description="Service version")
    uptime_seconds: Optional[float] = Field(None, description="Service uptime in seconds")


class ModelStatusResponse(BaseModel):
    """Model status response."""
    model_name: str = Field(..., description="Model name")
    loaded: bool = Field(..., description="Whether model is loaded")
    version: Optional[str] = Field(None, description="Model version")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
