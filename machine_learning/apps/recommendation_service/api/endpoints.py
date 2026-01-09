"""
Recommendation Service API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from apps.recommendation_service.api.dependencies import get_recommendation_service
from apps.recommendation_service.api.schemas.requests import (
    RecommendationRequest,
    PlantingScheduleRequest,
    SoilDataInput,
    WeatherDataInput,
    LocationInput,
)
from apps.recommendation_service.api.schemas.responses import (
    RecommendationResponse,
    PlantingScheduleResponse,
    RiceVarietyRecommendation,
)
from apps.recommendation_service.services.recommendation_service import RecommendationService
from apps.common.utils.logging_utils import logger


router = APIRouter()


@router.post("/varieties", response_model=RecommendationResponse)
async def get_variety_recommendations(
    request: RecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get rice variety recommendations based on conditions.
    
    Args:
        request: Request with soil, weather, and location data
        
    Returns:
        Top recommended rice varieties with scores
    """
    try:
        result = await service.get_recommendations(
            soil_data=request.soil_data.model_dump() if request.soil_data else None,
            weather_data=request.weather_data.model_dump() if request.weather_data else None,
            location=request.location.model_dump() if request.location else None,
            season=request.season,
            top_k=request.top_k or 5
        )
        
        return RecommendationResponse(
            recommendations=[
                RiceVarietyRecommendation(**rec) 
                for rec in result.get("recommendations", [])
            ],
            input_summary=result.get("input_summary"),
            generated_at=result.get("generated_at")
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in recommendations: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


@router.post("/planting-schedule", response_model=PlantingScheduleResponse)
async def get_planting_schedule(
    request: PlantingScheduleRequest,
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get optimal planting schedule for a location.
    """
    try:
        result = await service.get_planting_schedule(
            location=request.location.model_dump() if request.location else None,
            variety=request.variety,
            target_harvest_date=request.target_harvest_date
        )
        
        return PlantingScheduleResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating planting schedule: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate schedule")


@router.get("/varieties")
async def list_varieties(
    service: RecommendationService = Depends(get_recommendation_service)
):
    """List all available rice varieties."""
    return service.get_available_varieties()


@router.get("/varieties/{variety_id}")
async def get_variety_details(
    variety_id: str,
    service: RecommendationService = Depends(get_recommendation_service)
):
    """Get details for a specific rice variety."""
    variety = service.get_variety_details(variety_id)
    if not variety:
        raise HTTPException(status_code=404, detail="Variety not found")
    return variety


@router.get("/status")
async def get_service_status(
    service: RecommendationService = Depends(get_recommendation_service)
):
    """Get recommendation service status."""
    return {
        "service": "recommendation",
        "status": "ready" if service.is_ready() else "initializing",
        "model_info": service.get_model_info()
    }
