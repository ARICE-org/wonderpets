"""
Data Preprocessing for Soil Analysis

Handles soil sensor data cleaning and preparation.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class SoilDataPreprocessor:
    """
    Data preprocessing pipeline for soil analysis.
    
    Handles:
    - Sensor data validation
    - Missing value imputation
    - Outlier detection and handling
    - Unit conversions
    - Data normalization
    """
    
    # Valid ranges for soil parameters (for data validation)
    VALID_RANGES = {
        "ph": {"min": 0, "max": 14},
        "nitrogen": {"min": 0, "max": 200},  # kg/ha
        "phosphorus": {"min": 0, "max": 100},  # kg/ha
        "potassium": {"min": 0, "max": 200},  # kg/ha
        "organic_matter": {"min": 0, "max": 15},  # percentage
        "moisture": {"min": 0, "max": 100},  # percentage
        "temperature": {"min": -10, "max": 50}  # celsius
    }
    
    def __init__(self):
        self.scalers: Dict[str, Any] = {}
        self.imputers: Dict[str, Any] = {}
        self.fitted = False
        self.column_statistics: Dict[str, Dict[str, float]] = {}
    
    def fit(self, data: pd.DataFrame) -> "SoilDataPreprocessor":
        """
        Fit preprocessing transformers on training data.
        
        Args:
            data: Training soil data DataFrame
            
        Returns:
            Self for method chaining
        """
        # Compute statistics for each column
        for col in data.select_dtypes(include=[np.number]).columns:
            self.column_statistics[col] = {
                "mean": data[col].mean(),
                "std": data[col].std(),
                "median": data[col].median(),
                "min": data[col].min(),
                "max": data[col].max(),
                "q1": data[col].quantile(0.25),
                "q3": data[col].quantile(0.75)
            }
        
        self.fitted = True
        return self
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply preprocessing transformations.
        
        Args:
            data: Input soil data DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        if not self.fitted:
            raise ValueError("Preprocessor must be fitted before transform")
        
        df = data.copy()
        
        # Validate data ranges
        df = self._validate_ranges(df)
        
        # Handle missing values
        df = self._impute_missing(df)
        
        # Handle outliers
        df = self._handle_outliers(df)
        
        # Normalize values
        df = self._normalize(df)
        
        return df
    
    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform in one step."""
        return self.fit(data).transform(data)
    
    def inverse_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Reverse normalization for interpretable results."""
        df = data.copy()
        
        for col in df.select_dtypes(include=[np.number]).columns:
            if col in self.column_statistics:
                stats = self.column_statistics[col]
                # Reverse standard scaling
                df[col] = df[col] * stats["std"] + stats["mean"]
        
        return df
    
    def _validate_ranges(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clip values to valid ranges."""
        for col, ranges in self.VALID_RANGES.items():
            if col in df.columns:
                # Log warnings for out-of-range values
                out_of_range = (df[col] < ranges["min"]) | (df[col] > ranges["max"])
                if out_of_range.any():
                    # TODO: Add logging
                    pass
                
                # Clip to valid range
                df[col] = df[col].clip(lower=ranges["min"], upper=ranges["max"])
        
        return df
    
    def _impute_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values."""
        for col in df.select_dtypes(include=[np.number]).columns:
            if col in self.column_statistics:
                # Use median for imputation (robust to outliers)
                df[col] = df[col].fillna(self.column_statistics[col]["median"])
            else:
                df[col] = df[col].fillna(df[col].median())
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and handle outliers using IQR method."""
        for col in df.select_dtypes(include=[np.number]).columns:
            if col in self.column_statistics:
                stats = self.column_statistics[col]
                iqr = stats["q3"] - stats["q1"]
                lower_bound = stats["q1"] - 1.5 * iqr
                upper_bound = stats["q3"] + 1.5 * iqr
                
                # Clip outliers to bounds
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        return df
    
    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize numerical columns using standard scaling."""
        for col in df.select_dtypes(include=[np.number]).columns:
            if col in self.column_statistics:
                stats = self.column_statistics[col]
                if stats["std"] > 0:
                    df[col] = (df[col] - stats["mean"]) / stats["std"]
        
        return df
    
    def validate_sensor_reading(
        self, 
        reading: Dict[str, float]
    ) -> Tuple[bool, List[str]]:
        """
        Validate a single sensor reading.
        
        Args:
            reading: Dictionary of sensor values
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        for param, value in reading.items():
            if param in self.VALID_RANGES:
                ranges = self.VALID_RANGES[param]
                if value < ranges["min"] or value > ranges["max"]:
                    errors.append(
                        f"{param} value {value} is outside valid range "
                        f"[{ranges['min']}, {ranges['max']}]"
                    )
            
            if value is None or (isinstance(value, float) and np.isnan(value)):
                errors.append(f"{param} has missing or invalid value")
        
        return len(errors) == 0, errors
    
    def prepare_for_health_scoring(
        self, 
        data: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Prepare sensor data for health scoring (no normalization).
        
        Args:
            data: Raw sensor readings
            
        Returns:
            Cleaned data ready for health scoring
        """
        cleaned = {}
        
        for param, value in data.items():
            if param in self.VALID_RANGES:
                ranges = self.VALID_RANGES[param]
                # Clip to valid range
                cleaned[param] = max(ranges["min"], min(value, ranges["max"]))
            else:
                cleaned[param] = value
        
        return cleaned
