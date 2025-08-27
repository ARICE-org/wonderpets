from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime

class SoilSensorDeviceBase(BaseModel):
    sensor_desc: str = Field(..., alias="sensorDesc")
    curr_date: date = Field(..., alias="currDate")
    curr_time: time = Field(..., alias="currTime")
    device_status: bool = Field(..., alias="deviceStatus")

    model_config = {
        "populate_by_name": True,
    }

class SoilSensorDeviceCreate(SoilSensorDeviceBase):
    pass

class SoilSensorDeviceUpdate(BaseModel):
    sensor_desc: Optional[str] = Field(None, alias="sensorDesc")
    curr_date: Optional[date] = Field(None, alias="currDate")
    curr_time: Optional[time] = Field(None, alias="currTime")
    device_status: Optional[bool] = Field(None, alias="deviceStatus")

    model_config = {
        "populate_by_name": True,
    }

class SoilSensorDeviceInDB(SoilSensorDeviceBase):
    sensor_id: int = Field(..., alias="sensorId")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class SoilSensorDevice(SoilSensorDeviceInDB):
    pass
