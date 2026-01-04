"""
Training Script: Soil Forecast Model

This script trains the 3-month (90-120 day) soil forecasting model
aligned with rice planting seasons and growth stages.

Usage:
    python train_soil_forecast.py --data-source database
    python train_soil_forecast.py --data-source csv --data-path data/soil_timeseries.csv
"""

import argparse
import os
import sys
import logging
from datetime import datetime
import json

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.connectors.database import DatabaseConnector
from app.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Rice growth stages (days from planting)
RICE_GROWTH_STAGES = {
    'seedling': {
        'start': 0, 
        'end': 15, 
        'critical_nutrients': ['nitrogen', 'phosphorus'],
        'description': 'Initial growth phase requiring strong root development'
    },
    'tillering': {
        'start': 15, 
        'end': 45, 
        'critical_nutrients': ['nitrogen', 'potassium'],
        'description': 'Vegetative growth with tiller development'
    },
    'panicle_initiation': {
        'start': 45, 
        'end': 70, 
        'critical_nutrients': ['phosphorus', 'potassium'],
        'description': 'Reproductive stage initiation'
    },
    'flowering': {
        'start': 70, 
        'end': 90, 
        'critical_nutrients': ['potassium', 'nitrogen'],
        'description': 'Flowering and pollination phase'
    },
    'grain_filling': {
        'start': 90, 
        'end': 120, 
        'critical_nutrients': ['potassium', 'phosphorus'],
        'description': 'Grain development and maturation'
    }
}

FORECAST_DAYS = 120  # Full rice growing season


