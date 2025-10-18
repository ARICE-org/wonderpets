from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RiceVarietyBase(BaseModel):
    season_id: UUID = Field(..., alias="seasonId")
    rice_name: str = Field(..., alias="riceName")
    growth_duration: int = Field(..., alias="growthDuration")
    color: str = Field(..., alias="color")

    model_config = {
        "populate_by_name": True,
    }

class RiceVarietyCreate(RiceVarietyBase):
    pass

class RiceVarietyUpdate(BaseModel):
    season_id: Optional[UUID] = Field(None, alias="seasonId")
    rice_name: Optional[str] = Field(None, alias="riceName")
    growth_duration: Optional[int] = Field(None, alias="growthDuration")
    color: Optional[str] = Field(None, alias="color")


    model_config = {
        "populate_by_name": True,
    }

class RiceVarietyInDB(RiceVarietyBase):
    rice_variety_id: UUID = Field(..., alias="riceVarietyId")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class RiceVariety(RiceVarietyInDB):
    pass
