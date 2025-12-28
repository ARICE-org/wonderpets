"""
Soil Schemas

Pydantic models for soil analysis API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class LocationInput(BaseModel):
    """Location for soil analysis."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    farm_id: Optional[int] = Field(None, description="Farm database ID")
    field_name: Optional[str] = Field(None, description="Field or plot name")


class SoilSensorData(BaseModel):
    """Soil sensor reading data."""
    ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH level")
    nitrogen: Optional[float] = Field(None, ge=0, description="Nitrogen (kg/ha)")
    phosphorus: Optional[float] = Field(None, ge=0, description="Phosphorus (kg/ha)")
    potassium: Optional[float] = Field(None, ge=0, description="Potassium (kg/ha)")
    organic_matter: Optional[float] = Field(None, ge=0, le=15, description="Organic matter (%)")
    moisture: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture (%)")
    temperature: Optional[float] = Field(None, description="Soil temperature (°C)")
    electrical_conductivity: Optional[float] = Field(None, ge=0, description="EC (dS/m)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ph": 6.2,
                "nitrogen": 35,
                "phosphorus": 15,
                "potassium": 50,
                "organic_matter": 3.5,
                "moisture": 55,
                "temperature": 28
            }
        }


class SoilAnalysisRequest(BaseModel):
    """Request for soil health analysis."""
    soil_data: SoilSensorData = Field(..., description="Current soil sensor readings")
    location: Optional[LocationInput] = Field(None, description="Location of soil sample")
    sensor_id: Optional[str] = Field(None, description="Sensor device ID")
    reading_timestamp: Optional[str] = Field(None, description="When reading was taken")


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


class SoilForecastRequest(BaseModel):
    """Request for soil condition forecast."""
    current_soil_data: Optional[SoilSensorData] = Field(
        None, description="Current soil readings"
    )
    historical_data: Optional[Dict[str, List[float]]] = Field(
        None, description="Historical readings per parameter"
    )
    location: Optional[LocationInput] = Field(None, description="Farm location")
    planting_date: Optional[str] = Field(
        None, description="Expected planting date (YYYY-MM-DD)"
    )
    forecast_horizon_days: int = Field(
        default=90, 
        ge=30, 
        le=120, 
        description="Forecast horizon (30-120 days for rice season)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_soil_data": {
                    "ph": 6.2,
                    "nitrogen": 35,
                    "phosphorus": 15,
                    "potassium": 50,
                    "moisture": 55
                },
                "planting_date": "2025-01-15",
                "forecast_horizon_days": 90
            }
        }


class GrowthStageInfo(BaseModel):
    """Information about a rice growth stage."""
    stage: str = Field(..., description="Growth stage name")
    start_date: str = Field(..., description="Stage start date")
    end_date: str = Field(..., description="Stage end date")
    duration_days: int = Field(..., description="Stage duration in days")
    critical_parameters: List[str] = Field(..., description="Critical soil parameters")


class WeeklySoilSummary(BaseModel):
    """Weekly summary of soil conditions."""
    week: int = Field(..., description="Week number")
    start_date: str = Field(..., description="Week start date")
    end_date: str = Field(..., description="Week end date")
    parameters: Dict[str, Dict[str, float]] = Field(
        ..., description="Parameter statistics (avg, min, max)"
    )


class StageAlert(BaseModel):
    """Alert for a growth stage."""
    stage: str = Field(..., description="Growth stage")
    alerts: List[Dict[str, Any]] = Field(..., description="List of alerts")


class SoilOutlook(BaseModel):
    """Overall soil health outlook."""
    rating: str = Field(..., description="Outlook rating")
    score: float = Field(..., ge=0, le=100, description="Outlook score")
    summary: str = Field(..., description="Outlook summary")
    key_concerns: List[str] = Field(default=[], description="Key concerns")
    recommended_actions: List[str] = Field(default=[], description="Recommended actions")


class SoilForecastResponse(BaseModel):
    """Response containing soil condition forecast."""
    planting_date: Optional[str] = Field(None, description="Expected planting date")
    forecast_end_date: Optional[str] = Field(None, description="Forecast end date")
    location: Optional[Dict[str, Any]] = Field(None, description="Location info")
    growth_stage_timeline: List[Dict[str, Any]] = Field(
        default=[], description="Growth stages with dates"
    )
    parameter_forecasts: Dict[str, Any] = Field(
        default={}, description="Forecasted values per parameter"
    )
    weekly_summary: List[Dict[str, Any]] = Field(
        default=[], description="Weekly condition summaries"
    )
    stage_alerts: List[Dict[str, Any]] = Field(
        default=[], description="Alerts by growth stage"
    )
    overall_outlook: Dict[str, Any] = Field(
        default={}, description="Overall season outlook"
    )
    model_version: Optional[str] = Field(None, description="Model version used")
    generated_at: Optional[str] = Field(None, description="Timestamp of generation")
