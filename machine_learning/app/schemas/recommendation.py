"""
Recommendation Schemas

Pydantic models for recommendation API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class LocationInput(BaseModel):
    """Location input data."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    region: Optional[str] = Field(None, description="Region or province name")
    municipality: Optional[str] = Field(None, description="Municipality name")


class SoilDataInput(BaseModel):
    """Soil sensor data input."""
    ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH level")
    nitrogen: Optional[float] = Field(None, ge=0, description="Nitrogen content (kg/ha)")
    phosphorus: Optional[float] = Field(None, ge=0, description="Phosphorus content (kg/ha)")
    potassium: Optional[float] = Field(None, ge=0, description="Potassium content (kg/ha)")
    organic_matter: Optional[float] = Field(None, ge=0, le=100, description="Organic matter percentage")
    moisture: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture percentage")


class WeatherDataInput(BaseModel):
    """Weather data input."""
    temperature_avg: Optional[float] = Field(None, description="Average temperature (°C)")
    temperature_max: Optional[float] = Field(None, description="Maximum temperature (°C)")
    temperature_min: Optional[float] = Field(None, description="Minimum temperature (°C)")
    rainfall: Optional[float] = Field(None, ge=0, description="Rainfall amount (mm)")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Humidity percentage")
    sunshine_hours: Optional[float] = Field(None, ge=0, le=24, description="Daily sunshine hours")


class RecommendationRequest(BaseModel):
    """Request for rice variety recommendation."""
    soil_data: Optional[SoilDataInput] = Field(None, description="Current soil conditions")
    weather_data: Optional[WeatherDataInput] = Field(None, description="Current/expected weather")
    location: LocationInput = Field(..., description="Farm location")
    season: Optional[str] = Field(None, description="Planting season (wet/dry)")
    farm_size_hectares: Optional[float] = Field(None, ge=0, description="Farm size in hectares")
    irrigation_available: Optional[bool] = Field(None, description="Whether irrigation is available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "soil_data": {
                    "ph": 6.2,
                    "nitrogen": 35,
                    "phosphorus": 15,
                    "potassium": 50,
                    "moisture": 55
                },
                "weather_data": {
                    "temperature_avg": 28,
                    "rainfall": 150,
                    "humidity": 75
                },
                "location": {
                    "latitude": 14.5995,
                    "longitude": 120.9842,
                    "region": "Central Luzon"
                },
                "season": "wet"
            }
        }


class RiceVarietyRecommendation(BaseModel):
    """Single rice variety recommendation."""
    variety_id: Optional[int] = Field(None, description="Variety database ID")
    variety_name: str = Field(..., description="Rice variety name")
    confidence_score: float = Field(..., ge=0, le=1, description="Recommendation confidence (0-1)")
    rank: int = Field(..., ge=1, description="Recommendation rank")
    reasoning: Optional[str] = Field(None, description="Why this variety is recommended")
    
    # Variety characteristics
    maturity_days: Optional[int] = Field(None, description="Days to maturity")
    yield_potential: Optional[str] = Field(None, description="Expected yield potential")
    disease_resistance: Optional[List[str]] = Field(None, description="Disease resistances")
    water_requirement: Optional[str] = Field(None, description="Water requirement level")


class RecommendationResponse(BaseModel):
    """Response containing rice variety recommendations."""
    recommendations: List[RiceVarietyRecommendation] = Field(
        ..., description="List of recommended varieties"
    )
    input_summary: Optional[Dict[str, Any]] = Field(
        None, description="Summary of input conditions"
    )
    model_version: Optional[str] = Field(None, description="Model version used")
    generated_at: Optional[str] = Field(None, description="Timestamp of generation")


class ScheduleRequest(BaseModel):
    """Request for planting schedule recommendation."""
    location: LocationInput = Field(..., description="Farm location")
    season: Optional[str] = Field(None, description="Target season")
    weather_data: Optional[WeatherDataInput] = Field(None, description="Current weather")
    variety_id: Optional[int] = Field(None, description="Selected variety ID")


class ScheduleResponse(BaseModel):
    """Response containing planting schedule."""
    recommended_planting_window: Dict[str, Optional[str]] = Field(
        ..., description="Recommended planting window (start, end dates)"
    )
    optimal_planting_date: Optional[str] = Field(None, description="Optimal planting date")
    reasoning: Optional[str] = Field(None, description="Explanation for recommendation")
    weather_outlook: Optional[Dict[str, Any]] = Field(None, description="Weather outlook for period")
