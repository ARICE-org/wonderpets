import uuid
from sqlalchemy import UUID, Column, DateTime, String, Boolean, CHAR, ForeignKey, func
from app.db import Base

class Task(Base):
    __tablename__ = "task"
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("farming_schedule.schedule_id"), nullable=False)
    title = Column(String(50), nullable=False)
    caption = Column(String(200), nullable=False)
    status = Column(Boolean, nullable=False)
    priority_level = Column(CHAR(1), nullable=False)
    feedback = Column(Boolean, nullable=True)
    date = Column(DateTime(timezone=True), nullable=False)
