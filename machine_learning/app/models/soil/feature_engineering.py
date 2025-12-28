"""
Feature Engineering for Soil Analysis

Creates features for soil health scoring and forecasting.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


class SoilFeatureEngineer:
    """
    Feature engineering for soil analysis models.
    
    Creates features including:
    - Nutrient ratios
    - Temporal patterns
    - Seasonal adjustments
    - Derived soil indicators
    """
    
    def __init__(self):
        self.feature_names: List[str] = []
        self.fitted = False
    
    def fit(self, data: pd.DataFrame) -> "SoilFeatureEngineer":
        """
        Fit the feature engineer on training data.
        
        Args:
            data: Training soil data
            
        Returns:
            Self for method chaining
        """
        # TODO: Compute normalization parameters, feature statistics
        self.fitted = True
        return self
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform soil data into features.
        
        Args:
            data: Raw soil sensor data
            
        Returns:
            DataFrame with engineered features
        """
        df = data.copy()
        
        # Create nutrient ratios
        df = self._create_nutrient_ratios(df)
        
        # Create soil quality indicators
        df = self._create_quality_indicators(df)
        
        # Create temporal features (for forecasting)
        df = self._create_temporal_features(df)
        
        # Create interaction features
        df = self._create_interaction_features(df)
        
        return df
    
    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform in one step."""
        return self.fit(data).transform(data)
    
    def _create_nutrient_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create nutrient ratio features."""
        # N:P ratio (optimal ~4:1 for rice)
        if "nitrogen" in df.columns and "phosphorus" in df.columns:
            df["n_p_ratio"] = df["nitrogen"] / df["phosphorus"].replace(0, np.nan)
        
        # N:K ratio
        if "nitrogen" in df.columns and "potassium" in df.columns:
            df["n_k_ratio"] = df["nitrogen"] / df["potassium"].replace(0, np.nan)
        
        # P:K ratio
        if "phosphorus" in df.columns and "potassium" in df.columns:
            df["p_k_ratio"] = df["phosphorus"] / df["potassium"].replace(0, np.nan)
        
        return df
    
    def _create_quality_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived soil quality indicators."""
        # Fertility index
        if all(col in df.columns for col in ["nitrogen", "phosphorus", "potassium"]):
            df["fertility_index"] = (
                df["nitrogen"] * 0.4 + 
                df["phosphorus"] * 0.3 + 
                df["potassium"] * 0.3
            )
        
        # pH deviation from optimal (6.0-6.5 for rice)
        if "ph" in df.columns:
            optimal_ph = 6.25
            df["ph_deviation"] = abs(df["ph"] - optimal_ph)
        
        # Moisture adequacy
        if "moisture" in df.columns:
            optimal_moisture = 60
            df["moisture_adequacy"] = 100 - abs(df["moisture"] - optimal_moisture)
        
        return df
    
    def _create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create temporal features for time series forecasting."""
        if "date" in df.columns or isinstance(df.index, pd.DatetimeIndex):
            date_col = df.index if isinstance(df.index, pd.DatetimeIndex) else pd.to_datetime(df["date"])
            
            df["day_of_year"] = date_col.dayofyear
            df["month"] = date_col.month
            df["week_of_year"] = date_col.isocalendar().week
            
            # Season encoding (for tropical rice farming)
            df["is_wet_season"] = df["month"].isin([6, 7, 8, 9, 10]).astype(int)
            df["is_dry_season"] = df["month"].isin([11, 12, 1, 2, 3, 4, 5]).astype(int)
        
        return df
    
    def _create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features between parameters."""
        # pH-nutrient interactions
        if "ph" in df.columns and "nitrogen" in df.columns:
            df["ph_nitrogen_interaction"] = df["ph"] * df["nitrogen"]
        
        # Moisture-organic matter interaction
        if "moisture" in df.columns and "organic_matter" in df.columns:
            df["moisture_om_interaction"] = df["moisture"] * df["organic_matter"]
        
        return df
    
    def get_feature_importance_mapping(self) -> Dict[str, str]:
        """Get human-readable descriptions for features."""
        return {
            "n_p_ratio": "Nitrogen to Phosphorus ratio",
            "n_k_ratio": "Nitrogen to Potassium ratio",
            "p_k_ratio": "Phosphorus to Potassium ratio",
            "fertility_index": "Overall soil fertility score",
            "ph_deviation": "pH deviation from optimal range",
            "moisture_adequacy": "Moisture level adequacy score",
            "is_wet_season": "Wet season indicator",
            "is_dry_season": "Dry season indicator"
        }
