from sqlalchemy import Column, Integer, String, Date, Time, Boolean
from sqlalchemy.ext.declarative import declarative_base
from app.db import Base

# Base = declarative_base()

class SoilSensorDevice(Base):
    __tablename__ = "soil_sensor_device"
    sensor_id = Column(Integer, primary_key=True)
    sensor_desc = Column(String(50), nullable=False)
    curr_date = Column(Date, nullable=False)
    curr_time = Column(Time, nullable=False)
    device_status = Column(Boolean, nullable=False)
