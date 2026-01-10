from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
import io
import uuid

from sqlalchemy.orm import Session

from app.dependencies import get_db
from app import models
from app.models.soil_data import SoilData as SoilDataModel
from app.schemas.soil_data import (
    SoilData, 
    SoilDataCreate,
    SoilDataBulkUploadRequest,
    SoilDataBulkUploadResponse,
)
from app.packages.decorators.search_helpers import searchable
import app.controllers.soil_data_controller as soil_ctrl


router = APIRouter(
    prefix="/soil-data",
    tags=["Soil Data"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=SoilData,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new soil data record",
)
def create_soil_data(
    soil: SoilDataCreate,
    db: Session = Depends(get_db),
):
    """Create a single SoilData record by delegating to controller."""
    return soil_ctrl.create_soil_data(db=db, soil_data=soil)


@router.post(
    "/bulk-upload",
    response_model=SoilDataBulkUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk upload CSV-parsed soil data",
    description="""
    Upload parsed CSV data from the IoT sensor. This endpoint:
    1. Aggregates multiple readings into averages (moisture, pH, N, P, K)
    2. Saves the aggregated data to the database
    3. Chains to /soil-forecast/readings for forecast generation
    
    Returns the saved soil data and forecast response.
    """,
)
async def bulk_upload_soil_data(
    request: SoilDataBulkUploadRequest,
    db: Session = Depends(get_db),
):
    """
    Process bulk CSV data: aggregate, save, and chain to soil-forecast.
    """
    try:
        result = await soil_ctrl.bulk_upload_soil_data(db=db, request=request)
        return SoilDataBulkUploadResponse(
            soilData=result["soil_data"],
            forecast=result["forecast"],
            message=result["message"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing bulk upload: {str(e)}"
        )


@router.get(
    "/{soil_id}",
    response_model=SoilData,
    summary="Get a soil data record by ID",
)
def read_soil_data(soil_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieve a SoilData record by its UUID."""
    db_item = soil_ctrl.get_soil_data(db, soil_id=soil_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Soil data with ID {soil_id} not found")
    return db_item


@router.get(
    "/",
    response_model=List[SoilData],
    summary="List soil data records",
)
@searchable(fields=["sensor_id", "datetimestamp"], model=SoilDataModel)
def list_soil_data(
    skip: int = 0,
    limit: int = 100,
    status: Optional[bool] = None,
    db: Session = Depends(get_db),
    search: str = None,
):
    """List SoilData records with optional pagination and simple search."""
    return soil_ctrl.get_all_soil_data(db=db, skip=skip, limit=limit, status=status)


@router.post(
    "/upload-csv",
    response_model=SoilDataBulkUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a CSV file (aggregate + forecast)",
)
async def upload_soil_data_csv(
    file: UploadFile = File(...),
    farmerId: uuid.UUID = Form(...),
    plantingDate: str = Form(...),
    sensorId: Optional[uuid.UUID] = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a CSV file, aggregate rows into one SoilData, and generate a forecast."""
    try:
        result = await soil_ctrl.upload_soil_data_csv(
            db=db,
            file=file,
            farmer_id=farmerId,
            planting_date=plantingDate,
            sensor_id=sensorId,
        )
        return SoilDataBulkUploadResponse(
            soilData=result["soil_data"],
            forecast=result["forecast"],
            message=result["message"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CSV upload: {str(e)}",
        )


@router.delete(
    "/{soil_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a soil data record",
)
def delete_soil_data(soil_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a SoilData record by its UUID."""
    db_item = soil_ctrl.get_soil_data(db, soil_id=soil_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Soil data with ID {soil_id} not found")
    soil_ctrl.delete_soil_data(db=db, db_soil_data=db_item)
    return None
