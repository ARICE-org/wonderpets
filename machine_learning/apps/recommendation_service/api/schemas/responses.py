"""
Recommendation service response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class RiceVarietyRecommendation(BaseModel):
    """A single rice variety recommendation."""
    
    rank: int = Field(..., description="Recommendation rank (1 = best)")
    variety_id: str = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety display name")
    confidence_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Confidence score (0-1)"
    )
    match_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Match score (0-100%)"
    )
    
    # Variety details
    maturity_days: Optional[int] = Field(None, description="Days to maturity")
    yield_potential_tha: Optional[float] = Field(None, description="Yield potential (t/ha)")
    grain_quality: Optional[str] = Field(None, description="Grain quality rating")
    
    # Suitability scores
    soil_suitability: Optional[float] = Field(None, description="Soil match (0-100)")
    weather_suitability: Optional[float] = Field(None, description="Weather match (0-100)")
    
    # Reasoning
    strengths: Optional[List[str]] = Field(default_factory=list)
    considerations: Optional[List[str]] = Field(default_factory=list)
    recommendation_reason: Optional[str] = Field(None)


class InputSummary(BaseModel):
    """Summary of input conditions used for recommendation."""
    
    soil_health_score: Optional[float] = None
    weather_outlook: Optional[str] = None
    season: Optional[str] = None
    location_region: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Response with rice variety recommendations."""
    
    recommendations: List[RiceVarietyRecommendation] = Field(
        default_factory=list,
        description="Ranked variety recommendations"
    )
    input_summary: Optional[InputSummary] = Field(
        None,
        description="Summary of input conditions"
    )
    total_varieties_considered: Optional[int] = Field(
        None,
        description="Total varieties evaluated"
    )
    generated_at: Optional[str] = Field(None, description="Generation timestamp")


class PlantingWindow(BaseModel):
    """Optimal planting window."""
    
    start_date: str
    end_date: str
    optimal_date: Optional[str] = None


class PlantingScheduleResponse(BaseModel):
    """Response with planting schedule."""
    
    location: Optional[Dict[str, Any]] = None
    variety: Optional[str] = None
    recommended_planting_window: PlantingWindow
    expected_harvest_window: Optional[PlantingWindow] = None
    growth_stages: Optional[List[Dict[str, Any]]] = None
    season_type: Optional[str] = None
    recommendations: Optional[List[str]] = None
    generated_at: Optional[str] = None
