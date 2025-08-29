from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SeasonBase(BaseModel):
    name: str = Field(..., alias="name")

    model_config = {
        "populate_by_name": True,
    }

class SeasonCreate(SeasonBase):
    pass

class SeasonUpdate(BaseModel):
    name: Optional[str] = Field(None, alias="name")

    model_config = {
        "populate_by_name": True,
    }

class SeasonInDB(SeasonBase):
    season_id: str = Field(..., alias="seasonId")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class Season(SeasonInDB):
    pass
