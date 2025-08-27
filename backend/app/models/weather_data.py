from sqlalchemy import Column, String, TIMESTAMP, Float, CHAR
from sqlalchemy.ext.declarative import declarative_base
from app.db import Base

# Base = declarative_base()

class WeatherData(Base):
    __tablename__ = "weather_data"
    weather_id = Column(String(20), primary_key=True)
    datetime = Column(TIMESTAMP, nullable=False)
    max_temp = Column(Float, nullable=False)
    min_temp = Column(Float, nullable=False)
    rainfall = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    wind_direct = Column(CHAR(1), nullable=False)
