"""
Input Validators

Validation utilities for ML service inputs.
"""

from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validator for ML service inputs.
    
    Provides validation for:
    - Soil sensor data
    - Weather data
    - Location data
    - Request payloads
    """
    
    # Valid ranges for various parameters
    SOIL_RANGES = {
        "ph": {"min": 0, "max": 14, "optimal_min": 5.5, "optimal_max": 7.0},
        "nitrogen": {"min": 0, "max": 200, "unit": "kg/ha"},
        "phosphorus": {"min": 0, "max": 100, "unit": "kg/ha"},
        "potassium": {"min": 0, "max": 200, "unit": "kg/ha"},
        "organic_matter": {"min": 0, "max": 15, "unit": "%"},
        "moisture": {"min": 0, "max": 100, "unit": "%"},
        "temperature": {"min": -10, "max": 60, "unit": "°C"}
    }
    
    WEATHER_RANGES = {
        "temperature": {"min": -50, "max": 60, "unit": "°C"},
        "temperature_max": {"min": -50, "max": 60, "unit": "°C"},
        "temperature_min": {"min": -50, "max": 60, "unit": "°C"},
        "rainfall": {"min": 0, "max": 1000, "unit": "mm"},
        "humidity": {"min": 0, "max": 100, "unit": "%"},
        "wind_speed": {"min": 0, "max": 200, "unit": "km/h"}
    }
    
    LOCATION_RANGES = {
        "latitude": {"min": -90, "max": 90},
        "longitude": {"min": -180, "max": 180}
    }
    
    @classmethod
    def validate_soil_data(
        cls, 
        data: Dict[str, Any]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate soil sensor data.
        
        Args:
            data: Dictionary of soil parameter values
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        if not data:
            errors.append("Soil data is empty")
            return False, errors, warnings
        
        for param, value in data.items():
            if value is None:
                continue
            
            if param in cls.SOIL_RANGES:
                ranges = cls.SOIL_RANGES[param]
                
                # Check if value is numeric
                if not isinstance(value, (int, float)):
                    errors.append(f"{param} must be a number, got {type(value).__name__}")
                    continue
                
                # Check valid range
                if value < ranges["min"] or value > ranges["max"]:
                    errors.append(
                        f"{param} value {value} is outside valid range "
                        f"[{ranges['min']}, {ranges['max']}]"
                    )
                
                # Check optimal range (warning only)
                elif "optimal_min" in ranges and "optimal_max" in ranges:
                    if value < ranges["optimal_min"] or value > ranges["optimal_max"]:
                        warnings.append(
                            f"{param} value {value} is outside optimal range "
                            f"[{ranges['optimal_min']}, {ranges['optimal_max']}]"
                        )
        
        return len(errors) == 0, errors, warnings
    
    @classmethod
    def validate_weather_data(
        cls, 
        data: Dict[str, Any]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate weather data.
        
        Args:
            data: Dictionary of weather parameter values
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        if not data:
            return True, errors, warnings  # Weather data can be optional
        
        for param, value in data.items():
            if value is None:
                continue
            
            if param in cls.WEATHER_RANGES:
                ranges = cls.WEATHER_RANGES[param]
                
                if not isinstance(value, (int, float)):
                    errors.append(f"{param} must be a number")
                    continue
                
                if value < ranges["min"] or value > ranges["max"]:
                    errors.append(
                        f"{param} value {value} is outside valid range "
                        f"[{ranges['min']}, {ranges['max']}]"
                    )
        
        # Check temperature consistency
        if "temperature_max" in data and "temperature_min" in data:
            if data["temperature_max"] is not None and data["temperature_min"] is not None:
                if data["temperature_max"] < data["temperature_min"]:
                    errors.append("temperature_max cannot be less than temperature_min")
        
        return len(errors) == 0, errors, warnings
    
    @classmethod
    def validate_location(
        cls, 
        data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate location data.
        
        Args:
            data: Dictionary with latitude and longitude
            
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        if not data:
            errors.append("Location data is required")
            return False, errors
        
        # Check required fields
        if "latitude" not in data or data["latitude"] is None:
            errors.append("latitude is required")
        
        if "longitude" not in data or data["longitude"] is None:
            errors.append("longitude is required")
        
        if errors:
            return False, errors
        
        # Validate ranges
        lat = data["latitude"]
        lon = data["longitude"]
        
        if lat < -90 or lat > 90:
            errors.append(f"latitude {lat} must be between -90 and 90")
        
        if lon < -180 or lon > 180:
            errors.append(f"longitude {lon} must be between -180 and 180")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_date_string(
        cls, 
        date_str: str, 
        field_name: str = "date"
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a date string in YYYY-MM-DD format.
        
        Args:
            date_str: Date string to validate
            field_name: Name of field for error message
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        from datetime import datetime
        
        if not date_str:
            return True, None  # Optional
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True, None
        except ValueError:
            return False, f"{field_name} must be in YYYY-MM-DD format"
    
    @classmethod
    def validate_forecast_horizon(
        cls, 
        days: int, 
        min_days: int = 1, 
        max_days: int = 120
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate forecast horizon days.
        
        Args:
            days: Number of forecast days
            min_days: Minimum allowed days
            max_days: Maximum allowed days
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(days, int):
            return False, "forecast_horizon_days must be an integer"
        
        if days < min_days:
            return False, f"forecast_horizon_days must be at least {min_days}"
        
        if days > max_days:
            return False, f"forecast_horizon_days cannot exceed {max_days}"
        
        return True, None
    
    @classmethod
    def sanitize_input(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize input data by removing None values and trimming strings.
        
        Args:
            data: Input dictionary
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            if value is None:
                continue
            
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    continue
            
            if isinstance(value, dict):
                value = cls.sanitize_input(value)
                if not value:
                    continue
            
            sanitized[key] = value
        
        return sanitized
