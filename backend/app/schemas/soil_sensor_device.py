from pydantic import BaseModel, Field, UUID4, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class SoilSensorDeviceBase(BaseModel):
    sensor_desc: str = Field(..., max_length=50, alias="sensorDesc")
    device_status: bool = Field(default=True, alias="deviceStatus")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class SoilSensorDeviceCreate(SoilSensorDeviceBase):
    pass

class SoilSensorDevice(SoilSensorDeviceBase):
    sensor_id: uuid.UUID = Field(..., alias="sensorId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

class SoilSensorDeviceUpdate(BaseModel):
    sensor_desc: Optional[str] = Field(None, max_length=50, alias="sensorDesc")
    device_status: Optional[bool] = Field(None, alias="deviceStatus")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class SoilSensorDeviceInDB(SoilSensorDeviceBase):
    sensor_id: UUID4 = Field(..., alias="sensorId")
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class SoilSensorDevice(SoilSensorDeviceInDB):
    pass
