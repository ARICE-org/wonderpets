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


# =============================================================================
# HYBRID FORECAST SCHEMAS
# =============================================================================

class HybridForecastRequest(BaseModel):
    """Request for hybrid soil forecast."""
    current_soil_data: Optional[SoilSensorData] = Field(
        None, description="Current soil readings"
    )
    historical_data: Optional[Dict[str, List[float]]] = Field(
        None, description="Historical readings per parameter (for lag features)"
    )
    location: Optional[LocationInput] = Field(None, description="Farm location")
    planting_date: Optional[str] = Field(
        None, description="Expected planting date (YYYY-MM-DD)"
    )
    forecast_horizon_days: int = Field(
        default=90,
        ge=30,
        le=120,
        description="Forecast horizon (30-120 days)"
    )
    forecast_interval_days: int = Field(
        default=7,
        ge=1,
        le=14,
        description="Days between forecast points"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_soil_data": {
                    "ph": 6.2,
                    "nitrogen": 45,
                    "phosphorus": 20,
                    "potassium": 60,
                    "organic_matter": 3.5,
                    "moisture": 35
                },
                "planting_date": "2026-01-15",
                "forecast_horizon_days": 90,
                "forecast_interval_days": 7
            }
        }


class DetailedForecastPoint(BaseModel):
    """Single forecast point with all approach predictions."""
    date: str = Field(..., description="Forecast date (YYYY-MM-DD)")
    week_number: int = Field(..., description="Week number from planting")
    season: str = Field(..., description="Season (dry/wet)")
    nitrogen_ppm: float = Field(..., description="Nitrogen prediction (hybrid)")
    phosphorus_ppm: float = Field(..., description="Phosphorus prediction (hybrid)")
    potassium_meq: float = Field(..., description="Potassium prediction (hybrid)")
    pH: float = Field(..., description="pH prediction (hybrid)")
    soil_moisture_pct: float = Field(..., description="Moisture prediction (hybrid)")
    organic_matter_pct: float = Field(..., description="Organic matter prediction (hybrid)")
    soil_health_score: float = Field(..., ge=0, le=100, description="Health score")
    health_category: str = Field(..., description="Health category")


class WeeklyHybridSummary(BaseModel):
    """Weekly summary from hybrid forecast."""
    week_number: int = Field(..., description="Week number")
    season: str = Field(..., description="Season")
    nitrogen_ppm: float = Field(..., description="Average nitrogen")
    phosphorus_ppm: float = Field(..., description="Average phosphorus")
    potassium_meq: float = Field(..., description="Average potassium")
    pH: float = Field(..., description="Average pH")
    soil_moisture_pct: float = Field(..., description="Average moisture")
    organic_matter_pct: float = Field(..., description="Average organic matter")
    soil_health_score: float = Field(..., description="Average health score")
    health_category: str = Field(..., description="Health category")


class HybridForecastResponse(BaseModel):
    """Response containing hybrid soil forecast."""
    planting_date: str = Field(..., description="Planting date")
    forecast_end_date: str = Field(..., description="Forecast end date")
    forecast_interval_days: int = Field(..., description="Days between forecast points")
    approach: str = Field(default="hybrid", description="Approach used (always hybrid)")
    
    detailed_forecast: List[Dict[str, Any]] = Field(
        ..., description="Detailed daily/interval forecasts"
    )
    weekly_summary: List[Dict[str, Any]] = Field(
        ..., description="Weekly aggregated summaries"
    )
    
    model_version: str = Field(default="1.0", description="Model version")
    generated_at: str = Field(..., description="Generation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "planting_date": "2026-01-15",
                "forecast_end_date": "2026-04-15",
                "forecast_interval_days": 7,
                "approach": "hybrid",
                "detailed_forecast": [
                    {
                        "date": "2026-01-15",
                        "week_number": 1,
                        "season": "dry",
                        "nitrogen_ppm": 45.2,
                        "phosphorus_ppm": 18.5,
                        "potassium_meq": 0.85,
                        "pH": 6.3,
                        "soil_moisture_pct": 32.1,
                        "organic_matter_pct": 3.8,
                        "soil_health_score": 78.5,
                        "health_category": "Good"
                    }
                ],
                "weekly_summary": [
                    {
                        "week_number": 1,
                        "season": "dry",
                        "nitrogen_ppm": 45.0,
                        "soil_health_score": 78.0,
                        "health_category": "Good"
                    }
                ],
                "model_version": "1.0",
                "generated_at": "2026-01-04T10:30:00"
            }
        }


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


