from sqlalchemy import UUID, Column, String, Boolean, DateTime, func
import uuid
from app.db import Base

class SoilSensorDevice(Base):
    __tablename__ = "soil_sensor_devices"
    sensor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_desc = Column(String(100), nullable=False)
    device_status = Column(Boolean, default=True, nullable=False)
    created_date = Column(DateTime(timezone=True), default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
