"""
Recommendation-specific constants.
"""

from typing import Dict, Any, List


# Philippines rice varieties
RICE_VARIETIES: Dict[str, Dict[str, Any]] = {
    "IR64": {
        "name": "IR64",
        "type": "Indica",
        "maturity_days": 110,
        "yield_potential_tha": 6.0,
        "grain_quality": "Premium",
        "disease_resistance": ["Blast", "Bacterial Leaf Blight"],
        "description": "High-yielding variety with excellent grain quality"
    },
    "RC222": {
        "name": "NSIC Rc222 (Tubigan 18)",
        "type": "Indica",
        "maturity_days": 112,
        "yield_potential_tha": 7.5,
        "grain_quality": "Premium",
        "disease_resistance": ["Tungro", "Blast"],
        "description": "High-yielding, drought-tolerant variety"
    },
    "RC160": {
        "name": "NSIC Rc160 (Tubigan 11)",
        "type": "Indica",
        "maturity_days": 118,
        "yield_potential_tha": 7.0,
        "grain_quality": "Good",
        "disease_resistance": ["Blast"],
        "description": "Suitable for irrigated lowland areas"
    },
    "RC218": {
        "name": "NSIC Rc218 (Tubigan 17)",
        "type": "Indica",
        "maturity_days": 115,
        "yield_potential_tha": 7.2,
        "grain_quality": "Premium",
        "disease_resistance": ["Tungro", "Bacterial Leaf Blight"],
        "description": "High-yielding variety for wet and dry seasons"
    },
    "RC402": {
        "name": "NSIC Rc402 (Sahod Ulan 11)",
        "type": "Indica",
        "maturity_days": 108,
        "yield_potential_tha": 5.5,
        "grain_quality": "Good",
        "disease_resistance": ["Drought"],
        "drought_tolerance": "High",
        "description": "Drought-tolerant variety for rainfed areas"
    },
    "RC480": {
        "name": "NSIC Rc480 (Katihan 1)",
        "type": "Indica",
        "maturity_days": 90,
        "yield_potential_tha": 5.0,
        "grain_quality": "Good",
        "description": "Early maturing variety, good for short seasons"
    },
    "PSB_RC82": {
        "name": "PSB Rc82 (Peñaranda)",
        "type": "Indica",
        "maturity_days": 123,
        "yield_potential_tha": 6.5,
        "grain_quality": "Premium",
        "disease_resistance": ["Blast", "Bacterial Leaf Blight"],
        "description": "Premium quality, suitable for irrigated areas"
    },
    "MATATAG_9": {
        "name": "NSIC Rc298 (Matatag 9)",
        "type": "Indica",
        "maturity_days": 118,
        "yield_potential_tha": 8.0,
        "grain_quality": "Good",
        "disease_resistance": ["Tungro", "Blast", "Bacterial Leaf Blight"],
        "submergence_tolerance": "High",
        "description": "Flood-tolerant variety for flood-prone areas"
    }
}


# Variety requirements
VARIETY_REQUIREMENTS: Dict[str, Dict[str, Any]] = {
    "IR64": {
        "ph_range": (5.5, 7.0),
        "temperature_range": (20, 35),
        "water_requirement": "Medium",
        "soil_type": ["Clay", "Loam", "Clay Loam"],
        "nitrogen_need": "Medium"
    },
    "RC222": {
        "ph_range": (5.0, 7.5),
        "temperature_range": (22, 38),
        "water_requirement": "Low-Medium",
        "soil_type": ["Clay", "Loam", "Sandy Loam"],
        "nitrogen_need": "Medium-High"
    },
    "RC402": {
        "ph_range": (5.0, 7.5),
        "temperature_range": (22, 40),
        "water_requirement": "Low",
        "soil_type": ["Sandy", "Sandy Loam", "Loam"],
        "nitrogen_need": "Low-Medium"
    },
    "MATATAG_9": {
        "ph_range": (5.5, 7.0),
        "temperature_range": (20, 35),
        "water_requirement": "High",
        "flood_tolerance": "High",
        "soil_type": ["Clay", "Clay Loam"],
        "nitrogen_need": "Medium"
    }
}


# Planting seasons
PLANTING_SEASONS: Dict[str, Dict[str, Any]] = {
    "dry_season": {
        "name": "Dry Season Cropping",
        "months": [11, 12, 1, 2],
        "harvest_months": [3, 4, 5, 6],
        "irrigation_required": True,
        "recommended_varieties": ["IR64", "RC222", "RC218", "PSB_RC82"],
        "considerations": "Requires irrigation, higher yield potential"
    },
    "wet_season": {
        "name": "Wet Season Cropping",
        "months": [5, 6, 7, 8],
        "harvest_months": [9, 10, 11, 12],
        "irrigation_required": False,
        "recommended_varieties": ["RC222", "RC402", "MATATAG_9", "RC480"],
        "considerations": "Rainfed possible, watch for flooding and typhoons"
    }
}


# Soil type compatibility
SOIL_TYPE_COMPATIBILITY: Dict[str, List[str]] = {
    "Clay": ["IR64", "RC160", "RC218", "MATATAG_9", "PSB_RC82"],
    "Clay Loam": ["IR64", "RC222", "RC160", "RC218", "MATATAG_9"],
    "Loam": ["IR64", "RC222", "RC160", "RC402"],
    "Sandy Loam": ["RC222", "RC402", "RC480"],
    "Sandy": ["RC402", "RC480"]
}
