"""
Forecast Realigner Module

Realigns forecasts when new actual data deviates from predictions.
This is a key feature for maintaining accurate soil forecasts over time.

Key Concept:
- Calculate deviation between predicted vs actual
- Apply correction factor to remaining forecast
- Blend rule-based adjustment with ML correction
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CorrectionStrategy(str, Enum):
    """Strategies for forecast correction."""
    SHIFT = "SHIFT"  # Add constant offset to all remaining predictions
    DECAYING_SHIFT = "DECAYING_SHIFT"  # Apply decaying offset over time
    REFORECAST = "REFORECAST"  # Full reforecast with new baseline


@dataclass
class DeviationInfo:
    """Information about deviation between predicted and actual values."""
    predicted: float
    actual: float
    deviation: float
    deviation_pct: float
    strategy: CorrectionStrategy
    reason: str


@dataclass
class CorrectionInfo:
    """Correction to be applied to forecast."""
    strategy: CorrectionStrategy
    offset: Optional[float] = None
    initial_offset: Optional[float] = None
    decay_rate: Optional[float] = None
    scale_factor: Optional[float] = None
    reason: str = ""


class ForecastRealigner:
    """
    Realigns forecasts when new actual data deviates from predictions.
    
    This class handles the critical task of updating forecasts based on
    real sensor data, ensuring predictions stay accurate throughout
    the planting season.
    """
    
    # Target parameters to realign
    TARGET_PARAMETERS = [
        "nitrogen_ppm",
        "phosphorus_ppm",
        "potassium_meq",
        "pH",
        "soil_moisture_pct",
        "organic_matter_pct"
    ]
    
    # Deviation thresholds for correction strategy selection
    SMALL_DEVIATION_THRESHOLD = 5.0   # < 5% = small deviation
    MEDIUM_DEVIATION_THRESHOLD = 15.0  # 5-15% = medium deviation
    # > 15% = large deviation (triggers reforecast)
    
    def __init__(self, hybrid_model=None):
        """
        Initialize the forecast realigner.
        
        Args:
            hybrid_model: Optional hybrid forecast model for reforecasting
        """
        self.hybrid_model = hybrid_model
    
    def realign_forecast(
        self,
        active_forecast: Dict,
        new_reading: Dict,
        current_week: int
    ) -> Dict:
        """
        Realign forecast based on new sensor reading.
        
        Args:
            active_forecast: The existing forecast for this planting season
            new_reading: New sensor data (aggregated with mean, std, etc.)
            current_week: Which week of the forecast we're in (1-12)
        
        Returns:
            Dictionary containing:
            - realignment_date: When realignment occurred
            - week_of_realignment: Current week number
            - deviations: Dict of parameter deviations
            - corrections_applied: Dict of corrections for each parameter
            - updated_forecast: List of updated weekly predictions
            - health_score: Updated health score
            - weekly_summary: Updated weekly summary
        """
        realignment_result = {
            "realignment_date": datetime.now().isoformat(),
            "week_of_realignment": current_week,
            "deviations": {},
            "corrections_applied": {},
            "updated_forecast": {},
            "requires_reforecast": False
        }
        
        # Extract the prediction for current week from active forecast
        current_week_prediction = self._get_week_prediction(
            active_forecast, current_week
        )
        
        # Calculate deviations for each parameter
        for param in self.TARGET_PARAMETERS:
            # Get predicted value for this week
            predicted = current_week_prediction.get(param)
            
            # Get actual value from new reading
            actual = self._extract_actual_value(new_reading, param)
            
            if predicted is not None and actual is not None:
                # Calculate deviation
                deviation = actual - predicted
                deviation_pct = (deviation / predicted) * 100 if predicted != 0 else 0
                
                # Determine correction strategy
                correction = self._calculate_correction(
                    param=param,
                    deviation=deviation,
                    deviation_pct=deviation_pct,
                    remaining_weeks=12 - current_week,
                    current_trend=self._get_trend(new_reading, param)
                )
                
                realignment_result["deviations"][param] = {
                    "predicted": round(predicted, 2),
                    "actual": round(actual, 2),
                    "deviation": round(deviation, 2),
                    "deviation_pct": round(deviation_pct, 1),
                    "strategy": correction.strategy.value
                }
                
                realignment_result["corrections_applied"][param] = {
                    "strategy": correction.strategy.value,
                    "reason": correction.reason,
                    "offset": correction.offset,
                    "initial_offset": correction.initial_offset,
                    "decay_rate": correction.decay_rate
                }
                
                # Check if reforecast is needed
                if correction.strategy == CorrectionStrategy.REFORECAST:
                    realignment_result["requires_reforecast"] = True
        
        # Apply corrections to remaining forecast
        if realignment_result["requires_reforecast"]:
            # Generate new forecast from current state
            updated_forecast = self._reforecast_from_current(
                new_reading=new_reading,
                current_week=current_week,
                remaining_weeks=12 - current_week
            )
        else:
            # Apply corrections to existing forecast
            updated_forecast = self._apply_corrections_to_forecast(
                original_forecast=active_forecast,
                corrections=realignment_result["corrections_applied"],
                start_week=current_week + 1
            )
        
        realignment_result["updated_forecast"] = updated_forecast
        realignment_result["weekly_summary"] = self._build_weekly_summary(
            updated_forecast, current_week
        )
        realignment_result["health_score"] = self._calculate_health_score(new_reading)
        
        return realignment_result
    
    def _get_week_prediction(
        self,
        forecast: Dict,
        week: int
    ) -> Dict:
        """Extract prediction for a specific week from forecast."""
        # Try different forecast structures
        
        # Structure 1: weekly_summary list
        if "weekly_summary" in forecast:
            for week_data in forecast["weekly_summary"]:
                if week_data.get("week") == week:
                    return week_data
        
        # Structure 2: forecast.weekly_summary
        if "forecast" in forecast and "weekly_summary" in forecast["forecast"]:
            for week_data in forecast["forecast"]["weekly_summary"]:
                if week_data.get("week") == week:
                    return week_data
        
        # Structure 3: week_{n} keys
        week_key = f"week_{week}"
        if week_key in forecast:
            return forecast[week_key]
        
        # Default: return empty dict
        logger.warning(f"Could not find prediction for week {week}")
        return {}
    
    def _extract_actual_value(self, reading: Dict, param: str) -> Optional[float]:
        """Extract actual value from reading (handles aggregated structure)."""
        if param not in reading:
            return None
        
        value = reading[param]
        
        if isinstance(value, dict):
            # Aggregated format with mean, std, etc.
            return value.get("mean", value.get("latest"))
        else:
            return value
    
    def _get_trend(self, reading: Dict, param: str) -> str:
        """Get trend for a parameter from reading."""
        if param not in reading:
            return "stable"
        
        value = reading[param]
        if isinstance(value, dict):
            return value.get("trend", "stable")
        return "stable"
    
    def _calculate_correction(
        self,
        param: str,
        deviation: float,
        deviation_pct: float,
        remaining_weeks: int,
        current_trend: str
    ) -> CorrectionInfo:
        """
        Calculate how to correct the forecast based on deviation.
        
        Correction Strategies:
        1. SHIFT: Add constant offset to all remaining predictions
        2. DECAYING_SHIFT: Apply decaying offset over time
        3. REFORECAST: Generate new forecast from current state
        """
        abs_deviation_pct = abs(deviation_pct)
        
        # Small deviation (< 5%): Apply simple shift
        if abs_deviation_pct < self.SMALL_DEVIATION_THRESHOLD:
            return CorrectionInfo(
                strategy=CorrectionStrategy.SHIFT,
                offset=deviation * 0.5,  # Apply half the deviation as offset
                reason="Minor deviation - applying slight offset"
            )
        
        # Medium deviation (5-15%): Apply decaying shift
        elif abs_deviation_pct < self.MEDIUM_DEVIATION_THRESHOLD:
            # Adjust decay based on trend
            if current_trend == "increasing" and deviation > 0:
                decay_rate = 0.15  # Faster decay if trend reinforces deviation
            elif current_trend == "decreasing" and deviation < 0:
                decay_rate = 0.15
            else:
                decay_rate = 0.1  # Standard decay
            
            return CorrectionInfo(
                strategy=CorrectionStrategy.DECAYING_SHIFT,
                initial_offset=deviation * 0.7,
                decay_rate=decay_rate,
                reason="Moderate deviation - applying decaying correction"
            )
        
        # Large deviation (> 15%): Recommend reforecast
        else:
            return CorrectionInfo(
                strategy=CorrectionStrategy.REFORECAST,
                reason="Significant deviation - recommending reforecast from current state"
            )
    
    def _apply_corrections_to_forecast(
        self,
        original_forecast: Dict,
        corrections: Dict[str, Dict],
        start_week: int
    ) -> Dict:
        """Apply corrections to remaining forecast weeks."""
        updated = {}
        
        # Get the weekly data from forecast
        weekly_data = []
        if "weekly_summary" in original_forecast:
            weekly_data = original_forecast["weekly_summary"]
        elif "forecast" in original_forecast and "weekly_summary" in original_forecast["forecast"]:
            weekly_data = original_forecast["forecast"]["weekly_summary"]
        
        updated_weekly = []
        
        for week_data in weekly_data:
            week_num = week_data.get("week", 0)
            
            if week_num < start_week:
                # Keep past weeks unchanged
                updated_weekly.append(week_data)
            else:
                # Apply corrections to future weeks
                updated_week = dict(week_data)
                weeks_from_correction = week_num - start_week
                
                for param, correction in corrections.items():
                    if param not in week_data:
                        continue
                    
                    original_value = week_data[param]
                    if original_value is None:
                        continue
                    
                    strategy = correction.get("strategy")
                    
                    if strategy == "SHIFT":
                        offset = correction.get("offset", 0)
                        new_value = original_value + offset
                    
                    elif strategy == "DECAYING_SHIFT":
                        initial_offset = correction.get("initial_offset", 0)
                        decay_rate = correction.get("decay_rate", 0.1)
                        decay_factor = (1 - decay_rate) ** weeks_from_correction
                        new_value = original_value + (initial_offset * decay_factor)
                    
                    else:
                        new_value = original_value
                    
                    updated_week[param] = round(new_value, 2)
                
                updated_week["realigned"] = True
                updated_week["correction_applied"] = True
                updated_weekly.append(updated_week)
        
        updated["weekly_summary"] = updated_weekly
        return updated
    
    def _reforecast_from_current(
        self,
        new_reading: Dict,
        current_week: int,
        remaining_weeks: int
    ) -> Dict:
        """
        Generate new forecast from current state when deviation is too large.
        
        This uses the hybrid model if available, otherwise falls back to
        simple projection.
        """
        if self.hybrid_model and hasattr(self.hybrid_model, 'forecast_season'):
            # Use hybrid model for reforecast
            try:
                # Convert reading to historical format
                historical_data = self._reading_to_historical(new_reading)
                
                forecast_result = self.hybrid_model.forecast_season(
                    historical_data=historical_data,
                    planting_date=datetime.now() - timedelta(weeks=current_week),
                    forecast_days=remaining_weeks * 7,
                    interval_days=7
                )
                
                return forecast_result
            except Exception as e:
                logger.warning(f"Hybrid reforecast failed: {e}, using fallback")
        
        # Fallback: simple projection from current values
        return self._simple_projection(new_reading, current_week, remaining_weeks)
    
    def _simple_projection(
        self,
        current_data: Dict,
        current_week: int,
        remaining_weeks: int
    ) -> Dict:
        """Generate simple projection when ML model is unavailable."""
        weekly_summary = []
        
        for week_offset in range(remaining_weeks):
            week_num = current_week + week_offset + 1
            week_data = {"week": week_num, "realigned": True}
            
            for param in self.TARGET_PARAMETERS:
                base_value = self._extract_actual_value(current_data, param)
                if base_value is not None:
                    trend = self._get_trend(current_data, param)
                    
                    # Apply simple trend-based projection
                    if trend == "increasing":
                        projected = base_value * (1 + 0.02 * week_offset)
                    elif trend == "decreasing":
                        projected = base_value * (1 - 0.02 * week_offset)
                    else:
                        # Slight oscillation for stable
                        projected = base_value * (1 + 0.005 * week_offset * ((-1) ** week_offset))
                    
                    week_data[param] = round(projected, 2)
            
            weekly_summary.append(week_data)
        
        return {"weekly_summary": weekly_summary}
    
    def _reading_to_historical(self, reading: Dict) -> List[Dict]:
        """Convert aggregated reading to historical format for model."""
        record = {"date": datetime.now().strftime("%Y-%m-%d")}
        
        for param in self.TARGET_PARAMETERS:
            value = self._extract_actual_value(reading, param)
            if value is not None:
                record[param] = value
        
        return [record]
    
    def _build_weekly_summary(
        self,
        updated_forecast: Dict,
        current_week: int
    ) -> List[Dict]:
        """Build weekly summary from updated forecast."""
        weekly_summary = updated_forecast.get("weekly_summary", [])
        
        # Ensure each week has a health score
        for week_data in weekly_summary:
            if "health_score" not in week_data:
                week_data["health_score"] = self._calculate_week_health_score(week_data)
        
        return weekly_summary
    
    def _calculate_health_score(self, reading: Dict) -> float:
        """Calculate overall health score from reading."""
        # Optimal ranges for rice cultivation
        optimal_ranges = {
            "nitrogen_ppm": {"min": 40, "max": 80, "optimal": 60},
            "phosphorus_ppm": {"min": 15, "max": 40, "optimal": 25},
            "potassium_meq": {"min": 0.5, "max": 1.5, "optimal": 1.0},
            "pH": {"min": 5.5, "max": 7.0, "optimal": 6.2},
            "soil_moisture_pct": {"min": 25, "max": 50, "optimal": 35},
            "organic_matter_pct": {"min": 2.0, "max": 6.0, "optimal": 4.0},
        }
        
        weights = {
            "nitrogen_ppm": 0.20,
            "phosphorus_ppm": 0.15,
            "potassium_meq": 0.15,
            "pH": 0.20,
            "soil_moisture_pct": 0.15,
            "organic_matter_pct": 0.15,
        }
        
        total_score = 0
        total_weight = 0
        
        for param, ranges in optimal_ranges.items():
            value = self._extract_actual_value(reading, param)
            if value is not None:
                weight = weights.get(param, 0.1)
                score = self._param_score(value, ranges)
                total_score += score * weight
                total_weight += weight
        
        if total_weight > 0:
            return round((total_score / total_weight) * 100, 1)
        return 50.0
    
    def _calculate_week_health_score(self, week_data: Dict) -> float:
        """Calculate health score for a week's prediction."""
        return self._calculate_health_score(week_data)
    
    def _param_score(self, value: float, ranges: Dict) -> float:
        """Calculate score (0-1) for a parameter value."""
        min_val = ranges["min"]
        max_val = ranges["max"]
        optimal = ranges["optimal"]
        
        if min_val <= value <= max_val:
            # In range: 0.7 - 1.0 based on distance from optimal
            if value <= optimal:
                distance = (value - min_val) / (optimal - min_val) if optimal != min_val else 1
            else:
                distance = (max_val - value) / (max_val - optimal) if max_val != optimal else 1
            return 0.7 + (0.3 * distance)
        else:
            # Out of range: 0 - 0.7 based on how far out
            if value < min_val:
                distance = (min_val - value) / min_val if min_val != 0 else 1
            else:
                distance = (value - max_val) / max_val if max_val != 0 else 1
            return max(0, 0.7 - (0.7 * min(distance, 1)))


# Singleton instance
forecast_realigner = ForecastRealigner()
