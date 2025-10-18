import uuid
from sqlalchemy import UUID, Column, DateTime, Float, CHAR, func
from app.db import Base

class WeatherData(Base):
    __tablename__ = "weather_data"
    weather_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime(timezone=True), nullable=False, default=func.now())
    max_temp = Column(Float, nullable=False)
    min_temp = Column(Float, nullable=False)
    rainfall = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    wind_direct = Column(CHAR(1), nullable=False)
