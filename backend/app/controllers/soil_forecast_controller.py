"""
Soil Forecast Controller

Backend controller that orchestrates soil analysis.
Frontend only talks to this - never directly to ML service.

This controller handles:
1. Request validation and orchestration
2. Database operations (CRUD)
3. Coordinating between ML service and business logic service
4. Response formatting

Business logic is delegated to SoilForecastService for maintainability.
"""

from typing import Dict, Optional, Any, List
from datetime import datetime, date, timedelta
from uuid import UUID
import uuid

from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.soil_sensor_device import SoilSensorDevice
from app.schemas.soil_forecast import (
    UploadSensorDataRequest,
    SoilAnalysisResponse,
    GetForecastResponse,
    HealthScoreResponse,
    ReadingHistoryResponse,
    ReadingHistoryItem,
    ForecastSummary,
    TrendDirection,
)
from app.packages.sensor_aggregator import sensor_aggregator
from app.packages.ml_client import ml_client, MLServiceClient
from app.models.soil_forecast import SoilForecast, SoilReading, ForecastRealignment
from app.services.soil_forecast_service import soil_forecast_service, SoilForecastService


class EntityNotFoundError(Exception):
    """Exception raised when required entities (farmer/sensor) are not found."""
    def __init__(self, details: List[str]):
        self.details = details
        super().__init__(f"Validation failed: {details}")


