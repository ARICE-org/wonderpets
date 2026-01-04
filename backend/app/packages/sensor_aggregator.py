"""
Sensor Data Aggregator Module

Aggregates multiple sensor readings into model-ready format with summary statistics.
This preserves important information like variance and trends for more accurate forecasting.
"""

from typing import List, Dict, Optional
from datetime import datetime
import statistics


class SensorDataAggregator:
    """
    Aggregates multiple sensor readings into summary statistics.
    
    Why aggregation over raw data:
    1. Reduces noise from sensor fluctuations
    2. Provides more stable baseline for forecasting
    3. Includes variance info for confidence estimation
    """
    
    # Parameter mapping from schema field names to internal names
    PARAMETER_MAPPING = {
        "nitrogen": "nitrogen_ppm",
        "nitrogenLevel": "nitrogen_ppm",
        "nitrogen_level": "nitrogen_ppm",
        "phosphorus": "phosphorus_ppm",
        "phosphorusLevel": "phosphorus_ppm",
        "phosphorus_level": "phosphorus_ppm",
        "potassium": "potassium_meq",
        "potassiumLevel": "potassium_meq",
        "potassium_level": "potassium_meq",
        "ph": "pH",
        "pH": "pH",
        "soilPh": "pH",
        "soil_ph": "pH",
        "moisture": "soil_moisture_pct",
        "soilMoisture": "soil_moisture_pct",
        "soil_moisture": "soil_moisture_pct",
        "organic_matter": "organic_matter_pct",
        "organicMatter": "organic_matter_pct",
    }
    
    # Target parameters for the model
    TARGET_PARAMETERS = [
        "nitrogen_ppm",
        "phosphorus_ppm", 
        "potassium_meq",
        "pH",
        "soil_moisture_pct",
        "organic_matter_pct"
    ]
    
    def aggregate(self, readings: List[Dict]) -> Dict:
        """
        Aggregate sensor readings into summary statistics.
        
        Args:
            readings: List of sensor reading dictionaries from the request
            
        Returns:
            Dictionary with aggregated statistics for each parameter:
            {
                "nitrogen_ppm": {
                    "mean": 45.2,
                    "std": 2.1,
                    "min": 42.0,
                    "max": 48.0,
                    "count": 10,
                    "latest": 46.0,
                    "trend": "stable"
                },
                ...
            }
        """
        if not readings:
            raise ValueError("No readings provided for aggregation")
        
        # Normalize readings to use consistent parameter names
        normalized_readings = self._normalize_readings(readings)
        
        aggregated = {}
        
        for param in self.TARGET_PARAMETERS:
            values = [
                r[param] for r in normalized_readings 
                if param in r and r[param] is not None
            ]
            
            if values:
                aggregated[param] = {
                    "mean": round(statistics.mean(values), 2),
                    "std": round(statistics.stdev(values), 2) if len(values) > 1 else 0.0,
                    "min": round(min(values), 2),
                    "max": round(max(values), 2),
                    "count": len(values),
                    "latest": round(values[-1], 2),
                    "trend": self._calculate_trend(values)
                }
            else:
                # Parameter not found in readings
                aggregated[param] = None
        
        return aggregated
    
    def _normalize_readings(self, readings: List[Dict]) -> List[Dict]:
        """
        Normalize reading field names to consistent parameter names.
        
        Args:
            readings: Raw readings with various field name formats
            
        Returns:
            List of readings with normalized field names
        """
        normalized = []
        
        for reading in readings:
            normalized_reading = {}
            
            for key, value in reading.items():
                # Check if this key maps to a known parameter
                if key in self.PARAMETER_MAPPING:
                    param_name = self.PARAMETER_MAPPING[key]
                    normalized_reading[param_name] = value
                elif key in self.TARGET_PARAMETERS:
                    normalized_reading[key] = value
                else:
                    # Keep other fields as-is (e.g., timestamp)
                    normalized_reading[key] = value
            
            normalized.append(normalized_reading)
        
        return normalized
    
    def _calculate_trend(self, values: List[float]) -> str:
        """
        Determine if values are increasing, decreasing, or stable.
        
        Uses simple linear regression slope to determine trend direction.
        
        Args:
            values: List of numeric values in chronological order
            
        Returns:
            "increasing", "decreasing", or "stable"
        """
        if len(values) < 3:
            return "stable"
        
        # Simple linear regression slope calculation
        n = len(values)
        x_mean = (n - 1) / 2  # Mean of indices 0, 1, 2, ..., n-1
        y_mean = statistics.mean(values)
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        # Use 10% of std as threshold for significance
        std = statistics.stdev(values) if len(values) > 1 else 0
        threshold = std * 0.1 if std > 0 else 0.01
        
        if slope > threshold:
            return "increasing"
        elif slope < -threshold:
            return "decreasing"
        return "stable"
    
    def get_model_input(
        self,
        aggregated_data: Dict,
        planting_date: datetime,
        reading_date: datetime,
        historical_readings: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Prepare the full model input from aggregated data.
        
        Args:
            aggregated_data: Output from aggregate() method
            planting_date: Date when rice was planted
            reading_date: Date of current sensor reading
            historical_readings: Optional list of previous readings from DB
            
        Returns:
            Dictionary ready to send to ML service
        """
        days_since_planting = (reading_date - planting_date).days
        current_week = (days_since_planting // 7) + 1
        
        # Determine season based on month (Philippines)
        month = reading_date.month
        season = "dry" if month in [12, 1, 2, 3, 4, 5] else "wet"
        
        return {
            "current_data": aggregated_data,
            "planting_date": planting_date.isoformat(),
            "reading_date": reading_date.isoformat(),
            "current_week": current_week,
            "days_since_planting": days_since_planting,
            "season": season,
            "historical_readings": historical_readings or []
        }


# Singleton instance for use across the application
sensor_aggregator = SensorDataAggregator()
