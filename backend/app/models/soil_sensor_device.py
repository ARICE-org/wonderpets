from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db import Base
from datetime import datetime

class SoilSensorDevice(Base):
    __tablename__ = "soil_sensor_devices"
    
    sensor_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True
    )
    sensor_desc = Column(String(50), nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    device_status = Column(Boolean, default=True, nullable=False)
