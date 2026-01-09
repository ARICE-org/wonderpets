"""
Generic feature engineering utilities.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Generic feature engineering utility class.
    
    Provides common feature engineering operations:
    - Temporal features extraction
    - Statistical aggregations
    - Rolling window features
    - Encoding utilities
    """
    
    # =========================================================================
    # Temporal Features
    # =========================================================================
    
    @staticmethod
    def extract_date_features(date: datetime) -> Dict[str, int]:
        """
        Extract temporal features from a datetime.
        
        Args:
            date: Input datetime
            
        Returns:
            Dictionary of temporal features
        """
        return {
            "year": date.year,
            "month": date.month,
            "day": date.day,
            "day_of_week": date.weekday(),
            "day_of_year": date.timetuple().tm_yday,
            "week_of_year": date.isocalendar()[1],
            "quarter": (date.month - 1) // 3 + 1,
            "is_weekend": 1 if date.weekday() >= 5 else 0,
        }
    
    @staticmethod
    def get_season(month: int, hemisphere: str = "northern") -> str:
        """
        Get season from month.
        
        Args:
            month: Month number (1-12)
            hemisphere: 'northern' or 'southern'
            
        Returns:
            Season name
        """
        if hemisphere == "northern":
            if month in [12, 1, 2]:
                return "winter"
            elif month in [3, 4, 5]:
                return "spring"
            elif month in [6, 7, 8]:
                return "summer"
            else:
                return "autumn"
        else:
            if month in [12, 1, 2]:
                return "summer"
            elif month in [3, 4, 5]:
                return "autumn"
            elif month in [6, 7, 8]:
                return "winter"
            else:
                return "spring"
    
    @staticmethod
    def get_philippines_season(month: int) -> str:
        """
        Get Philippines wet/dry season from month.
        
        Args:
            month: Month number (1-12)
            
        Returns:
            'wet' or 'dry'
        """
        # Wet season: June to November
        # Dry season: December to May
        if month in [6, 7, 8, 9, 10, 11]:
            return "wet"
        return "dry"
    
    # =========================================================================
    # Statistical Aggregations
    # =========================================================================
    
    @staticmethod
    def calculate_statistics(values: np.ndarray) -> Dict[str, float]:
        """
        Calculate statistical features from an array.
        
        Args:
            values: Input array
            
        Returns:
            Dictionary of statistics
        """
        if len(values) == 0:
            return {
                "mean": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "median": 0.0,
                "count": 0,
            }
        
        return {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "median": float(np.median(values)),
            "count": len(values),
        }
    
    @staticmethod
    def calculate_trend(values: np.ndarray) -> str:
        """
        Determine trend direction from values.
        
        Args:
            values: Time-ordered values
            
        Returns:
            'increasing', 'decreasing', or 'stable'
        """
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        threshold = np.std(values) * 0.1  # 10% of std as threshold
        
        if slope > threshold:
            return "increasing"
        elif slope < -threshold:
            return "decreasing"
        return "stable"
    
    # =========================================================================
    # Rolling Window Features
    # =========================================================================
    
    @staticmethod
    def rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
        """Calculate rolling mean."""
        if len(values) < window:
            return np.array([np.mean(values)] * len(values))
        
        result = np.convolve(values, np.ones(window) / window, mode="valid")
        # Pad beginning with first valid value
        padding = np.full(window - 1, result[0])
        return np.concatenate([padding, result])
    
    @staticmethod
    def rolling_std(values: np.ndarray, window: int) -> np.ndarray:
        """Calculate rolling standard deviation."""
        result = []
        for i in range(len(values)):
            start = max(0, i - window + 1)
            result.append(np.std(values[start:i + 1]))
        return np.array(result)
    
    # =========================================================================
    # Encoding
    # =========================================================================
    
    @staticmethod
    def one_hot_encode(
        value: str, 
        categories: List[str]
    ) -> Dict[str, int]:
        """
        One-hot encode a categorical value.
        
        Args:
            value: Value to encode
            categories: List of all possible categories
            
        Returns:
            Dictionary with one-hot encoding
        """
        return {cat: 1 if cat == value else 0 for cat in categories}
    
    @staticmethod
    def cyclical_encode(value: int, max_value: int) -> Tuple[float, float]:
        """
        Encode cyclical features (e.g., month, day of week) using sin/cos.
        
        Args:
            value: Current value (0-indexed)
            max_value: Maximum value in cycle
            
        Returns:
            Tuple of (sin, cos) encoding
        """
        angle = 2 * np.pi * value / max_value
        return float(np.sin(angle)), float(np.cos(angle))
