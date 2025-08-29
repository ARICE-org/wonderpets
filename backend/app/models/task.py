from sqlalchemy import Column, String, Boolean, TIMESTAMP, CHAR, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.db import Base

# Base = declarative_base()

class Task(Base):
    __tablename__ = "task"
    task_id = Column(String(20), primary_key=True)
    schedule_id = Column(String(20), ForeignKey("farming_schedule.schedule_id"), nullable=False)
    title = Column(String(50), nullable=False)
    caption = Column(String(200), nullable=False)
    status = Column(Boolean, nullable=False)
    priority_level = Column(CHAR(1), nullable=False)
    feedback = Column(Boolean, nullable=False)
    date = Column(TIMESTAMP, nullable=False)
