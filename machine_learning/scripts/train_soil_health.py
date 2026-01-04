"""
Training Script: Soil Health Scoring Model

This script trains and optimizes the soil health scoring model that:
- Calculates health scores (0-100) based on soil parameters
- Optimizes scoring weights based on yield data
- Identifies deficiencies and generates recommendations

Usage:
    python train_soil_health.py --data-source database
    python train_soil_health.py --data-source csv --data-path data/soil_data.csv
"""

import argparse
import os
import sys
import logging
from datetime import datetime
import json

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
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


# Optimal ranges for rice cultivation
OPTIMAL_RANGES = {
    'ph': {'min': 5.5, 'max': 7.0, 'optimal': 6.5},
    'nitrogen': {'min': 20, 'max': 50, 'optimal': 35},
    'phosphorus': {'min': 15, 'max': 40, 'optimal': 25},
    'potassium': {'min': 100, 'max': 200, 'optimal': 150},
    'moisture': {'min': 40, 'max': 70, 'optimal': 55},
    'organic_matter': {'min': 2, 'max': 5, 'optimal': 3.5},
    'electrical_conductivity': {'min': 0, 'max': 4, 'optimal': 2}
}

# Default parameter weights
DEFAULT_WEIGHTS = {
    'ph': 0.20,
    'nitrogen': 0.18,
    'phosphorus': 0.15,
    'potassium': 0.15,
    'moisture': 0.12,
    'organic_matter': 0.10,
    'electrical_conductivity': 0.10
}


