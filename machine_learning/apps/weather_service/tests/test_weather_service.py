"""
Tests for Weather Service.
"""

import pytest
from datetime import datetime

from apps.weather_service.services.weather_service import WeatherService
from apps.weather_service.models.weather_forecast_model import WeatherForecastModel


class TestWeatherForecastModel:
    """Tests for WeatherForecastModel."""
    
    def test_model_initialization(self):
        """Test model initializes correctly."""
        model = WeatherForecastModel()
        assert model.model_name == "weather_forecast"
        assert model.version == "1.0"
    
    def test_forecast_generation(self):
        """Test forecast generation."""
        model = WeatherForecastModel()
        
        result = model.forecast(
            historical_data={},
            horizon_days=7,
            location={"latitude": 14.5, "longitude": 121.0}
        )
        
        assert "forecast_start" in result
        assert "forecast_end" in result
        assert "daily_forecast" in result
    
    def test_fallback_prediction(self):
        """Test fallback prediction when model not trained."""
        model = WeatherForecastModel()
        model.forecast_horizon_days = 7
        
        result = model._fallback_predict({})
        
        assert "dates" in result
        assert "temperature_max" in result
        assert len(result["dates"]) == 7


class TestWeatherService:
    """Tests for WeatherService."""
    
    @pytest.fixture
    def service(self):
        """Create a test service instance."""
        return WeatherService()
    
    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.is_ready() is True
    
    @pytest.mark.asyncio
    async def test_get_forecast(self, service):
        """Test forecast retrieval."""
        result = await service.get_forecast(
            location={"latitude": 14.5, "longitude": 121.0},
            horizon_days=7
        )
        
        assert "forecast_start" in result
        assert "daily_forecasts" in result
        assert len(result["daily_forecasts"]) == 7
    
    @pytest.mark.asyncio
    async def test_get_current_weather(self, service):
        """Test current weather retrieval."""
        result = await service.get_current_weather(
            latitude=14.5,
            longitude=121.0
        )
        
        assert "temperature" in result
        assert "humidity" in result
    
    def test_validation(self, service):
        """Test input validation."""
        is_valid, errors = service._validate_input(
            location={"latitude": 14.5, "longitude": 121.0},
            horizon_days=30
        )
        assert is_valid is True
        
        is_valid, errors = service._validate_input(
            location=None,
            horizon_days=100
        )
        assert is_valid is False
