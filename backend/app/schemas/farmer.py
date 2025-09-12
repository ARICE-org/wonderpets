from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

# Base schema with API-friendly camelCase field aliases
class FarmerBase(BaseModel):
    first_name: str = Field(..., alias="firstName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    last_name: str = Field(..., alias="lastName")
    address: str = Field(..., alias="address")
    phone_number: str = Field(..., alias="phoneNumber")

    model_config = {
        "populate_by_name": True,
    }


class FarmerCreate(FarmerBase):
    pass


class FarmerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, alias="firstName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    last_name: Optional[str] = Field(None, alias="lastName")
    address: Optional[str] = None
    phone_number: Optional[str] = Field(None, alias="phoneNumber")

    model_config = {
        "populate_by_name": True,
    }


class FarmerInDB(FarmerBase):
    farmer_id: UUID = Field(..., alias="farmerId")
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class Farmer(FarmerInDB):
    pass
