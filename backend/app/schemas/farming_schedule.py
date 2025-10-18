from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class FarmingScheduleBase(BaseModel):
    farmer_id: UUID = Field(..., alias="farmerId")
    farm_dataset_id: UUID = Field(..., alias="farmDatasetId")
    farmer_feedback: Optional[bool] = Field(None, alias="farmerFeedback")

    model_config = {
        "populate_by_name": True,
    }

class FarmingScheduleCreate(FarmingScheduleBase):
    pass

class FarmingScheduleUpdate(BaseModel):
    farmer_id: Optional[UUID] = Field(None, alias="farmerId")
    farm_dataset_id: Optional[UUID] = Field(None, alias="farmDatasetId")
    farmer_feedback: Optional[bool] = Field(None, alias="farmerFeedback")

    model_config = {
        "populate_by_name": True,
    }

class FarmingScheduleInDB(FarmingScheduleBase):
    schedule_id: UUID = Field(..., alias="scheduleId")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class FarmingSchedule(FarmingScheduleInDB):
    pass
