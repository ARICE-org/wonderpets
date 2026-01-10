"""
Soil Forecast Service

Business logic for soil forecast operations.
Handles calculations, recommendations, and data transformations.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
from uuid import UUID

from app.schemas.soil_forecast import (
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


class SoilForecastService:
    """
    Service layer for soil forecast business logic.
    
    Handles:
    - Health score calculations
    - Realignment strategy determination
    - Recommendation generation
    - Alert generation
    - Data formatting and transformations
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
    
    # Realignment configuration
    REALIGNMENT_CONFIG = {
        "forecast_horizon_days": 90,  # Standard rice growing season
        "max_deviation_for_shift": 15.0,  # % deviation before full reforecast
        "min_days_between_readings": 1,  # Prevent duplicate readings same day
        "max_weeks_for_realignment": 12,  # After week 12, forecast is complete
    }

    
    def calculate_health_score(self, aggregated_data: Dict) -> float:
        """
        Calculate overall soil health score from aggregated data.
        
        Args:
            aggregated_data: Dict with parameter values (can be dicts with "mean" or floats)
            
        Returns:
            Health score between 0 and 100
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
                param_data = aggregated_data[param]
                if isinstance(param_data, dict):
                    value = param_data.get("mean", 0)
                else:
                    value = param_data
                
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
    
    def get_health_category(self, score: float) -> HealthCategory:
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
    
    def determine_realignment_strategy(
        self,
        active_forecast: Optional[Dict],
        aggregated_data: Dict,
        current_week: int,
        reading_date: date
    ) -> Dict[str, Any]:
        """
        Determine the appropriate realignment strategy based on current conditions.
        Returns:
            Dict with strategy, should_realign, max_deviation, and reason
        """
        if not active_forecast:
            return {
                "strategy": "NEW_FORECAST",
                "should_realign": False,
                "max_deviation": None,
                "reason": "No active forecast found for this farm/planting date"
            }
        
        # Check if beyond max weeks
        if current_week > self.REALIGNMENT_CONFIG["max_weeks_for_realignment"]:
            return {
                "strategy": "COMPLETE_AND_NEW",
                "should_realign": False,
                "max_deviation": None,
                "reason": f"Current week ({current_week}) exceeds max realignment weeks ({self.REALIGNMENT_CONFIG['max_weeks_for_realignment']})"
            }
        
        # Get predicted values for current week from forecast
        forecast_data = active_forecast.get("forecast_data", {})
        weekly_summary = forecast_data.get("weekly_summary", [])
        
        # Find the prediction for current week
        predicted_values = {}
        for week_data in weekly_summary:
            if week_data.get("week_number") == current_week:
                predicted_values = week_data
                break
        
        if not predicted_values:
            return {
                "strategy": "REALIGN_SHIFT",
                "should_realign": True,
                "max_deviation": 0,
                "reason": "No prediction found for current week, applying simple shift"
            }
        
        # Calculate deviations
        max_deviation = 0.0
        deviations = {}
        
        for param in self.OPTIMAL_RANGES.keys():
            pred_val = predicted_values.get(param)
            actual_data = aggregated_data.get(param)
            
            if pred_val is not None and actual_data is not None:
                if isinstance(actual_data, dict):
                    actual_val = actual_data.get("mean", 0)
                else:
                    actual_val = actual_data
                
                if pred_val != 0:
                    deviation_pct = abs((actual_val - pred_val) / pred_val * 100)
                    deviations[param] = deviation_pct
                    max_deviation = max(max_deviation, deviation_pct)
        
        if max_deviation < 5.0:
            return {
                "strategy": "REALIGN_SHIFT",
                "should_realign": True,
                "max_deviation": max_deviation,
                "deviations": deviations,
                "reason": f"Small deviation ({max_deviation:.1f}%), applying simple shift"
            }
        elif max_deviation < self.REALIGNMENT_CONFIG["max_deviation_for_shift"]:
            return {
                "strategy": "REALIGN_DECAYING",
                "should_realign": True,
                "max_deviation": max_deviation,
                "deviations": deviations,
                "reason": f"Moderate deviation ({max_deviation:.1f}%), applying decaying shift"
            }
        else:
            return {
                "strategy": "REALIGN_REFORECAST",
                "should_realign": True,
                "max_deviation": max_deviation,
                "deviations": deviations,
                "reason": f"Large deviation ({max_deviation:.1f}%), triggering full reforecast"
            }
    
    def calculate_deviations(
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
    
    
    def generate_recommendations(
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
        
        recommendations.sort(key=lambda r: r.priority)
        
        return recommendations[:10]
    
    def generate_alerts(self, aggregated_data: Dict) -> List[Alert]:
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
    
    def calculate_next_reading(
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
    
    def format_weekly_forecast(
        self,
        forecast_data: Dict,
        start_date: date
    ) -> List[WeeklyForecast]:
        """Format forecast data into weekly forecast list."""
        weekly = []
        
        # If forecast_data has weekly_summary, use it
        if "weekly_summary" in forecast_data:
            for week_data in forecast_data["weekly_summary"]:
                week_num = week_data.get("week", week_data.get("week_number", len(weekly) + 1))
                week_date = start_date + timedelta(weeks=week_num - 1)
                
                health_score = week_data.get("health_score", week_data.get("soil_health_score", 70))
                
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
                    health_category=self.get_health_category(health_score),
                    nitrogen_status=week_data.get("nitrogenStatus", "good"),
                    phosphorus_status=week_data.get("phosphorusStatus", "good"),
                    potassium_status=week_data.get("potassiumStatus", "good"),
                    ph_status=week_data.get("phStatus", "good"),
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
    
    def build_forecast_summary(
        self,
        forecast_id: UUID,
        farmer_id: UUID,
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
            farmer_id=farmer_id,
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

    def convert_to_aggregated_schema(self, aggregated_data: Dict) -> AggregatedSoilData:
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
    
    def build_aggregated_data_from_reading(self, reading) -> AggregatedSoilData:
        """Build AggregatedSoilData from a SoilReading model instance."""
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
            nitrogen_ppm=to_param_stats(reading.nitrogen_ppm),
            phosphorus_ppm=to_param_stats(reading.phosphorus_ppm),
            potassium_meq=to_param_stats(reading.potassium_meq),
            pH=to_param_stats(reading.ph),
            soil_moisture_pct=to_param_stats(reading.soil_moisture_pct),
            organic_matter_pct=to_param_stats(reading.organic_matter_pct)
        )
    
    def generate_fallback_forecast(
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
            week_data = {"week_number": week}
            
            for param in self.OPTIMAL_RANGES.keys():
                if param in aggregated_data and aggregated_data[param]:
                    param_data = aggregated_data[param]
                    if isinstance(param_data, dict):
                        base_value = param_data.get("mean", self.OPTIMAL_RANGES[param]["optimal"])
                        trend = param_data.get("trend", "stable")
                    else:
                        base_value = param_data
                        trend = "stable"
                    
                    # Simple projection based on trend
                    weeks_ahead = week - current_week
                    if trend == "increasing":
                        projected = base_value * (1 + 0.02 * weeks_ahead)
                    elif trend == "decreasing":
                        projected = base_value * (1 - 0.02 * weeks_ahead)
                    else:
                        projected = base_value * (1 + 0.005 * weeks_ahead * ((-1) ** week)) 
                    
                    week_data[param] = round(projected, 2)
            
            # Calculate health score for this week
            week_health = self.calculate_health_score(week_data)
            week_data["soil_health_score"] = week_health
            week_data["health_category"] = self.get_health_category(week_health).value
            
            # Add default status fields for fallback consistency
            week_data["nitrogenStatus"] = "good"
            week_data["phosphorusStatus"] = "good"
            week_data["potassiumStatus"] = "good"
            week_data["phStatus"] = "good"
            
            weekly_summary.append(week_data)
        
        return {
            "weekly_summary": weekly_summary,
            "health_score": self.calculate_health_score(aggregated_data),
            "model_info": {"type": "fallback", "version": "1.0"}
        }
    
    
    def calculate_current_week(self, planting_date) -> int:
        """Calculate current week number from planting date."""
        if isinstance(planting_date, datetime):
            planting_date = planting_date.date()
        days_since_planting = (date.today() - planting_date).days
        return max(1, (days_since_planting // 7) + 1)


soil_forecast_service = SoilForecastService()
