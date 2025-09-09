from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base

class FarmingSchedule(Base):
    __tablename__ = "farming_schedule"
    schedule_id = Column(String(20), primary_key=True)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmer.farmer_id"), nullable=False)
    farm_dataset_id = Column(String(20), ForeignKey("farm_dataset.farm_dataset_id"), nullable=False)
    farmer_feedback = Column(Boolean, nullable=False)
