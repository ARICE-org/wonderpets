"""
Data Preprocessing for Weather Forecasting

Handles weather data cleaning and preparation for time series models.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class WeatherDataPreprocessor:
    """
    Data preprocessing pipeline for weather forecasting.
    
    Handles:
    - Missing value interpolation (time series appropriate)
    - Outlier detection for weather data
    - Data resampling and alignment
    - Normalization for neural network models
    """
    
    def __init__(self):
        self.scalers: Dict[str, Any] = {}
        self.fitted = False
        self.columns_stats: Dict[str, Dict[str, float]] = {}
    
    def fit(self, data: pd.DataFrame) -> "WeatherDataPreprocessor":
        """
        Fit preprocessing transformers on training data.
        
        Args:
            data: Training time series DataFrame
            
        Returns:
            Self for method chaining
        """
        # TODO: Compute statistics for scaling and imputation
        for col in data.select_dtypes(include=[np.number]).columns:
            self.columns_stats[col] = {
                "mean": data[col].mean(),
                "std": data[col].std(),
                "min": data[col].min(),
                "max": data[col].max()
            }
        
        self.fitted = True
        return self
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply preprocessing transformations.
        
        Args:
            data: Input time series DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        if not self.fitted:
            raise ValueError("Preprocessor must be fitted before transform")
        
        df = data.copy()
        
        # Ensure datetime index
        df = self._ensure_datetime_index(df)
        
        # Handle missing values (time series interpolation)
        df = self._interpolate_missing(df)
        
        # Handle outliers
        df = self._handle_outliers(df)
        
        # Normalize values
        df = self._normalize(df)
        
        return df
    
    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform in one step."""
        return self.fit(data).transform(data)
    
    def inverse_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Reverse normalization for predictions."""
        # TODO: Implement inverse transformation
        return data
    
    def _ensure_datetime_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure DataFrame has proper datetime index."""
        if not isinstance(df.index, pd.DatetimeIndex):
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df = df.set_index("date")
            elif "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.set_index("timestamp")
        return df
    
    def _interpolate_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Interpolate missing values using time series methods."""
        # TODO: Implement time-aware interpolation
        # Strategy: linear interpolation, forward/backward fill
        return df.interpolate(method="time").fillna(method="bfill").fillna(method="ffill")
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle outliers in weather data."""
        # TODO: Implement weather-specific outlier handling
        # Consider physical constraints (e.g., temperature range)
        return df
    
    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize numerical columns."""
        # TODO: Apply normalization using fitted statistics
        return df
    
    def validate_weather_data(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate weather data for physical constraints.
        
        Args:
            data: Weather DataFrame
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check temperature ranges
        if "temperature_max" in data.columns:
            if data["temperature_max"].max() > 50:
                warnings.append("Unusually high maximum temperature detected")
        
        # Check rainfall
        if "rainfall" in data.columns:
            if (data["rainfall"] < 0).any():
                warnings.append("Negative rainfall values detected")
        
        # Check humidity
        if "humidity" in data.columns:
            if ((data["humidity"] < 0) | (data["humidity"] > 100)).any():
                warnings.append("Humidity values outside 0-100 range")
        
        return len(warnings) == 0, warnings
