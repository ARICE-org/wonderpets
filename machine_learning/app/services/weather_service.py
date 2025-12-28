"""
Weather Service

Business logic layer for weather forecasting.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from app.models.weather import (
    WeatherForecastModel,
    WeatherFeatureEngineer,
    WeatherDataPreprocessor
)
from app.schemas.weather import (
    WeatherForecastRequest,
    WeatherForecastResponse,
    DailyWeatherForecast
)

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Service for weather forecasting.
    
    Provides weather predictions for agricultural planning.
    """
    
    def __init__(self):
        self.model: Optional[WeatherForecastModel] = None
        self.feature_engineer: Optional[WeatherFeatureEngineer] = None
        self.preprocessor: Optional[WeatherDataPreprocessor] = None
        self._initialized = False
    
    async def initialize(self, model_path: str) -> None:
        """
        Initialize the service with trained models.
        
        Args:
            model_path: Path to the trained model files
        """
        try:
            self.model = WeatherForecastModel()
            self.model.load(model_path)
            
            self.feature_engineer = WeatherFeatureEngineer()
            self.preprocessor = WeatherDataPreprocessor()
            
            self._initialized = True
            logger.info("Weather service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize weather service: {e}")
            raise
    
    async def get_forecast(
        self,
        request: WeatherForecastRequest
    ) -> WeatherForecastResponse:
        """
        Get weather forecast for specified location and period.
        
        Args:
            request: Forecast request with location and date range
            
        Returns:
            WeatherForecastResponse with daily forecasts
        """
        # Validate input
        is_valid, errors = self._validate_input(request)
        if not is_valid:
            raise ValueError(f"Invalid input: {', '.join(errors)}")
        
        # Get historical data for the location
        historical_data = await self._fetch_historical_data(request.location)
        
        # Generate forecast
        if self.model and self.model.is_trained:
            forecast_result = self.model.forecast(
                historical_data=historical_data,
                horizon_days=request.horizon_days,
                location=request.location.model_dump() if request.location else None
            )
        else:
            # Return placeholder forecast
            forecast_result = self._placeholder_forecast(request)
        
        # Format response
        return self._format_response(forecast_result, request)
    
    async def get_historical_analysis(
        self,
        location: Dict[str, float],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get historical weather analysis for a location.
        
        Args:
            location: Location coordinates
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            Historical weather analysis
        """
        # TODO: Implement historical analysis
        return {
            "location": location,
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "summary": {
                "avg_temperature": None,
                "total_rainfall": None,
                "avg_humidity": None
            },
            "trends": []
        }
    
    async def _fetch_historical_data(
        self,
        location: Any
    ) -> Dict[str, Any]:
        """Fetch historical weather data for model input."""
        # TODO: Implement data fetching from database or external API
        return {}
    
    def _validate_input(self, request: WeatherForecastRequest) -> tuple:
        """Validate input request."""
        errors = []
        
        if not request.location:
            errors.append("location is required")
        
        if request.horizon_days <= 0:
            errors.append("horizon_days must be positive")
        
        if request.horizon_days > 90:
            errors.append("horizon_days cannot exceed 90")
        
        return len(errors) == 0, errors
    
    def _placeholder_forecast(
        self,
        request: WeatherForecastRequest
    ) -> Dict[str, Any]:
        """Generate placeholder forecast when model not available."""
        from datetime import timedelta
        
        start_date = datetime.now()
        dates = [
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(1, request.horizon_days + 1)
        ]
        
        return {
            "dates": dates,
            "daily_forecast": {
                "temperature_max": [30.0] * request.horizon_days,
                "temperature_min": [24.0] * request.horizon_days,
                "rainfall": [0.0] * request.horizon_days,
                "humidity": [70.0] * request.horizon_days
            },
            "location": request.location.model_dump() if request.location else None,
            "forecast_start": start_date.strftime("%Y-%m-%d"),
            "horizon_days": request.horizon_days
        }
    
    def _format_response(
        self,
        forecast_result: Dict[str, Any],
        request: WeatherForecastRequest
    ) -> WeatherForecastResponse:
        """Format forecast result into response schema."""
        daily_forecasts = []
        
        dates = forecast_result.get("dates", [])
        daily_data = forecast_result.get("daily_forecast", {})
        
        for i, date in enumerate(dates):
            daily_forecasts.append(
                DailyWeatherForecast(
                    date=date,
                    temperature_max=daily_data.get("temperature_max", [None])[i] if i < len(daily_data.get("temperature_max", [])) else None,
                    temperature_min=daily_data.get("temperature_min", [None])[i] if i < len(daily_data.get("temperature_min", [])) else None,
                    rainfall=daily_data.get("rainfall", [None])[i] if i < len(daily_data.get("rainfall", [])) else None,
                    humidity=daily_data.get("humidity", [None])[i] if i < len(daily_data.get("humidity", [])) else None
                )
            )
        
        return WeatherForecastResponse(
            location=request.location,
            forecast_start=forecast_result.get("forecast_start"),
            forecast_end=dates[-1] if dates else None,
            horizon_days=request.horizon_days,
            daily_forecasts=daily_forecasts
        )
    
    def is_ready(self) -> bool:
        """Check if service is ready to handle requests."""
        return self._initialized and self.model is not None
