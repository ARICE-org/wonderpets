"""
Model Metrics Utility

Functions for calculating and tracking ML model performance metrics.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ModelMetrics:
    """
    Utility class for calculating model performance metrics.
    
    Supports metrics for:
    - Classification models (recommendation)
    - Regression models (forecasting)
    - Time series models (weather, soil forecast)
    """
    
    # Classification Metrics
    
    @staticmethod
    def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate accuracy score.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            
        Returns:
            Accuracy score (0-1)
        """
        if len(y_true) == 0:
            return 0.0
        return np.mean(y_true == y_pred)
    
    @staticmethod
    def precision(
        y_true: np.ndarray, 
        y_pred: np.ndarray, 
        average: str = "weighted"
    ) -> float:
        """
        Calculate precision score.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            average: Averaging method (weighted, macro, micro)
            
        Returns:
            Precision score
        """
        try:
            from sklearn.metrics import precision_score
            return precision_score(y_true, y_pred, average=average, zero_division=0)
        except ImportError:
            logger.warning("sklearn not available, returning 0")
            return 0.0
    
    @staticmethod
    def recall(
        y_true: np.ndarray, 
        y_pred: np.ndarray, 
        average: str = "weighted"
    ) -> float:
        """
        Calculate recall score.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            average: Averaging method
            
        Returns:
            Recall score
        """
        try:
            from sklearn.metrics import recall_score
            return recall_score(y_true, y_pred, average=average, zero_division=0)
        except ImportError:
            logger.warning("sklearn not available, returning 0")
            return 0.0
    
    @staticmethod
    def f1_score(
        y_true: np.ndarray, 
        y_pred: np.ndarray, 
        average: str = "weighted"
    ) -> float:
        """
        Calculate F1 score.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            average: Averaging method
            
        Returns:
            F1 score
        """
        try:
            from sklearn.metrics import f1_score
            return f1_score(y_true, y_pred, average=average, zero_division=0)
        except ImportError:
            logger.warning("sklearn not available, returning 0")
            return 0.0
    
    # Regression Metrics
    
    @staticmethod
    def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate Mean Absolute Error.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            MAE value
        """
        if len(y_true) == 0:
            return 0.0
        return np.mean(np.abs(y_true - y_pred))
    
    @staticmethod
    def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate Mean Squared Error.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            MSE value
        """
        if len(y_true) == 0:
            return 0.0
        return np.mean((y_true - y_pred) ** 2)
    
    @staticmethod
    def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate Root Mean Squared Error.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            RMSE value
        """
        return np.sqrt(ModelMetrics.mse(y_true, y_pred))
    
    @staticmethod
    def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate Mean Absolute Percentage Error.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            MAPE value (percentage)
        """
        if len(y_true) == 0:
            return 0.0
        
        # Avoid division by zero
        mask = y_true != 0
        if not np.any(mask):
            return 0.0
        
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    @staticmethod
    def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate R-squared (coefficient of determination).
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            R² score
        """
        if len(y_true) == 0:
            return 0.0
        
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        
        if ss_tot == 0:
            return 0.0
        
        return 1 - (ss_res / ss_tot)
    
    # Comprehensive Evaluation
    
    @classmethod
    def evaluate_classification(
        cls,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        class_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation for classification models.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            class_names: Optional list of class names
            
        Returns:
            Dictionary of metrics
        """
        return {
            "accuracy": cls.accuracy(y_true, y_pred),
            "precision_weighted": cls.precision(y_true, y_pred, "weighted"),
            "recall_weighted": cls.recall(y_true, y_pred, "weighted"),
            "f1_weighted": cls.f1_score(y_true, y_pred, "weighted"),
            "precision_macro": cls.precision(y_true, y_pred, "macro"),
            "recall_macro": cls.recall(y_true, y_pred, "macro"),
            "f1_macro": cls.f1_score(y_true, y_pred, "macro"),
            "n_samples": len(y_true)
        }
    
    @classmethod
    def evaluate_regression(
        cls,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Comprehensive evaluation for regression models.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of metrics
        """
        return {
            "mae": cls.mae(y_true, y_pred),
            "mse": cls.mse(y_true, y_pred),
            "rmse": cls.rmse(y_true, y_pred),
            "mape": cls.mape(y_true, y_pred),
            "r2": cls.r2_score(y_true, y_pred),
            "n_samples": len(y_true)
        }
    
    @classmethod
    def evaluate_time_series(
        cls,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        horizon: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluation for time series forecasting models.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            horizon: Forecast horizon (for horizon-specific metrics)
            
        Returns:
            Dictionary of metrics
        """
        metrics = cls.evaluate_regression(y_true, y_pred)
        
        # Add time-series specific metrics
        if len(y_true) > 1:
            # Direction accuracy (did we predict the trend correctly?)
            true_direction = np.sign(np.diff(y_true))
            pred_direction = np.sign(np.diff(y_pred))
            metrics["direction_accuracy"] = np.mean(true_direction == pred_direction)
        
        if horizon:
            metrics["forecast_horizon"] = horizon
        
        return metrics
    
    @staticmethod
    def format_metrics(metrics: Dict[str, Any], precision: int = 4) -> Dict[str, Any]:
        """
        Format metrics for display/storage.
        
        Args:
            metrics: Dictionary of metrics
            precision: Decimal precision for floats
            
        Returns:
            Formatted metrics dictionary
        """
        formatted = {}
        
        for key, value in metrics.items():
            if isinstance(value, float):
                formatted[key] = round(value, precision)
            else:
                formatted[key] = value
        
        return formatted
