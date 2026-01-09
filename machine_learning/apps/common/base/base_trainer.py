"""
Abstract base class for model trainers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseTrainer(ABC):
    """
    Abstract base class for model training pipelines.
    
    Provides common functionality for:
    - Data loading and preprocessing
    - Train/test splitting
    - Model training and evaluation
    - Model saving
    """
    
    def __init__(self, trainer_name: str, output_path: str):
        self.trainer_name = trainer_name
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def load_data(self, data_path: str) -> Any:
        """
        Load training data from disk.
        
        Args:
            data_path: Path to data file(s)
            
        Returns:
            Loaded data (format depends on implementation)
        """
        pass
    
    @abstractmethod
    def preprocess_data(self, data: Any) -> Tuple[Any, Any]:
        """
        Preprocess data for training.
        
        Args:
            data: Raw loaded data
            
        Returns:
            Tuple of (features, targets)
        """
        pass
    
    @abstractmethod
    def train(self, X, y, **kwargs) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            X: Training features
            y: Training targets
            **kwargs: Additional parameters
            
        Returns:
            Training metrics
        """
        pass
    
    @abstractmethod
    def evaluate(self, X, y) -> Dict[str, float]:
        """
        Evaluate the trained model.
        
        Args:
            X: Test features
            y: Test targets
            
        Returns:
            Evaluation metrics
        """
        pass
    
    def run_pipeline(
        self,
        data_path: str,
        test_size: float = 0.2,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run the complete training pipeline.
        
        Args:
            data_path: Path to training data
            test_size: Fraction of data for testing
            **kwargs: Additional training parameters
            
        Returns:
            Dictionary with training and evaluation results
        """
        logger.info(f"Starting training pipeline: {self.trainer_name}")
        
        # Load data
        logger.info("Loading data...")
        data = self.load_data(data_path)
        
        # Preprocess
        logger.info("Preprocessing data...")
        X, y = self.preprocess_data(data)
        
        # Split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Train
        logger.info("Training model...")
        train_metrics = self.train(X_train, y_train, **kwargs)
        
        # Evaluate
        logger.info("Evaluating model...")
        eval_metrics = self.evaluate(X_test, y_test)
        
        logger.info(f"Training complete. Metrics: {eval_metrics}")
        
        return {
            "train_metrics": train_metrics,
            "eval_metrics": eval_metrics,
            "data_info": {
                "total_samples": len(X),
                "train_samples": len(X_train),
                "test_samples": len(X_test)
            }
        }
