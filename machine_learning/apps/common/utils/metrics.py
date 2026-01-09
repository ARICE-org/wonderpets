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
    
    # =========================================================================
    # Classification Metrics
    # =========================================================================
    
    @staticmethod
    def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate accuracy score."""
        if len(y_true) == 0:
            return 0.0
        return float(np.mean(y_true == y_pred))
    
    @staticmethod
    def precision(
        y_true: np.ndarray, 
        y_pred: np.ndarray, 
        average: str = "weighted"
    ) -> float:
        """Calculate precision score."""
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
        """Calculate recall score."""
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
        """Calculate F1 score."""
        try:
            from sklearn.metrics import f1_score
            return f1_score(y_true, y_pred, average=average, zero_division=0)
        except ImportError:
            logger.warning("sklearn not available, returning 0")
            return 0.0
    
    # =========================================================================
    # Regression Metrics
    # =========================================================================
    
    @staticmethod
    def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Squared Error."""
        return float(np.mean((y_true - y_pred) ** 2))
    
    @staticmethod
    def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Root Mean Squared Error."""
        return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    
    @staticmethod
    def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Absolute Error."""
        return float(np.mean(np.abs(y_true - y_pred)))
    
    @staticmethod
    def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Absolute Percentage Error."""
        mask = y_true != 0
        if not np.any(mask):
            return 0.0
        return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)
    
    @staticmethod
    def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate R-squared (coefficient of determination)."""
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        if ss_tot == 0:
            return 0.0
        return float(1 - (ss_res / ss_tot))
    
    # =========================================================================
    # Convenience Methods
    # =========================================================================
    
    @classmethod
    def get_regression_metrics(
        cls, 
        y_true: np.ndarray, 
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """Get all regression metrics in one call."""
        return {
            "mse": cls.mse(y_true, y_pred),
            "rmse": cls.rmse(y_true, y_pred),
            "mae": cls.mae(y_true, y_pred),
            "mape": cls.mape(y_true, y_pred),
            "r2": cls.r2_score(y_true, y_pred),
        }
    
    @classmethod
    def get_classification_metrics(
        cls, 
        y_true: np.ndarray, 
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """Get all classification metrics in one call."""
        return {
            "accuracy": cls.accuracy(y_true, y_pred),
            "precision": cls.precision(y_true, y_pred),
            "recall": cls.recall(y_true, y_pred),
            "f1": cls.f1_score(y_true, y_pred),
        }
