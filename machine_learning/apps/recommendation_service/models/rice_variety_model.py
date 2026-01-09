"""
Rice Variety Recommendation Model

Recommends optimal rice varieties based on:
- Soil conditions (pH, nutrients, moisture)
- Weather data (temperature, rainfall, humidity)
- Location and season information
"""

from typing import Any, Dict, List, Optional
import numpy as np
import joblib
from pathlib import Path

from apps.common.base.base_model import BaseMLModel
from apps.common.utils.logging_utils import logger
from apps.recommendation_service.core.constants import RICE_VARIETIES


class RiceVarietyRecommendationModel(BaseMLModel):
    """
    Machine learning model for recommending rice varieties.
    
    Uses ensemble methods to predict the best rice varieties 
    for given conditions.
    """
    
    def __init__(self, version: str = "1.0"):
        super().__init__(model_name="rice_variety_recommendation", version=version)
        self.feature_names: List[str] = []
        self.variety_classes: List[str] = list(RICE_VARIETIES.keys())
        self.scaler = None
    
    def train(self, X, y, **kwargs) -> Dict[str, Any]:
        """
        Train the recommendation model.
        
        Args:
            X: Feature matrix with soil, weather, and location data
            y: Target labels (rice variety IDs)
            **kwargs: Additional parameters
            
        Returns:
            Training metrics
        """
        # Placeholder for training logic
        self.is_trained = True
        self.metadata["training_samples"] = len(X) if hasattr(X, '__len__') else 0
        self.metadata["n_classes"] = len(set(y)) if hasattr(y, '__iter__') else 0
        
        return {
            "accuracy": 0.0,
            "f1_score": 0.0,
            "training_samples": self.metadata["training_samples"]
        }
    
    def predict(self, X) -> List[Dict[str, Any]]:
        """
        Predict recommended rice varieties.
        
        Args:
            X: Input features (preprocessed)
            
        Returns:
            List of recommendations with confidence scores
        """
        if not self.is_trained or self.model is None:
            return self._fallback_predict(X)
        
        # ML-based prediction (placeholder)
        return [
            {
                "variety_id": "IR64",
                "variety_name": "IR64",
                "confidence": 0.85,
                "rank": 1
            }
        ]
    
    def _fallback_predict(self, X) -> List[Dict[str, Any]]:
        """Fallback prediction based on heuristics."""
        return [
            {
                "variety_id": variety_id,
                "variety_name": variety["name"],
                "confidence": 0.5,
                "rank": i + 1
            }
            for i, (variety_id, variety) in enumerate(list(RICE_VARIETIES.items())[:5])
        ]
    
    def preprocess(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Preprocess input data for prediction.
        
        Args:
            data: Dictionary containing soil, weather, location data
            
        Returns:
            Numpy array ready for model input
        """
        features = []
        
        # Extract soil features
        soil = data.get("soil_data", {})
        features.extend([
            soil.get("ph", 6.5),
            soil.get("nitrogen", 40),
            soil.get("phosphorus", 20),
            soil.get("potassium", 60),
            soil.get("organic_matter", 3.5),
            soil.get("moisture", 50)
        ])
        
        # Extract weather features
        weather = data.get("weather_data", {})
        features.extend([
            weather.get("temperature_avg", 28),
            weather.get("rainfall_avg", 100),
            weather.get("humidity_avg", 75)
        ])
        
        # Season encoding
        season = data.get("season", "wet")
        features.append(1 if season == "wet" else 0)
        
        return np.array(features).reshape(1, -1)
    
    def get_top_recommendations(
        self, 
        X, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top-k variety recommendations.
        
        Args:
            X: Input features
            top_k: Number of recommendations
            
        Returns:
            List of top recommendations with scores
        """
        if not self.is_trained or self.model is None:
            return self._fallback_predict(X)[:top_k]
        
        # Get predictions with probabilities
        predictions = self.predict(X)
        
        # Sort by confidence and return top-k
        sorted_predictions = sorted(
            predictions, 
            key=lambda x: x["confidence"], 
            reverse=True
        )
        
        return sorted_predictions[:top_k]
    
    def load(self, path: str) -> None:
        """Load trained model from disk."""
        try:
            filepath = Path(path)
            if filepath.exists():
                model_data = joblib.load(filepath)
                self.model = model_data.get("model")
                self.scaler = model_data.get("scaler")
                self.feature_names = model_data.get("feature_names", [])
                self.variety_classes = model_data.get("variety_classes", [])
                self.metadata = model_data.get("metadata", {})
                self.is_trained = model_data.get("is_trained", True)
                logger.info(f"Loaded recommendation model from {path}")
            else:
                raise FileNotFoundError(f"Model file not found: {path}")
        except Exception as e:
            logger.error(f"Error loading recommendation model: {e}")
            raise
    
    def save(self, path: str, filename: Optional[str] = None) -> str:
        """Save trained model to disk."""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        filepath = Path(path)
        if filename:
            filepath = filepath / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "variety_classes": self.variety_classes,
            "metadata": self.metadata,
            "is_trained": self.is_trained,
            "version": self.version
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Saved recommendation model to {filepath}")
        return str(filepath)
