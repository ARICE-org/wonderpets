from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FarmDatasetBase(BaseModel):
    rice_variety_id: UUID = Field(..., alias="riceVarietyId")
    weather_id: UUID = Field(..., alias="weatherId")
    analysis_id: Optional[UUID] = Field(None, alias="analysisId")
    planting_date_start: datetime = Field(..., alias="plantingDateStart")

    model_config = {
        "populate_by_name": True,
    }

class FarmDatasetCreate(FarmDatasetBase):
    pass

class FarmDatasetUpdate(BaseModel):
    rice_variety_id: Optional[UUID] = Field(None, alias="riceVarietyId")
    weather_id: Optional[UUID] = Field(None, alias="weatherId")
    analysis_id: Optional[UUID] = Field(None, alias="analysisId")
    planting_date_start: Optional[datetime] = Field(None, alias="plantingDateStart")

    model_config = {
        "populate_by_name": True,
    }

class FarmDatasetInDB(FarmDatasetBase):
    farm_dataset_id: UUID = Field(..., alias="farmDatasetId")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class FarmDataset(FarmDatasetInDB):
    pass
