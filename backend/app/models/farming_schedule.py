from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.db import Base

# Base = declarative_base()

class FarmingSchedule(Base):
    __tablename__ = "farming_schedule"
    schedule_id = Column(String(20), primary_key=True)
    farmer_id = Column(String(20), ForeignKey("farmer.farmer_id"), nullable=False)
    farm_dataset_id = Column(String(20), ForeignKey("farm_dataset.farm_dataset_id"), nullable=False)
    farmer_feedback = Column(Boolean, nullable=False)
