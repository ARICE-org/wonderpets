"""
Threshold constants for ML services.
"""

from typing import Dict, Any


# Health score thresholds and categories
HEALTH_SCORE_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    "excellent": {"min": 85, "max": 100, "label": "Excellent", "color": "green"},
    "good": {"min": 70, "max": 84, "label": "Good", "color": "light_green"},
    "fair": {"min": 55, "max": 69, "label": "Fair", "color": "yellow"},
    "poor": {"min": 40, "max": 54, "label": "Poor", "color": "orange"},
    "critical": {"min": 0, "max": 39, "label": "Critical", "color": "red"},
}


# Soil parameter ranges for validation and scoring
SOIL_PARAMETER_RANGES: Dict[str, Dict[str, Any]] = {
    "ph": {
        "min": 0,
        "max": 14,
        "optimal_min": 5.5,
        "optimal_max": 7.0,
        "unit": "",
        "description": "Soil pH level",
    },
    "nitrogen": {
        "min": 0,
        "max": 200,
        "optimal_min": 40,
        "optimal_max": 80,
        "unit": "kg/ha",
        "description": "Available nitrogen",
    },
    "phosphorus": {
        "min": 0,
        "max": 100,
        "optimal_min": 15,
        "optimal_max": 30,
        "unit": "kg/ha",
        "description": "Available phosphorus",
    },
    "potassium": {
        "min": 0,
        "max": 200,
        "optimal_min": 80,
        "optimal_max": 150,
        "unit": "kg/ha",
        "description": "Available potassium",
    },
    "organic_matter": {
        "min": 0,
        "max": 15,
        "optimal_min": 3,
        "optimal_max": 5,
        "unit": "%",
        "description": "Organic matter content",
    },
    "moisture": {
        "min": 0,
        "max": 100,
        "optimal_min": 25,
        "optimal_max": 40,
        "unit": "%",
        "description": "Soil moisture content",
    },
    "temperature": {
        "min": -10,
        "max": 60,
        "optimal_min": 20,
        "optimal_max": 35,
        "unit": "°C",
        "description": "Soil temperature",
    },
    "electrical_conductivity": {
        "min": 0,
        "max": 10,
        "optimal_min": 0.2,
        "optimal_max": 2.0,
        "unit": "dS/m",
        "description": "Electrical conductivity",
    },
}


# Weather parameter ranges for validation
WEATHER_PARAMETER_RANGES: Dict[str, Dict[str, Any]] = {
    "temperature": {
        "min": -50,
        "max": 60,
        "unit": "°C",
        "description": "Air temperature",
    },
    "temperature_max": {
        "min": -50,
        "max": 60,
        "unit": "°C",
        "description": "Maximum temperature",
    },
    "temperature_min": {
        "min": -50,
        "max": 60,
        "unit": "°C",
        "description": "Minimum temperature",
    },
    "rainfall": {
        "min": 0,
        "max": 1000,
        "unit": "mm",
        "description": "Rainfall amount",
    },
    "humidity": {
        "min": 0,
        "max": 100,
        "unit": "%",
        "description": "Relative humidity",
    },
    "wind_speed": {
        "min": 0,
        "max": 200,
        "unit": "km/h",
        "description": "Wind speed",
    },
}


# Location validation ranges
LOCATION_RANGES: Dict[str, Dict[str, float]] = {
    "latitude": {"min": -90, "max": 90},
    "longitude": {"min": -180, "max": 180},
}
