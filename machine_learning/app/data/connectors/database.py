"""
Database Connector

PostgreSQL database connection and query utilities for the ML service.
"""

from typing import Any, Dict, List, Optional
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """
    Database connector for PostgreSQL.
    
    Handles:
    - Connection pooling
    - Query execution
    - Data fetching for ML training/inference
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database connector.
        
        Args:
            database_url: Database connection URL (defaults to settings)
        """
        self.database_url = database_url or settings.DATABASE_URL
        self._engine = None
        self._session_factory = None
    
    def connect(self) -> None:
        """Establish database connection with connection pooling."""
        try:
            self._engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True
            )
            self._session_factory = sessionmaker(bind=self._engine)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database connection closed")
    
    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.
        
        Yields:
            SQLAlchemy session
        """
        if not self._session_factory:
            self.connect()
        
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
    
    # Data fetching methods for ML
    
    def get_soil_data(
        self,
        farm_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch soil sensor data for ML training/inference.
        
        Args:
            farm_id: Optional farm ID to filter
            start_date: Start date for data range
            end_date: End date for data range
            limit: Maximum number of records
            
        Returns:
            List of soil data records
        """
        query = """
            SELECT 
                sd.id,
                sd.soil_sensor_device_id,
                sd.ph,
                sd.nitrogen,
                sd.phosphorus,
                sd.potassium,
                sd.moisture,
                sd.temperature,
                sd.timestamp,
                ssd.farmer_id
            FROM soil_data sd
            JOIN soil_sensor_devices ssd ON sd.soil_sensor_device_id = ssd.id
            WHERE 1=1
        """
        params = {}
        
        if farm_id:
            query += " AND ssd.farmer_id = :farm_id"
            params["farm_id"] = farm_id
        
        if start_date:
            query += " AND sd.timestamp >= :start_date"
            params["start_date"] = start_date
        
        if end_date:
            query += " AND sd.timestamp <= :end_date"
            params["end_date"] = end_date
        
        query += " ORDER BY sd.timestamp DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query, params)
    
    def get_weather_data(
        self,
        location_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch weather data for ML training/inference.
        
        Args:
            location_id: Optional location/farm ID
            start_date: Start date for data range
            end_date: End date for data range
            limit: Maximum number of records
            
        Returns:
            List of weather data records
        """
        query = """
            SELECT 
                id,
                farm_dataset_id,
                temperature,
                humidity,
                rainfall,
                wind_speed,
                weather_condition,
                recorded_at
            FROM weather_data
            WHERE 1=1
        """
        params = {}
        
        if location_id:
            query += " AND farm_dataset_id = :location_id"
            params["location_id"] = location_id
        
        if start_date:
            query += " AND recorded_at >= :start_date"
            params["start_date"] = start_date
        
        if end_date:
            query += " AND recorded_at <= :end_date"
            params["end_date"] = end_date
        
        query += " ORDER BY recorded_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query, params)
    
    def get_rice_varieties(self) -> List[Dict[str, Any]]:
        """
        Fetch all rice varieties for recommendation model.
        
        Returns:
            List of rice variety records
        """
        query = """
            SELECT 
                id,
                name,
                description,
                maturity_days,
                yield_potential,
                water_requirement,
                disease_resistance
            FROM rice_varieties
            WHERE is_active = true
            ORDER BY name
        """
        return self.execute_query(query)
    
    def get_farming_history(
        self,
        farmer_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch farming history for training data.
        
        Args:
            farmer_id: Optional farmer ID to filter
            limit: Maximum number of records
            
        Returns:
            List of farming history records
        """
        query = """
            SELECT 
                fh.id,
                fh.farmer_id,
                fh.rice_variety_id,
                fh.season_id,
                fh.planting_date,
                fh.harvest_date,
                fh.yield_amount,
                fh.notes,
                rv.name as variety_name,
                s.name as season_name
            FROM farming_history fh
            JOIN rice_varieties rv ON fh.rice_variety_id = rv.id
            JOIN seasons s ON fh.season_id = s.id
            WHERE 1=1
        """
        params = {}
        
        if farmer_id:
            query += " AND fh.farmer_id = :farmer_id"
            params["farmer_id"] = farmer_id
        
        query += " ORDER BY fh.planting_date DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query, params)
    
    def health_check(self) -> bool:
        """
        Check database connection health.
        
        Returns:
            True if connection is healthy
        """
        try:
            result = self.execute_query("SELECT 1 as health")
            return len(result) > 0
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