class SoilHealthModelTrainer:
    """Trainer for soil health scoring model."""
    
    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'trained_models', 'soil'
        )
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.soil_params = ['ph', 'nitrogen', 'phosphorus', 'potassium', 'moisture']
        self.model = None
        self.optimized_weights = None
        
    def load_data_from_database(self) -> pd.DataFrame:
        """Load soil data with yield information from database."""
        logger.info("Loading data from database...")
        
        db = DatabaseConnector()
        
        query = """
        SELECT 
            sd.ph, sd.nitrogen, sd.phosphorus, sd.potassium, 
            sd.moisture, sd.organic_matter, sd.electrical_conductivity,
            fh.yield_amount
        FROM farming_history fh
        JOIN soil_data sd ON fh.soil_data_id = sd.id
        WHERE fh.yield_amount IS NOT NULL
        """
        
        with db.engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        logger.info(f"Loaded {len(df)} records from database")
        return df
    
    def load_data_from_csv(self, filepath: str) -> pd.DataFrame:
        """Load soil data from CSV file."""
        logger.info(f"Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} records from CSV")
        return df
    
    @staticmethod
    def calculate_parameter_score(value: float, param_name: str) -> float:
        """Calculate individual parameter score (0-100)."""
        ranges = OPTIMAL_RANGES.get(param_name)
        if not ranges:
            return 50.0
        
        optimal = ranges['optimal']
        min_val = ranges['min']
        max_val = ranges['max']
        
        if min_val <= value <= max_val:
            distance = abs(value - optimal)
            max_distance = max(optimal - min_val, max_val - optimal)
            score = 100 - (distance / max_distance) * 30
        elif value < min_val:
            deficit = (min_val - value) / min_val
            score = max(0, 70 - deficit * 70)
        else:
            excess = (value - max_val) / max_val
            score = max(0, 70 - excess * 70)
        
        return score
    
    def calculate_health_score(self, row: pd.Series, weights: dict = None) -> float:
        """Calculate overall soil health score."""
        weights = weights or DEFAULT_WEIGHTS
        total_score = 0
        total_weight = 0
        
        for param, weight in weights.items():
            if param in row and pd.notna(row[param]):
                param_score = self.calculate_parameter_score(row[param], param)
                total_score += param_score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def train_yield_predictor(self, df: pd.DataFrame):
        """Train a model to predict yield from soil parameters."""
        logger.info("Training yield prediction model...")
        
        # Prepare features
        X = df[self.soil_params].fillna(df[self.soil_params].mean())
        y = df['yield_amount']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)
        
        logger.info(f"Yield Prediction - MAE: {mae:.4f}, R2: {r2:.4f}")
        logger.info(f"CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        return {
            'mae': float(mae),
            'r2': float(r2),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std())
        }
    
    def optimize_weights(self, df: pd.DataFrame):
        """Optimize parameter weights based on feature importance."""
        logger.info("Optimizing parameter weights...")
        
        if self.model is None:
            raise ValueError("Must train yield predictor first")
        
        # Get feature importance
        importance = dict(zip(self.soil_params, self.model.feature_importances_))
        
        # Normalize to create weights
        total = sum(importance.values())
        self.optimized_weights = {k: v / total for k, v in importance.items()}
        
        # Log optimized weights
        print("\nOptimized Parameter Weights:")
        for param, weight in sorted(self.optimized_weights.items(), 
                                     key=lambda x: x[1], reverse=True):
            print(f"  {param}: {weight:.4f}")
        
        return self.optimized_weights
    
    def validate_health_score(self, df: pd.DataFrame) -> dict:
        """Validate correlation between health score and yield."""
        logger.info("Validating health score correlation...")
        
        # Calculate health scores with default weights
        df['health_score_default'] = df.apply(
            lambda row: self.calculate_health_score(row, DEFAULT_WEIGHTS), 
            axis=1
        )
        
        # Calculate health scores with optimized weights
        if self.optimized_weights:
            df['health_score_optimized'] = df.apply(
                lambda row: self.calculate_health_score(row, self.optimized_weights),
                axis=1
            )
        
        # Calculate correlations
        corr_default = df['health_score_default'].corr(df['yield_amount'])
        
        if self.optimized_weights:
            corr_optimized = df['health_score_optimized'].corr(df['yield_amount'])
        else:
            corr_optimized = None
        
        logger.info(f"Correlation (default weights): {corr_default:.4f}")
        if corr_optimized:
            logger.info(f"Correlation (optimized weights): {corr_optimized:.4f}")
        
        return {
            'correlation_default': float(corr_default),
            'correlation_optimized': float(corr_optimized) if corr_optimized else None
        }
    
    def save_model(self, metrics: dict, correlations: dict):
        """Save trained model and configuration."""
        logger.info(f"Saving model to {self.model_dir}...")
        
        # Save yield prediction model
        joblib.dump(self.model, os.path.join(self.model_dir, 'soil_health_model.pkl'))
        
        # Save configuration
        config = {
            'optimal_ranges': OPTIMAL_RANGES,
            'default_weights': DEFAULT_WEIGHTS,
            'optimized_weights': self.optimized_weights,
            'soil_parameters': self.soil_params,
            'metrics': metrics,
            'correlations': correlations
        }
        
        with open(os.path.join(self.model_dir, 'parameter_weights.json'), 'w') as f:
            json.dump(config, f, indent=2)
        
        # Save metadata
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'model_type': 'RandomForestRegressor',
            'scoring_method': 'weighted_parameter_scoring'
        }
        
        with open(os.path.join(self.model_dir, 'health_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Model saved successfully!")


def main():
    parser = argparse.ArgumentParser(description='Train soil health scoring model')
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
        '--model-dir',
        type=str,
        help='Directory to save trained model'
    )
    
    args = parser.parse_args()
    
    trainer = SoilHealthModelTrainer(model_dir=args.model_dir)
    
    # Load data
    if args.data_source == 'database':
        df = trainer.load_data_from_database()
    else:
        if not args.data_path:
            parser.error("--data-path is required when data-source is csv")
        df = trainer.load_data_from_csv(args.data_path)
    
    # Train yield predictor
    metrics = trainer.train_yield_predictor(df)
    
    # Optimize weights
    trainer.optimize_weights(df)
    
    # Validate health scores
    correlations = trainer.validate_health_score(df)
    
    # Save model
    trainer.save_model(metrics, correlations)
    
    # Print summary
    print("\n" + "=" * 50)
    print("SOIL HEALTH MODEL TRAINING SUMMARY")
    print("=" * 50)
    print(f"\nYield Prediction Metrics:")
    print(f"  MAE: {metrics['mae']:.4f}")
    print(f"  R2:  {metrics['r2']:.4f}")
    print(f"\nHealth Score Correlations:")
    print(f"  Default weights:   {correlations['correlation_default']:.4f}")
    if correlations['correlation_optimized']:
        print(f"  Optimized weights: {correlations['correlation_optimized']:.4f}")
    
    logger.info("Training complete!")
    return metrics


if __name__ == '__main__':
    main()
