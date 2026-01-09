from pydantic import BaseModel, Field
from typing import Optional, List
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


# Bulk Upload Schemas for CSV processing
class SoilReadingItem(BaseModel):
    """Single reading from CSV data."""
    timestamp: datetime
    moisture: float = Field(..., ge=0, le=100)
    pH: float = Field(..., ge=0, le=14)
    nitrogen: float = Field(..., ge=0)
    phosphorus: float = Field(..., ge=0)
    potassium: float = Field(..., ge=0)
    organic_matter: Optional[float] = Field(None, ge=0, alias="organicMatter")
    temperature: Optional[float] = Field(None)

    model_config = {
        "populate_by_name": True,
    }


class SoilDataBulkUploadRequest(BaseModel):
    """Request for bulk uploading CSV-parsed soil data."""
    sensor_id: UUID = Field(..., alias="sensorId")
    farmer_id: UUID = Field(..., alias="farmerId")
    planting_date: str = Field(..., alias="plantingDate")
    readings: List[SoilReadingItem]

    model_config = {
        "populate_by_name": True,
    }


class SoilDataBulkUploadResponse(BaseModel):
    """Response from bulk upload with chained forecast."""
    soil_data: SoilData = Field(..., alias="soilData")
    forecast: Optional[dict] = None
    message: str

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

