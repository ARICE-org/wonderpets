from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from .. import models
from app.schemas.soil_sensor_device import SoilSensorDevice, SoilSensorDeviceCreate, SoilSensorDeviceUpdate

def get_soil_sensor_device(db: Session, sensor_id: uuid.UUID) -> Optional[models.SoilSensorDevice]:
    """Get a single SoilSensorDevice by its UUID.

    Args:
        db: Session - Database session.
        sensor_id: uuid.UUID - The UUID of the sensor device to retrieve.

    Returns:
        Optional[models.SoilSensorDevice]: The matching SoilSensorDevice or
            ``None`` if no record is found.
    """
    return db.query(models.SoilSensorDevice).filter(models.SoilSensorDevice.sensor_id == sensor_id).first()

def get_soil_sensor_devices(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[bool] = None
    
) -> List[models.SoilSensorDevice]:
    """Retrieve SoilSensorDevice records with optional pagination and filtering.

    Args:
        db: Session - Database session.
        skip: int - Number of records to skip (offset).
        limit: int - Maximum number of records to return.
        status: Optional[bool] - Optional device status filter. When provided,
            the query will be filtered by `models.SoilSensorDevice.device_status`.

    Returns:
        List[models.SoilSensorDevice]: A list of matching SoilSensorDevice
            instances.
    """
    query = db.query(models.SoilSensorDevice)
    if status is not None:
        query = query.filter(models.SoilSensorDevice.device_status == status)
    return query.offset(skip).limit(limit).all()

def create_soil_sensor_device(
    db: Session, 
    sensor_data: SoilSensorDeviceCreate
) -> models.SoilSensorDevice:
    """Create a new SoilSensorDevice record.

    Args:
        db: Session - Database session.
        sensor_data: SoilSensorDeviceCreate - DTO containing fields for the
            new sensor device.

    Returns:
        models.SoilSensorDevice: The created SoilSensorDevice instance.
    """
    db_sensor = models.SoilSensorDevice(
        sensor_desc=sensor_data.sensor_desc,
        device_status=sensor_data.device_status
    )
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def update_soil_sensor_device(
    db: Session, 
    db_sensor: models.SoilSensorDevice,
    sensor_data: SoilSensorDeviceUpdate
) -> models.SoilSensorDevice:
    """Update fields on an existing SoilSensorDevice.

    Args:
        db: Session - Database session.
        db_sensor: models.SoilSensorDevice - The existing DB model instance to
            update.
        sensor_data: SoilSensorDeviceUpdate - Pydantic model containing the
            update fields. Only set fields will be applied.

    Returns:
        models.SoilSensorDevice: The updated SoilSensorDevice instance.
    """
    update_data = sensor_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_sensor, field, value)
    
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def delete_soil_sensor_device(
    db: Session, 
    db_sensor: models.SoilSensorDevice
) -> models.SoilSensorDevice:
    """Delete a SoilSensorDevice record.

    Args:
        db: Session - Database session.
        db_sensor: models.SoilSensorDevice - The instance to delete.

    Returns:
        models.SoilSensorDevice: The deleted SoilSensorDevice instance as it
            existed prior to deletion.
    """
    db.delete(db_sensor)
    db.commit()
    return db_sensor

