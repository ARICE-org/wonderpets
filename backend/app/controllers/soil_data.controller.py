import io
from sqlalchemy.orm import Session 
from typing import List, Optional
import uuid
from .. import models
from app.schemas.soil_data import SoilDataBase, SoilData, SoilDataCreate, SoilDataUpdate
import pandas as pd
from fastapi import UploadFile, File


def get_soil_data(db: Session, soil_id: uuid.UUID) -> Optional[models.SoilData]:
    """Get a single SoilData record by its UUID.

    Args:
        db: Session - Database session.
        soil_id: uuid.UUID - The UUID of the SoilData to retrieve.

    Returns:
        Optional[models.SoilData]: The matching SoilData instance or ``None`` if
            no record is found.
    """
    return db.query(models.SoilData).filter(models.SoilData.soil_id == soil_id).first()

def get_all_soil_data(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[bool] = None
) -> List[models.SoilData]:
    """Retrieve SoilData records with optional pagination and status filter.

    Args:
        db: Session - Database session.
        skip: int - Number of records to skip (offset).
        limit: int - Maximum number of records to return.
        status: Optional[bool] - Optional status filter. When provided, the
            query is filtered accordingly.

    Returns:
        List[models.SoilData]: A list of SoilData records matching the query.
    """
    query = db.query(models.SoilData)
    if status is not None: 
        query = query.filter(models.SoilSensorDevice.sensor_id == status)
    return query.offset(skip).limit(limit).all()


def create_soil_data(
    db: Session, 
    soil_data: SoilDataCreate
) -> models.SoilData:
    """Create a new SoilData record from a schema object.

    Args:
        db: Session - Database session.
        soil_data: SoilDataCreate - Data transfer object containing fields to
            create the SoilData record.

    Returns:
        models.SoilData: The newly created SoilData instance.
    """

    db_soil_data = models.SoilData(
        sensor_id=soil_data.sensor_id,
        moisture_level=soil_data.moisture_level,
        pH_level=soil_data.pH_level,
        temperature=soil_data.temperature
    )
    db.add(db_soil_data)
    db.commit()
    db.refresh(db_soil_data)
    return db_soil_data


def bulk_create_soil_data(
    db: Session,
    soil_data_list: List[SoilDataCreate]
) -> List[models.SoilData]:
    """Create multiple SoilData records in a single operation.

    Args:
        db: Session - Database session.
        soil_data_list: List[SoilDataCreate] - List of DTOs describing each
            SoilData to create.

    Returns:
        List[models.SoilData]: The list of created SoilData instances.
    """
    db_soil_data_list = []
    for soil_data in soil_data_list:
        db_soil_data = models.SoilData(
            sensor_id=soil_data.sensor_id,
            moisture_level=soil_data.moisture_level,
            pH_level=soil_data.pH_level,
            temperature=soil_data.temperature
        )
        db.add(db_soil_data)
        db_soil_data_list.append(db_soil_data)
    db.commit()
    for db_soil_data in db_soil_data_list:
        db.refresh(db_soil_data)
    return db_soil_data_list

def delete_soil_data(
    db: Session, 
    db_soil_data: models.SoilData
) -> models.SoilData:
    """Delete an existing SoilData record.

    Args:
        db: Session - Database session.
        db_soil_data: models.SoilData - The SoilData instance to delete.

    Returns:
        models.SoilData: The deleted SoilData instance as it existed prior to
            deletion.
    """
    db.delete(db_soil_data)
    db.commit()
    return db_soil_data


async def upload_soil_data_csv(
       db: Session,
       file: UploadFile
   ):
       """Bulk create SoilData records from an uploaded CSV file.

       Args:
           db: Session - Database session.
           file: UploadFile - CSV file to parse. Expected columns: sensor_id,
               moisture_level, pH_level, temperature.

       Returns:
           List[models.SoilData]: The list of created SoilData instances.
       """

       contents = await file.read()
       df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
       soil_data_list = [
           SoilDataCreate(
               sensor_id=row["sensor_id"],
               moisture_level=row["moisture_level"],
               pH_level=row["pH_level"],
               temperature=row["temperature"]
           ) for index, row in df.iterrows()
       ]
       return bulk_create_soil_data(db, soil_data_list)
