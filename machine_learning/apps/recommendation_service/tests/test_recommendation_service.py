"""
Tests for Recommendation Service.
"""

import pytest
from datetime import datetime

from apps.recommendation_service.services.recommendation_service import RecommendationService
from apps.recommendation_service.models.rice_variety_model import RiceVarietyRecommendationModel


class TestRiceVarietyModel:
    """Tests for RiceVarietyRecommendationModel."""
    
    def test_model_initialization(self):
        """Test model initializes correctly."""
        model = RiceVarietyRecommendationModel()
        assert model.model_name == "rice_variety_recommendation"
        assert model.version == "1.0"
    
    def test_preprocess(self):
        """Test data preprocessing."""
        model = RiceVarietyRecommendationModel()
        
        data = {
            "soil_data": {
                "ph": 6.5,
                "nitrogen": 45,
                "phosphorus": 18
            },
            "weather_data": {
                "temperature_avg": 28,
                "rainfall_avg": 150
            },
            "season": "wet"
        }
        
        result = model.preprocess(data)
        assert result.shape == (1, 10)
    
    def test_fallback_predict(self):
        """Test fallback prediction."""
        model = RiceVarietyRecommendationModel()
        
        result = model._fallback_predict({})
        
        assert len(result) == 5
        assert "variety_id" in result[0]
        assert "confidence" in result[0]


class TestRecommendationService:
    """Tests for RecommendationService."""
    
    @pytest.fixture
    def service(self):
        """Create a test service instance."""
        return RecommendationService()
    
    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.is_ready() is True
    
    @pytest.mark.asyncio
    async def test_get_recommendations(self, service):
        """Test recommendations retrieval."""
        result = await service.get_recommendations(
            soil_data={"ph": 6.5, "nitrogen": 45},
            weather_data={"temperature_avg": 28},
            season="wet",
            top_k=3
        )
        
        assert "recommendations" in result
        assert len(result["recommendations"]) == 3
        assert result["recommendations"][0]["rank"] == 1
    
    @pytest.mark.asyncio
    async def test_get_planting_schedule(self, service):
        """Test planting schedule generation."""
        result = await service.get_planting_schedule(
            location={"latitude": 14.5, "longitude": 121.0}
        )
        
        assert "recommended_planting_window" in result
        assert "start_date" in result["recommended_planting_window"]
    
    def test_get_available_varieties(self, service):
        """Test variety listing."""
        varieties = service.get_available_varieties()
        
        assert len(varieties) > 0
        assert "id" in varieties[0]
        assert "name" in varieties[0]
    
    def test_get_variety_details(self, service):
        """Test variety details retrieval."""
        variety = service.get_variety_details("IR64")
        
        assert variety is not None
        assert variety["name"] == "IR64"
    
    def test_rule_based_scoring(self, service):
        """Test rule-based variety scoring."""
        from apps.recommendation_service.core.constants import RICE_VARIETIES
        
        variety = RICE_VARIETIES["RC402"]
        score = service._calculate_variety_score(
            "RC402",
            variety,
            {"ph": 6.5},
            {"is_drought_prone": True},
            "dry"
        )
        
        assert score > 50  # Should get drought tolerance bonus
