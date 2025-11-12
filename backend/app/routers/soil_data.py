from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
import io
import uuid

from sqlalchemy.orm import Session

from app.dependencies import get_db
from app import models
from app.models.soil_data import SoilData as SoilDataModel
from app.schemas.soil_data import SoilData, SoilDataCreate
from app.packages.decorators.search_helpers import searchable


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
    """Create a single SoilData record."""
    db_soil = models.SoilData(
        sensor_id=soil.sensor_id,
        datetimestamp=soil.datetimestamp,
        soil_moisture=soil.soil_moisture,
        soil_ph=soil.soil_ph,
        nitrogen_level=soil.nitrogen_level,
        phosphorus_level=soil.phosphorus_level,
        potassium_level=soil.potassium_level,
    )
    db.add(db_soil)
    db.commit()
    db.refresh(db_soil)
    return db_soil


@router.get(
    "/{soil_id}",
    response_model=SoilData,
    summary="Get a soil data record by ID",
)
def read_soil_data(soil_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieve a SoilData record by its UUID."""
    db_item = db.query(models.SoilData).filter(models.SoilData.soil_id == soil_id).first()
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
    query = db.query(models.SoilData)
    if status is not None:
        query = query.filter(models.SoilData.sensor_id == status)
    return query.offset(skip).limit(limit).all()


@router.post(
    "/upload-csv",
    response_model=List[SoilData],
    summary="Upload a CSV file to bulk create soil data",
)
def upload_soil_data_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a CSV file and create SoilData records in bulk.

    Expected CSV columns: sensor_id, moisture_level, pH_level, temperature
    (column names are case-sensitive and must match the upload handling code).
    """
    # Delegate to the controller-like logic in-place: parse CSV and create records
    contents = file.file.read().decode("utf-8")
    import pandas as pd
    df = pd.read_csv(io.StringIO(contents))
    created = []
    for _, row in df.iterrows():
        sd = SoilDataCreate(
            sensor_id=row["sensor_id"],
            datetimestamp=row.get("datetimestamp") or row.get("dateTimeStamp"),
            soil_moisture=row.get("soil_moisture") or row.get("soilMoisture"),
            soil_ph=row.get("soil_ph") or row.get("soilPh"),
            nitrogen_level=row.get("nitrogen_level") or row.get("nitrogenLevel"),
            phosphorus_level=row.get("phosphorus_level") or row.get("phosphorusLevel"),
            potassium_level=row.get("potassium_level") or row.get("potassiumLevel"),
        )
        db_item = models.SoilData(
            sensor_id=sd.sensor_id,
            datetimestamp=sd.datetimestamp,
            soil_moisture=sd.soil_moisture,
            soil_ph=sd.soil_ph,
            nitrogen_level=sd.nitrogen_level,
            phosphorus_level=sd.phosphorus_level,
            potassium_level=sd.potassium_level,
        )
        db.add(db_item)
        created.append(db_item)
    db.commit()
    for it in created:
        db.refresh(it)
    return created


@router.delete(
    "/{soil_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a soil data record",
)
def delete_soil_data(soil_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a SoilData record by its UUID."""
    db_item = db.query(models.SoilData).filter(models.SoilData.soil_id == soil_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Soil data with ID {soil_id} not found")
    db.delete(db_item)
    db.commit()
    return None
