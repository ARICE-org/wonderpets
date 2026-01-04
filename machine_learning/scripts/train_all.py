"""
Training Script: Train All Models

This script trains all ML models for the ARICE project:
- Rice Variety Recommendation Model
- Weather Forecasting Model
- Soil Health Scoring Model
- Soil Forecast Model

Usage:
    python train_all.py --data-source database
    python train_all.py --skip-weather
"""

import argparse
import os
import sys
import logging
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def train_recommendation_model(data_source: str, data_path: str = None):
    """Train the rice variety recommendation model."""
    from train_recommendation import RecommendationModelTrainer
    
    logger.info("\n" + "=" * 60)
    logger.info("TRAINING: Rice Variety Recommendation Model")
    logger.info("=" * 60)
    
    trainer = RecommendationModelTrainer()
    
    if data_source == 'database':
        df = trainer.load_data_from_database()
    else:
        df = trainer.load_data_from_csv(data_path)
    
    X, y = trainer.preprocess_data(df)
    metrics = trainer.train(X, y)
    trainer.save_model()
    
    return metrics


def train_weather_model(data_source: str, data_path: str = None):
    """Train the weather forecasting models."""
    from train_weather import WeatherModelTrainer
    
    logger.info("\n" + "=" * 60)
    logger.info("TRAINING: Weather Forecasting Model")
    logger.info("=" * 60)
    
    trainer = WeatherModelTrainer()
    
    if data_source == 'database':
        df = trainer.load_data_from_database()
    else:
        df = trainer.load_data_from_csv(data_path)
    
    metrics = trainer.train_all(df)
    trainer.save_models()
    
    return metrics


def train_soil_health_model(data_source: str, data_path: str = None):
    """Train the soil health scoring model."""
    from train_soil_health import SoilHealthModelTrainer
    
    logger.info("\n" + "=" * 60)
    logger.info("TRAINING: Soil Health Scoring Model")
    logger.info("=" * 60)
    
    trainer = SoilHealthModelTrainer()
    
    if data_source == 'database':
        df = trainer.load_data_from_database()
    else:
        df = trainer.load_data_from_csv(data_path)
    
    metrics = trainer.train_yield_predictor(df)
    trainer.optimize_weights(df)
    correlations = trainer.validate_health_score(df)
    trainer.save_model(metrics, correlations)
    
    return {**metrics, **correlations}


def train_soil_forecast_model(data_source: str, data_path: str = None):
    """Train the soil 3-month forecast model."""
    from train_soil_forecast import SoilForecastModelTrainer
    
    logger.info("\n" + "=" * 60)
    logger.info("TRAINING: Soil 3-Month Forecast Model")
    logger.info("=" * 60)
    
    trainer = SoilForecastModelTrainer()
    
    if data_source == 'database':
        df = trainer.load_data_from_database()
    else:
        df = trainer.load_data_from_csv(data_path)
    
    df = trainer.create_features(df)
    X, y, target_cols = trainer.prepare_training_data(df, horizon=90)
    metrics = trainer.train(X, y, target_cols)
    trainer.save_model(metrics, target_cols)
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description='Train all ML models')
    parser.add_argument(
        '--data-source',
        choices=['database', 'csv'],
        default='database',
        help='Source of training data'
    )
    parser.add_argument(
        '--skip-recommendation',
        action='store_true',
        help='Skip training recommendation model'
    )
    parser.add_argument(
        '--skip-weather',
        action='store_true',
        help='Skip training weather model'
    )
    parser.add_argument(
        '--skip-soil-health',
        action='store_true',
        help='Skip training soil health model'
    )
    parser.add_argument(
        '--skip-soil-forecast',
        action='store_true',
        help='Skip training soil forecast model'
    )
    
    args = parser.parse_args()
    
    start_time = datetime.now()
    all_metrics = {}
    
    print("\n" + "=" * 60)
    print("ARICE ML MODEL TRAINING PIPELINE")
    print("=" * 60)
    print(f"Start time: {start_time}")
    print(f"Data source: {args.data_source}")
    
    try:
        # Train recommendation model
        if not args.skip_recommendation:
            all_metrics['recommendation'] = train_recommendation_model(args.data_source)
        
        # Train weather model
        if not args.skip_weather:
            all_metrics['weather'] = train_weather_model(args.data_source)
        
        # Train soil health model
        if not args.skip_soil_health:
            all_metrics['soil_health'] = train_soil_health_model(args.data_source)
        
        # Train soil forecast model
        if not args.skip_soil_forecast:
            all_metrics['soil_forecast'] = train_soil_forecast_model(args.data_source)
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Print summary
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE - SUMMARY")
    print("=" * 60)
    print(f"Duration: {duration}")
    print(f"Models trained: {list(all_metrics.keys())}")
    
    # Save overall metrics
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'trained_models'
    )
    
    training_summary = {
        'trained_at': start_time.isoformat(),
        'duration_seconds': duration.total_seconds(),
        'data_source': args.data_source,
        'models': list(all_metrics.keys()),
        'metrics': all_metrics
    }
    
    with open(os.path.join(output_dir, 'training_summary.json'), 'w') as f:
        json.dump(training_summary, f, indent=2, default=str)
    
    print(f"\nTraining summary saved to: {output_dir}/training_summary.json")
    
    return all_metrics


if __name__ == '__main__':
    main()
