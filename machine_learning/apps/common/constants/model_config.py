"""
Default model configurations and hyperparameters.
"""

from typing import Dict, Any


# Default hyperparameters for various model types
DEFAULT_HYPERPARAMETERS: Dict[str, Dict[str, Any]] = {
    "random_forest": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "random_state": 42,
    },
    "gradient_boosting": {
        "n_estimators": 100,
        "learning_rate": 0.1,
        "max_depth": 6,
        "random_state": 42,
    },
    "xgboost": {
        "n_estimators": 100,
        "learning_rate": 0.1,
        "max_depth": 6,
        "random_state": 42,
    },
    "lstm": {
        "units": 64,
        "dropout": 0.2,
        "epochs": 100,
        "batch_size": 32,
    },
    "hybrid_soil": {
        "rule_weight": 0.6,
        "ml_weight": 0.4,
        "fusion_method": "weighted_average",
        "confidence_threshold": 0.7,
    },
}


# Model version tracking
MODEL_VERSIONS: Dict[str, str] = {
    "soil_health": "1.0.0",
    "soil_forecast": "1.0.0",
    "hybrid_soil_forecast": "1.0.0",
    "weather_forecast": "1.0.0",
    "recommendation": "1.0.0",
}
