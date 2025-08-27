from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FarmingScheduleBase(BaseModel):
    farmer_id: str = Field(..., alias="farmerId")
    farm_dataset_id: str = Field(..., alias="farmDatasetId")
    farmer_feedback: bool = Field(..., alias="farmerFeedback")

    model_config = {
        "populate_by_name": True,
    }

class FarmingScheduleCreate(FarmingScheduleBase):
    pass

class FarmingScheduleUpdate(BaseModel):
    farmer_id: Optional[str] = Field(None, alias="farmerId")
    farm_dataset_id: Optional[str] = Field(None, alias="farmDatasetId")
    farmer_feedback: Optional[bool] = Field(None, alias="farmerFeedback")

    model_config = {
        "populate_by_name": True,
    }

class FarmingScheduleInDB(FarmingScheduleBase):
    schedule_id: str = Field(..., alias="scheduleId")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class FarmingSchedule(FarmingScheduleInDB):
    pass
