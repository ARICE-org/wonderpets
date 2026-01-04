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
from app.controllers.soil_forecast_controller import soil_forecast_controller
from app.schemas.soil_forecast import (
    UploadSensorDataRequest,
    SoilAnalysisResponse,
    GetForecastResponse,
    HealthScoreResponse,
    ReadingHistoryResponse,
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
    
    If an active forecast exists for the farm/planting date, it will be realigned
    based on the new data. Otherwise, a new forecast is generated.
    """
)
async def upload_sensor_readings(
    request: UploadSensorDataRequest,
    db: Session = Depends(get_db),
) -> SoilAnalysisResponse:
    """
    Upload sensor readings and get updated forecast.
    
    This is the main endpoint for soil analysis. The frontend parses
    the CSV from the IoT sensor and sends structured data here.
    
    The backend handles:
    1. Data validation and aggregation
    2. Storage in database
    3. Communication with ML service
    4. Forecast generation/realignment
    5. Recommendation generation
    """
    try:
        response = await soil_forecast_controller.process_sensor_reading(
            db=db,
            request=request
        )
        return response
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
    "/forecast/{farm_id}",
    response_model=GetForecastResponse,
    summary="Get current forecast for a farm",
    description="""
    Retrieve the current active forecast for a farm.
    Returns the full weekly forecast, health score, and next reading recommendation.
    """
)
async def get_forecast(
    farm_id: UUID,
    db: Session = Depends(get_db),
) -> GetForecastResponse:
    """Get current forecast for a farm."""
    result = await soil_forecast_controller.get_forecast(db=db, farm_id=farm_id)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No forecast found for farm {farm_id}"
        )
    
    return result


@router.get(
    "/health/{farm_id}",
    response_model=HealthScoreResponse,
    summary="Get current health score for a farm",
    description="""
    Get the most recent soil health score for a farm based on the latest reading.
    """
)
async def get_health_score(
    farm_id: UUID,
    db: Session = Depends(get_db),
) -> HealthScoreResponse:
    """Get current health score for a farm."""
    result = await soil_forecast_controller.get_health_score(db=db, farm_id=farm_id)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No soil data found for farm {farm_id}"
        )
    
    return result


@router.get(
    "/history/{farm_id}",
    response_model=ReadingHistoryResponse,
    summary="Get reading history for a farm",
    description="""
    Get historical sensor readings for a farm.
    Useful for viewing trends and past data.
    """
)
async def get_reading_history(
    farm_id: UUID,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> ReadingHistoryResponse:
    """Get reading history for a farm."""
    return await soil_forecast_controller.get_reading_history(
        db=db,
        farm_id=farm_id,
        limit=limit
    )
