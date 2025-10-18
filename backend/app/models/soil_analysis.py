import uuid
from sqlalchemy import UUID, Column, DateTime, Text, ForeignKey, func
from app.db import Base

class SoilAnalysis(Base):
    __tablename__ = "soil_analysis"
    analysis_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    soil_id = Column(UUID(as_uuid=True), ForeignKey("soil_data.soil_id"), nullable=False)
    analysis_date = Column(DateTime(timezone=True), nullable=False, default=func.now())
    soil_health_summary = Column(Text, nullable=False)
    recommendations = Column(Text, nullable=False)
