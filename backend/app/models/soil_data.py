from sqlalchemy import Column, String, TIMESTAMP, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base

# Base = declarative_base()

class SoilData(Base):
    __tablename__ = "soil_data"
    soil_id = Column(String(20), primary_key=True)
    timestamp = Column(TIMESTAMP, nullable=False)
    soil_moisture = Column(Float, nullable=False)
    soil_ph = Column(Float, nullable=False)
    nitrogen_level = Column(Float, nullable=False)
    phosphorus_level = Column(Float, nullable=False)
    potassium_level = Column(Float, nullable=False)
    sensor_id = Column(UUID, ForeignKey("soil_sensor_devices.sensor_id"), nullable=False)
