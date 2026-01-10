"""
Soil Forecast Router

API endpoints for soil forecast operations.
Frontend calls these endpoints - they handle all ML service communication internally.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.controllers.soil_forecast_controller import soil_forecast_controller, EntityNotFoundError
from app.schemas.soil_forecast import (
    UploadSensorDataRequest,
    SoilAnalysisResponse,
    GetForecastResponse,
    HealthScoreResponse,
    ReadingHistoryResponse,
    WeeklyForecast,
)


router = APIRouter(
    prefix="/soil-forecast",
    tags=["Soil Forecast"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/readings",
    response_model=SoilAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload sensor readings and get forecast",
    description="""
    Upload parsed sensor readings from the IoT device and receive:
    - Current soil health score and category
    - 12-week forecast (new or realigned)
    - Personalized recommendations
    - Alerts for critical conditions
    - Next reading recommendation
    """
)
async def upload_sensor_readings(
    request: UploadSensorDataRequest,
    db: Session = Depends(get_db),
) -> SoilAnalysisResponse:
    """
    Upload sensor readings and get updated forecast.
    """
    try:
        response = await soil_forecast_controller.process_sensor_reading(
            db=db,
            request=request
        )
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"details": e.details}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing sensor readings: {str(e)}"
        )


@router.get(
    "/forecast/{farmer_id}",
    response_model=GetForecastResponse,
    summary="Get current forecast for a farmer",
    description="""
    Retrieve the current active forecast for a farmer.
    Returns the full weekly forecast, health score, and next reading recommendation.
    """
)
async def get_forecast(
    farmer_id: UUID,
    db: Session = Depends(get_db),
) -> GetForecastResponse:
    """Get current forecast for a farmer."""
    result = await soil_forecast_controller.get_forecast(db=db, farm_id=farmer_id)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No forecast found for farmer {farmer_id}"
        )
    
    return result


@router.get(
    "/health/{farmer_id}",
    response_model=HealthScoreResponse,
    summary="Get current health score for a farmer",
    description="""
    Get the most recent soil health score for a farmer based on the latest reading.
    """
)
async def get_health_score(
    farmer_id: UUID,
    db: Session = Depends(get_db),
) -> HealthScoreResponse:
    """Get current health score for a farm."""
    result = await soil_forecast_controller.get_health_score(db=db, farm_id=farmer_id)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No soil data found for farm {farmer_id}"
        )
    
    return result


@router.get(
    "/history/{farmer_id}",
    response_model=ReadingHistoryResponse,
    summary="Get reading history for a farmer",
    description="""
    Get historical sensor readings for a farmer.
    Useful for viewing trends and past data.
    """
)
async def get_reading_history(
    farmer_id: UUID,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> ReadingHistoryResponse:
    """Get reading history for a farm."""
    return await soil_forecast_controller.get_reading_history(
        db=db,
        farm_id=farmer_id,
        limit=limit
    )


@router.get(
    "/weekly-forecast/{farmer_id}",
    response_model=Optional[WeeklyForecast],
    summary="Get forecast for the current week",
    description="""
    Retrieve the soil forecast for the current week based on height/date of planting.
    """
)
async def get_current_week_forecast(
    farmer_id: UUID,
    db: Session = Depends(get_db),
) -> Optional[WeeklyForecast]:
    """Get forecast for the current week for a farmer."""
    return await soil_forecast_controller.get_current_week_forecast(db=db, farm_id=farmer_id)
