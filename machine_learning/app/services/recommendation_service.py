"""
Recommendation Service

Business logic layer for rice variety recommendations.
Orchestrates data preprocessing, model prediction, and result formatting.
"""

from typing import Any, Dict, List, Optional
import logging

from app.models.recommendation import (
    RiceVarietyRecommendationModel,
    RecommendationFeatureEngineer,
    RecommendationDataPreprocessor
)
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RiceVarietyRecommendation
)
from app.utils.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service for rice variety recommendations.
    
    Handles the full pipeline from input validation to
    formatted recommendation output.
    """
    
    def __init__(self):
        self.model: Optional[RiceVarietyRecommendationModel] = None
        self.feature_engineer: Optional[RecommendationFeatureEngineer] = None
        self.preprocessor: Optional[RecommendationDataPreprocessor] = None
        self._initialized = False
    
    async def initialize(self, model_path: str) -> None:
        """
        Initialize the service with trained models.
        
        Args:
            model_path: Path to the trained model files
        """
        try:
            self.model = RiceVarietyRecommendationModel()
            self.model.load(model_path)
            
            self.feature_engineer = RecommendationFeatureEngineer()
            self.preprocessor = RecommendationDataPreprocessor()
            
            self._initialized = True
            logger.info("Recommendation service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize recommendation service: {e}")
            raise
    
    async def get_recommendations(
        self,
        request: RecommendationRequest,
        top_k: int = 5
    ) -> RecommendationResponse:
        """
        Get rice variety recommendations based on input conditions.
        
        Args:
            request: Recommendation request with soil, weather, and location data
            top_k: Number of top recommendations to return
            
        Returns:
            RecommendationResponse with ranked variety recommendations
        """
        # Validate input
        is_valid, errors = self._validate_input(request)
        if not is_valid:
            raise ValueError(f"Invalid input: {', '.join(errors)}")
        
        # Prepare input data
        input_data = self._prepare_input(request)
        
        # Preprocess data
        preprocessed = self.preprocessor.transform(input_data) if self.preprocessor else input_data
        
        # Engineer features
        features = self.feature_engineer.transform(preprocessed) if self.feature_engineer else preprocessed
        
        # Get model predictions
        if self.model and self.model.is_trained:
            predictions = self.model.get_top_recommendations(features, top_k=top_k)
        else:
            # Fallback to rule-based recommendations
            predictions = self._rule_based_recommendations(request, top_k)
        
        # Format response
        return self._format_response(predictions, request)
    
    async def get_planting_schedule(
        self,
        request: RecommendationRequest
    ) -> Dict[str, Any]:
        """
        Get optimal planting schedule based on conditions.
        
        Args:
            request: Request with location and season data
            
        Returns:
            Recommended planting schedule
        """
        # TODO: Implement planting schedule logic
        return {
            "recommended_planting_window": {
                "start": None,
                "end": None
            },
            "optimal_planting_date": None,
            "reasoning": "Schedule calculation not yet implemented"
        }
    
    def _validate_input(self, request: RecommendationRequest) -> tuple:
        """Validate input request."""
        errors = []
        
        if not request.soil_data:
            errors.append("soil_data is required")
        
        if not request.location:
            errors.append("location is required")
        
        return len(errors) == 0, errors
    
    def _prepare_input(self, request: RecommendationRequest) -> Dict[str, Any]:
        """Prepare input data for processing."""
        return {
            "soil_data": request.soil_data.model_dump() if request.soil_data else {},
            "weather_data": request.weather_data.model_dump() if request.weather_data else {},
            "location": request.location.model_dump() if request.location else {},
            "season": request.season
        }
    
    def _rule_based_recommendations(
        self,
        request: RecommendationRequest,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Fallback rule-based recommendations when model is not available.
        
        Args:
            request: Input request
            top_k: Number of recommendations
            
        Returns:
            List of recommendations based on rules
        """
        # TODO: Implement rule-based logic based on soil and weather conditions
        return [
            {
                "variety_id": i,
                "variety_name": f"Rice Variety {i}",
                "confidence": 0.8 - (i * 0.1),
                "rank": i,
                "reasoning": "Rule-based recommendation (model not loaded)"
            }
            for i in range(1, min(top_k + 1, 6))
        ]
    
    def _format_response(
        self,
        predictions: List[Dict[str, Any]],
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """Format predictions into response schema."""
        recommendations = [
            RiceVarietyRecommendation(
                variety_id=pred.get("variety_id"),
                variety_name=pred.get("variety_name", "Unknown"),
                confidence_score=pred.get("confidence", 0.0),
                rank=pred.get("rank", 0),
                reasoning=pred.get("reasoning", "")
            )
            for pred in predictions
        ]
        
        return RecommendationResponse(
            recommendations=recommendations,
            input_summary={
                "location": request.location.model_dump() if request.location else None,
                "season": request.season
            }
        )
    
    def is_ready(self) -> bool:
        """Check if service is ready to handle requests."""
        return self._initialized and self.model is not None
