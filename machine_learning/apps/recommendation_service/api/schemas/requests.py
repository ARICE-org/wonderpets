"""
Recommendation service request schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class SoilDataInput(BaseModel):
    """Soil data input for recommendations."""
    
    ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH")
    nitrogen: Optional[float] = Field(None, ge=0, description="Nitrogen (kg/ha)")
    phosphorus: Optional[float] = Field(None, ge=0, description="Phosphorus (kg/ha)")
    potassium: Optional[float] = Field(None, ge=0, description="Potassium (kg/ha)")
    organic_matter: Optional[float] = Field(None, ge=0, description="Organic matter (%)")
    moisture: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture (%)")
    soil_type: Optional[str] = Field(None, description="Soil type classification")


class WeatherDataInput(BaseModel):
    """Weather data input for recommendations."""
    
    temperature_avg: Optional[float] = Field(None, description="Average temperature (°C)")
    temperature_max: Optional[float] = Field(None, description="Max temperature (°C)")
    temperature_min: Optional[float] = Field(None, description="Min temperature (°C)")
    rainfall_avg: Optional[float] = Field(None, description="Average rainfall (mm)")
    humidity_avg: Optional[float] = Field(None, description="Average humidity (%)")
    is_flood_prone: Optional[bool] = Field(False, description="Flood-prone area")
    is_drought_prone: Optional[bool] = Field(False, description="Drought-prone area")


class LocationInput(BaseModel):
    """Location input for recommendations."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    region: Optional[str] = Field(None, description="Region/Province")
    municipality: Optional[str] = Field(None, description="Municipality/City")
    elevation_m: Optional[float] = Field(None, description="Elevation (meters)")


class RecommendationRequest(BaseModel):
    """Request for rice variety recommendations."""
    
    soil_data: Optional[SoilDataInput] = Field(None, description="Soil conditions")
    weather_data: Optional[WeatherDataInput] = Field(None, description="Weather conditions")
    location: Optional[LocationInput] = Field(None, description="Farm location")
    season: Optional[str] = Field(
        None, 
        description="Planting season (dry/wet)"
    )
    top_k: Optional[int] = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of recommendations to return"
    )
    farmer_preferences: Optional[dict] = Field(
        None,
        description="Farmer preferences (yield, quality, maturity)"
    )


class PlantingScheduleRequest(BaseModel):
    """Request for planting schedule."""
    
    location: LocationInput = Field(..., description="Farm location")
    variety: Optional[str] = Field(None, description="Selected variety (optional)")
    target_harvest_date: Optional[str] = Field(
        None,
        description="Target harvest date (YYYY-MM-DD)"
    )
