"""
Abstract base class for all ML models in the ARICE system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import joblib
import os


class BaseMLModel(ABC):
    """
    Abstract base class for all machine learning models.
    
    All models must implement train, predict, save, and load methods.
    """
    
    def __init__(self, model_name: str, version: str = "1.0"):
        self.model_name = model_name
        self.version = version
        self.model = None
        self.is_trained = False
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def train(self, X, y, **kwargs) -> Dict[str, Any]:
        """
        Train the model on the provided data.
        
        Args:
            X: Training features
            y: Training labels/targets
            **kwargs: Additional training parameters
            
        Returns:
            Dictionary containing training metrics
        """
        pass
    
    @abstractmethod
    def predict(self, X) -> Any:
        """
        Make predictions on new data.
        
        Args:
            X: Input features for prediction
            
        Returns:
            Model predictions
        """
        pass
    
    @abstractmethod
    def preprocess(self, data: Any) -> Any:
        """
        Preprocess input data before prediction.
        
        Args:
            data: Raw input data
            
        Returns:
            Preprocessed data ready for model input
        """
        pass
    
    def save(self, path: str, filename: Optional[str] = None) -> str:
        """
        Save the trained model to disk.
        
        Args:
            path: Directory path to save the model
            filename: Optional custom filename (defaults to model_name_version.pkl)
            
        Returns:
            Full path to the saved model file
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        os.makedirs(path, exist_ok=True)
        
        if filename is None:
            filename = f"{self.model_name}_v{self.version}.pkl"
        
        filepath = os.path.join(path, filename)
        
        model_data = {
            "model": self.model,
            "model_name": self.model_name,
            "version": self.version,
            "metadata": self.metadata,
            "is_trained": self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        return filepath
    
    def load(self, path: str) -> None:
        """
        Load a trained model from disk.
        
        Args:
            path: Path to the model file
        """
        model_data = joblib.load(path)
        
        self.model = model_data["model"]
        self.model_name = model_data.get("model_name", self.model_name)
        self.version = model_data.get("version", self.version)
        self.metadata = model_data.get("metadata", {})
        self.is_trained = model_data.get("is_trained", True)
    
    def get_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model_name": self.model_name,
            "version": self.version,
            "is_trained": self.is_trained,
            "metadata": self.metadata
        }
