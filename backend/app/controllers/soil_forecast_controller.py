"""
Soil Forecast Controller

Backend controller that orchestrates soil analysis.
Frontend only talks to this - never directly to ML service.

This controller handles:
1. Validating and aggregating sensor data
2. Storing readings in the database
3. Calling the ML service for forecasts
4. Generating recommendations
5. Formatting responses for the frontend
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
from uuid import UUID
import uuid

from sqlalchemy.orm import Session

from app.schemas.soil_forecast import (
    SensorReading,
    UploadSensorDataRequest,
    SoilAnalysisResponse,
    GetForecastResponse,
    HealthScoreResponse,
    ReadingHistoryResponse,
    ReadingHistoryItem,
    WeeklyForecast,
    ForecastSummary,
    Recommendation,
    Alert,
    NextReadingRecommendation,
    DeviationInfo,
    HealthCategory,
    RecommendationType,
    CorrectionStrategy,
    AggregatedSoilData,
    ParameterStatistics,
    TrendDirection,
)
from app.packages.sensor_aggregator import sensor_aggregator
from app.packages.ml_client import ml_client, MLServiceClient
from app import models


class SoilForecastController:
    """
    Controller for soil forecast operations.
    
    Orchestrates the flow between Frontend, Database, and ML Service.
    """
    
    # Health score thresholds
    HEALTH_THRESHOLDS = {
        "excellent": 85,
        "good": 70,
        "moderate": 55,
        "poor": 40,
    }
    
    # Optimal ranges for rice cultivation (Philippines)
    OPTIMAL_RANGES = {
        "nitrogen_ppm": {"min": 40, "max": 80, "optimal": 60},
        "phosphorus_ppm": {"min": 15, "max": 40, "optimal": 25},
        "potassium_meq": {"min": 0.5, "max": 1.5, "optimal": 1.0},
        "pH": {"min": 5.5, "max": 7.0, "optimal": 6.2},
        "soil_moisture_pct": {"min": 25, "max": 50, "optimal": 35},
        "organic_matter_pct": {"min": 2.0, "max": 6.0, "optimal": 4.0},
    }
    
    def __init__(self, ml_service: Optional[MLServiceClient] = None):
        """
        Initialize the controller.
        
        Args:
            ml_service: Optional ML service client for dependency injection
        """
        self.ml_client = ml_service or ml_client
    
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
        """
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
        
        # 5. Store reading in database
        reading_record = await self._save_reading(
            db=db,
            farm_id=request.farm_id,
            sensor_id=request.sensor_id,
            aggregated_data=aggregated,
            reading_date=reading_date,
            week_number=current_week
        )
        
        # 6. Check for active forecast
        active_forecast = await self._get_active_forecast(
            db=db,
            farm_id=request.farm_id,
            planting_date=request.planting_date
        )
        
        # 7. Call ML Service
        try:
            if active_forecast:
                # Realign existing forecast
                ml_response = await self.ml_client.realign_forecast(
                    current_data=aggregated,
                    existing_forecast=active_forecast.get("forecast_data", {}),
                    current_week=current_week
                )
                status = "forecast_realigned"
                
                # Calculate deviations
                deviations = self._calculate_deviations(
                    predicted=active_forecast.get("forecast_data", {}).get(f"week_{current_week}", {}),
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
            ml_response = self._generate_fallback_forecast(
                aggregated_data=aggregated,
                planting_date=request.planting_date,
                current_week=current_week
            )
            status = "new_forecast_generated"
            deviations = None
        
        # 8. Save/update forecast in database
        forecast_record = await self._save_or_update_forecast(
            db=db,
            farm_id=request.farm_id,
            planting_date=request.planting_date,
            forecast_data=ml_response,
            is_realignment=active_forecast is not None
        )
        
        # 9. Calculate health score
        health_score = self._calculate_health_score(aggregated)
        health_category = self._get_health_category(health_score)
        
        # 10. Generate recommendations
        recommendations = self._generate_recommendations(
            health_score=health_score,
            aggregated_data=aggregated,
            deviations=deviations
        )
        
        # 11. Generate alerts
        alerts = self._generate_alerts(aggregated)
        
        # 12. Calculate next reading recommendation
        next_reading = self._calculate_next_reading(
            current_week=current_week,
            deviations=deviations
        )
        
        # 13. Format weekly forecast
        weekly_forecast = self._format_weekly_forecast(
            forecast_data=ml_response.forecast if hasattr(ml_response, 'forecast') else ml_response.get('forecast', {}),
            start_date=request.planting_date
        )
        
        # 14. Build response
        return SoilAnalysisResponse(
            status=status,
            health_score=health_score,
            health_category=health_category,
            current_week=current_week,
            current_readings=self._convert_to_aggregated_schema(aggregated),
            deviations=deviations,
            forecast_summary=self._build_forecast_summary(
                forecast_id=forecast_record.get("id") if forecast_record else uuid.uuid4(),
                farm_id=request.farm_id,
                planting_date=request.planting_date,
                weekly_forecast=weekly_forecast,
                realignment_count=active_forecast.get("realignment_count", 0) + 1 if active_forecast else 0
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
        # TODO: Implement database query
        # For now, return None
        return None
    
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
        # TODO: Get latest reading from database and calculate health score
        return None
    
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
        # TODO: Implement database query
        return ReadingHistoryResponse(
            farm_id=farm_id,
            total_readings=0,
            readings=[]
        )
    
    # =========================================================================
    # Private Helper Methods
    # =========================================================================
    
    async def _save_reading(
        self,
        db: Session,
        farm_id: UUID,
        sensor_id: Optional[UUID],
        aggregated_data: Dict,
        reading_date: date,
        week_number: int
    ) -> Dict:
        """Save sensor reading to database."""
        # TODO: Implement actual database save using SoilReading model
        # For now, return a mock record
        return {
            "id": uuid.uuid4(),
            "farm_id": farm_id,
            "sensor_id": sensor_id,
            "reading_date": reading_date,
            "week_number": week_number,
            "aggregated_data": aggregated_data
        }
    
    async def _get_active_forecast(
        self,
        db: Session,
        farm_id: UUID,
        planting_date: date
    ) -> Optional[Dict]:
        """Get active forecast for a farm and planting date."""
        # TODO: Implement actual database query
        # For now, return None (no active forecast)
        return None
    
    async def _save_or_update_forecast(
        self,
        db: Session,
        farm_id: UUID,
        planting_date: date,
        forecast_data: Any,
        is_realignment: bool
    ) -> Dict:
        """Save new forecast or update existing one."""
        # TODO: Implement actual database save/update
        return {
            "id": uuid.uuid4(),
            "farm_id": farm_id,
            "planting_date": planting_date,
            "created_at": datetime.now(),
            "is_realignment": is_realignment
        }
    
    def _calculate_health_score(self, aggregated_data: Dict) -> float:
        """
        Calculate overall soil health score from aggregated data.
        
        Returns a score between 0 and 100.
        """
        scores = []
        weights = {
            "nitrogen_ppm": 0.20,
            "phosphorus_ppm": 0.15,
            "potassium_meq": 0.15,
            "pH": 0.20,
            "soil_moisture_pct": 0.15,
            "organic_matter_pct": 0.15,
        }
        
        for param, weight in weights.items():
            if param in aggregated_data and aggregated_data[param]:
                value = aggregated_data[param].get("mean", aggregated_data[param])
                if isinstance(value, dict):
                    value = value.get("mean", 0)
                
                optimal = self.OPTIMAL_RANGES.get(param, {})
                if optimal:
                    score = self._calculate_parameter_score(
                        value=value,
                        min_val=optimal["min"],
                        max_val=optimal["max"],
                        optimal_val=optimal["optimal"]
                    )
                    scores.append(score * weight)
        
        if not scores:
            return 50.0  # Default score if no data
        
        # Normalize to 0-100 scale
        total_weight = sum(weights.get(p, 0) for p in aggregated_data if aggregated_data.get(p))
        if total_weight > 0:
            return round(sum(scores) / total_weight * 100, 1)
        return 50.0
    
    def _calculate_parameter_score(
        self,
        value: float,
        min_val: float,
        max_val: float,
        optimal_val: float
    ) -> float:
        """
        Calculate score for a single parameter.
        
        Returns a score between 0 and 1.
        """
        if min_val <= value <= max_val:
            # Within range, calculate distance from optimal
            if value <= optimal_val:
                distance = (value - min_val) / (optimal_val - min_val) if optimal_val != min_val else 1
            else:
                distance = (max_val - value) / (max_val - optimal_val) if max_val != optimal_val else 1
            return 0.7 + (0.3 * distance)  # 70-100% score when in range
        else:
            # Outside range
            if value < min_val:
                distance = (min_val - value) / min_val if min_val != 0 else 1
            else:
                distance = (value - max_val) / max_val if max_val != 0 else 1
            return max(0, 0.7 - (0.7 * min(distance, 1)))  # 0-70% score when out of range
    
    def _get_health_category(self, score: float) -> HealthCategory:
        """Get health category from score."""
        if score >= self.HEALTH_THRESHOLDS["excellent"]:
            return HealthCategory.EXCELLENT
        elif score >= self.HEALTH_THRESHOLDS["good"]:
            return HealthCategory.GOOD
        elif score >= self.HEALTH_THRESHOLDS["moderate"]:
            return HealthCategory.MODERATE
        elif score >= self.HEALTH_THRESHOLDS["poor"]:
            return HealthCategory.POOR
        else:
            return HealthCategory.CRITICAL
    
    def _calculate_deviations(
        self,
        predicted: Dict,
        actual: Dict
    ) -> Optional[Dict[str, DeviationInfo]]:
        """Calculate deviations between predicted and actual values."""
        if not predicted:
            return None
        
        deviations = {}
        
        for param in self.OPTIMAL_RANGES.keys():
            pred_val = predicted.get(param)
            actual_val = actual.get(param, {}).get("mean") if isinstance(actual.get(param), dict) else actual.get(param)
            
            if pred_val is not None and actual_val is not None:
                deviation = actual_val - pred_val
                deviation_pct = (deviation / pred_val * 100) if pred_val != 0 else 0
                
                # Determine correction strategy based on deviation magnitude
                if abs(deviation_pct) < 5:
                    strategy = CorrectionStrategy.SHIFT
                elif abs(deviation_pct) < 15:
                    strategy = CorrectionStrategy.DECAYING_SHIFT
                else:
                    strategy = CorrectionStrategy.REFORECAST
                
                deviations[param] = DeviationInfo(
                    predicted=pred_val,
                    actual=actual_val,
                    deviation=round(deviation, 2),
                    deviation_pct=round(deviation_pct, 1),
                    correction_applied=strategy
                )
        
        return deviations if deviations else None
    
    def _generate_recommendations(
        self,
        health_score: float,
        aggregated_data: Dict,
        deviations: Optional[Dict] = None
    ) -> List[Recommendation]:
        """Generate recommendations based on current data and deviations."""
        recommendations = []
        
        # Check each parameter against optimal ranges
        for param, ranges in self.OPTIMAL_RANGES.items():
            if param in aggregated_data and aggregated_data[param]:
                value = aggregated_data[param].get("mean") if isinstance(aggregated_data[param], dict) else aggregated_data[param]
                
                if value is None:
                    continue
                
                param_display = param.replace("_", " ").replace("ppm", "(ppm)").replace("meq", "(meq)").replace("pct", "(%)")
                
                if value < ranges["min"]:
                    recommendations.append(Recommendation(
                        type=RecommendationType.ACTION_REQUIRED,
                        parameter=param,
                        message=f"{param_display} is below optimal range ({value:.1f} < {ranges['min']}). Consider adding appropriate fertilizer.",
                        priority=2
                    ))
                elif value > ranges["max"]:
                    recommendations.append(Recommendation(
                        type=RecommendationType.WARNING,
                        parameter=param,
                        message=f"{param_display} is above optimal range ({value:.1f} > {ranges['max']}). Reduce application.",
                        priority=2
                    ))
                else:
                    # Check if close to optimal
                    distance_to_optimal = abs(value - ranges["optimal"])
                    range_size = ranges["max"] - ranges["min"]
                    
                    if distance_to_optimal < range_size * 0.2:
                        recommendations.append(Recommendation(
                            type=RecommendationType.POSITIVE,
                            parameter=param,
                            message=f"{param_display} is near optimal ({value:.1f}). Maintain current practices.",
                            priority=5
                        ))
        
        # Add deviation-based recommendations
        if deviations:
            for param, dev_info in deviations.items():
                if abs(dev_info.deviation_pct) > 10:
                    if dev_info.deviation > 0:
                        recommendations.append(Recommendation(
                            type=RecommendationType.INFO,
                            parameter=param,
                            message=f"{param} is {dev_info.deviation_pct:.1f}% higher than forecasted. Forecast has been adjusted.",
                            priority=3
                        ))
                    else:
                        recommendations.append(Recommendation(
                            type=RecommendationType.WARNING,
                            parameter=param,
                            message=f"{param} is {abs(dev_info.deviation_pct):.1f}% lower than forecasted. Consider intervention.",
                            priority=2
                        ))
        
        # Sort by priority (lower number = higher priority)
        recommendations.sort(key=lambda r: r.priority)
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _generate_alerts(self, aggregated_data: Dict) -> List[Alert]:
        """Generate alerts for critical conditions."""
        alerts = []
        
        # Critical thresholds (more extreme than optimal ranges)
        critical_thresholds = {
            "nitrogen_ppm": {"low": 20, "high": 100},
            "pH": {"low": 4.5, "high": 8.0},
            "soil_moisture_pct": {"low": 15, "high": 70},
        }
        
        for param, thresholds in critical_thresholds.items():
            if param in aggregated_data and aggregated_data[param]:
                value = aggregated_data[param].get("mean") if isinstance(aggregated_data[param], dict) else aggregated_data[param]
                
                if value is None:
                    continue
                
                if value < thresholds["low"]:
                    alerts.append(Alert(
                        severity="high" if value < thresholds["low"] * 0.5 else "medium",
                        parameter=param,
                        message=f"Critical: {param} is dangerously low!",
                        threshold_exceeded=True,
                        current_value=value,
                        threshold_value=thresholds["low"]
                    ))
                elif value > thresholds["high"]:
                    alerts.append(Alert(
                        severity="high" if value > thresholds["high"] * 1.5 else "medium",
                        parameter=param,
                        message=f"Critical: {param} is dangerously high!",
                        threshold_exceeded=True,
                        current_value=value,
                        threshold_value=thresholds["high"]
                    ))
        
        return alerts
    
    def _calculate_next_reading(
        self,
        current_week: int,
        deviations: Optional[Dict] = None
    ) -> NextReadingRecommendation:
        """Calculate when user should take next reading."""
        if deviations:
            max_deviation = max(
                abs(d.deviation_pct) for d in deviations.values()
            )
            
            if max_deviation > 10:
                days_until_next = 5
                reason = "Significant deviation detected. Early re-reading recommended."
            elif max_deviation > 5:
                days_until_next = 7
                reason = "Moderate changes observed. Weekly reading recommended."
            else:
                days_until_next = 14
                reason = "Forecast is tracking well. Bi-weekly reading sufficient."
        else:
            # New forecast, recommend weekly readings initially
            days_until_next = 7
            reason = "Initial forecast generated. Weekly readings recommended to calibrate."
        
        next_date = date.today() + timedelta(days=days_until_next)
        
        return NextReadingRecommendation(
            recommended_date=next_date,
            days_from_now=days_until_next,
            reason=reason
        )
    
    def _format_weekly_forecast(
        self,
        forecast_data: Dict,
        start_date: date
    ) -> List[WeeklyForecast]:
        """Format forecast data into weekly forecast list."""
        weekly = []
        
        # If forecast_data has weekly_summary, use it
        if "weekly_summary" in forecast_data:
            for week_data in forecast_data["weekly_summary"]:
                week_num = week_data.get("week", len(weekly) + 1)
                week_date = start_date + timedelta(weeks=week_num - 1)
                
                health_score = week_data.get("health_score", 70)
                
                weekly.append(WeeklyForecast(
                    week=week_num,
                    date=week_date,
                    nitrogen_ppm=week_data.get("nitrogen_ppm"),
                    phosphorus_ppm=week_data.get("phosphorus_ppm"),
                    potassium_meq=week_data.get("potassium_meq"),
                    pH=week_data.get("pH"),
                    soil_moisture_pct=week_data.get("soil_moisture_pct"),
                    organic_matter_pct=week_data.get("organic_matter_pct"),
                    health_score=health_score,
                    health_category=self._get_health_category(health_score),
                    realigned=week_data.get("realigned", False),
                    correction_applied=week_data.get("correction_applied")
                ))
        else:
            # Generate default 12-week forecast structure
            for week_num in range(1, 13):
                week_date = start_date + timedelta(weeks=week_num - 1)
                weekly.append(WeeklyForecast(
                    week=week_num,
                    date=week_date,
                    nitrogen_ppm=None,
                    phosphorus_ppm=None,
                    potassium_meq=None,
                    pH=None,
                    soil_moisture_pct=None,
                    organic_matter_pct=None,
                    health_score=70.0,
                    health_category=HealthCategory.GOOD,
                    realigned=False,
                    correction_applied=None
                ))
        
        return weekly
    
    def _build_forecast_summary(
        self,
        forecast_id: UUID,
        farm_id: UUID,
        planting_date: date,
        weekly_forecast: List[WeeklyForecast],
        realignment_count: int = 0
    ) -> ForecastSummary:
        """Build forecast summary from weekly data."""
        if weekly_forecast:
            forecast_start = weekly_forecast[0].date
            forecast_end = weekly_forecast[-1].date
            avg_health = sum(w.health_score for w in weekly_forecast) / len(weekly_forecast)
            
            # Determine overall trend
            if len(weekly_forecast) >= 3:
                first_half_avg = sum(w.health_score for w in weekly_forecast[:len(weekly_forecast)//2]) / (len(weekly_forecast)//2)
                second_half_avg = sum(w.health_score for w in weekly_forecast[len(weekly_forecast)//2:]) / (len(weekly_forecast) - len(weekly_forecast)//2)
                
                if second_half_avg > first_half_avg + 2:
                    trend = TrendDirection.INCREASING
                elif second_half_avg < first_half_avg - 2:
                    trend = TrendDirection.DECREASING
                else:
                    trend = TrendDirection.STABLE
            else:
                trend = TrendDirection.STABLE
        else:
            forecast_start = planting_date
            forecast_end = planting_date + timedelta(weeks=12)
            avg_health = 70.0
            trend = TrendDirection.STABLE
        
        return ForecastSummary(
            forecast_id=forecast_id,
            farm_id=farm_id,
            planting_date=planting_date,
            forecast_start=forecast_start,
            forecast_end=forecast_end,
            total_weeks=len(weekly_forecast),
            average_health_score=round(avg_health, 1),
            trend=trend,
            created_at=datetime.now(),
            last_updated=datetime.now(),
            realignment_count=realignment_count
        )
    
    def _convert_to_aggregated_schema(self, aggregated_data: Dict) -> AggregatedSoilData:
        """Convert aggregated data dict to AggregatedSoilData schema."""
        def to_param_stats(data: Optional[Dict]) -> Optional[ParameterStatistics]:
            if not data:
                return None
            return ParameterStatistics(
                mean=data.get("mean", 0),
                std=data.get("std", 0),
                min=data.get("min", 0),
                max=data.get("max", 0),
                count=data.get("count", 0),
                latest=data.get("latest", 0),
                trend=TrendDirection(data.get("trend", "stable"))
            )
        
        return AggregatedSoilData(
            nitrogen_ppm=to_param_stats(aggregated_data.get("nitrogen_ppm")),
            phosphorus_ppm=to_param_stats(aggregated_data.get("phosphorus_ppm")),
            potassium_meq=to_param_stats(aggregated_data.get("potassium_meq")),
            pH=to_param_stats(aggregated_data.get("pH")),
            soil_moisture_pct=to_param_stats(aggregated_data.get("soil_moisture_pct")),
            organic_matter_pct=to_param_stats(aggregated_data.get("organic_matter_pct"))
        )
    
    def _generate_fallback_forecast(
        self,
        aggregated_data: Dict,
        planting_date: date,
        current_week: int
    ) -> Dict:
        """
        Generate fallback forecast when ML service is unavailable.
        Uses simple rule-based projections.
        """
        weekly_summary = []
        
        for week in range(current_week, current_week + 12):
            week_data = {"week": week}
            
            for param in self.OPTIMAL_RANGES.keys():
                if param in aggregated_data and aggregated_data[param]:
                    base_value = aggregated_data[param].get("mean", self.OPTIMAL_RANGES[param]["optimal"])
                    trend = aggregated_data[param].get("trend", "stable")
                    
                    # Simple projection based on trend
                    weeks_ahead = week - current_week
                    if trend == "increasing":
                        projected = base_value * (1 + 0.02 * weeks_ahead)
                    elif trend == "decreasing":
                        projected = base_value * (1 - 0.02 * weeks_ahead)
                    else:
                        projected = base_value * (1 + 0.005 * weeks_ahead * ((-1) ** week))  # Slight oscillation
                    
                    week_data[param] = round(projected, 2)
            
            # Calculate health score for this week
            week_health = self._calculate_health_score(week_data)
            week_data["health_score"] = week_health
            
            weekly_summary.append(week_data)
        
        return {
            "forecast": {
                "weekly_summary": weekly_summary
            },
            "health_score": self._calculate_health_score(aggregated_data),
            "model_info": {"type": "fallback", "version": "1.0"}
        }


# Singleton instance
soil_forecast_controller = SoilForecastController()
