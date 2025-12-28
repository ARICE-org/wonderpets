"""
Training Script: Weather Forecasting Model

This script trains the weather forecasting model using Prophet for
time series prediction of temperature, rainfall, and humidity.

Usage:
    python train_weather.py --data-source database
    python train_weather.py --data-source csv --data-path data/weather_data.csv
"""

import argparse
import os
import sys
import logging
from datetime import datetime
import json

import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json
from sklearn.metrics import mean_absolute_error, mean_squared_error

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


class WeatherModelTrainer:
    """Trainer for weather forecasting models using Prophet."""
    
    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'trained_models', 'weather'
        )
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.weather_params = ['temperature', 'humidity', 'rainfall']
        self.models = {}
        self.metrics = {}
        
    def load_data_from_database(self) -> pd.DataFrame:
        """Load weather data from the database."""
        logger.info("Loading data from database...")
        
        db = DatabaseConnector()
        
        query = """
        SELECT date, temperature, humidity, rainfall, wind_speed
        FROM weather_data
        ORDER BY date
        """
        
        with db.engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        df['date'] = pd.to_datetime(df['date'])
        logger.info(f"Loaded {len(df)} records from database")
        logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
        
        return df
    
    def load_data_from_csv(self, filepath: str) -> pd.DataFrame:
        """Load weather data from CSV file."""
        logger.info(f"Loading data from {filepath}...")
        df = pd.read_csv(filepath, parse_dates=['date'])
        logger.info(f"Loaded {len(df)} records from CSV")
        return df
    
    def train_prophet_model(self, df: pd.DataFrame, param: str, 
                            test_days: int = 30) -> dict:
        """Train a Prophet model for a specific weather parameter."""
        logger.info(f"Training Prophet model for {param}...")
        
        # Prepare data for Prophet
        prophet_df = df[['date', param]].rename(
            columns={'date': 'ds', param: 'y'}
        ).dropna()
        
        # Split data
        train_df = prophet_df[:-test_days]
        test_df = prophet_df[-test_days:]
        
        # Configure Prophet based on parameter
        if param == 'temperature':
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
        elif param == 'rainfall':
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.1
            )
        else:  # humidity
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False
            )
        
        # Train
        model.fit(train_df)
        
        # Predict
        future = model.make_future_dataframe(periods=test_days)
        forecast = model.predict(future)
        
        # Evaluate
        test_predictions = forecast.tail(test_days)['yhat'].values
        test_actual = test_df['y'].values
        
        mae = mean_absolute_error(test_actual, test_predictions)
        rmse = np.sqrt(mean_squared_error(test_actual, test_predictions))
        mape = np.mean(np.abs((test_actual - test_predictions) / test_actual)) * 100
        
        logger.info(f"{param} - MAE: {mae:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.2f}%")
        
        self.models[param] = model
        self.metrics[param] = {
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape),
            'train_samples': len(train_df),
            'test_samples': len(test_df)
        }
        
        return self.metrics[param]
    
    def train_all(self, df: pd.DataFrame, test_days: int = 30):
        """Train models for all weather parameters."""
        logger.info("Training models for all weather parameters...")
        
        all_metrics = {}
        for param in self.weather_params:
            if param in df.columns:
                metrics = self.train_prophet_model(df, param, test_days)
                all_metrics[param] = metrics
            else:
                logger.warning(f"Column {param} not found in data")
        
        return all_metrics
    
    def save_models(self):
        """Save all trained models."""
        logger.info(f"Saving models to {self.model_dir}...")
        
        for param, model in self.models.items():
            model_path = os.path.join(self.model_dir, f'{param}_prophet_model.json')
            with open(model_path, 'w') as f:
                f.write(model_to_json(model))
            logger.info(f"Saved {param} model")
        
        # Save metrics
        metrics_path = os.path.join(self.model_dir, 'metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        # Save metadata
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'parameters': self.weather_params,
            'model_type': 'Prophet'
        }
        
        with open(os.path.join(self.model_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("All models saved successfully!")
    
    def generate_forecast(self, param: str, days: int = 30) -> pd.DataFrame:
        """Generate forecast for a specific parameter."""
        if param not in self.models:
            raise ValueError(f"No trained model for {param}")
        
        model = self.models[param]
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)


def main():
    parser = argparse.ArgumentParser(description='Train weather forecasting model')
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
        '--test-days',
        type=int,
        default=30,
        help='Number of days to use for testing'
    )
    parser.add_argument(
        '--model-dir',
        type=str,
        help='Directory to save trained models'
    )
    
    args = parser.parse_args()
    
    trainer = WeatherModelTrainer(model_dir=args.model_dir)
    
    # Load data
    if args.data_source == 'database':
        df = trainer.load_data_from_database()
    else:
        if not args.data_path:
            parser.error("--data-path is required when data-source is csv")
        df = trainer.load_data_from_csv(args.data_path)
    
    # Train all models
    metrics = trainer.train_all(df, test_days=args.test_days)
    
    # Save models
    trainer.save_models()
    
    # Print summary
    print("\n" + "=" * 50)
    print("WEATHER MODEL TRAINING SUMMARY")
    print("=" * 50)
    for param, m in metrics.items():
        print(f"\n{param.upper()}:")
        print(f"  MAE:  {m['mae']:.4f}")
        print(f"  RMSE: {m['rmse']:.4f}")
        print(f"  MAPE: {m['mape']:.2f}%")
    
    logger.info("Training complete!")
    return metrics


if __name__ == '__main__':
    main()
