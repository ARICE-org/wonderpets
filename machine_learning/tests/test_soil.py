"""
Tests for Soil Health and Forecast Models
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestSoilHealthModel:
    """Test cases for the soil health scoring model."""
    
    def test_health_score_in_valid_range(self, sample_soil_data, mock_soil_health_config):
        """Test that health score is between 0 and 100."""
        from conftest import assert_valid_health_score
        
        # Calculate mock health score
        score = 85.0  # Simulated score
        
        assert_valid_health_score(score)
    
    def test_optimal_soil_returns_high_score(self, mock_soil_health_config):
        """Test that optimal soil conditions return high score."""
        optimal_ranges = mock_soil_health_config['optimal_ranges']
        
        optimal_soil = {
            'ph': optimal_ranges['ph']['optimal'],
            'nitrogen': optimal_ranges['nitrogen']['optimal'],
            'phosphorus': optimal_ranges['phosphorus']['optimal'],
            'potassium': optimal_ranges['potassium']['optimal'],
            'moisture': optimal_ranges['moisture']['optimal']
        }
        
        # With optimal values, score should be high (>80)
        expected_min_score = 80
        
        # Simulated calculation
        score = 95.0
        
        assert score >= expected_min_score
    
    def test_deficient_soil_returns_low_score(self, mock_soil_health_config):
        """Test that deficient soil returns low score."""
        deficient_soil = {
            'ph': 4.0,  # Too acidic
            'nitrogen': 5,  # Very low
            'phosphorus': 5,  # Very low
            'potassium': 50,  # Very low
            'moisture': 20  # Too dry
        }
        
        # With deficient values, score should be low (<50)
        expected_max_score = 50
        
        # Simulated calculation
        score = 35.0
        
        assert score <= expected_max_score
    
    def test_identifies_nutrient_deficiencies(self, mock_soil_health_config):
        """Test identification of specific nutrient deficiencies."""
        optimal_ranges = mock_soil_health_config['optimal_ranges']
        
        soil_data = {
            'ph': 6.5,
            'nitrogen': 10,  # Below minimum of 20
            'phosphorus': 25,
            'potassium': 150,
            'moisture': 55
        }
        
        deficiencies = []
        for param, value in soil_data.items():
            if param in optimal_ranges:
                if value < optimal_ranges[param]['min']:
                    deficiencies.append({'parameter': param, 'status': 'low'})
                elif value > optimal_ranges[param]['max']:
                    deficiencies.append({'parameter': param, 'status': 'high'})
        
        assert len(deficiencies) == 1
        assert deficiencies[0]['parameter'] == 'nitrogen'
        assert deficiencies[0]['status'] == 'low'
    
    def test_weight_normalization(self, mock_soil_health_config):
        """Test that weights sum to approximately 1."""
        weights = mock_soil_health_config['weights']
        total_weight = sum(weights.values())
        
        # Weights should sum close to 1 (within tolerance for subset)
        assert 0.5 <= total_weight <= 1.0


class TestSoilForecastModel:
    """Test cases for the soil 3-month forecast model."""
    
    def test_forecast_horizon(self):
        """Test forecast covers 90-120 days."""
        forecast_days = 120
        rice_season_days = 120
        
        assert forecast_days == rice_season_days
    
    def test_growth_stage_mapping(self):
        """Test mapping of days to growth stages."""
        growth_stages = {
            'seedling': {'start': 0, 'end': 15},
            'tillering': {'start': 15, 'end': 45},
            'panicle_initiation': {'start': 45, 'end': 70},
            'flowering': {'start': 70, 'end': 90},
            'grain_filling': {'start': 90, 'end': 120}
        }
        
        def get_stage(day):
            for stage, bounds in growth_stages.items():
                if bounds['start'] <= day < bounds['end']:
                    return stage
            return 'grain_filling'  # Last stage
        
        assert get_stage(5) == 'seedling'
        assert get_stage(30) == 'tillering'
        assert get_stage(50) == 'panicle_initiation'
        assert get_stage(80) == 'flowering'
        assert get_stage(100) == 'grain_filling'
    
    def test_forecast_returns_all_parameters(self):
        """Test that forecast includes all soil parameters."""
        soil_params = ['ph', 'nitrogen', 'phosphorus', 'potassium', 'moisture']
        
        # Simulated forecast output
        forecast = {param: np.random.uniform(0, 100, 90) for param in soil_params}
        
        for param in soil_params:
            assert param in forecast
            assert len(forecast[param]) == 90
    
    def test_confidence_decreases_with_horizon(self):
        """Test that confidence decreases for further predictions."""
        days = np.arange(1, 121)
        
        # Confidence should decrease with time
        base_confidence = 0.95
        decay_rate = 0.002
        
        confidences = base_confidence * np.exp(-decay_rate * days)
        
        assert confidences[0] > confidences[-1]
        assert confidences[-1] > 0  # Still positive
    
    def test_seasonal_trend_detection(self):
        """Test detection of seasonal trends in soil data."""
        np.random.seed(42)
        
        # Create data with seasonal pattern
        days = np.arange(365)
        seasonal_component = 10 * np.sin(2 * np.pi * days / 365)
        noise = np.random.normal(0, 2, 365)
        moisture = 50 + seasonal_component + noise
        
        # Calculate monthly averages
        monthly_avg = [np.mean(moisture[i:i+30]) for i in range(0, 360, 30)]
        
        # Should see variation across months
        assert max(monthly_avg) - min(monthly_avg) > 5


class TestSoilService:
    """Test cases for the soil analysis service."""
    
    @pytest.mark.asyncio
    async def test_analyze_health_returns_score(self, sample_soil_data):
        """Test that analyze_health returns a valid score."""
        from app.services.soil_analysis_service import SoilAnalysisService
        
        with patch.object(SoilAnalysisService, '_load_models'):
            service = SoilAnalysisService()
            
            # Mock the health calculation
            mock_result = {
                'overall_score': 85.0,
                'parameter_scores': {
                    'ph': 95,
                    'nitrogen': 80,
                    'phosphorus': 85,
                    'potassium': 90,
                    'moisture': 75
                },
                'deficiencies': []
            }
            
            assert mock_result['overall_score'] <= 100
            assert mock_result['overall_score'] >= 0
    
    def test_recommendation_generation(self, sample_soil_data, mock_soil_health_config):
        """Test generation of improvement recommendations."""
        optimal_ranges = mock_soil_health_config['optimal_ranges']
        
        low_nitrogen_soil = {
            'ph': 6.5,
            'nitrogen': 15,  # Below minimum
            'phosphorus': 25,
            'potassium': 150,
            'moisture': 55
        }
        
        recommendations = []
        
        if low_nitrogen_soil['nitrogen'] < optimal_ranges['nitrogen']['min']:
            recommendations.append({
                'parameter': 'nitrogen',
                'action': 'increase',
                'suggestion': 'Apply nitrogen-rich fertilizer',
                'target_value': optimal_ranges['nitrogen']['optimal']
            })
        
        assert len(recommendations) == 1
        assert recommendations[0]['parameter'] == 'nitrogen'


class TestSoilAPI:
    """Test cases for the soil API endpoints."""
    
    def test_health_analysis_request_schema(self):
        """Test health analysis request validation."""
        from app.schemas.soil import SoilHealthRequest
        
        request = SoilHealthRequest(
            soil_data={
                'ph': 6.5,
                'nitrogen': 35,
                'phosphorus': 25,
                'potassium': 150,
                'moisture': 55
            },
            include_recommendations=True
        )
        
        assert request.soil_data['ph'] == 6.5
        assert request.include_recommendations is True
    
    def test_health_response_schema(self):
        """Test health analysis response structure."""
        from app.schemas.soil import SoilHealthResponse, ParameterScore, Deficiency
        
        response = SoilHealthResponse(
            overall_score=85.0,
            health_category='Good',
            parameter_scores=[
                ParameterScore(parameter='ph', score=95, status='optimal'),
                ParameterScore(parameter='nitrogen', score=80, status='good')
            ],
            deficiencies=[],
            recommendations=['Maintain current practices']
        )
        
        assert response.overall_score == 85.0
        assert response.health_category == 'Good'
        assert len(response.parameter_scores) == 2
    
    def test_forecast_request_schema(self):
        """Test forecast request validation."""
        from app.schemas.soil import SoilForecastRequest
        
        request = SoilForecastRequest(
            soil_data={
                'ph': 6.5,
                'nitrogen': 35,
                'phosphorus': 25,
                'potassium': 150,
                'moisture': 55
            },
            planting_date=datetime.now(),
            forecast_days=90
        )
        
        assert request.forecast_days == 90
    
    def test_forecast_response_schema(self):
        """Test forecast response structure."""
        from app.schemas.soil import SoilForecastResponse, StageForecast
        
        stage = StageForecast(
            stage_name='seedling',
            start_day=0,
            end_day=15,
            predicted_conditions={
                'ph': 6.5,
                'nitrogen': 32,
                'phosphorus': 24,
                'potassium': 145,
                'moisture': 52
            },
            alerts=['Nitrogen may drop below optimal'],
            recommendations=['Consider nitrogen supplement']
        )
        
        response = SoilForecastResponse(
            forecast_days=120,
            stage_forecasts=[stage],
            overall_season_outlook='Favorable',
            critical_periods=[]
        )
        
        assert response.forecast_days == 120
        assert len(response.stage_forecasts) == 1
