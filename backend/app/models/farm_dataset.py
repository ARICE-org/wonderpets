from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from app.db import Base

class FarmDataset(Base):
    __tablename__ = "farm_dataset"
    farm_dataset_id = Column(String(20), primary_key=True)
    rice_variety_id = Column(String(20), ForeignKey("rice_variety.rice_variety_id"), nullable=False)
    weather_id = Column(String(20), ForeignKey("weather_data.weather_id"), nullable=False)
    analysis_id = Column(String(20))
    planting_date_start = Column(TIMESTAMP, nullable=False)
