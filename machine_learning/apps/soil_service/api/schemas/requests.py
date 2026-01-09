"""
Request schemas for soil service API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, List, Optional, Union


class LocationInput(BaseModel):
    """Location for soil analysis."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    farm_id: Optional[int] = Field(None, description="Farm database ID")
    field_name: Optional[str] = Field(None, description="Field or plot name")


class AggregatedValue(BaseModel):
    """Aggregated sensor value with statistics."""
    mean: float
    std: Optional[float] = 0.0
    min: Optional[float] = None
    max: Optional[float] = None
    count: Optional[int] = 1
    latest: Optional[float] = None
    trend: Optional[str] = "stable"


class SoilSensorData(BaseModel):
    """
    Soil sensor reading data.
    
    Accepts either:
    - Simple float values: {"ph": 6.2, "nitrogen": 35}
    - Aggregated values: {"ph": {"mean": 6.2, "std": 0.1, ...}}
    """
    ph: Optional[Union[float, AggregatedValue, Dict[str, Any]]] = Field(None, description="Soil pH level")
    nitrogen: Optional[Union[float, AggregatedValue, Dict[str, Any]]] = Field(None, description="Nitrogen (kg/ha)")
    phosphorus: Optional[Union[float, AggregatedValue, Dict[str, Any]]] = Field(None, description="Phosphorus (kg/ha)")
    potassium: Optional[Union[float, AggregatedValue, Dict[str, Any]]] = Field(None, description="Potassium (kg/ha)")
    organic_matter: Optional[Union[float, AggregatedValue, Dict[str, Any]]] = Field(None, description="Organic matter (%)")
    moisture: Optional[Union[float, AggregatedValue, Dict[str, Any]]] = Field(None, description="Soil moisture (%)")
    temperature: Optional[Union[float, AggregatedValue, Dict[str, Any]]] = Field(None, description="Soil temperature (°C)")
    electrical_conductivity: Optional[Union[float, AggregatedValue, Dict[str, Any]]] = Field(None, description="EC (dS/m)")
    
    def get_value(self, field: str) -> Optional[float]:
        """Get the actual value from a field, handling both formats."""
        value = getattr(self, field, None)
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, dict):
            return value.get("mean") or value.get("latest")
        if isinstance(value, AggregatedValue):
            return value.mean
        return None
    
    def to_flat_dict(self) -> Dict[str, float]:
        """Convert to flat dictionary with just the mean values."""
        result = {}
        for field in ["ph", "nitrogen", "phosphorus", "potassium", 
                     "organic_matter", "moisture", "temperature", "electrical_conductivity"]:
            value = self.get_value(field)
            if value is not None:
                result[field] = value
        return result
    
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


class HybridForecastRequest(BaseModel):
    """Request for hybrid soil forecast."""
    current_soil_data: SoilSensorData = Field(..., description="Current soil readings")
    planting_date: str = Field(..., description="Planting date (YYYY-MM-DD)")
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
        description="Interval between forecasts"
    )
    location: Optional[LocationInput] = Field(None, description="Farm location")
    
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
                "planting_date": "2026-01-15",
                "forecast_horizon_days": 90,
                "forecast_interval_days": 7
            }
        }


class RealignForecastRequest(BaseModel):
    """Request to realign an existing forecast with new data."""
    current_data: Dict[str, Any] = Field(..., description="Current sensor data")
    existing_forecast: Dict[str, Any] = Field(..., description="Existing forecast to realign")
    current_week: int = Field(..., ge=1, description="Current week of planting cycle")
