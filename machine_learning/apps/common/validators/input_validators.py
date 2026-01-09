"""
Input Validators

Validation utilities for ML service inputs.
"""

from typing import Any, Dict, List, Optional, Tuple
import logging
from apps.common.constants.thresholds import (
    SOIL_PARAMETER_RANGES,
    WEATHER_PARAMETER_RANGES,
    LOCATION_RANGES,
)

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
            
            if param in SOIL_PARAMETER_RANGES:
                ranges = SOIL_PARAMETER_RANGES[param]
                
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
            errors.append("Weather data is empty")
            return False, errors, warnings
        
        for param, value in data.items():
            if value is None:
                continue
            
            if param in WEATHER_PARAMETER_RANGES:
                ranges = WEATHER_PARAMETER_RANGES[param]
                
                if not isinstance(value, (int, float)):
                    errors.append(f"{param} must be a number, got {type(value).__name__}")
                    continue
                
                if value < ranges["min"] or value > ranges["max"]:
                    errors.append(
                        f"{param} value {value} is outside valid range "
                        f"[{ranges['min']}, {ranges['max']}]"
                    )
        
        return len(errors) == 0, errors, warnings
    
    @classmethod
    def validate_location(
        cls,
        latitude: float,
        longitude: float
    ) -> Tuple[bool, List[str]]:
        """
        Validate geographic coordinates.
        
        Args:
            latitude: Latitude value
            longitude: Longitude value
            
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        lat_range = LOCATION_RANGES["latitude"]
        lon_range = LOCATION_RANGES["longitude"]
        
        if not isinstance(latitude, (int, float)):
            errors.append("Latitude must be a number")
        elif latitude < lat_range["min"] or latitude > lat_range["max"]:
            errors.append(f"Latitude {latitude} is outside valid range [-90, 90]")
        
        if not isinstance(longitude, (int, float)):
            errors.append("Longitude must be a number")
        elif longitude < lon_range["min"] or longitude > lon_range["max"]:
            errors.append(f"Longitude {longitude} is outside valid range [-180, 180]")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_date_string(cls, date_str: str, format: str = "%Y-%m-%d") -> Tuple[bool, str]:
        """
        Validate a date string.
        
        Args:
            date_str: Date string to validate
            format: Expected date format
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        from datetime import datetime
        
        try:
            datetime.strptime(date_str, format)
            return True, ""
        except ValueError as e:
            return False, f"Invalid date format: {date_str}. Expected format: {format}"
    
    @classmethod
    def validate_forecast_horizon(
        cls,
        days: int,
        min_days: int = 7,
        max_days: int = 120
    ) -> Tuple[bool, str]:
        """
        Validate forecast horizon.
        
        Args:
            days: Number of forecast days
            min_days: Minimum allowed days
            max_days: Maximum allowed days
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(days, int):
            return False, "Forecast horizon must be an integer"
        
        if days < min_days:
            return False, f"Forecast horizon must be at least {min_days} days"
        
        if days > max_days:
            return False, f"Forecast horizon cannot exceed {max_days} days"
        
        return True, ""
