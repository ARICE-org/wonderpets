"""
Forecast Realignment Service

Handles realignment of forecasts with new sensor data.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import logging

from apps.common.utils.logging_utils import logger


class ForecastRealignmentService:
    """
    Service for realigning forecasts with new sensor data.
    
    When new sensor readings arrive, this service adjusts future
    forecasts to reflect actual conditions while preserving
    the overall forecast structure.
    """
    
    def __init__(self):
        self._initialized = True
    
    def realign_forecast(
        self,
        original_forecast: Dict[str, Any],
        current_data: Optional[Dict[str, float]] = None,
        current_week: int = 1,
        new_planting_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Realign an existing forecast with new sensor data.
        
        Args:
            original_forecast: The original forecast data
            current_data: Current sensor readings to realign with
            current_week: Current week in the planting cycle
            new_planting_date: Optional new planting date (YYYY-MM-DD)
            
        Returns:
            Realigned forecast with updated predictions
        """
        try:
            # Calculate date offset if new planting date provided
            if new_planting_date:
                new_date = datetime.strptime(new_planting_date, "%Y-%m-%d")
                original_date_str = original_forecast.get("planting_date", "")
                if original_date_str:
                    original_date = datetime.strptime(original_date_str, "%Y-%m-%d")
                else:
                    original_date = datetime.now()
                date_offset = (new_date - original_date).days
            else:
                date_offset = 0
                new_planting_date = original_forecast.get("planting_date", datetime.now().strftime("%Y-%m-%d"))
            
            # Realign forecasts
            realigned_forecast = self._realign_detailed_forecast(
                original_forecast.get("detailed_forecast", []),
                date_offset,
                current_data,
                current_week
            )
            
            realigned_weekly = self._realign_weekly_summary(
                original_forecast.get("weekly_summary", []),
                date_offset,
                current_data,
                current_week
            )
            
            new_end_date = self._calculate_new_end_date(
                original_forecast.get("forecast_end_date", ""),
                date_offset
            )
            
            return {
                "planting_date": new_planting_date,
                "forecast_end_date": new_end_date,
                "forecast_interval_days": original_forecast.get("forecast_interval_days", 7),
                "approach": original_forecast.get("approach", "hybrid") + "_realigned",
                "detailed_forecast": realigned_forecast,
                "weekly_summary": realigned_weekly,
                "model_version": original_forecast.get("model_version", "1.0"),
                "generated_at": datetime.now().isoformat(),
                "realignment_info": {
                    "original_planting_date": original_forecast.get("planting_date", ""),
                    "new_planting_date": new_planting_date,
                    "date_offset_days": date_offset,
                    "realigned_at_week": current_week,
                    "current_data_used": current_data is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Error realigning forecast: {e}")
            raise ValueError(f"Failed to realign forecast: {e}")
    
    def _realign_detailed_forecast(
        self,
        detailed_forecast: List[Dict[str, Any]],
        date_offset: int,
        current_data: Optional[Dict[str, float]] = None,
        current_week: int = 1
    ) -> List[Dict[str, Any]]:
        """Realign detailed forecast entries with new data."""
        realigned = []
        
        for entry in detailed_forecast:
            new_entry = entry.copy()
            week_num = entry.get("week_number", 0)
            
            if "date" in entry:
                try:
                    original_date = datetime.strptime(entry["date"], "%Y-%m-%d")
                    new_date = original_date + timedelta(days=date_offset)
                    new_entry["date"] = new_date.strftime("%Y-%m-%d")
                    
                    # Update season based on new date
                    month = new_date.month
                    new_entry["season"] = 'dry' if month in [12, 1, 2, 3, 4, 5] else 'wet'
                except ValueError:
                    pass
            
            # Apply adjustment based on current data for future weeks
            if current_data and week_num >= current_week:
                new_entry = self._apply_data_adjustment(new_entry, current_data, week_num, current_week)
            
            realigned.append(new_entry)
        
        return realigned
    
    def _realign_weekly_summary(
        self,
        weekly_summary: List[Dict[str, Any]],
        date_offset: int,
        current_data: Optional[Dict[str, float]] = None,
        current_week: int = 1
    ) -> List[Dict[str, Any]]:
        """Realign weekly summary entries with new data."""
        realigned = []
        
        for entry in weekly_summary:
            new_entry = entry.copy()
            week_num = entry.get("week_number", 0)
            
            for date_field in ["week_start", "week_end", "start_date", "end_date"]:
                if date_field in entry:
                    try:
                        original_date = datetime.strptime(entry[date_field], "%Y-%m-%d")
                        new_date = original_date + timedelta(days=date_offset)
                        new_entry[date_field] = new_date.strftime("%Y-%m-%d")
                    except ValueError:
                        pass
            
            # Apply adjustment based on current data for future weeks
            if current_data and week_num >= current_week:
                new_entry = self._apply_data_adjustment(new_entry, current_data, week_num, current_week)
            
            realigned.append(new_entry)
        
        return realigned
    
    def _apply_data_adjustment(
        self,
        entry: Dict[str, Any],
        current_data: Dict[str, float],
        week_num: int,
        current_week: int
    ) -> Dict[str, Any]:
        """
        Apply adjustment to forecast entry based on current sensor data.
        
        Uses decay factor: the further from current week, the less impact.
        """
        # Mapping from sensor params to forecast params
        param_mapping = {
            'nitrogen': 'nitrogen_ppm',
            'phosphorus': 'phosphorus_ppm',
            'potassium': 'potassium_meq',
            'ph': 'pH',
            'moisture': 'soil_moisture_pct',
            'organic_matter': 'organic_matter_pct'
        }
        
        # Decay factor: closer weeks get more adjustment
        weeks_ahead = week_num - current_week
        decay_factor = max(0.1, 1.0 - (weeks_ahead * 0.1))  # Minimum 10% impact
        
        for sensor_param, forecast_param in param_mapping.items():
            if sensor_param in current_data and forecast_param in entry:
                current_val = current_data[sensor_param]
                forecast_val = entry[forecast_param]
                
                # Blend current value with forecast, weighted by decay
                if isinstance(forecast_val, (int, float)) and isinstance(current_val, (int, float)):
                    adjusted = (current_val * decay_factor) + (forecast_val * (1 - decay_factor))
                    entry[forecast_param] = round(adjusted, 2)
        
        return entry
    
    def _calculate_new_end_date(
        self,
        original_end_date: str,
        date_offset: int
    ) -> str:
        """Calculate new forecast end date."""
        if not original_end_date:
            return ""
        
        try:
            original_date = datetime.strptime(original_end_date, "%Y-%m-%d")
            new_date = original_date + timedelta(days=date_offset)
            return new_date.strftime("%Y-%m-%d")
        except ValueError:
            return original_end_date
    
    def validate_realignment_request(
        self,
        original_forecast: Dict[str, Any],
        new_planting_date: str
    ) -> tuple:
        """
        Validate a realignment request.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not original_forecast:
            errors.append("Original forecast is required")
        
        if not new_planting_date:
            errors.append("New planting date is required")
        else:
            try:
                new_date = datetime.strptime(new_planting_date, "%Y-%m-%d")
                
                # Check if date is in the past (warning only)
                if new_date.date() < datetime.now().date():
                    logger.warning(f"New planting date {new_planting_date} is in the past")
            except ValueError:
                errors.append("Invalid date format. Use YYYY-MM-DD")
        
        if not original_forecast.get("detailed_forecast"):
            errors.append("Original forecast must contain detailed_forecast data")
        
        return len(errors) == 0, errors
