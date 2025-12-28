"""
Training Script: Rice Variety Recommendation Model

This script trains the recommendation model for suggesting rice varieties
based on soil conditions and weather patterns.

Usage:
    python train_recommendation.py --data-source database
    python train_recommendation.py --data-source csv --data-path data/training_data.csv
"""

import argparse
import os
import sys
import logging
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
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


class RecommendationModelTrainer:
    """Trainer for rice variety recommendation model."""
    
    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'trained_models', 'recommendation'
        )
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.feature_cols = [
            'ph', 'nitrogen', 'phosphorus', 'potassium', 'moisture',
            'temperature', 'humidity', 'rainfall'
        ]
        
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
    def load_data_from_database(self) -> pd.DataFrame:
        """Load training data from the database."""
        logger.info("Loading data from database...")
        
        db = DatabaseConnector()
        
        query = """
        SELECT 
            sd.ph, sd.nitrogen, sd.phosphorus, sd.potassium, sd.moisture,
            wd.temperature, wd.humidity, wd.rainfall,
            rv.name as variety_name,
            fh.yield_amount
        FROM farming_history fh
        JOIN soil_data sd ON fh.soil_data_id = sd.id
        JOIN weather_data wd ON fh.weather_data_id = wd.id
        JOIN rice_varieties rv ON fh.variety_id = rv.id
        WHERE fh.yield_amount IS NOT NULL
        """
        
        with db.engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        logger.info(f"Loaded {len(df)} records from database")
        return df
    
    def load_data_from_csv(self, filepath: str) -> pd.DataFrame:
        """Load training data from CSV file."""
        logger.info(f"Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} records from CSV")
        return df
    
    def preprocess_data(self, df: pd.DataFrame):
        """Preprocess and prepare features."""
        logger.info("Preprocessing data...")
        
        # Handle missing values
        df = df.dropna(subset=self.feature_cols + ['variety_name'])
        
        # Extract features and labels
        X = df[self.feature_cols]
        y = df['variety_name']
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        logger.info(f"Preprocessed {len(df)} samples with {len(self.label_encoder.classes_)} varieties")
        
        return X_scaled, y_encoded
    
    def train(self, X, y, hyperparameter_tuning: bool = False):
        """Train the recommendation model."""
        logger.info("Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        if hyperparameter_tuning:
            logger.info("Performing hyperparameter tuning...")
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            
            grid_search = GridSearchCV(
                RandomForestClassifier(random_state=42),
                param_grid,
                cv=5,
                scoring='accuracy',
                n_jobs=-1
            )
            grid_search.fit(X_train, y_train)
            
            self.model = grid_search.best_estimator_
            logger.info(f"Best parameters: {grid_search.best_params_}")
        else:
            logger.info("Training with default parameters...")
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42
            )
            self.model.fit(X_train, y_train)
        
        # Evaluate
        logger.info("Evaluating model...")
        y_pred = self.model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)
        
        logger.info(f"Test Accuracy: {accuracy:.4f}")
        logger.info(f"CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_
        ))
        
        # Feature importance
        importance_df = pd.DataFrame({
            'feature': self.feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nFeature Importance:")
        print(importance_df.to_string(index=False))
        
        return {
            'accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': importance_df.to_dict('records')
        }
    
    def save_model(self):
        """Save trained model and artifacts."""
        logger.info(f"Saving model to {self.model_dir}...")
        
        joblib.dump(self.model, os.path.join(self.model_dir, 'rice_variety_model.pkl'))
        joblib.dump(self.scaler, os.path.join(self.model_dir, 'feature_scaler.pkl'))
        joblib.dump(self.label_encoder, os.path.join(self.model_dir, 'label_encoder.pkl'))
        
        # Save metadata
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'feature_columns': self.feature_cols,
            'varieties': list(self.label_encoder.classes_),
            'model_type': 'RandomForestClassifier'
        }
        
        import json
        with open(os.path.join(self.model_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Model saved successfully!")


def main():
    parser = argparse.ArgumentParser(description='Train rice variety recommendation model')
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
        '--hyperparameter-tuning',
        action='store_true',
        help='Perform hyperparameter tuning'
    )
    parser.add_argument(
        '--model-dir',
        type=str,
        help='Directory to save trained model'
    )
    
    args = parser.parse_args()
    
    trainer = RecommendationModelTrainer(model_dir=args.model_dir)
    
    # Load data
    if args.data_source == 'database':
        df = trainer.load_data_from_database()
    else:
        if not args.data_path:
            parser.error("--data-path is required when data-source is csv")
        df = trainer.load_data_from_csv(args.data_path)
    
    # Preprocess and train
    X, y = trainer.preprocess_data(df)
    metrics = trainer.train(X, y, hyperparameter_tuning=args.hyperparameter_tuning)
    
    # Save model
    trainer.save_model()
    
    logger.info("Training complete!")
    return metrics


if __name__ == '__main__':
    main()
