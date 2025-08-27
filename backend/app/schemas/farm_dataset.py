from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FarmDatasetBase(BaseModel):
    rice_variety_id: str = Field(..., alias="riceVarietyId")
    weather_id: str = Field(..., alias="weatherId")
    analysis_id: Optional[str] = Field(None, alias="analysisId")
    planting_date_start: datetime = Field(..., alias="plantingDateStart")

    model_config = {
        "populate_by_name": True,
    }

class FarmDatasetCreate(FarmDatasetBase):
    pass

class FarmDatasetUpdate(BaseModel):
    rice_variety_id: Optional[str] = Field(None, alias="riceVarietyId")
    weather_id: Optional[str] = Field(None, alias="weatherId")
    analysis_id: Optional[str] = Field(None, alias="analysisId")
    planting_date_start: Optional[datetime] = Field(None, alias="plantingDateStart")

    model_config = {
        "populate_by_name": True,
    }

class FarmDatasetInDB(FarmDatasetBase):
    farm_dataset_id: str = Field(..., alias="farmDatasetId")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class FarmDataset(FarmDatasetInDB):
    pass