class SoilForecastModelTrainer:
    """Trainer for soil 3-month forecasting model."""
    
    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'trained_models', 'soil'
        )
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.soil_params = ['ph', 'nitrogen', 'phosphorus', 'potassium', 'moisture']
        self.forecast_horizons = [30, 60, 90, 120]  # Days ahead
        
        self.model = None
        self.scaler = StandardScaler()
        self.feature_cols = None
        
    def load_data_from_database(self) -> pd.DataFrame:
        """Load historical soil data with timestamps."""
        logger.info("Loading data from database...")
        
        db = DatabaseConnector()
        
        query = """
        SELECT 
            sd.created_at as date,
            sd.ph, sd.nitrogen, sd.phosphorus, sd.potassium, sd.moisture,
            wd.temperature, wd.humidity, wd.rainfall
        FROM soil_data sd
        LEFT JOIN weather_data wd ON DATE(sd.created_at) = DATE(wd.date)
        ORDER BY sd.created_at
        """
        
        with db.engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        df['date'] = pd.to_datetime(df['date'])
        logger.info(f"Loaded {len(df)} records from database")
        logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
        
        return df
    
    def load_data_from_csv(self, filepath: str) -> pd.DataFrame:
        """Load soil data from CSV file."""
        logger.info(f"Loading data from {filepath}...")
        df = pd.read_csv(filepath, parse_dates=['date'])
        logger.info(f"Loaded {len(df)} records from CSV")
        return df
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time series features for forecasting."""
        logger.info("Creating time series features...")
        
        df = df.sort_values('date').copy()
        
        # Time-based features
        df['day_of_year'] = df['date'].dt.dayofyear
        df['month'] = df['date'].dt.month
        df['week'] = df['date'].dt.isocalendar().week.astype(int)
        
        # Lag features
        for param in self.soil_params:
            df[f'{param}_lag7'] = df[param].shift(7)
            df[f'{param}_lag14'] = df[param].shift(14)
            df[f'{param}_lag30'] = df[param].shift(30)
            df[f'{param}_rolling_mean_7'] = df[param].rolling(window=7).mean()
            df[f'{param}_rolling_std_7'] = df[param].rolling(window=7).std()
            df[f'{param}_rolling_mean_30'] = df[param].rolling(window=30).mean()
        
        # Create target variables (future soil values)
        for horizon in self.forecast_horizons:
            for param in self.soil_params:
                df[f'{param}_future_{horizon}d'] = df[param].shift(-horizon)
        
        # Drop rows with NaN
        df = df.dropna()
        
        logger.info(f"Created features. Final shape: {df.shape}")
        
        return df
    
    def prepare_training_data(self, df: pd.DataFrame, horizon: int = 90):
        """Prepare features and targets for training."""
        # Define feature columns
        self.feature_cols = (
            self.soil_params +
            ['temperature', 'humidity', 'rainfall', 'day_of_year', 'month'] +
            [f'{p}_lag7' for p in self.soil_params] +
            [f'{p}_lag30' for p in self.soil_params] +
            [f'{p}_rolling_mean_7' for p in self.soil_params] +
            [f'{p}_rolling_mean_30' for p in self.soil_params]
        )
        
        # Filter to only existing columns
        self.feature_cols = [c for c in self.feature_cols if c in df.columns]
        
        # Target columns
        target_cols = [f'{p}_future_{horizon}d' for p in self.soil_params]
        
        X = df[self.feature_cols].fillna(df[self.feature_cols].mean())
        y = df[target_cols].fillna(df[target_cols].mean())
        
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Targets shape: {y.shape}")
        
        return X, y, target_cols
    
    def train(self, X, y, target_cols):
        """Train the multi-output forecasting model."""
        logger.info("Training soil forecast model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train multi-output regressor
        base_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        self.model = MultiOutputRegressor(base_model)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        
        metrics = {}
        print("\n90-Day Forecast Performance:")
        print("=" * 50)
        
        for i, param in enumerate(self.soil_params):
            mae = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
            rmse = np.sqrt(mean_squared_error(y_test.iloc[:, i], y_pred[:, i]))
            r2 = r2_score(y_test.iloc[:, i], y_pred[:, i])
            
            metrics[param] = {
                'mae': float(mae),
                'rmse': float(rmse),
                'r2': float(r2)
            }
            
            print(f"{param.capitalize():15} - MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}")
        
        return metrics
    
    def save_model(self, metrics: dict, target_cols: list):
        """Save trained model and configuration."""
        logger.info(f"Saving model to {self.model_dir}...")
        
        # Save model and scaler
        joblib.dump(self.model, os.path.join(self.model_dir, 'soil_forecast_model.pkl'))
        joblib.dump(self.scaler, os.path.join(self.model_dir, 'forecast_scaler.pkl'))
        
        # Save configuration
        config = {
            'feature_columns': self.feature_cols,
            'target_columns': target_cols,
            'soil_parameters': self.soil_params,
            'forecast_days': FORECAST_DAYS,
            'forecast_horizons': self.forecast_horizons,
            'rice_growth_stages': RICE_GROWTH_STAGES,
            'metrics': metrics
        }
        
        with open(os.path.join(self.model_dir, 'forecast_config.json'), 'w') as f:
            json.dump(config, f, indent=2, default=str)
        
        # Save metadata
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'model_type': 'MultiOutputRegressor(GradientBoostingRegressor)',
            'purpose': 'Soil 3-month forecast aligned with rice growth stages'
        }
        
        with open(os.path.join(self.model_dir, 'forecast_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Model saved successfully!")


def main():
    parser = argparse.ArgumentParser(description='Train soil 3-month forecast model')
    parser.add_argument(
        '--data-source',
        choices=['database', 'csv'],
        default='database',
        help='Source of training data'
    )
    parser.add_argument(
        '--data-path',
        type=str,
        help='Path to CSV file (required if data-source is csv)'
    )
    parser.add_argument(
        '--forecast-horizon',
        type=int,
        default=90,
        help='Days ahead to forecast (default: 90)'
    )
    parser.add_argument(
        '--model-dir',
        type=str,
        help='Directory to save trained model'
    )
    
    args = parser.parse_args()
    
    trainer = SoilForecastModelTrainer(model_dir=args.model_dir)
    
    # Load data
    if args.data_source == 'database':
        df = trainer.load_data_from_database()
    else:
        if not args.data_path:
            parser.error("--data-path is required when data-source is csv")
        df = trainer.load_data_from_csv(args.data_path)
    
    # Create features
    df = trainer.create_features(df)
    
    # Prepare training data
    X, y, target_cols = trainer.prepare_training_data(df, horizon=args.forecast_horizon)
    
    # Train model
    metrics = trainer.train(X, y, target_cols)
    
    # Save model
    trainer.save_model(metrics, target_cols)
    
    # Print summary
    print("\n" + "=" * 50)
    print("SOIL FORECAST MODEL TRAINING SUMMARY")
    print("=" * 50)
    print(f"\nForecast Horizon: {args.forecast_horizon} days")
    print(f"Rice Growing Season: {FORECAST_DAYS} days")
    print("\nGrowth Stages Covered:")
    for stage, info in RICE_GROWTH_STAGES.items():
        print(f"  {stage}: Day {info['start']}-{info['end']}")
        print(f"    Critical: {', '.join(info['critical_nutrients'])}")
    
    logger.info("Training complete!")
    return metrics


if __name__ == '__main__':
    main()
