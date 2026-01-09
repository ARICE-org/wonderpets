"""
Soil Health Model

Machine learning model for soil health scoring.
Analyzes soil sensor data to produce health scores and identify deficiencies.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import joblib
import os

from apps.common.base.base_model import BaseMLModel
from apps.soil_service.core.constants import SOIL_OPTIMAL_RANGES, SOIL_PARAMETER_WEIGHTS


class SoilHealthModel(BaseMLModel):
    """
    Model for soil health scoring.
    
    Analyzes soil sensor data to produce health scores
    and identify deficiencies.
    """
    
    def __init__(self, version: str = "1.0"):
        super().__init__(model_name="soil_health", version=version)
        self.parameter_weights = SOIL_PARAMETER_WEIGHTS.copy()
        self.optimal_ranges = SOIL_OPTIMAL_RANGES.copy()
    
    def train(self, X, y, **kwargs) -> Dict[str, Any]:
        """
        Train the soil health scoring model.
        
        Args:
            X: Soil sensor data features
            y: Health scores or labels
            **kwargs: Additional parameters
            
        Returns:
            Training metrics
        """
        # TODO: Implement ML training logic
        self.is_trained = True
        self.metadata["training_samples"] = len(X) if hasattr(X, '__len__') else 0
        
        return {
            "mae": 0.0,
            "rmse": 0.0,
            "r2_score": 0.0,
            "training_samples": self.metadata["training_samples"]
        }
    
    def predict(self, X) -> Dict[str, Any]:
        """
        Predict soil health score.
        
        Args:
            X: Preprocessed soil data
            
        Returns:
            Dictionary with overall score and parameter breakdown
        """
        return self.calculate_health_score(X)
    
    def preprocess(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Preprocess soil sensor data.
        
        Args:
            data: Raw soil sensor readings
            
        Returns:
            Preprocessed data array
        """
        return np.array([data.get(k, 0) for k in self.parameter_weights.keys()])
    
    def calculate_health_score(self, soil_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate overall health score from soil parameters.
        
        Args:
            soil_data: Dictionary of soil parameter values
            
        Returns:
            Comprehensive health assessment
        """
        parameter_scores = {}
        deficiencies = []
        recommendations = []
        
        for param, weight in self.parameter_weights.items():
            if param in soil_data and soil_data[param] is not None:
                value = soil_data[param]
                ranges = self.optimal_ranges.get(param, {})
                
                score = self._calculate_parameter_score(value, ranges)
                parameter_scores[param] = {
                    "value": value,
                    "score": score,
                    "status": self._get_status(score),
                    "optimal_range": f"{ranges.get('min', 'N/A')} - {ranges.get('max', 'N/A')}"
                }
                
                if score < 60:
                    deficiency = self._identify_deficiency(param, value, ranges)
                    if deficiency:
                        deficiencies.append(deficiency)
                        recommendations.append(self._get_recommendation(param, value, ranges))
        
        total_weight = sum(
            self.parameter_weights[p] 
            for p in parameter_scores.keys() 
            if p in self.parameter_weights
        )
        
        overall_score = sum(
            parameter_scores[p]["score"] * self.parameter_weights[p]
            for p in parameter_scores.keys()
            if p in self.parameter_weights
        ) / total_weight if total_weight > 0 else 0
        
        return {
            "overall_score": round(overall_score, 2),
            "overall_status": self._get_status(overall_score),
            "parameter_scores": parameter_scores,
            "deficiencies": deficiencies,
            "recommendations": recommendations
        }
    
    def _calculate_parameter_score(
        self, 
        value: float, 
        ranges: Dict[str, float]
    ) -> float:
        """Calculate score for a single parameter."""
        if not ranges:
            return 50.0
        
        optimal = ranges.get("optimal", (ranges.get("min", 0) + ranges.get("max", 100)) / 2)
        min_val = ranges.get("min", 0)
        max_val = ranges.get("max", 100)
        
        if min_val <= value <= max_val:
            distance_from_optimal = abs(value - optimal)
            max_distance = max(optimal - min_val, max_val - optimal)
            score = 100 - (distance_from_optimal / max_distance * 30)
        else:
            if value < min_val:
                distance = min_val - value
                range_size = max_val - min_val
            else:
                distance = value - max_val
                range_size = max_val - min_val
            
            score = max(0, 70 - (distance / range_size * 70))
        
        return round(score, 2)
    
    def _get_status(self, score: float) -> str:
        """Get status label from score."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        elif score >= 20:
            return "Poor"
        else:
            return "Critical"
    
    def _identify_deficiency(
        self, 
        param: str, 
        value: float, 
        ranges: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """Identify deficiency for a parameter."""
        min_val = ranges.get("min", 0)
        max_val = ranges.get("max", 100)
        
        if value < min_val:
            return {
                "parameter": param,
                "type": "deficiency",
                "current_value": value,
                "required_minimum": min_val,
                "severity": "high" if value < min_val * 0.5 else "medium"
            }
        elif value > max_val:
            return {
                "parameter": param,
                "type": "excess",
                "current_value": value,
                "maximum_allowed": max_val,
                "severity": "high" if value > max_val * 1.5 else "medium"
            }
        return None
    
    def _get_recommendation(
        self, 
        param: str, 
        value: float, 
        ranges: Dict[str, float]
    ) -> str:
        """Get improvement recommendation for a parameter."""
        recommendations = {
            "ph": {
                "low": "Apply agricultural lime to increase soil pH",
                "high": "Apply sulfur or acidifying fertilizers to lower pH"
            },
            "nitrogen": {
                "low": "Apply nitrogen-rich fertilizers (urea, ammonium sulfate)",
                "high": "Reduce nitrogen application, consider cover crops"
            },
            "phosphorus": {
                "low": "Apply phosphate fertilizers (DAP, TSP)",
                "high": "Avoid phosphorus fertilizers, focus on other nutrients"
            },
            "potassium": {
                "low": "Apply potash fertilizers (MOP, SOP)",
                "high": "Reduce potassium application"
            },
            "organic_matter": {
                "low": "Add compost, green manure, or organic amendments",
                "high": "Organic matter level is good, maintain current practices"
            },
            "moisture": {
                "low": "Increase irrigation frequency or improve water retention",
                "high": "Improve drainage, reduce irrigation frequency"
            }
        }
        
        min_val = ranges.get("min", 0)
        direction = "low" if value < min_val else "high"
        
        return recommendations.get(param, {}).get(
            direction,
            f"Adjust {param} levels to be within optimal range"
        )
