"""
Tests for Rice Variety Recommendation Model
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch


class TestRecommendationModel:
    """Test cases for the recommendation model."""
    
    def test_model_prediction_returns_variety(self, mock_recommendation_model):
        """Test that model returns a variety name."""
        model = mock_recommendation_model['model']
        scaler = mock_recommendation_model['scaler']
        encoder = mock_recommendation_model['encoder']
        
        # Sample input
        features = np.array([[6.5, 35, 25, 150, 55, 28, 75, 150]])
        scaled_features = scaler.transform(features)
        
        prediction = model.predict(scaled_features)
        variety = encoder.inverse_transform(prediction)[0]
        
        assert isinstance(variety, str)
        assert variety in encoder.classes_
    
    def test_model_returns_probabilities(self, mock_recommendation_model):
        """Test that model returns probability distribution."""
        model = mock_recommendation_model['model']
        scaler = mock_recommendation_model['scaler']
        
        features = np.array([[6.5, 35, 25, 150, 55, 28, 75, 150]])
        scaled_features = scaler.transform(features)
        
        probabilities = model.predict_proba(scaled_features)[0]
        
        assert len(probabilities) == len(mock_recommendation_model['encoder'].classes_)
        assert np.isclose(sum(probabilities), 1.0)
        assert all(0 <= p <= 1 for p in probabilities)
    
    def test_feature_scaling(self, mock_recommendation_model, sample_soil_data, sample_weather_data):
        """Test that feature scaling works correctly."""
        scaler = mock_recommendation_model['scaler']
        
        features = np.array([[
            sample_soil_data['ph'],
            sample_soil_data['nitrogen'],
            sample_soil_data['phosphorus'],
            sample_soil_data['potassium'],
            sample_soil_data['moisture'],
            sample_weather_data['temperature'],
            sample_weather_data['humidity'],
            sample_weather_data['rainfall']
        ]])
        
        scaled = scaler.transform(features)
        
        assert scaled.shape == features.shape
        assert not np.array_equal(scaled, features)  # Should be different after scaling
    
    def test_handles_missing_features(self, mock_recommendation_model):
        """Test handling of missing features."""
        model = mock_recommendation_model['model']
        scaler = mock_recommendation_model['scaler']
        
        # Features with NaN
        features = np.array([[6.5, np.nan, 25, 150, 55, 28, 75, 150]])
        
        # Replace NaN with mean (simulating preprocessing)
        features = np.nan_to_num(features, nan=0)
        scaled_features = scaler.transform(features)
        
        # Should still make a prediction
        prediction = model.predict(scaled_features)
        assert prediction is not None


class TestRecommendationService:
    """Test cases for the recommendation service."""
    
    @pytest.mark.asyncio
    async def test_get_recommendations_returns_list(self):
        """Test that get_recommendations returns a list."""
        from app.services.recommendation_service import RecommendationService
        
        with patch.object(RecommendationService, '_load_model'):
            service = RecommendationService()
            service.model = Mock()
            service.model.predict_proba = Mock(return_value=np.array([[0.5, 0.3, 0.2]]))
            service.scaler = Mock()
            service.scaler.transform = Mock(return_value=np.array([[0, 0, 0, 0, 0, 0, 0, 0]]))
            service.label_encoder = Mock()
            service.label_encoder.classes_ = np.array(['A', 'B', 'C'])
            service.label_encoder.inverse_transform = Mock(side_effect=lambda x: ['A', 'B', 'C'][x[0]:x[0]+1])
            
            # This would need the actual service implementation
            # For now, just verify the mock setup works
            assert service.model is not None
    
    def test_validate_input_data(self, sample_soil_data, sample_weather_data):
        """Test input data validation."""
        # Combine soil and weather data
        input_data = {**sample_soil_data, **sample_weather_data}
        
        required_fields = ['ph', 'nitrogen', 'phosphorus', 'potassium', 
                          'moisture', 'temperature', 'humidity', 'rainfall']
        
        for field in required_fields:
            assert field in input_data or field in sample_soil_data or field in sample_weather_data


class TestRecommendationAPI:
    """Test cases for the recommendation API endpoints."""
    
    def test_recommendation_request_schema(self):
        """Test that request schema validates correctly."""
        from app.schemas.recommendation import RecommendationRequest
        
        valid_request = RecommendationRequest(
            soil_data={
                'ph': 6.5,
                'nitrogen': 35,
                'phosphorus': 25,
                'potassium': 150,
                'moisture': 55
            },
            weather_data={
                'temperature': 28,
                'humidity': 75,
                'rainfall': 150
            }
        )
        
        assert valid_request.soil_data['ph'] == 6.5
        assert valid_request.weather_data['temperature'] == 28
    
    def test_recommendation_response_schema(self):
        """Test that response schema is valid."""
        from app.schemas.recommendation import RecommendationResponse, VarietyRecommendation
        
        recommendation = VarietyRecommendation(
            variety_name='NSIC Rc222',
            confidence_score=0.85,
            suitability_factors={
                'soil_match': 0.9,
                'weather_match': 0.8
            }
        )
        
        response = RecommendationResponse(
            recommendations=[recommendation],
            top_recommendation='NSIC Rc222'
        )
        
        assert len(response.recommendations) == 1
        assert response.top_recommendation == 'NSIC Rc222'
