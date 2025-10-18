from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    schedule_id: UUID = Field(..., alias="scheduleId")
    title: str = Field(..., alias="title")
    caption: str = Field(..., alias="caption")
    status: bool = Field(..., alias="status")
    priority_level: str = Field(..., alias="priorityLevel")
    feedback: Optional[bool] = Field(None, alias="feedback")
    date: datetime = Field(..., alias="date")

    model_config = {
        "populate_by_name": True,
    }

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, alias="title")
    caption: Optional[str] = Field(None, alias="caption")
    status: Optional[bool] = Field(None, alias="status")
    priority_level: Optional[str] = Field(None, alias="priorityLevel")
    feedback: Optional[bool] = Field(None, alias="feedback")
    date: Optional[datetime] = Field(None, alias="date")

    model_config = {
        "populate_by_name": True,
    }

class TaskInDB(TaskBase):
    task_id: UUID = Field(..., alias="taskId")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class Task(TaskInDB):
    pass
