"""
Recommendation API Router

Endpoints for rice variety recommendations.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    ScheduleRequest,
    ScheduleResponse
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()

# Service instance (would be dependency injected in production)
recommendation_service = RecommendationService()


@router.post("/variety", response_model=RecommendationResponse)
async def get_variety_recommendations(
    request: RecommendationRequest,
    top_k: int = 5
):
    """
    Get rice variety recommendations based on soil, weather, and location data.
    
    Args:
        request: Recommendation request containing soil data, weather data, and location
        top_k: Number of top recommendations to return (default: 5)
    
    Returns:
        List of recommended rice varieties with confidence scores
    """
    try:
        response = await recommendation_service.get_recommendations(request, top_k=top_k)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@router.post("/schedule", response_model=ScheduleResponse)
async def get_planting_schedule(request: ScheduleRequest):
    """
    Get optimal planting schedule based on conditions.
    
    Args:
        request: Schedule request with location and season preferences
    
    Returns:
        Recommended planting schedule with optimal dates
    """
    try:
        # Convert to recommendation request format
        rec_request = RecommendationRequest(
            location=request.location,
            season=request.season,
            weather_data=request.weather_data
        )
        schedule = await recommendation_service.get_planting_schedule(rec_request)
        return ScheduleResponse(**schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule error: {str(e)}")


@router.get("/status")
async def get_recommendation_status():
    """
    Check recommendation service status.
    
    Returns:
        Service status and model information
    """
    return {
        "service": "recommendation",
        "ready": recommendation_service.is_ready(),
        "model_loaded": recommendation_service.model is not None if hasattr(recommendation_service, 'model') else False
    }
