"""
Response schemas for soil service API.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class ParameterScore(BaseModel):
    """Score for individual soil parameter."""
    parameter: str = Field(..., description="Parameter name")
    value: float = Field(..., description="Measured value")
    score: float = Field(..., ge=0, le=100, description="Parameter score (0-100)")
    status: str = Field(..., description="Status (Excellent/Good/Fair/Poor/Critical)")
    optimal_range: str = Field(..., description="Optimal range for rice cultivation")


class DeficiencyInfo(BaseModel):
    """Information about a soil deficiency."""
    parameter: str = Field(..., description="Deficient parameter")
    type: str = Field(..., description="Type: 'deficiency' or 'excess'")
    current_value: float = Field(..., description="Current measured value")
    required_minimum: Optional[float] = Field(None, description="Required minimum value")
    maximum_allowed: Optional[float] = Field(None, description="Maximum allowed value")
    severity: str = Field(..., description="Severity: 'high', 'medium', 'low'")


class SoilHealthResponse(BaseModel):
    """Response containing soil health analysis."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall health score (0-100)")
    overall_status: str = Field(..., description="Overall status label")
    parameter_scores: List[ParameterScore] = Field(
        ..., description="Individual parameter scores"
    )
    deficiencies: List[Dict[str, Any]] = Field(
        default=[], description="Identified deficiencies"
    )
    recommendations: List[str] = Field(
        default=[], description="Improvement recommendations"
    )
    analysis_timestamp: Optional[str] = Field(None, description="Analysis timestamp")


class WeeklySummary(BaseModel):
    """Weekly soil condition summary."""
    week: int = Field(..., description="Week number")
    start_date: str = Field(..., description="Week start date")
    end_date: str = Field(..., description="Week end date")
    soil_health_score: float = Field(..., description="Predicted health score")
    health_category: str = Field(..., description="Health category")
    parameters: Dict[str, Dict[str, float]] = Field(
        ..., description="Parameter predictions"
    )


class DetailedForecast(BaseModel):
    """Detailed daily forecast point."""
    date: str = Field(..., description="Forecast date")
    day_of_cycle: int = Field(..., description="Day in planting cycle")
    parameters: Dict[str, float] = Field(..., description="Parameter predictions")
    health_score: float = Field(..., description="Predicted health score")


class HybridForecastResponse(BaseModel):
    """Response for hybrid forecast."""
    planting_date: str = Field(..., description="Planting date")
    forecast_end_date: str = Field(..., description="Forecast end date")
    forecast_interval_days: int = Field(..., description="Interval between forecasts")
    approach: str = Field(default="hybrid", description="Forecasting approach used")
    weekly_summary: List[Dict[str, Any]] = Field(..., description="Weekly summaries")
    detailed_forecast: List[Dict[str, Any]] = Field(..., description="Detailed forecasts")
    model_version: str = Field(default="1.0", description="Model version")
    generated_at: str = Field(..., description="Forecast generation timestamp")


class RealignForecastResponse(BaseModel):
    """Response for realigned forecast."""
    planting_date: str = Field(..., description="Planting date")
    forecast_end_date: str = Field(..., description="Forecast end date")
    forecast_interval_days: int = Field(..., description="Interval between forecasts")
    approach: str = Field(default="hybrid", description="Forecasting approach")
    weekly_summary: List[Dict[str, Any]] = Field(..., description="Realigned weekly summaries")
    detailed_forecast: List[Dict[str, Any]] = Field(..., description="Realigned forecasts")
    model_version: str = Field(default="1.0", description="Model version")
    generated_at: str = Field(..., description="Realignment timestamp")
    realignment_info: Dict[str, Any] = Field(
        default={}, description="Information about the realignment"
    )
