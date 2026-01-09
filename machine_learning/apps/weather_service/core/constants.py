"""
Weather-specific constants.
"""

from typing import Dict, Any, List


# Weather parameters tracked
WEATHER_PARAMETERS: Dict[str, Dict[str, Any]] = {
    "temperature_max": {
        "unit": "°C",
        "optimal_rice_range": (25, 35),
        "critical_low": 15,
        "critical_high": 45,
        "description": "Maximum daily temperature"
    },
    "temperature_min": {
        "unit": "°C",
        "optimal_rice_range": (20, 28),
        "critical_low": 10,
        "critical_high": 35,
        "description": "Minimum daily temperature"
    },
    "temperature_avg": {
        "unit": "°C",
        "optimal_rice_range": (25, 30),
        "critical_low": 18,
        "critical_high": 38,
        "description": "Average daily temperature"
    },
    "rainfall": {
        "unit": "mm",
        "optimal_rice_daily": (5, 10),
        "flood_risk": 50,
        "drought_threshold": 0,
        "description": "Daily rainfall amount"
    },
    "humidity": {
        "unit": "%",
        "optimal_rice_range": (60, 80),
        "disease_risk_high": 90,
        "description": "Relative humidity"
    },
    "wind_speed": {
        "unit": "km/h",
        "optimal_rice_range": (0, 15),
        "damage_threshold": 40,
        "description": "Wind speed"
    },
    "solar_radiation": {
        "unit": "MJ/m²",
        "optimal_rice_range": (15, 25),
        "description": "Solar radiation"
    },
    "evapotranspiration": {
        "unit": "mm/day",
        "typical_range": (3, 8),
        "description": "Evapotranspiration rate"
    }
}


# Philippines season definitions
SEASON_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "dry": {
        "name": "Dry Season (Tagaraw)",
        "months": [12, 1, 2, 3, 4, 5],
        "typical_rainfall_mm": (0, 100),
        "typical_temperature": (28, 35),
        "rice_considerations": "Requires irrigation, risk of water stress"
    },
    "wet": {
        "name": "Wet Season (Tag-ulan)",
        "months": [6, 7, 8, 9, 10, 11],
        "typical_rainfall_mm": (200, 400),
        "typical_temperature": (25, 32),
        "rice_considerations": "Rain-fed cultivation possible, flood risk"
    }
}


# Philippines climate zones
CLIMATE_ZONES: Dict[str, Dict[str, Any]] = {
    "type_1": {
        "description": "Two pronounced seasons: dry (Nov-Apr), wet (May-Oct)",
        "regions": ["Ilocos", "Central Luzon", "parts of Mindoro"],
        "rice_season_recommendation": "Plant during wet season start"
    },
    "type_2": {
        "description": "No dry season with very pronounced maximum rainfall (Nov-Jan)",
        "regions": ["Eastern Samar", "parts of Leyte", "Surigao"],
        "rice_season_recommendation": "Avoid planting during peak rain"
    },
    "type_3": {
        "description": "Seasons not very pronounced, relatively dry (Nov-Apr)",
        "regions": ["Western Visayas", "Zamboanga Peninsula"],
        "rice_season_recommendation": "Flexible planting window"
    },
    "type_4": {
        "description": "Rainfall evenly distributed throughout the year",
        "regions": ["Eastern Mindanao", "Batanes"],
        "rice_season_recommendation": "Year-round cultivation possible"
    }
}


# Typhoon season information
TYPHOON_SEASON: Dict[str, Any] = {
    "peak_months": [7, 8, 9, 10, 11],
    "off_season_months": [2, 3, 4],
    "average_per_year": 20,
    "rice_impact": "High wind and flooding can damage crops"
}
