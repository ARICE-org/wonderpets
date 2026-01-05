"""
Soil Forecast Schemas

Pydantic schemas for soil forecast requests and responses.
These are used by the Backend API endpoints that the Frontend calls.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from enum import Enum

class HealthCategory(str, Enum):
    """Soil health category based on score."""
    EXCELLENT = "Excellent"
    GOOD = "Good"
    MODERATE = "Moderate"
    POOR = "Poor"
    CRITICAL = "Critical"


class TrendDirection(str, Enum):
    """Trend direction for parameter values."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"


class CorrectionStrategy(str, Enum):
    """Strategies for forecast correction."""
    SHIFT = "SHIFT"
    DECAYING_SHIFT = "DECAYING_SHIFT"
    REFORECAST = "REFORECAST"

class SensorReading(BaseModel):
    """Single sensor reading from IoT device."""
    timestamp: datetime
    ph: Optional[float] = Field(None, ge=0, le=14, alias="pH")
    nitrogen: Optional[float] = Field(None, ge=0, alias="nitrogen")
    phosphorus: Optional[float] = Field(None, ge=0, alias="phosphorus")
    potassium: Optional[float] = Field(None, ge=0, alias="potassium")
    moisture: Optional[float] = Field(None, ge=0, le=100, alias="moisture")
    organic_matter: Optional[float] = Field(None, ge=0, alias="organicMatter")
    temperature: Optional[float] = Field(None, alias="temperature")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "timestamp": "2026-01-04T08:00:00",
                "pH": 6.2,
                "nitrogen": 45,
                "phosphorus": 20,
                "potassium": 65,
                "moisture": 35,
                "organicMatter": 3.5,
                "temperature": 28
            }
        }
    }


class UploadSensorDataRequest(BaseModel):
    """
    Request to upload sensor readings (Option B: Parsed Data).
    Frontend parses the CSV and sends structured data.
    """
    farmer_id: UUID = Field(..., alias="farmerId")
    sensor_id: Optional[UUID] = Field(None, alias="sensorId")
    readings: List[SensorReading]
    planting_date: date = Field(..., alias="plantingDate")
    reading_date: Optional[date] = Field(None, alias="readingDate")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "farmerId": "123e4567-e89b-12d3-a456-426614174000",
                "sensorId": "223e4567-e89b-12d3-a456-426614174001",
                "readings": [
                    {
                        "timestamp": "2026-01-04T08:00:00",
                        "pH": 6.2,
                        "nitrogen": 45,
                        "phosphorus": 20,
                        "potassium": 65,
                        "moisture": 35,
                        "organicMatter": 3.5
                    }
                ],
                "plantingDate": "2026-01-01"
            }
        }
    }

class ParameterStatistics(BaseModel):
    """Statistics for a single soil parameter."""
    mean: float
    std: float
    min: float
    max: float
    count: int
    latest: float
    trend: TrendDirection

    model_config = {
        "json_schema_extra": {
            "example": {
                "mean": 45.2,
                "std": 2.1,
                "min": 42.0,
                "max": 48.0,
                "count": 10,
                "latest": 46.0,
                "trend": "stable"
            }
        }
    }


class AggregatedSoilData(BaseModel):
    """Aggregated soil data with statistics for each parameter."""
    nitrogen_ppm: Optional[ParameterStatistics] = Field(None, alias="nitrogenPpm")
    phosphorus_ppm: Optional[ParameterStatistics] = Field(None, alias="phosphorusPpm")
    potassium_meq: Optional[ParameterStatistics] = Field(None, alias="potassiumMeq")
    pH: Optional[ParameterStatistics] = None
    soil_moisture_pct: Optional[ParameterStatistics] = Field(None, alias="soilMoisturePct")
    organic_matter_pct: Optional[ParameterStatistics] = Field(None, alias="organicMatterPct")

    model_config = {
        "populate_by_name": True,
    }


class DeviationInfo(BaseModel):
    """Information about deviation between predicted and actual values."""
    predicted: float
    actual: float
    deviation: float
    deviation_pct: float = Field(..., alias="deviationPct")
    correction_applied: CorrectionStrategy = Field(..., alias="correctionApplied")

    model_config = {
        "populate_by_name": True,
    }

class WeeklyForecast(BaseModel):
    """Forecast for a single week."""
    week: int
    date: date
    nitrogen_ppm: Optional[float] = Field(None, alias="nitrogenPpm")
    phosphorus_ppm: Optional[float] = Field(None, alias="phosphorusPpm")
    potassium_meq: Optional[float] = Field(None, alias="potassiumMeq")
    pH: Optional[float] = None
    soil_moisture_pct: Optional[float] = Field(None, alias="soilMoisturePct")
    organic_matter_pct: Optional[float] = Field(None, alias="organicMatterPct")
    health_score: float = Field(..., alias="healthScore")
    health_category: HealthCategory = Field(..., alias="healthCategory")
    realigned: bool = False
    correction_applied: Optional[CorrectionStrategy] = Field(None, alias="correctionApplied")

    model_config = {
        "populate_by_name": True,
    }


