from sqlalchemy import UUID, Column, DateTime, Float, ForeignKey, func
import uuid
from app.db import Base

class SoilData(Base):
    __tablename__ = "soil_data"
    soil_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    datetimestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    soil_moisture = Column(Float, nullable=False)
    soil_ph = Column(Float, nullable=False)
    nitrogen_level = Column(Float, nullable=False)
    phosphorus_level = Column(Float, nullable=False)
    potassium_level = Column(Float, nullable=False)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("soil_sensor_devices.sensor_id"), nullable=False)
