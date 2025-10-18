from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class SoilDataBase(BaseModel):
    datetimestamp: datetime = Field(..., alias="dateTimeStamp")
    soil_moisture: float = Field(..., alias="soilMoisture")
    soil_ph: float = Field(..., alias="soilPh")
    nitrogen_level: float = Field(..., alias="nitrogenLevel")
    phosphorus_level: float = Field(..., alias="phosphorusLevel")
    potassium_level: float = Field(..., alias="potassiumLevel")
    sensor_id: UUID = Field(..., alias="sensorId")

    model_config = {
        "populate_by_name": True,
    }

class SoilDataCreate(SoilDataBase):
    pass

class SoilDataUpdate(BaseModel):
    datetimestamp: Optional[datetime] = Field(None, alias="dateTimeStamp")
    soil_moisture: Optional[float] = Field(None, alias="soilMoisture")
    soil_ph: Optional[float] = Field(None, alias="soilPh")
    nitrogen_level: Optional[float] = Field(None, alias="nitrogenLevel")
    phosphorus_level: Optional[float] = Field(None, alias="phosphorusLevel")
    potassium_level: Optional[float] = Field(None, alias="potassiumLevel")
    sensor_id: Optional[UUID] = Field(None, alias="sensorId")

    model_config = {
        "populate_by_name": True,
    }

class SoilDataInDB(SoilDataBase):
    soil_id: UUID = Field(..., alias="soilId")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class SoilData(SoilDataInDB):
    pass
