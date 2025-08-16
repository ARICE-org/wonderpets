from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Base schema with API-friendly camelCase field aliases
class UserBase(BaseModel):
    first_name: str = Field(..., alias="firstName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    last_name: str = Field(..., alias="lastName")
    address: str = Field("pacol,nagacity")
    phone_number: str = Field(..., alias="phoneNumber")

    model_config = {
        "populate_by_name": True,
    }


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, alias="firstName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    last_name: Optional[str] = Field(None, alias="lastName")
    address: Optional[str] = None
    phone_number: Optional[str] = Field(None, alias="phoneNumber")

    model_config = {
        "populate_by_name": True,
    }


class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class User(UserInDB):
    pass
