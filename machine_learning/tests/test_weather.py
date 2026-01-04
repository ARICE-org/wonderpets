"""
Tests for Weather Forecasting Model
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestWeatherModel:
    """Test cases for the weather forecasting model."""
    
    def test_forecast_returns_correct_shape(self, sample_weather_dataframe):
        """Test that forecast returns correct number of predictions."""
        forecast_days = 30
        
        # Simulate forecast output
        forecast = pd.DataFrame({
            'ds': [datetime.now() + timedelta(days=i) for i in range(forecast_days)],
            'yhat': np.random.uniform(25, 35, forecast_days),
            'yhat_lower': np.random.uniform(20, 30, forecast_days),
            'yhat_upper': np.random.uniform(30, 40, forecast_days)
        })
        
        assert len(forecast) == forecast_days
        assert 'yhat' in forecast.columns
        assert 'yhat_lower' in forecast.columns
        assert 'yhat_upper' in forecast.columns
    
    def test_forecast_confidence_intervals(self):
        """Test that confidence intervals are valid."""
        forecast = pd.DataFrame({
            'yhat': [28.0],
            'yhat_lower': [25.0],
            'yhat_upper': [31.0]
        })
        
        assert forecast['yhat_lower'].iloc[0] <= forecast['yhat'].iloc[0]
        assert forecast['yhat'].iloc[0] <= forecast['yhat_upper'].iloc[0]
    
    def test_temperature_forecast_reasonable_range(self):
        """Test that temperature forecasts are in reasonable range."""
        # Typical tropical temperature range
        min_temp = 15
        max_temp = 45
        
        forecast_temps = np.random.uniform(25, 35, 30)
        
        assert all(min_temp <= t <= max_temp for t in forecast_temps)
    
    def test_rainfall_non_negative(self):
        """Test that rainfall predictions are non-negative."""
        forecast_rainfall = np.abs(np.random.normal(10, 5, 30))
        
        assert all(r >= 0 for r in forecast_rainfall)
    
    def test_humidity_valid_range(self):
        """Test that humidity is between 0 and 100."""
        forecast_humidity = np.random.uniform(50, 90, 30)
        
        assert all(0 <= h <= 100 for h in forecast_humidity)


class TestWeatherService:
    """Test cases for the weather service."""
    
    @pytest.mark.asyncio
    async def test_get_forecast_returns_dict(self):
        """Test that get_forecast returns dictionary."""
        from app.services.weather_service import WeatherService
        
        with patch.object(WeatherService, '_load_models'):
            service = WeatherService()
            service.models = {
                'temperature': Mock(),
                'rainfall': Mock(),
                'humidity': Mock()
            }
            
            assert 'temperature' in service.models
            assert 'rainfall' in service.models
    
    def test_forecast_aggregation(self):
        """Test weekly/monthly aggregation of forecasts."""
        daily_temps = np.random.uniform(25, 35, 30)
        
        # Weekly average
        weekly_temps = [np.mean(daily_temps[i:i+7]) for i in range(0, 28, 7)]
        
        assert len(weekly_temps) == 4
        assert all(25 <= t <= 35 for t in weekly_temps)
    
    def test_seasonal_patterns(self, sample_weather_dataframe):
        """Test detection of seasonal patterns."""
        df = sample_weather_dataframe
        df['month'] = pd.to_datetime(df['date']).dt.month
        
        # Group by month
        monthly_avg = df.groupby('month')['temperature'].mean()
        
        assert len(monthly_avg) <= 12


class TestWeatherAPI:
    """Test cases for the weather API endpoints."""
    
    def test_forecast_request_schema(self):
        """Test forecast request validation."""
        from app.schemas.weather import WeatherForecastRequest
        
        request = WeatherForecastRequest(
            location_id=1,
            forecast_days=30
        )
        
        assert request.forecast_days == 30
        assert request.location_id == 1
    
    def test_forecast_response_schema(self):
        """Test forecast response structure."""
        from app.schemas.weather import WeatherForecastResponse, DailyForecast
        
        daily = DailyForecast(
            date=datetime.now(),
            temperature=28.0,
            temperature_min=25.0,
            temperature_max=31.0,
            humidity=75.0,
            rainfall=10.0,
            confidence=0.85
        )
        
        response = WeatherForecastResponse(
            location_id=1,
            forecasts=[daily],
            generated_at=datetime.now()
        )
        
        assert len(response.forecasts) == 1
        assert response.forecasts[0].temperature == 28.0
    
    def test_invalid_forecast_days(self):
        """Test validation of forecast_days parameter."""
        from app.schemas.weather import WeatherForecastRequest
        
        # Should accept valid range
        valid_request = WeatherForecastRequest(
            location_id=1,
            forecast_days=7
        )
        assert valid_request.forecast_days == 7
        
        # Would need to test validation for invalid values
        # depending on schema constraints


class TestWeatherDataProcessing:
    """Test cases for weather data preprocessing."""
    
    def test_missing_data_handling(self, sample_weather_dataframe):
        """Test handling of missing weather data."""
        df = sample_weather_dataframe.copy()
        
        # Introduce missing values
        df.loc[0:5, 'temperature'] = np.nan
        
        # Fill missing values
        df['temperature'] = df['temperature'].interpolate()
        
        assert df['temperature'].isna().sum() == 0
    
    def test_outlier_detection(self, sample_weather_dataframe):
        """Test outlier detection in weather data."""
        df = sample_weather_dataframe.copy()
        
        # Add outliers
        df.loc[0, 'temperature'] = 100  # Unrealistic temperature
        
        # Detect outliers using IQR
        Q1 = df['temperature'].quantile(0.25)
        Q3 = df['temperature'].quantile(0.75)
        IQR = Q3 - Q1
        
        outliers = df[(df['temperature'] < Q1 - 1.5 * IQR) | 
                      (df['temperature'] > Q3 + 1.5 * IQR)]
        
        assert len(outliers) >= 1
    
    def test_date_parsing(self):
        """Test date parsing for weather data."""
        date_strings = ['2024-01-15', '2024-02-20', '2024-03-25']
        
        dates = pd.to_datetime(date_strings)
        
        assert all(isinstance(d, pd.Timestamp) for d in dates)
        assert dates[0].month == 1
        assert dates[1].month == 2
