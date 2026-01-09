"""
Weather Service

Business logic layer for weather forecasting.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from apps.weather_service.models.weather_forecast_model import WeatherForecastModel
from apps.weather_service.core.constants import WEATHER_PARAMETERS, SEASON_DEFINITIONS
from apps.common.utils.logging_utils import logger


class WeatherService:
    """
    Service for weather forecasting.
    
    Provides weather predictions for agricultural planning.
    """
    
    def __init__(self):
        self.model: Optional[WeatherForecastModel] = None
        self._initialized = False
        self._auto_initialize()
    
    def _auto_initialize(self) -> None:
        """Auto-initialize with fallback models."""
        try:
            self.model = WeatherForecastModel()
            self._initialized = True
            logger.info("Weather service auto-initialized")
        except Exception as e:
            logger.error(f"Failed to auto-initialize weather service: {e}")
    
    def is_ready(self) -> bool:
        """Check if service is ready."""
        return self._initialized
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        if self.model:
            return {
                "name": self.model.model_name,
                "version": self.model.version,
                "is_trained": self.model.is_trained
            }
        return {"status": "not_loaded"}
    
    async def initialize(self, model_path: str) -> None:
        """Initialize the service with trained models."""
        try:
            self.model = WeatherForecastModel()
            try:
                self.model.load(model_path)
                logger.info("Weather model loaded successfully")
            except FileNotFoundError:
                logger.warning("Weather model not found, using fallback")
            
            self._initialized = True
            logger.info("Weather service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize weather service: {e}")
            raise
    
    async def get_forecast(
        self,
        location: Optional[Dict[str, float]] = None,
        horizon_days: int = 30,
        start_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get weather forecast for specified location and period.
        
        Args:
            location: Location coordinates (lat, lon)
            horizon_days: Number of days to forecast
            start_date: Forecast start date
            
        Returns:
            Forecast data with daily predictions
        """
        is_valid, errors = self._validate_input(location, horizon_days)
        if not is_valid:
            raise ValueError(f"Invalid input: {', '.join(errors)}")
        
        if start_date:
            forecast_start = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            forecast_start = datetime.now()
        
        if self.model and self.model.is_trained:
            forecast_result = self.model.forecast(
                historical_data={},
                horizon_days=horizon_days,
                location=location
            )
            daily_forecasts = self._format_daily_forecasts(forecast_result)
        else:
            daily_forecasts = self._generate_fallback_forecast(
                forecast_start, horizon_days, location
            )
        
        return {
            "location": location,
            "forecast_start": forecast_start.strftime("%Y-%m-%d"),
            "forecast_end": (forecast_start + timedelta(days=horizon_days)).strftime("%Y-%m-%d"),
            "horizon_days": horizon_days,
            "daily_forecasts": daily_forecasts,
            "summary": self._calculate_summary(daily_forecasts),
            "generated_at": datetime.now().isoformat()
        }
    
    async def get_historical_analysis(
        self,
        location: Optional[Dict[str, float]] = None,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """Get historical weather analysis for a location."""
        return {
            "location": location,
            "period": {
                "start": start_date,
                "end": end_date
            },
            "summary": {
                "avg_temperature": None,
                "total_rainfall": None,
                "avg_humidity": None
            },
            "trends": []
        }
    
    async def get_current_weather(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """Get current weather for a location."""
        # Placeholder - would integrate with weather API
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "timestamp": datetime.now().isoformat(),
            "temperature": 28.5,
            "humidity": 75,
            "condition": "Partly Cloudy",
            "rainfall": 0
        }
    
    def _validate_input(
        self,
        location: Optional[Dict],
        horizon_days: int
    ) -> tuple:
        """Validate input parameters."""
        errors = []
        
        if horizon_days <= 0:
            errors.append("horizon_days must be positive")
        
        if horizon_days > 90:
            errors.append("horizon_days cannot exceed 90")
        
        return len(errors) == 0, errors
    
    def _generate_fallback_forecast(
        self,
        start_date: datetime,
        horizon_days: int,
        location: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate fallback forecast when model not available."""
        import numpy as np
        
        forecasts = []
        
        for day in range(horizon_days):
            forecast_date = start_date + timedelta(days=day + 1)
            month = forecast_date.month
            
            # Seasonal adjustment for Philippines
            is_wet_season = month in [6, 7, 8, 9, 10, 11]
            
            base_temp = 30 if is_wet_season else 32
            base_rain = 8 if is_wet_season else 2
            base_humidity = 80 if is_wet_season else 65
            
            forecasts.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "temperature_max": round(base_temp + np.random.uniform(-2, 4), 1),
                "temperature_min": round(base_temp - np.random.uniform(4, 8), 1),
                "temperature_avg": round(base_temp + np.random.uniform(-1, 2), 1),
                "rainfall": round(max(0, base_rain + np.random.uniform(-5, 15)), 1),
                "rainfall_probability": 70 if is_wet_season else 30,
                "humidity": round(base_humidity + np.random.uniform(-10, 10), 1),
                "wind_speed": round(np.random.uniform(5, 20), 1),
                "condition": "Rainy" if is_wet_season else "Sunny",
                "rice_suitability": "Good" if 25 <= base_temp <= 35 else "Marginal"
            })
        
        return forecasts
    
    def _format_daily_forecasts(
        self,
        forecast_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Format raw forecast into daily structure."""
        daily = forecast_result.get("daily_forecast", {})
        dates = forecast_result.get("dates", [])
        
        formatted = []
        for i, date in enumerate(dates):
            formatted.append({
                "date": date,
                "temperature_max": daily.get("temperature_max", [None])[i] if i < len(daily.get("temperature_max", [])) else None,
                "temperature_min": daily.get("temperature_min", [None])[i] if i < len(daily.get("temperature_min", [])) else None,
                "rainfall": daily.get("rainfall", [None])[i] if i < len(daily.get("rainfall", [])) else None,
                "humidity": daily.get("humidity", [None])[i] if i < len(daily.get("humidity", [])) else None
            })
        
        return formatted
    
    def _calculate_summary(
        self,
        daily_forecasts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate summary statistics from forecasts."""
        if not daily_forecasts:
            return {}
        
        temps = [f.get("temperature_avg") for f in daily_forecasts if f.get("temperature_avg")]
        rainfalls = [f.get("rainfall") for f in daily_forecasts if f.get("rainfall") is not None]
        humidities = [f.get("humidity") for f in daily_forecasts if f.get("humidity")]
        
        return {
            "avg_temperature": round(sum(temps) / len(temps), 1) if temps else None,
            "total_rainfall": round(sum(rainfalls), 1) if rainfalls else None,
            "avg_humidity": round(sum(humidities) / len(humidities), 1) if humidities else None,
            "rainy_days": len([r for r in rainfalls if r > 1]),
            "hot_days": len([t for t in temps if t and t > 35]),
            "favorable_days": len([f for f in daily_forecasts if f.get("rice_suitability") == "Good"])
        }