class SoilForecastController:
    """
    Controller for soil forecast operations.
    
    Orchestrates the flow between Frontend, Database, and ML Service.
    Delegates business logic to SoilForecastService.
    """
    
    def __init__(
        self,
        ml_service: Optional[MLServiceClient] = None,
        forecast_service: Optional[SoilForecastService] = None
    ):
        """
        Initialize the controller.
        
        Args:
            ml_service: Optional ML service client for dependency injection
            forecast_service: Optional forecast service for dependency injection
        """
        self.ml_client = ml_service or ml_client
        self.service = forecast_service or soil_forecast_service
    
    async def process_sensor_reading(
        self,
        db: Session,
        request: UploadSensorDataRequest
    ) -> SoilAnalysisResponse:
        """
        Main endpoint called by Frontend.
        Handles everything: validation, DB, ML calls, response formatting.
        
        Args:
            db: Database session
            request: Sensor data upload request from frontend
            
        Returns:
            SoilAnalysisResponse with health score, forecast, and recommendations
            
        Raises:
            EntityNotFoundError: If farmer or sensor ID doesn't exist
        """
        # 0. Validate farmer and sensor existence BEFORE any processing
        validation_errors = await self._validate_entities(
            db=db,
            farmer_id=request.farmer_id,
            sensor_id=request.sensor_id
        )
        if validation_errors:
            raise EntityNotFoundError(details=validation_errors)
        
        # 1. Convert readings to dictionaries for aggregation
        readings_dicts = [
            {
                "timestamp": r.timestamp,
                "nitrogen": r.nitrogen,
                "phosphorus": r.phosphorus,
                "potassium": r.potassium,
                "pH": r.ph,
                "moisture": r.moisture,
                "organic_matter": r.organic_matter,
                "temperature": r.temperature,
            }
            for r in request.readings
        ]
        
        # 2. Aggregate readings
        aggregated = sensor_aggregator.aggregate(readings_dicts)
        
        # 3. Determine reading date
        reading_date = request.reading_date or date.today()
        
        # 4. Calculate current week
        days_since_planting = (reading_date - request.planting_date).days
        current_week = max(1, (days_since_planting // 7) + 1)
        
        # 5. Calculate health score using service
        health_score = self.service.calculate_health_score(aggregated)
        health_category = self.service.get_health_category(health_score)
        
        # 6. Check for active forecast
        active_forecast = await self._get_active_forecast(
            db=db,
            farm_id=request.farmer_id,
            planting_date=request.planting_date
        )
        
        # 7. Determine realignment strategy using service
        strategy = self.service.determine_realignment_strategy(
            active_forecast=active_forecast,
            aggregated_data=aggregated,
            current_week=current_week,
            reading_date=reading_date
        )
        
        # 8. Call ML Service based on strategy
        try:
            if strategy["should_realign"]:
                # Realign existing forecast based on strategy
                ml_response = await self.ml_client.realign_forecast(
                    current_data=aggregated,
                    existing_forecast=active_forecast.get("forecast_data", {}),
                    current_week=current_week
                )
                status = f"forecast_realigned_{strategy['strategy'].lower()}"
                
                # Calculate deviations from weekly summary
                weekly_summary = active_forecast.get("forecast_data", {}).get("weekly_summary", [])
                predicted_week = next(
                    (w for w in weekly_summary if w.get("week_number") == current_week),
                    {}
                )
                deviations = self.service.calculate_deviations(
                    predicted=predicted_week,
                    actual=aggregated
                )
            else:
                # Generate new forecast
                ml_response = await self.ml_client.generate_forecast(
                    current_data=aggregated,
                    planting_date=request.planting_date
                )
                status = "new_forecast_generated"
                deviations = None
                
        except Exception as e:
            # Fallback: generate forecast locally without ML service
            ml_response = self.service.generate_fallback_forecast(
                aggregated_data=aggregated,
                planting_date=request.planting_date,
                current_week=current_week
            )
            status = "new_forecast_generated"
            deviations = None
        
        # 9. Save/update forecast in database
        forecast_record = await self._save_or_update_forecast(
            db=db,
            farm_id=request.farmer_id,
            planting_date=request.planting_date,
            forecast_data=ml_response,
            is_realignment=strategy["should_realign"],
            baseline_reading=aggregated if not strategy["should_realign"] else None
        )
        
        # 10. Store reading in database (after forecast so we can link it)
        reading_record = await self._save_reading(
            db=db,
            farm_id=request.farmer_id,
            sensor_id=request.sensor_id,
            aggregated_data=aggregated,
            reading_date=reading_date,
            week_number=current_week,
            health_score=health_score,
            health_category=health_category.value,
            forecast_id=forecast_record.get("id")
        )
        
        # 11. Generate recommendations using service
        recommendations = self.service.generate_recommendations(
            health_score=health_score,
            aggregated_data=aggregated,
            deviations=deviations
        )
        
        # 12. Generate alerts using service
        alerts = self.service.generate_alerts(aggregated)
        
        # 13. Calculate next reading recommendation using service
        next_reading = self.service.calculate_next_reading(
            current_week=current_week,
            deviations=deviations
        )
        
        # 14. Format weekly forecast using service
        # Handle different response structures from ML service vs fallback
        if hasattr(ml_response, 'forecast'):
            # MLForecastResponse object with forecast attribute
            forecast_data = ml_response.forecast
        elif isinstance(ml_response, dict):
            # Dict - check if 'forecast' is nested or if weekly_summary is at top level
            if 'forecast' in ml_response:
                forecast_data = ml_response['forecast']
            elif 'weekly_summary' in ml_response:
                # Fallback forecast has weekly_summary at top level
                forecast_data = ml_response
            else:
                forecast_data = ml_response
        else:
            forecast_data = {}
        
        weekly_forecast = self.service.format_weekly_forecast(
            forecast_data=forecast_data,
            start_date=request.planting_date
        )
        
        # 15. Build response
        return SoilAnalysisResponse(
            status=status,
            health_score=health_score,
            health_category=health_category,
            current_week=current_week,
            current_readings=self.service.convert_to_aggregated_schema(aggregated),
            deviations=deviations,
            forecast_summary=self.service.build_forecast_summary(
                forecast_id=forecast_record.get("id") if forecast_record else uuid.uuid4(),
                farmer_id=request.farmer_id,
                planting_date=request.planting_date,
                weekly_forecast=weekly_forecast,
                realignment_count=strategy.get("realignment_count", 0) + 1 if strategy["should_realign"] else 0
            ),
            weekly_forecast=weekly_forecast,
            recommendations=recommendations,
            alerts=alerts,
            next_reading=next_reading
        )
    
    async def get_forecast(
        self,
        db: Session,
        farm_id: UUID
    ) -> Optional[GetForecastResponse]:
        """
        Get current forecast for a farm.
        
        Args:
            db: Database session
            farm_id: Farm UUID
            
        Returns:
            GetForecastResponse or None if no forecast exists
        """
        # Query for active forecast
        forecast = db.query(SoilForecast).filter(
            SoilForecast.farm_id == farm_id,
            SoilForecast.status == 'active'
        ).order_by(SoilForecast.created_at.desc()).first()
        
        if not forecast:
            return None
        
        # Get latest reading for this farm
        latest_reading = db.query(SoilReading).filter(
            SoilReading.farm_id == farm_id
        ).order_by(SoilReading.reading_date.desc()).first()
        
        # Format weekly forecast from stored data using service
        weekly_forecast = self.service.format_weekly_forecast(
            forecast_data=forecast.forecast_data or {},
            start_date=forecast.planting_date.date() if isinstance(forecast.planting_date, datetime) else forecast.planting_date
        )
        
        # Calculate average health score from weekly forecasts
        health_scores = [w.health_score for w in weekly_forecast if w.health_score is not None]
        average_health_score = sum(health_scores) / len(health_scores) if health_scores else 70.0
        
        # Determine trend from weekly forecasts
        if len(health_scores) >= 2:
            if health_scores[-1] > health_scores[0]:
                trend = TrendDirection.INCREASING
            elif health_scores[-1] < health_scores[0]:
                trend = TrendDirection.DECREASING
            else:
                trend = TrendDirection.STABLE
        else:
            trend = TrendDirection.STABLE
        
        # Build forecast summary
        forecast_summary = ForecastSummary(
            forecast_id=forecast.forecast_id,
            farmer_id=forecast.farm_id,
            planting_date=forecast.planting_date.date() if isinstance(forecast.planting_date, datetime) else forecast.planting_date,
            forecast_start=forecast.forecast_start_date.date() if isinstance(forecast.forecast_start_date, datetime) else forecast.forecast_start_date,
            forecast_end=forecast.forecast_end_date.date() if isinstance(forecast.forecast_end_date, datetime) else forecast.forecast_end_date,
            total_weeks=len(weekly_forecast),
            average_health_score=average_health_score,
            trend=trend,
            created_at=forecast.created_at,
            last_updated=forecast.last_realignment_date or forecast.created_at,
            realignment_count=forecast.realignment_count or 0
        )
        
        # Calculate current health from latest reading or forecast
        current_health_score = latest_reading.health_score if latest_reading and latest_reading.health_score else 70.0
        current_health_category = self.service.get_health_category(current_health_score)
        
        # Calculate next reading recommendation using service
        current_week = self.service.calculate_current_week(forecast.planting_date)
        next_reading = self.service.calculate_next_reading(current_week=current_week, deviations=None)
        
        return GetForecastResponse(
            forecast_summary=forecast_summary,
            weekly_forecast=weekly_forecast,
            current_health_score=current_health_score,
            current_health_category=current_health_category,
            last_reading_date=latest_reading.reading_date if latest_reading else None,
            next_reading=next_reading
        )
    
    async def get_health_score(
        self,
        db: Session,
        farm_id: UUID
    ) -> Optional[HealthScoreResponse]:
        """
        Get current health score for a farm.
        
        Args:
            db: Database session
            farm_id: Farm UUID
            
        Returns:
            HealthScoreResponse or None if no data exists
        """
        # Get latest reading for this farm
        latest_reading = db.query(SoilReading).filter(
            SoilReading.farm_id == farm_id
        ).order_by(SoilReading.reading_date.desc()).first()
        
        if not latest_reading:
            return None
        
        # Calculate parameter scores from stored data using service
        parameter_scores = {}
        for param in self.service.OPTIMAL_RANGES.keys():
            param_data = getattr(latest_reading, param.lower().replace("ph", "ph"), None)
            if param_data and isinstance(param_data, dict):
                value = param_data.get("mean", 0)
                score = self.service._calculate_parameter_score(
                    value=value,
                    min_val=self.service.OPTIMAL_RANGES[param]["min"],
                    max_val=self.service.OPTIMAL_RANGES[param]["max"],
                    optimal_val=self.service.OPTIMAL_RANGES[param]["optimal"]
                )
                parameter_scores[param] = round(score * 100, 1)
        
        health_score = latest_reading.health_score or 70.0
        health_category = self.service.get_health_category(health_score)
        
        return HealthScoreResponse(
            health_score=health_score,
            health_category=health_category,
            parameter_scores=parameter_scores,
            timestamp=latest_reading.reading_date
        )
    
    async def get_reading_history(
        self,
        db: Session,
        farm_id: UUID,
        limit: int = 50
    ) -> ReadingHistoryResponse:
        """
        Get reading history for a farm.
        
        Args:
            db: Database session
            farm_id: Farm UUID
            limit: Maximum number of readings to return
            
        Returns:
            ReadingHistoryResponse with list of readings
        """
        # Query readings from database
        readings = db.query(SoilReading).filter(
            SoilReading.farm_id == farm_id
        ).order_by(SoilReading.reading_date.desc()).limit(limit).all()
        
        total_count = db.query(SoilReading).filter(
            SoilReading.farm_id == farm_id
        ).count()
        
        # Convert to response items using service
        reading_items = []
        for reading in readings:
            aggregated_data = self.service.build_aggregated_data_from_reading(reading)
            
            reading_items.append(ReadingHistoryItem(
                reading_id=reading.reading_id,
                reading_date=reading.reading_date,
                week_number=reading.week_number or 1,
                health_score=reading.health_score or 70.0,
                aggregated_data=aggregated_data
            ))
        
        return ReadingHistoryResponse(
            farmer_id=farm_id,
            total_readings=total_count,
            readings=reading_items
        )
    
    async def _validate_entities(
        self,
        db: Session,
        farmer_id: UUID,
        sensor_id: Optional[UUID]
    ) -> List[str]:
        """
        Validate that farmer and sensor exist in the database.
        
        Args:
            db: Database session
            farmer_id: Farmer UUID to validate
            sensor_id: Optional sensor UUID to validate
            
        Returns:
            List of error messages (empty if all valid)
        """
        errors = []
        
        # Check if farmer exists
        farmer = db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
        if not farmer:
            errors.append(f"User {farmer_id} doesn't exist")
        
        # Check if sensor exists (only if sensor_id is provided)
        if sensor_id:
            sensor = db.query(SoilSensorDevice).filter(
                SoilSensorDevice.sensor_id == sensor_id
            ).first()
            if not sensor:
                errors.append(f"Sensor {sensor_id} doesn't exist")
        
        return errors
    
    async def _save_reading(
        self,
        db: Session,
        farm_id: UUID,
        sensor_id: Optional[UUID],
        aggregated_data: Dict,
        reading_date: date,
        week_number: int,
        health_score: float = None,
        health_category: str = None,
        forecast_id: UUID = None
    ) -> SoilReading:
        """Save sensor reading to database."""
        reading = SoilReading(
            farm_id=farm_id,
            sensor_id=sensor_id,
            forecast_id=forecast_id,
            reading_date=datetime.combine(reading_date, datetime.min.time()) if isinstance(reading_date, date) else reading_date,
            week_number=week_number,
            nitrogen_ppm=aggregated_data.get("nitrogen_ppm"),
            phosphorus_ppm=aggregated_data.get("phosphorus_ppm"),
            potassium_meq=aggregated_data.get("potassium_meq"),
            ph=aggregated_data.get("pH"),
            soil_moisture_pct=aggregated_data.get("soil_moisture_pct"),
            organic_matter_pct=aggregated_data.get("organic_matter_pct"),
            health_score=health_score,
            health_category=health_category,
            raw_readings=None  # Could store raw readings if needed
        )
        
        db.add(reading)
        db.commit()
        db.refresh(reading)
        
        return reading
    
    async def _get_active_forecast(
        self,
        db: Session,
        farm_id: UUID,
        planting_date: date
    ) -> Optional[Dict]:
        """
        Get active forecast for a farm and planting date.
        Returns:
            Dict with forecast data if realignment should occur, None for new forecast
        """
        # Convert date to datetime for comparison if needed
        planting_datetime = datetime.combine(planting_date, datetime.min.time()) if isinstance(planting_date, date) else planting_date
        
        forecast_end = planting_datetime + timedelta(days=self.service.REALIGNMENT_CONFIG["forecast_horizon_days"])
        current_datetime = datetime.now()
        
        if current_datetime > forecast_end:
            return None
        
        forecast = db.query(SoilForecast).filter(
            SoilForecast.farm_id == farm_id,
            SoilForecast.status == 'active',
            SoilForecast.planting_date == planting_datetime
        ).first()
        
        if not forecast:
            return None
        
        days_since_planting = (current_datetime - planting_datetime).days
        current_week = (days_since_planting // 7) + 1
        
        if current_week > self.service.REALIGNMENT_CONFIG["max_weeks_for_realignment"]:
            forecast.status = 'completed'
            db.commit()
            return None
        
        return {
            "id": forecast.forecast_id,
            "farm_id": forecast.farm_id,
            "planting_date": forecast.planting_date,
            "forecast_data": forecast.forecast_data,
            "weekly_summary": forecast.weekly_summary,
            "realignment_count": forecast.realignment_count or 0,
            "current_week": current_week,
            "model": forecast
        }
    
    async def _save_or_update_forecast(
        self,
        db: Session,
        farm_id: UUID,
        planting_date: date,
        forecast_data: Any,
        is_realignment: bool,
        baseline_reading: Dict = None
    ) -> Dict:
        """Save new forecast or update existing one."""
        planting_datetime = datetime.combine(planting_date, datetime.min.time()) if isinstance(planting_date, date) else planting_date
        
        # Extract forecast data from ML response
        if hasattr(forecast_data, 'detailed_forecast'):
            forecast_dict = {
                "detailed_forecast": forecast_data.detailed_forecast,
                "weekly_summary": forecast_data.weekly_summary,
                "planting_date": forecast_data.planting_date,
                "forecast_end_date": forecast_data.forecast_end_date,
                "model_version": forecast_data.model_version
            }
            weekly_summary = forecast_data.weekly_summary
        elif isinstance(forecast_data, dict):
            forecast_dict = forecast_data
            weekly_summary = forecast_data.get("weekly_summary", [])
        else:
            forecast_dict = {"data": str(forecast_data)}
            weekly_summary = []
        
        if is_realignment:
            existing = db.query(SoilForecast).filter(
                SoilForecast.farm_id == farm_id,
                SoilForecast.status == 'active',
                SoilForecast.planting_date == planting_datetime
            ).first()
            
            if existing:
                existing.forecast_data = forecast_dict
                existing.weekly_summary = weekly_summary
                existing.last_realignment_date = datetime.now()
                existing.realignment_count = (existing.realignment_count or 0) + 1
                db.commit()
                db.refresh(existing)
                return {
                    "id": existing.forecast_id,
                    "farm_id": existing.farm_id,
                    "planting_date": existing.planting_date,
                    "created_at": existing.created_at,
                    "is_realignment": True
                }
        
        # Create new forecast
        forecast_end = planting_datetime + timedelta(days=90)
        
        new_forecast = SoilForecast(
            farm_id=farm_id,
            planting_date=planting_datetime,
            forecast_start_date=planting_datetime,
            forecast_end_date=forecast_end,
            status='active',
            model_version=forecast_dict.get("model_version", "1.0") if isinstance(forecast_dict, dict) else "1.0",
            approach_used='hybrid',
            baseline_reading=baseline_reading,
            forecast_data=forecast_dict,
            weekly_summary=weekly_summary,
            realignment_count=0
        )
        
        db.add(new_forecast)
        db.commit()
        db.refresh(new_forecast)
        
        return {
            "id": new_forecast.forecast_id,
            "farm_id": new_forecast.farm_id,
            "planting_date": new_forecast.planting_date,
            "created_at": new_forecast.created_at,
            "is_realignment": False
        }

soil_forecast_controller = SoilForecastController()
