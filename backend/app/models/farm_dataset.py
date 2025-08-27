from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.db import Base

# Base = declarative_base()

class FarmDataset(Base):
    __tablename__ = "farm_dataset"
    farm_dataset_id = Column(String(20), primary_key=True)
    rice_variety_id = Column(String(20), ForeignKey("rice_variety.rice_variety_id"), nullable=False)
    weather_id = Column(String(20), ForeignKey("weather_data.weather_id"), nullable=False)
    analysis_id = Column(String(20))
    planting_date_start = Column(TIMESTAMP, nullable=False)
