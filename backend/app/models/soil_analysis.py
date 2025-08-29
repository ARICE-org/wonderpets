from sqlalchemy import Column, String, TIMESTAMP, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.db import Base

# Base = declarative_base()

class SoilAnalysis(Base):
    __tablename__ = "soil_analysis"
    analysis_id = Column(String(20), primary_key=True)
    soil_id = Column(String(20), ForeignKey("soil_data.soil_id"), nullable=False)
    analysis_date = Column(TIMESTAMP, nullable=False)
    soil_health_summary = Column(Text, nullable=False)
    recommendations = Column(Text, nullable=False)
