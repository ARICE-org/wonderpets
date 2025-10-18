import uuid
from sqlalchemy import UUID, Column, Boolean, DateTime, ForeignKey, func
from app.db import Base

class FarmingSchedule(Base):
    __tablename__ = "farming_schedule"
    schedule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmer.farmer_id"), nullable=False)
    farm_dataset_id = Column(UUID(as_uuid=True), ForeignKey("farm_dataset.farm_dataset_id"), nullable=False)
    farmer_feedback = Column(Boolean, nullable=True)
