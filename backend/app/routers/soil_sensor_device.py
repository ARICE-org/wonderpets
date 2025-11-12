from app.packages.decorators.search_helpers import searchable
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.dependencies import get_db
from app.models.soil_sensor_device import SoilSensorDevice as SoilSensorDeviceModel
from app.schemas.soil_sensor_device import SoilSensorDevice, SoilSensorDeviceCreate, SoilSensorDeviceUpdate
from app.controllers.soil_sensor_device import get_soil_sensor_device, get_soil_sensor_devices, create_soil_sensor_device, update_soil_sensor_device, delete_soil_sensor_device

router = APIRouter(
    prefix="/sensors",
    tags=["Sensors"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/",
    response_model=SoilSensorDevice,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new soil sensor device"
)
def create_soil_sensor(
    sensor: SoilSensorDeviceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new soil sensor device with the given details.
    """
    return create_soil_sensor_device(db=db, sensor_data=sensor)

@router.get(
    "/{sensor_id}",
    response_model=SoilSensorDevice,
    summary="Get a specific soil sensor device by ID"
)
def read_soil_sensor(
    sensor_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific soil sensor device by its unique ID.
    """
    db_sensor = get_soil_sensor_device(db, sensor_id=sensor_id)
    if db_sensor is None:
        raise HTTPException(
            status_code=404,
            detail=f"Soil sensor device with ID {sensor_id} not found"
        )
    return db_sensor

@router.get(
    "/",
    response_model=List[SoilSensorDevice],
    summary="List all soil sensor devices"
)
@searchable(fields=["sensor_desc", "device_status"], mode="ilike", model=SoilSensorDeviceModel)
def list_soil_sensors(
    skip: int = 0,
    limit: int = 100,
    status: bool = True,
    db: Session = Depends(get_db),
    search: str = None
):
    """
    Retrieve a list of all soil sensor devices with optional status filtering.
    """
    return get_soil_sensor_devices(
        db, 
        skip=skip, 
        limit=limit, 
        status=status,
        search=search
    )

@router.put(
    "/{sensor_id}",
    response_model=SoilSensorDevice,
    summary="Update a soil sensor device"
)
def update_soil_sensor(
    sensor_id: uuid.UUID,
    sensor: SoilSensorDeviceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update the details of a specific soil sensor device.
    """
    db_sensor = get_soil_sensor_device(db, sensor_id=sensor_id)
    if db_sensor is None:
        raise HTTPException(
            status_code=404,
            detail=f"Soil sensor device with ID {sensor_id} not found"
        )
    return update_soil_sensor_device(
        db=db, 
        db_sensor=db_sensor, 
        sensor_data=sensor
    )

@router.delete(
    "/{sensor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a soil sensor device"
)
def delete_soil_sensor(
    sensor_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a specific soil sensor device by its ID.
    """
    db_sensor = get_soil_sensor_device(db, sensor_id=sensor_id)
    if db_sensor is None:
        raise HTTPException(
            status_code=404,
            detail=f"Soil sensor device with ID {sensor_id} not found"
        )
    delete_soil_sensor_device(db=db, db_sensor=db_sensor)
    return None



# def get_soil_sensor_device(db: Session, sensor_id: uuid.UUID) -> Optional[models.SoilSensorDevice]:
#     """Get a single soil sensor device by ID"""
#     return db.query(models.SoilSensorDevice).filter(models.SoilSensorDevice.sensor_id == sensor_id).first()
