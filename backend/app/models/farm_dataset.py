import uuid
from sqlalchemy import UUID, Column, DateTime, String, ForeignKey, func
from app.db import Base

class FarmDataset(Base):
    __tablename__ = "farm_dataset"
    farm_dataset_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rice_variety_id = Column(UUID(as_uuid=True), ForeignKey("rice_variety.rice_variety_id"), nullable=False)
    weather_id = Column(UUID(as_uuid=True), ForeignKey("weather_data.weather_id"), nullable=False)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("soil_analysis.analysis_id"), nullable=True)
    planting_date_start = Column(DateTime(timezone=True), nullable=False)
