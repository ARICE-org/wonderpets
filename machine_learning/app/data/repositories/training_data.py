"""
Training Data Repository

Repository for managing and preparing training data for ML models.
"""

from typing import Any, Dict, List, Optional, Tuple
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.data.connectors.database import DatabaseConnector

logger = logging.getLogger(__name__)


class TrainingDataRepository:
    """
    Repository for ML training data.
    
    Handles:
    - Data fetching and aggregation
    - Feature preparation
    - Train/test splitting
    - Data versioning
    """
    
    def __init__(self, db_connector: Optional[DatabaseConnector] = None):
        """
        Initialize training data repository.
        
        Args:
            db_connector: Database connector instance
        """
        self.db = db_connector or DatabaseConnector()
    
    def get_recommendation_training_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get training data for recommendation model.
        
        Combines:
        - Farming history with outcomes
        - Associated soil conditions
        - Weather during growing season
        - Rice variety information
        
        Args:
            start_date: Start date for data range
            end_date: End date for data range
            
        Returns:
            DataFrame with training features and labels
        """
        # Fetch farming history
        history = self.db.get_farming_history(limit=10000)
        
        if not history:
            logger.warning("No farming history data found")
            return pd.DataFrame()
        
        df = pd.DataFrame(history)
        
        # TODO: Join with soil data, weather data for each record
        # This would involve matching timestamps and locations
        
        logger.info(f"Prepared {len(df)} recommendation training samples")
        return df
    
    def get_weather_training_data(
        self,
        location_id: Optional[int] = None,
        lookback_days: int = 365
    ) -> pd.DataFrame:
        """
        Get training data for weather forecasting model.
        
        Args:
            location_id: Optional location filter
            lookback_days: Days of historical data to fetch
            
        Returns:
            DataFrame with weather time series
        """
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
        weather_data = self.db.get_weather_data(
            location_id=location_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not weather_data:
            logger.warning("No weather data found")
            return pd.DataFrame()
        
        df = pd.DataFrame(weather_data)
        
        # Convert timestamp to datetime
        if "recorded_at" in df.columns:
            df["recorded_at"] = pd.to_datetime(df["recorded_at"])
            df = df.set_index("recorded_at")
            df = df.sort_index()
        
        logger.info(f"Prepared {len(df)} weather training samples")
        return df
    
    def get_soil_training_data(
        self,
        farm_id: Optional[int] = None,
        lookback_days: int = 365
    ) -> pd.DataFrame:
        """
        Get training data for soil health model.
        
        Args:
            farm_id: Optional farm filter
            lookback_days: Days of historical data
            
        Returns:
            DataFrame with soil sensor time series
        """
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
        soil_data = self.db.get_soil_data(
            farm_id=farm_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not soil_data:
            logger.warning("No soil data found")
            return pd.DataFrame()
        
        df = pd.DataFrame(soil_data)
        
        # Convert timestamp to datetime
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.set_index("timestamp")
            df = df.sort_index()
        
        logger.info(f"Prepared {len(df)} soil training samples")
        return df
    
    def prepare_features_and_labels(
        self,
        df: pd.DataFrame,
        label_column: str,
        feature_columns: Optional[List[str]] = None,
        drop_na: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare features and labels for training.
        
        Args:
            df: Input DataFrame
            label_column: Name of the label/target column
            feature_columns: List of feature column names
            drop_na: Whether to drop rows with missing values
            
        Returns:
            Tuple of (features, labels, feature_names)
        """
        if drop_na:
            df = df.dropna()
        
        if feature_columns is None:
            feature_columns = [c for c in df.columns if c != label_column]
        
        # Filter to numeric columns
        numeric_cols = df[feature_columns].select_dtypes(include=[np.number]).columns.tolist()
        
        X = df[numeric_cols].values
        y = df[label_column].values
        
        return X, y, numeric_cols
    
    def split_train_test(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data into training and testing sets.
        
        Args:
            X: Features
            y: Labels
            test_size: Proportion for test set
            random_state: Random seed
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        try:
            from sklearn.model_selection import train_test_split
            return train_test_split(X, y, test_size=test_size, random_state=random_state)
        except ImportError:
            # Manual split if sklearn not available
            np.random.seed(random_state)
            indices = np.random.permutation(len(X))
            test_count = int(len(X) * test_size)
            
            test_idx = indices[:test_count]
            train_idx = indices[test_count:]
            
            return X[train_idx], X[test_idx], y[train_idx], y[test_idx]
    
    def split_time_series(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split time series data chronologically.
        
        Args:
            df: Time series DataFrame (index should be datetime)
            test_size: Proportion for test set
            
        Returns:
            Tuple of (train_df, test_df)
        """
        split_idx = int(len(df) * (1 - test_size))
        
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        return train_df, test_df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics for a dataset.
        
        Args:
            df: DataFrame to summarize
            
        Returns:
            Dictionary with summary statistics
        """
        return {
            "n_samples": len(df),
            "n_features": len(df.columns),
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_summary": df.describe().to_dict() if len(df) > 0 else {}
        }
