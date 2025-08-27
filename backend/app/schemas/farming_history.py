from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class FarmingHistoryBase(BaseModel):
    farmer_id: str = Field(..., alias="farmerId")
    history_date: Optional[date] = Field(None, alias="historyDate")
    history_title: Optional[str] = Field(None, alias="historyTitle")
    yields: Optional[float]

    model_config = {
        "populate_by_name": True,
    }

class FarmingHistoryCreate(FarmingHistoryBase):
    pass

class FarmingHistoryUpdate(BaseModel):
    farmer_id: Optional[str] = Field(None, alias="farmerId")
    history_date: Optional[date] = Field(None, alias="historyDate")
    history_title: Optional[str] = Field(None, alias="historyTitle")
    yields: Optional[float]

    model_config = {
        "populate_by_name": True,
    }

class FarmingHistoryInDB(FarmingHistoryBase):
    history_id: str = Field(..., alias="historyId")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class FarmingHistory(FarmingHistoryInDB):
    pass
