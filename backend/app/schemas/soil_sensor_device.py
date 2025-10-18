from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class SoilSensorDeviceBase(BaseModel):
    sensor_desc: str = Field(..., max_length=50, alias="sensorDesc")
    device_status: bool = Field(default=True, alias="deviceStatus")

    model_config = {
        "populate_by_name": True,
    }

class SoilSensorDeviceCreate(SoilSensorDeviceBase):
    pass

class SoilSensorDeviceUpdate(BaseModel):
    sensor_desc: Optional[str] = Field(None, max_length=50, alias="sensorDesc")
    device_status: Optional[bool] = Field(None, alias="deviceStatus")
    updated_date: Optional[datetime] = Field(default=datetime.now(), alias="updatedDate")

    model_config = {
        "populate_by_name": True,
    }

class SoilSensorDeviceInDB(SoilSensorDeviceBase):
    sensor_id: UUID = Field(..., alias="sensorId")
    created_date: Optional[datetime] = Field(default=datetime.now(), alias="createdDate")
    updated_date: Optional[datetime] = Field(default=datetime.now(), alias="updatedDate")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class SoilSensorDevice(SoilSensorDeviceInDB):
    pass
