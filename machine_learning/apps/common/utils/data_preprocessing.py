"""
Generic data preprocessing utilities.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Generic data preprocessing utility class.
    
    Provides common preprocessing operations:
    - Normalization/Standardization
    - Missing value handling
    - Outlier detection and handling
    - Data type conversions
    """
    
    @staticmethod
    def normalize(
        data: np.ndarray,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> np.ndarray:
        """
        Normalize data to [0, 1] range.
        
        Args:
            data: Input array
            min_val: Optional minimum value (uses data min if not provided)
            max_val: Optional maximum value (uses data max if not provided)
            
        Returns:
            Normalized array
        """
        min_val = min_val if min_val is not None else np.min(data)
        max_val = max_val if max_val is not None else np.max(data)
        
        if max_val == min_val:
            return np.zeros_like(data)
        
        return (data - min_val) / (max_val - min_val)
    
    @staticmethod
    def standardize(
        data: np.ndarray,
        mean: Optional[float] = None,
        std: Optional[float] = None
    ) -> np.ndarray:
        """
        Standardize data to zero mean and unit variance.
        
        Args:
            data: Input array
            mean: Optional mean (uses data mean if not provided)
            std: Optional standard deviation (uses data std if not provided)
            
        Returns:
            Standardized array
        """
        mean = mean if mean is not None else np.mean(data)
        std = std if std is not None else np.std(data)
        
        if std == 0:
            return np.zeros_like(data)
        
        return (data - mean) / std
    
    @staticmethod
    def handle_missing_values(
        data: Dict[str, Any],
        strategy: str = "mean",
        fill_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Handle missing values in a dictionary of data.
        
        Args:
            data: Dictionary with potentially missing values
            strategy: How to handle missing values ('mean', 'median', 'fill', 'drop')
            fill_value: Value to use when strategy is 'fill'
            
        Returns:
            Dictionary with missing values handled
        """
        result = {}
        
        for key, value in data.items():
            if value is None:
                if strategy == "fill" and fill_value is not None:
                    result[key] = fill_value
                elif strategy == "drop":
                    continue
                else:
                    result[key] = 0.0
            elif isinstance(value, (list, np.ndarray)):
                arr = np.array(value)
                mask = np.isnan(arr) | (arr is None)
                if np.any(mask):
                    if strategy == "mean":
                        fill = np.nanmean(arr)
                    elif strategy == "median":
                        fill = np.nanmedian(arr)
                    elif strategy == "fill":
                        fill = fill_value if fill_value is not None else 0.0
                    else:
                        fill = 0.0
                    arr[mask] = fill
                result[key] = arr.tolist() if isinstance(value, list) else arr
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def detect_outliers(
        data: np.ndarray,
        method: str = "iqr",
        threshold: float = 1.5
    ) -> np.ndarray:
        """
        Detect outliers in data.
        
        Args:
            data: Input array
            method: Detection method ('iqr', 'zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            Boolean mask where True indicates outlier
        """
        if method == "iqr":
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            return (data < lower) | (data > upper)
        elif method == "zscore":
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return np.zeros(len(data), dtype=bool)
            z_scores = np.abs((data - mean) / std)
            return z_scores > threshold
        else:
            raise ValueError(f"Unknown method: {method}")
    
    @staticmethod
    def clip_outliers(
        data: np.ndarray,
        lower_percentile: float = 1,
        upper_percentile: float = 99
    ) -> np.ndarray:
        """
        Clip outliers to percentile bounds.
        
        Args:
            data: Input array
            lower_percentile: Lower percentile for clipping
            upper_percentile: Upper percentile for clipping
            
        Returns:
            Clipped array
        """
        lower = np.percentile(data, lower_percentile)
        upper = np.percentile(data, upper_percentile)
        return np.clip(data, lower, upper)
