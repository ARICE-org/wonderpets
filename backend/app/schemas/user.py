from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str = Field(..., alias="email")
    hashed_password: str = Field(..., alias="hashedPassword")

    model_config = {
        "populate_by_name": True,
    }

class UserCreate(UserBase):
    hashed_password: str = Field(..., alias="password")

    model_config = {
        "populate_by_name": True,
    }




class UserUpdate(BaseModel):
    email: Optional[str] = Field(..., alias="email")
    hashed_password: Optional[str] = Field(..., alias="hashedPassword")

    model_config = {
        "populate_by_name": True,
    }

class UserInDB(UserBase):
    uuid: UUID = Field(..., alias="userId")
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class User(UserBase):
    pass