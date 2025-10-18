from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from .. import models
from app.schemas.soil_sensor_device import SoilSensorDevice, SoilSensorDeviceCreate, SoilSensorDeviceUpdate

def get_soil_sensor_device(db: Session, sensor_id: uuid.UUID) -> Optional[models.SoilSensorDevice]:
    """Get a single soil sensor device by ID"""
    return db.query(models.SoilSensorDevice).filter(models.SoilSensorDevice.sensor_id == sensor_id).first()

def get_soil_sensor_devices(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[bool] = None
) -> List[models.SoilSensorDevice]:
    """Get a list of soil sensor devices with optional status filter"""
    query = db.query(models.SoilSensorDevice)
    if status is not None:
        query = query.filter(models.SoilSensorDevice.device_status == status)
    return query.offset(skip).limit(limit).all()

def create_soil_sensor_device(
    db: Session, 
    sensor_data: SoilSensorDeviceCreate
) -> models.SoilSensorDevice:
    """Create a new soil sensor device"""
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
    """Update an existing soil sensor device"""
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
    """Delete a soil sensor device"""
    db.delete(db_sensor)
    db.commit()
    return db_sensor
