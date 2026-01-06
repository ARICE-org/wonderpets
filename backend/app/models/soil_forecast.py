"""
Soil Forecast Database Model

Model for storing soil forecasts, readings, and realignment history.
"""

import uuid
from sqlalchemy import (
    UUID, Column, DateTime, Float, ForeignKey, Integer, 
    String, Text, Boolean, JSON, func
)
from sqlalchemy.orm import relationship
from app.db import Base


class SoilForecast(Base):
    """
    Active forecasts table.
    
    Stores the generated 3-month soil forecasts for each farm/planting season.
    """
    __tablename__ = "soil_forecasts"
    
    # Primary key
    forecast_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farmer.farmer_id"), nullable=False)
    
    # Forecast period
    planting_date = Column(DateTime(timezone=True), nullable=False)
    forecast_start_date = Column(DateTime(timezone=True), nullable=False)
    forecast_end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Status: 'active', 'completed', 'superseded'
    status = Column(String(20), default='active', nullable=False)
    
    # Model information
    model_version = Column(String(20), default='1.0')
    approach_used = Column(String(20), default='hybrid')  # 'hybrid', 'rule_based', 'pure_ml'
    
    # Baseline reading at forecast creation (JSON)
    # Stores the aggregated sensor data used to generate the forecast
    baseline_reading = Column(JSON, nullable=True)
    
    # Current forecast data (JSON)
    # Updated on each realignment
    forecast_data = Column(JSON, nullable=False)
    
    # Weekly summary for quick access (JSON array)
    weekly_summary = Column(JSON, nullable=True)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    last_realignment_date = Column(DateTime(timezone=True), nullable=True)
    realignment_count = Column(Integer, default=0)
    
    # Relationships
    readings = relationship("SoilReading", back_populates="forecast")
    realignments = relationship("ForecastRealignment", back_populates="forecast")
    
    def __repr__(self):
        return f"<SoilForecast(id={self.forecast_id}, farm={self.farm_id}, status={self.status})>"


class SoilReading(Base):
    """
    Soil reading history table.
    
    Stores each sensor reading upload for a farm, linked to active forecasts.
    """
    __tablename__ = "soil_readings"
    
    # Primary key
    reading_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farmer.farmer_id"), nullable=False)
    forecast_id = Column(UUID(as_uuid=True), ForeignKey("soil_forecasts.forecast_id"), nullable=True)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("soil_sensor_devices.sensor_id"), nullable=True)
    
    # Reading metadata
    reading_date = Column(DateTime(timezone=True), nullable=False)
    week_number = Column(Integer, nullable=True)
    
    # Aggregated readings (JSON objects with mean, std, min, max, trend)
    nitrogen_ppm = Column(JSON, nullable=True)
    phosphorus_ppm = Column(JSON, nullable=True)
    potassium_meq = Column(JSON, nullable=True)
    ph = Column(JSON, nullable=True)
    soil_moisture_pct = Column(JSON, nullable=True)
    organic_matter_pct = Column(JSON, nullable=True)
    
    # Calculated health score at time of reading
    health_score = Column(Float, nullable=True)
    health_category = Column(String(20), nullable=True)
    
    # Raw readings (optional, for audit purposes)
    raw_readings = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    forecast = relationship("SoilForecast", back_populates="readings")
    realignment = relationship("ForecastRealignment", back_populates="reading", uselist=False)
    
    def __repr__(self):
        return f"<SoilReading(id={self.reading_id}, farm={self.farm_id}, week={self.week_number})>"


class ForecastRealignment(Base):
    """
    Forecast realignment history table.
    
    Tracks each time a forecast was realigned based on new sensor data.
    Useful for auditing and improving model accuracy.
    """
    __tablename__ = "forecast_realignments"
    
    # Primary key
    realignment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    forecast_id = Column(UUID(as_uuid=True), ForeignKey("soil_forecasts.forecast_id"), nullable=False)
    reading_id = Column(UUID(as_uuid=True), ForeignKey("soil_readings.reading_id"), nullable=False)
    
    # Realignment metadata
    realignment_date = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    week_of_realignment = Column(Integer, nullable=False)
    
    # What changed (JSON objects)
    deviations = Column(JSON, nullable=False)  # Predicted vs actual for each parameter
    corrections_applied = Column(JSON, nullable=False)  # Correction strategy per parameter
    
    # Full reforecast flag
    required_reforecast = Column(Boolean, default=False)
    
    # Before and after snapshots (JSON)
    # Useful for debugging and model improvement
    forecast_before = Column(JSON, nullable=True)
    forecast_after = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    forecast = relationship("SoilForecast", back_populates="realignments")
    reading = relationship("SoilReading", back_populates="realignment")
    
    def __repr__(self):
        return f"<ForecastRealignment(id={self.realignment_id}, week={self.week_of_realignment})>"
