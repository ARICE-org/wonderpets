"""
Tests for Soil Analysis Service.
"""

import pytest
from datetime import datetime

from apps.soil_service.services.soil_analysis_service import SoilAnalysisService
from apps.soil_service.models.soil_health_model import SoilHealthModel


class TestSoilHealthModel:
    """Tests for SoilHealthModel."""
    
    def test_model_initialization(self):
        """Test model initializes correctly."""
        model = SoilHealthModel()
        assert model.model_name == "soil_health"
        assert model.version == "1.0"
    
    def test_health_score_calculation(self):
        """Test health score calculation with valid data."""
        model = SoilHealthModel()
        
        soil_data = {
            "ph": 6.5,
            "nitrogen": 45,
            "phosphorus": 18,
            "potassium": 60,
            "organic_matter": 3.5,
            "moisture": 55
        }
        
        result = model.calculate_health_score(soil_data)
        
        assert "overall_score" in result
        assert "overall_status" in result
        assert "parameter_scores" in result
        assert 0 <= result["overall_score"] <= 100
    
    def test_health_score_with_deficiencies(self):
        """Test health score detects deficiencies."""
        model = SoilHealthModel()
        
        soil_data = {
            "ph": 4.0,  # Too low
            "nitrogen": 10,  # Too low
            "phosphorus": 5,  # Too low
            "potassium": 60,
            "organic_matter": 3.5,
            "moisture": 55
        }
        
        result = model.calculate_health_score(soil_data)
        
        assert len(result["deficiencies"]) > 0
        assert len(result["recommendations"]) > 0
    
    def test_parameter_score_in_optimal_range(self):
        """Test parameter scoring when value is in optimal range."""
        model = SoilHealthModel()
        
        score = model._calculate_parameter_score(
            value=6.0,
            ranges={"min": 5.5, "max": 7.0, "optimal": 6.0}
        )
        
        assert score >= 70  # Should be high when optimal
    
    def test_parameter_score_below_range(self):
        """Test parameter scoring when value is below optimal range."""
        model = SoilHealthModel()
        
        score = model._calculate_parameter_score(
            value=4.0,
            ranges={"min": 5.5, "max": 7.0, "optimal": 6.0}
        )
        
        assert score < 70  # Should be lower


class TestSoilAnalysisService:
    """Tests for SoilAnalysisService."""
    
    @pytest.fixture
    def service(self):
        """Create a test service instance."""
        return SoilAnalysisService()
    
    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.is_ready() is True
    
    @pytest.mark.asyncio
    async def test_analyze_health(self, service):
        """Test health analysis."""
        soil_data = {
            "ph": 6.5,
            "nitrogen": 45,
            "phosphorus": 18,
            "potassium": 60,
            "organic_matter": 3.5,
            "moisture": 55
        }
        
        result = await service.analyze_health(soil_data)
        
        assert "overall_score" in result
        assert "parameter_scores" in result
    
    @pytest.mark.asyncio
    async def test_hybrid_forecast(self, service):
        """Test hybrid forecast generation."""
        soil_data = {
            "nitrogen": 45,
            "phosphorus": 18,
            "potassium": 60,
            "ph": 6.5,
            "moisture": 55,
            "organic_matter": 3.5
        }
        
        result = await service.hybrid_forecast(
            current_soil_data=soil_data,
            planting_date="2025-01-15",
            forecast_horizon_days=90,
            forecast_interval_days=7
        )
        
        assert "planting_date" in result
        assert "detailed_forecast" in result
        assert len(result["detailed_forecast"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_detailed_score(self, service):
        """Test detailed score retrieval."""
        soil_data = {
            "ph": 6.5,
            "nitrogen": 45,
            "phosphorus": 18,
            "potassium": 60,
            "organic_matter": 3.5,
            "moisture": 55
        }
        
        result = await service.get_detailed_score(soil_data)
        
        assert "overall_score" in result
        assert "score_interpretation" in result
        assert "parameter_details" in result


class TestHybridForecastModel:
    """Tests for HybridSoilForecastModel."""
    
    def test_model_initialization(self):
        """Test hybrid model initializes correctly."""
        from apps.soil_service.models.hybrid_forecast_model import HybridSoilForecastModel
        
        model = HybridSoilForecastModel()
        assert model.model_name == "hybrid_soil_forecast"
        assert model.seasonal_baseline is not None
    
    def test_season_detection(self):
        """Test season detection for Philippines."""
        from apps.soil_service.models.hybrid_forecast_model import SoilScienceRules
        
        # Dry season months
        assert SoilScienceRules.get_season(1) == "dry"
        assert SoilScienceRules.get_season(3) == "dry"
        assert SoilScienceRules.get_season(12) == "dry"
        
        # Wet season months
        assert SoilScienceRules.get_season(6) == "wet"
        assert SoilScienceRules.get_season(9) == "wet"
    
    def test_forecast_season(self):
        """Test seasonal forecast generation."""
        from apps.soil_service.models.hybrid_forecast_model import HybridSoilForecastModel
        
        model = HybridSoilForecastModel()
        
        result = model.forecast_season(
            planting_date=datetime(2025, 1, 15),
            forecast_days=30,
            interval_days=7
        )
        
        assert "planting_date" in result
        assert "forecast_end_date" in result
        assert "detailed_forecast" in result
        assert len(result["detailed_forecast"]) > 0
