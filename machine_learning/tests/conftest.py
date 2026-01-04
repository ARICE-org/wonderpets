"""
Test Configuration for Machine Learning Service

This file contains pytest fixtures and configuration for testing
the ML models and services.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_soil_data() -> Dict[str, float]:
    """Sample soil data for testing."""
    return {
        'ph': 6.5,
        'nitrogen': 35.0,
        'phosphorus': 25.0,
        'potassium': 150.0,
        'moisture': 55.0,
        'organic_matter': 3.5,
        'electrical_conductivity': 2.0
    }


@pytest.fixture
def sample_weather_data() -> Dict[str, float]:
    """Sample weather data for testing."""
    return {
        'temperature': 28.0,
        'humidity': 75.0,
        'rainfall': 150.0,
        'wind_speed': 10.0
    }


@pytest.fixture
def sample_soil_dataframe() -> pd.DataFrame:
    """Sample soil dataframe for testing models."""
    np.random.seed(42)
    n_samples = 100
    
    return pd.DataFrame({
        'ph': np.random.uniform(5.0, 8.0, n_samples),
        'nitrogen': np.random.uniform(10, 60, n_samples),
        'phosphorus': np.random.uniform(10, 50, n_samples),
        'potassium': np.random.uniform(80, 250, n_samples),
        'moisture': np.random.uniform(30, 80, n_samples),
        'organic_matter': np.random.uniform(1, 6, n_samples),
        'electrical_conductivity': np.random.uniform(0, 6, n_samples)
    })


@pytest.fixture
def sample_weather_dataframe() -> pd.DataFrame:
    """Sample weather dataframe for testing models."""
    np.random.seed(42)
    n_days = 365
    
    dates = [datetime.now() - timedelta(days=i) for i in range(n_days)]
    
    return pd.DataFrame({
        'date': dates,
        'temperature': np.random.uniform(20, 35, n_days),
        'humidity': np.random.uniform(50, 90, n_days),
        'rainfall': np.random.uniform(0, 50, n_days),
        'wind_speed': np.random.uniform(0, 20, n_days)
    })


@pytest.fixture
def sample_training_data() -> pd.DataFrame:
    """Sample training data with soil, weather, and yield info."""
    np.random.seed(42)
    n_samples = 100
    
    varieties = ['NSIC Rc222', 'NSIC Rc160', 'NSIC Rc216', 'PSB Rc82', 'NSIC Rc238']
    
    return pd.DataFrame({
        'ph': np.random.uniform(5.5, 7.0, n_samples),
        'nitrogen': np.random.uniform(20, 50, n_samples),
        'phosphorus': np.random.uniform(15, 40, n_samples),
        'potassium': np.random.uniform(100, 200, n_samples),
        'moisture': np.random.uniform(40, 70, n_samples),
        'temperature': np.random.uniform(25, 32, n_samples),
        'humidity': np.random.uniform(60, 85, n_samples),
        'rainfall': np.random.uniform(100, 300, n_samples),
        'variety_name': np.random.choice(varieties, n_samples),
        'yield_amount': np.random.uniform(3, 8, n_samples)
    })


# ============================================================================
# Model Fixtures
# ============================================================================

@pytest.fixture
def mock_recommendation_model():
    """Mock recommendation model for testing."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    
    # Create simple mock model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    scaler = StandardScaler()
    encoder = LabelEncoder()
    
    # Fit with dummy data
    X = np.random.rand(50, 8)
    y = np.random.choice(['Variety A', 'Variety B', 'Variety C'], 50)
    
    scaler.fit(X)
    y_encoded = encoder.fit_transform(y)
    model.fit(scaler.transform(X), y_encoded)
    
    return {
        'model': model,
        'scaler': scaler,
        'encoder': encoder
    }


@pytest.fixture
def mock_soil_health_config() -> Dict[str, Any]:
    """Mock configuration for soil health model."""
    return {
        'optimal_ranges': {
            'ph': {'min': 5.5, 'max': 7.0, 'optimal': 6.5},
            'nitrogen': {'min': 20, 'max': 50, 'optimal': 35},
            'phosphorus': {'min': 15, 'max': 40, 'optimal': 25},
            'potassium': {'min': 100, 'max': 200, 'optimal': 150},
            'moisture': {'min': 40, 'max': 70, 'optimal': 55}
        },
        'weights': {
            'ph': 0.20,
            'nitrogen': 0.18,
            'phosphorus': 0.15,
            'potassium': 0.15,
            'moisture': 0.12
        }
    }


# ============================================================================
# Test Environment Fixtures
# ============================================================================

@pytest.fixture
def temp_model_dir(tmp_path):
    """Create a temporary directory for model storage."""
    model_dir = tmp_path / "trained_models"
    model_dir.mkdir()
    (model_dir / "recommendation").mkdir()
    (model_dir / "weather").mkdir()
    (model_dir / "soil").mkdir()
    return model_dir


@pytest.fixture
def mock_database_url():
    """Mock database URL for testing."""
    return "sqlite:///:memory:"


# ============================================================================
# Helper Functions
# ============================================================================

def assert_valid_health_score(score: float):
    """Assert that a health score is valid (0-100)."""
    assert isinstance(score, (int, float)), "Score must be numeric"
    assert 0 <= score <= 100, f"Score {score} must be between 0 and 100"


def assert_valid_forecast(forecast: Dict[str, Any]):
    """Assert that a forecast response is valid."""
    assert 'predictions' in forecast, "Forecast must contain predictions"
    assert 'confidence' in forecast or 'uncertainty' in forecast, \
        "Forecast must contain confidence or uncertainty"


def assert_valid_recommendation(recommendation: Dict[str, Any]):
    """Assert that a recommendation response is valid."""
    assert 'variety' in recommendation, "Recommendation must contain variety"
    assert 'confidence' in recommendation, "Recommendation must contain confidence"