class ForecastSummary(BaseModel):
    """Summary of the full forecast period."""
    forecast_id: UUID = Field(..., alias="forecastId")
    farmer_id: UUID = Field(..., alias="farmerId")
    planting_date: date = Field(..., alias="plantingDate")
    forecast_start: date = Field(..., alias="forecastStart")
    forecast_end: date = Field(..., alias="forecastEnd")
    total_weeks: int = Field(..., alias="totalWeeks")
    average_health_score: float = Field(..., alias="averageHealthScore")
    trend: TrendDirection
    created_at: datetime = Field(..., alias="createdAt")
    last_updated: datetime = Field(..., alias="lastUpdated")
    realignment_count: int = Field(0, alias="realignmentCount")

    model_config = {
        "populate_by_name": True,
    }

class RecommendationType(str, Enum):
    """Type of recommendation."""
    POSITIVE = "positive"
    WARNING = "warning"
    ACTION_REQUIRED = "action_required"
    INFO = "info"


class Recommendation(BaseModel):
    """A single recommendation for the farmer."""
    type: RecommendationType
    parameter: Optional[str] = None
    message: str
    priority: int = Field(1, ge=1, le=5)  # 1 = highest priority


class Alert(BaseModel):
    """Alert for critical conditions."""
    severity: str  # "low", "medium", "high", "critical"
    parameter: str
    message: str
    threshold_exceeded: bool = Field(..., alias="thresholdExceeded")
    current_value: float = Field(..., alias="currentValue")
    threshold_value: float = Field(..., alias="thresholdValue")

    model_config = {
        "populate_by_name": True,
    }


class NextReadingRecommendation(BaseModel):
    """Recommendation for when to take next sensor reading."""
    recommended_date: date = Field(..., alias="recommendedDate")
    days_from_now: int = Field(..., alias="daysFromNow")
    reason: str

    model_config = {
        "populate_by_name": True,
    }

class SoilAnalysisResponse(BaseModel):
    """
    Response after uploading sensor reading and generating/updating forecast.
    This is the main response the Frontend receives.
    """
    status: str  
    health_score: float = Field(..., alias="healthScore")
    health_category: HealthCategory = Field(..., alias="healthCategory")
    
    # Current state
    current_week: Optional[int] = Field(None, alias="currentWeek")
    current_readings: Optional[AggregatedSoilData] = Field(None, alias="currentReadings")
    
    # Deviations (only if realigning)
    deviations: Optional[Dict[str, DeviationInfo]] = None
    
    # Forecast data
    forecast_summary: Optional[ForecastSummary] = Field(None, alias="forecastSummary")
    weekly_forecast: List[WeeklyForecast] = Field(..., alias="weeklyForecast")
    
    # Recommendations
    recommendations: List[Recommendation] = []
    alerts: List[Alert] = []
    
    # Next reading suggestion
    next_reading: Optional[NextReadingRecommendation] = Field(None, alias="nextReading")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "status": "forecast_realigned",
                "healthScore": 72.5,
                "healthCategory": "Good",
                "currentWeek": 4,
                "deviations": {
                    "nitrogen_ppm": {
                        "predicted": 44.0,
                        "actual": 47.0,
                        "deviation": 3.0,
                        "deviationPct": 6.8,
                        "correctionApplied": "DECAYING_SHIFT"
                    }
                },
                "weeklyForecast": [
                    {
                        "week": 5,
                        "date": "2026-02-01",
                        "nitrogenPpm": 46.5,
                        "healthScore": 74.2,
                        "healthCategory": "Good"
                    }
                ],
                "recommendations": [
                    {
                        "type": "positive",
                        "message": "Nitrogen levels are higher than expected. Maintain current practices."
                    }
                ],
                "nextReading": {
                    "recommendedDate": "2026-01-18",
                    "daysFromNow": 7,
                    "reason": "Weekly reading recommended based on moderate deviations."
                }
            }
        }
    }


class GetForecastResponse(BaseModel):
    """Response for GET forecast endpoint."""
    forecast_summary: ForecastSummary = Field(..., alias="forecastSummary")
    weekly_forecast: List[WeeklyForecast] = Field(..., alias="weeklyForecast")
    current_health_score: float = Field(..., alias="currentHealthScore")
    current_health_category: HealthCategory = Field(..., alias="currentHealthCategory")
    last_reading_date: Optional[datetime] = Field(None, alias="lastReadingDate")
    next_reading: Optional[NextReadingRecommendation] = Field(None, alias="nextReading")

    model_config = {
        "populate_by_name": True,
    }


class HealthScoreResponse(BaseModel):
    """Response for health score endpoint."""
    health_score: float = Field(..., alias="healthScore")
    health_category: HealthCategory = Field(..., alias="healthCategory")
    parameter_scores: Dict[str, float] = Field(..., alias="parameterScores")
    timestamp: datetime

    model_config = {
        "populate_by_name": True,
    }


class ReadingHistoryItem(BaseModel):
    """Single item in reading history."""
    reading_id: UUID = Field(..., alias="readingId")
    reading_date: datetime = Field(..., alias="readingDate")
    week_number: int = Field(..., alias="weekNumber")
    health_score: float = Field(..., alias="healthScore")
    aggregated_data: AggregatedSoilData = Field(..., alias="aggregatedData")

    model_config = {
        "populate_by_name": True,
    }


class ReadingHistoryResponse(BaseModel):
    """Response for reading history endpoint."""
    farmer_id: UUID = Field(..., alias="farmerId")
    total_readings: int = Field(..., alias="totalReadings")
    readings: List[ReadingHistoryItem]

    model_config = {
        "populate_by_name": True,
    }
