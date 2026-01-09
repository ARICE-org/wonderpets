"""
Soil-specific constants.
"""

from typing import Dict, Any, List


# Optimal ranges for rice cultivation
SOIL_OPTIMAL_RANGES: Dict[str, Dict[str, Any]] = {
    "ph": {
        "min": 5.5,
        "max": 7.0,
        "optimal": 6.0,
        "critical_low": 4.5,
        "critical_high": 8.5,
        "unit": ""
    },
    "nitrogen": {
        "min": 20,
        "max": 60,
        "optimal": 40,
        "critical_low": 10,
        "critical_high": 100,
        "unit": "kg/ha"
    },
    "phosphorus": {
        "min": 10,
        "max": 25,
        "optimal": 15,
        "critical_low": 5,
        "critical_high": 50,
        "unit": "kg/ha"
    },
    "potassium": {
        "min": 40,
        "max": 80,
        "optimal": 60,
        "critical_low": 20,
        "critical_high": 150,
        "unit": "kg/ha"
    },
    "organic_matter": {
        "min": 2.0,
        "max": 5.0,
        "optimal": 3.5,
        "critical_low": 1.0,
        "critical_high": 10.0,
        "unit": "%"
    },
    "moisture": {
        "min": 40,
        "max": 80,
        "optimal": 60,
        "critical_low": 20,
        "critical_high": 95,
        "unit": "%"
    },
    "temperature": {
        "min": 20,
        "max": 35,
        "optimal": 28,
        "critical_low": 10,
        "critical_high": 45,
        "unit": "°C"
    },
    "electrical_conductivity": {
        "min": 0.2,
        "max": 2.0,
        "optimal": 0.8,
        "critical_low": 0,
        "critical_high": 4.0,
        "unit": "dS/m"
    }
}


# Parameter weights for health scoring
SOIL_PARAMETER_WEIGHTS: Dict[str, float] = {
    "ph": 0.20,
    "nitrogen": 0.20,
    "phosphorus": 0.15,
    "potassium": 0.15,
    "organic_matter": 0.15,
    "moisture": 0.15
}


# Rice growth stages (Philippines context)
GROWTH_STAGES: List[Dict[str, Any]] = [
    {
        "name": "Germination",
        "start_day": 0,
        "end_day": 7,
        "critical_parameters": ["moisture", "temperature"],
        "optimal_moisture": (60, 80),
        "description": "Seed germination phase"
    },
    {
        "name": "Seedling",
        "start_day": 8,
        "end_day": 21,
        "critical_parameters": ["nitrogen", "moisture", "ph"],
        "optimal_moisture": (50, 70),
        "description": "Early vegetative growth"
    },
    {
        "name": "Tillering",
        "start_day": 22,
        "end_day": 45,
        "critical_parameters": ["nitrogen", "phosphorus", "potassium"],
        "optimal_moisture": (40, 60),
        "description": "Active tillering and root development"
    },
    {
        "name": "Stem Elongation",
        "start_day": 46,
        "end_day": 60,
        "critical_parameters": ["nitrogen", "potassium"],
        "optimal_moisture": (50, 70),
        "description": "Stem growth phase"
    },
    {
        "name": "Booting",
        "start_day": 61,
        "end_day": 70,
        "critical_parameters": ["nitrogen", "phosphorus"],
        "optimal_moisture": (60, 80),
        "description": "Panicle development"
    },
    {
        "name": "Heading",
        "start_day": 71,
        "end_day": 80,
        "critical_parameters": ["potassium", "moisture"],
        "optimal_moisture": (60, 80),
        "description": "Panicle emergence"
    },
    {
        "name": "Flowering",
        "start_day": 81,
        "end_day": 90,
        "critical_parameters": ["moisture", "temperature"],
        "optimal_moisture": (60, 75),
        "description": "Pollination phase"
    },
    {
        "name": "Grain Filling",
        "start_day": 91,
        "end_day": 105,
        "critical_parameters": ["potassium", "moisture"],
        "optimal_moisture": (50, 65),
        "description": "Grain development"
    },
    {
        "name": "Maturity",
        "start_day": 106,
        "end_day": 120,
        "critical_parameters": ["moisture"],
        "optimal_moisture": (20, 40),
        "description": "Grain maturation and drying"
    }
]


# Philippines seasonal patterns
PHILIPPINES_SEASONS: Dict[str, Dict[str, Any]] = {
    "dry": {
        "months": [12, 1, 2, 3, 4, 5],
        "typical_moisture": (10, 25),
        "irrigation_required": True
    },
    "wet": {
        "months": [6, 7, 8, 9, 10, 11],
        "typical_moisture": (30, 50),
        "drainage_important": True
    }
}
