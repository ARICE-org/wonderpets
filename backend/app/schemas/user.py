from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str = Field(..., alias="email")
    phone_number: Optional[str] = Field(..., alias="phoneNumber")

    model_config = {
        "populate_by_name": True,
    }

class UserCreate(UserBase):
    password: str = Field(..., alias="password")

    model_config = {
        "populate_by_name": True,
    }

class UserUpdate(BaseModel):
    email: Optional[str] = Field(..., alias="email")
    password: Optional[str] = Field(..., alias="password")
    phone_number: Optional[str] = Field(None, alias="phoneNumber")

    model_config = {
        "populate_by_name": True,
    }

class UserInDB(UserBase):
    user_id: UUID = Field(..., alias="userId")
    password: str = Field(..., alias="password")
    created_at: Optional[datetime] = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class User(UserBase):
    pass