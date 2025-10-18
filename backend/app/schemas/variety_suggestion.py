from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VarietySuggestionBase(BaseModel):
    rice_variety_id: UUID = Field(..., alias="riceVarietyId")
    date_generated: datetime = Field(..., alias="dateGenerated")
    feedback: bool = Field(..., alias="feedback")

    model_config = {
        "populate_by_name": True,
    }

class VarietySuggestionCreate(VarietySuggestionBase):
    pass

class VarietySuggestionUpdate(BaseModel):
    rice_variety_id: Optional[UUID] = Field(None, alias="riceVarietyId")
    date_generated: Optional[datetime] = Field(None, alias="dateGenerated")
    feedback: Optional[bool] = Field(None, alias="feedback")

    model_config = {
        "populate_by_name": True,
    }

class VarietySuggestionInDB(VarietySuggestionBase):
    variety_sugg_id: str = Field(..., alias="varietySuggId")
    created_date: Optional[datetime] = Field(default=datetime.now(), alias="createdDate")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class VarietySuggestion(VarietySuggestionInDB):
    pass