# =============================================================================
# FORECAST REALIGNMENT SCHEMAS (Backend → ML Service)
# =============================================================================

class RealignForecastRequest(BaseModel):
    """Request to realign an existing forecast with new sensor data."""
    current_data: Dict[str, Any] = Field(
        ..., description="New aggregated sensor data with statistics"
    )
    existing_forecast: Dict[str, Any] = Field(
        ..., description="The existing forecast to realign"
    )
    current_week: int = Field(
        ..., ge=1, le=12, description="Current week of the planting cycle"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_data": {
                    "nitrogen_ppm": {"mean": 47.0, "std": 2.1, "trend": "stable"},
                    "phosphorus_ppm": {"mean": 21.5, "std": 1.8, "trend": "stable"},
                    "pH": {"mean": 6.3, "std": 0.1, "trend": "stable"}
                },
                "existing_forecast": {
                    "weekly_summary": [
                        {"week": 4, "nitrogen_ppm": 44.0, "phosphorus_ppm": 20.0}
                    ]
                },
                "current_week": 4
            }
        }


class DeviationDetail(BaseModel):
    """Detail about deviation between predicted and actual."""
    predicted: float
    actual: float
    deviation: float
    deviation_pct: float = Field(..., alias="deviationPct")
    strategy: str
    
    class Config:
        populate_by_name = True


class CorrectionDetail(BaseModel):
    """Detail about correction applied."""
    strategy: str
    reason: str
    offset: Optional[float] = None
    initial_offset: Optional[float] = Field(None, alias="initialOffset")
    decay_rate: Optional[float] = Field(None, alias="decayRate")
    
    class Config:
        populate_by_name = True


class RealignForecastResponse(BaseModel):
    """Response after realigning a forecast."""
    health_score: float = Field(..., description="Updated health score")
    health_category: str = Field(..., description="Health category")
    realignment_date: str = Field(..., description="When realignment occurred")
    week_of_realignment: int = Field(..., description="Week number of realignment")
    requires_reforecast: bool = Field(
        False, description="Whether full reforecast was needed"
    )
    deviations: Dict[str, Any] = Field(
        ..., description="Deviations for each parameter"
    )
    corrections_applied: Dict[str, Any] = Field(
        ..., description="Corrections applied to each parameter"
    )
    forecast: Dict[str, Any] = Field(
        ..., description="Updated forecast data"
    )
    weekly_summary: List[Dict[str, Any]] = Field(
        ..., description="Updated weekly summaries"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "health_score": 74.5,
                "health_category": "Good",
                "realignment_date": "2026-01-25T10:30:00",
                "week_of_realignment": 4,
                "requires_reforecast": False,
                "deviations": {
                    "nitrogen_ppm": {
                        "predicted": 44.0,
                        "actual": 47.0,
                        "deviation": 3.0,
                        "deviation_pct": 6.8,
                        "strategy": "DECAYING_SHIFT"
                    }
                },
                "corrections_applied": {
                    "nitrogen_ppm": {
                        "strategy": "DECAYING_SHIFT",
                        "reason": "Moderate deviation - applying decaying correction",
                        "initial_offset": 2.1,
                        "decay_rate": 0.1
                    }
                },
                "forecast": {},
                "weekly_summary": []
            }
        }


class HealthScoreRequest(BaseModel):
    """Request for health score calculation."""
    soil_data: Dict[str, Any] = Field(
        ..., description="Soil data (raw or aggregated)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "soil_data": {
                    "nitrogen_ppm": 45.0,
                    "phosphorus_ppm": 20.0,
                    "potassium_meq": 0.85,
                    "pH": 6.2,
                    "soil_moisture_pct": 35.0,
                    "organic_matter_pct": 3.5
                }
            }
        }


class HealthScoreResponse(BaseModel):
    """Response with calculated health score."""
    health_score: float = Field(..., description="Overall health score (0-100)")
    health_category: str = Field(..., description="Health category")
    parameter_scores: Dict[str, float] = Field(
        ..., description="Individual parameter scores"
    )
