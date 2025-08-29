from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.db import Base

# Base = declarative_base()

class RiceVariety(Base):
    __tablename__ = "rice_variety"
    rice_variety_id = Column(String(20), primary_key=True)
    season_id = Column(String(20), ForeignKey("season.season_id"), nullable=False)
    rice_name = Column(String(100), nullable=False)
    growth_duration = Column(Integer, nullable=False)
    color = Column(String(20), nullable=False)
