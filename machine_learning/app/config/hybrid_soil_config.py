"""
Hybrid Soil Forecasting Configuration
======================================

Configuration settings for the hybrid soil forecasting model.
Combines Rule-Based Expert System with Machine Learning.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class HybridModelConfig:
    """
    Configuration for hybrid soil forecasting model.
    
    This combines rule-based soil science knowledge with 
    machine learning for improved accuracy and explainability.
    """
    
    # ==========================================================================
    # HYBRID ARCHITECTURE SETTINGS
    # ==========================================================================
    
    # Fusion method: "weighted_average", "stacking", "dynamic"
    fusion_method: str = "weighted_average"
    
    # Default weights for combining predictions
    rule_weight: float = 0.6  # Trust rules more (explainability)
    ml_weight: float = 0.4    # ML for residual correction
    
    # Whether to learn optimal weights from validation data
    learn_weights: bool = True
    
    # Below this confidence, rely more on rules
    confidence_threshold: float = 0.7
    
    # ==========================================================================
    # ML MODEL SETTINGS (Random Forest)
    # ==========================================================================
    
    ml_model_type: str = "RandomForest"
    n_estimators: int = 100
    max_depth: int = 6  # Limited to prevent overfitting
    min_samples_split: int = 15
    min_samples_leaf: int = 5
    random_state: int = 42
    cv_folds: int = 5
    
    # ==========================================================================
    # TARGET PARAMETERS
    # ==========================================================================
    
    target_parameters: List[str] = field(default_factory=lambda: [
        'nitrogen_ppm',
        'phosphorus_ppm', 
        'potassium_meq',
        'pH',
        'soil_moisture_pct',
        'organic_matter_pct'
    ])
    
    # ==========================================================================
    # FORECAST SETTINGS
    # ==========================================================================
    
    default_forecast_horizon_days: int = 90
    default_forecast_interval_days: int = 3
    max_forecast_horizon_days: int = 120
    
    # ==========================================================================
    # SEASONAL DEFINITIONS (Philippines)
    # ==========================================================================
    
    dry_season_months: List[int] = field(default_factory=lambda: [12, 1, 2, 3, 4, 5])
    wet_season_months: List[int] = field(default_factory=lambda: [6, 7, 8, 9, 10, 11])


@dataclass
class SoilScienceRulesConfig:
    """
    Soil science rules based on agricultural literature.
    
    These rules encode domain knowledge about soil parameter behavior
    across seasons for rice cultivation in tropical climates.
    """
    
    # Optimal ranges for rice cultivation
    optimal_ranges: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        'nitrogen_ppm': (40, 80),
        'phosphorus_ppm': (15, 30),
        'potassium_meq': (0.5, 1.5),
        'pH': (5.5, 7.0),
        'soil_moisture_pct': (25, 40),
        'organic_matter_pct': (3, 5)
    })
    
    # Seasonal change rules (percentage change per season)
    seasonal_rules: Dict[str, Dict] = field(default_factory=lambda: {
        'nitrogen_ppm': {
            'optimal_range': (40, 80),
            'wet_change_pct': (-10, -15),  # Leaching during wet season
            'dry_change_pct': (-5, -8),    # Volatilization during dry season
        },
        'phosphorus_ppm': {
            'optimal_range': (15, 30),
            'wet_change_pct': (-2, -5),
            'dry_change_pct': (0, -2),
        },
        'potassium_meq': {
            'optimal_range': (0.5, 1.5),
            'wet_change_pct': (-8, -12),   # Leaching
            'dry_change_pct': (-3, -5),
        },
        'pH': {
            'optimal_range': (5.5, 7.0),
            'wet_change_units': (-0.1, -0.3),  # Acidification in wet season
            'dry_change_units': (0, 0.1),
        },
        'soil_moisture_pct': {
            'optimal_range': (25, 40),
            'wet_typical': (30, 50),
            'dry_typical': (10, 25),
        },
        'organic_matter_pct': {
            'optimal_range': (3, 5),
            'wet_change_pct': (-3, -5),    # Faster decomposition
            'dry_change_pct': (-1, -2),
        }
    })
    
    # Parameter weights for health scoring
    parameter_weights: Dict[str, float] = field(default_factory=lambda: {
        'nitrogen_ppm': 0.20,
        'phosphorus_ppm': 0.15,
        'potassium_meq': 0.15,
        'pH': 0.20,
        'soil_moisture_pct': 0.15,
        'organic_matter_pct': 0.15
    })


@dataclass 
class EvaluationConfig:
    """Configuration for model evaluation."""
    
    # Train/test split ratio
    train_test_split: float = 0.8
    
    # Metrics to compute
    evaluation_metrics: List[str] = field(default_factory=lambda: [
        'r2_score',
        'rmse',
        'mae',
        'mape',
        'explained_variance'
    ])
    
    # Comparison criteria for thesis
    comparison_criteria: Dict[str, str] = field(default_factory=lambda: {
        'accuracy': 'R² score on test data',
        'interpretability': 'Can explain why prediction was made',
        'robustness': 'Performance on unseen conditions',
        'computational_cost': 'Time and resources needed',
        'data_requirements': 'Amount of training data needed'
    })


# Default configurations
DEFAULT_HYBRID_CONFIG = HybridModelConfig()
DEFAULT_RULES_CONFIG = SoilScienceRulesConfig()
DEFAULT_EVAL_CONFIG = EvaluationConfig()
