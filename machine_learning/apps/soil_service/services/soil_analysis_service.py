"""
Soil Analysis Service

Business logic layer for soil health scoring and forecasting.
Provides:
- Health scoring (0-100 scale)
- 3-month seasonal forecasting
- Hybrid forecasting (Rule-Based + ML)
- Improvement recommendations
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging
import numpy as np

from apps.soil_service.models.soil_health_model import SoilHealthModel
from apps.soil_service.models.hybrid_forecast_model import HybridSoilForecastModel
from apps.soil_service.core.constants import SOIL_OPTIMAL_RANGES, SOIL_PARAMETER_WEIGHTS
from apps.common.utils.logging_utils import logger


class SoilAnalysisService:
    """
    Service for soil health analysis and forecasting.
    
    Provides comprehensive soil analysis including:
    - Overall health scoring (0-100)
    - Individual parameter scores
    - 3-month forecasts aligned with rice planting seasons
    - Hybrid forecasting (Rule-Based + ML combination)
    - Deficiency analysis and recommendations
    """
    
    def __init__(self):
        self.health_model: Optional[SoilHealthModel] = None
        self.hybrid_forecast_model: Optional[HybridSoilForecastModel] = None
        self._initialized = False
        
        # Auto-initialize with default/fallback models
        self._auto_initialize()
    
    def _auto_initialize(self) -> None:
        """
        Auto-initialize with rule-based fallback models.
        This ensures the service is always usable even without trained models.
        """
        try:
            self.health_model = SoilHealthModel()
            self.hybrid_forecast_model = HybridSoilForecastModel()
            self._initialized = True
            logger.info("Soil analysis service auto-initialized with rule-based models")
        except Exception as e:
            logger.error(f"Failed to auto-initialize soil analysis service: {e}")
    
    def is_ready(self) -> bool:
        """Check if service is ready to handle requests."""
        return self._initialized and self.health_model is not None
    
    async def initialize(self, model_path: str) -> None:
        """
        Initialize the service with models.
        
        Args:
            model_path: Path to the model files
        """
        try:
            self.health_model = SoilHealthModel()
            
            try:
                self.health_model.load(f"{model_path}/soil_health_model.pkl")
            except FileNotFoundError:
                logger.warning("Soil health model not found, using rule-based scoring")
            
            try:
                self.hybrid_forecast_model = HybridSoilForecastModel()
                self.hybrid_forecast_model.load(f"{model_path}/hybrid_soil_forecast.joblib")
                logger.info("Hybrid forecast model loaded successfully")
            except FileNotFoundError:
                logger.warning("Hybrid forecast model not found, using fallback methods")
                self.hybrid_forecast_model = HybridSoilForecastModel()
            except Exception as e:
                logger.warning(f"Error loading hybrid model: {e}, using fallback methods")
                self.hybrid_forecast_model = HybridSoilForecastModel()
            
            self._initialized = True
            logger.info("Soil analysis service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize soil analysis service: {e}")
            raise
    
    def _extract_soil_data(self, data: Any) -> Dict[str, float]:
        """
        Extract soil data from various input formats.
        
        Handles:
        - Request objects with soil_data attribute
        - SoilSensorData objects with get_value/to_flat_dict methods
        - Plain dictionaries with flat or aggregated values
        """
        # If it's a request object, get the nested soil_data
        if hasattr(data, 'soil_data'):
            data = data.soil_data
        elif hasattr(data, 'current_soil_data'):
            data = data.current_soil_data
        
        # If it has to_flat_dict method (SoilSensorData), use it
        if hasattr(data, 'to_flat_dict'):
            return data.to_flat_dict()
        
        # If it's a dict, normalize the values
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if value is None:
                    continue
                if isinstance(value, (int, float)):
                    result[key] = float(value)
                elif isinstance(value, dict):
                    # Aggregated format: {"mean": ..., "std": ...}
                    result[key] = value.get('mean') or value.get('latest') or 0.0
                else:
                    # Try to extract from object
                    if hasattr(value, 'mean'):
                        result[key] = float(value.mean)
                    elif hasattr(value, '__float__'):
                        result[key] = float(value)
            return result
        
        logger.warning(f"Unknown soil data format: {type(data)}")
        return {}
    
    async def analyze_health(self, request: Any) -> Dict[str, Any]:
        """
        Analyze soil health and generate health score.
        
        Args:
            request: SoilAnalysisRequest or dict with soil sensor readings
            
        Returns:
            Dictionary with overall score and parameter breakdown
        """
        if not self.is_ready():
            self._auto_initialize()
            if not self.is_ready():
                raise ValueError("Soil analysis service is not ready")
        
        # Extract soil data from request object or dict
        soil_data = self._extract_soil_data(request)
        logger.info(f"Analyzing health for soil data: {soil_data}")
        
        is_valid, errors = self._validate_soil_data(soil_data)
        if not is_valid:
            logger.warning(f"Soil data validation warnings: {errors}")
        
        health_result = self.health_model.calculate_health_score(soil_data)
        return health_result
    
    async def get_detailed_score(self, soil_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed health scoring with parameter breakdown.
        
        Args:
            soil_data: Soil sensor readings
            
        Returns:
            Detailed scoring with explanations
        """
        health_response = await self.analyze_health(soil_data)
        
        detailed_scores = {
            "overall_score": health_response["overall_score"],
            "overall_status": health_response["overall_status"],
            "score_interpretation": self._interpret_score(health_response["overall_score"]),
            "parameter_details": []
        }
        
        for param, data in health_response.get("parameter_scores", {}).items():
            detailed_scores["parameter_details"].append({
                "parameter": param,
                "value": data["value"],
                "score": data["score"],
                "status": data["status"],
                "optimal_range": data["optimal_range"],
                "interpretation": self._interpret_parameter(
                    param, data["value"], data["score"]
                )
            })
        
        detailed_scores["deficiencies"] = health_response.get("deficiencies", [])
        detailed_scores["recommendations"] = health_response.get("recommendations", [])
        
        return detailed_scores
    
    async def hybrid_forecast(
        self,
        request: Any
    ) -> Dict[str, Any]:
        """
        Generate hybrid soil forecast combining Rule-Based and ML approaches.
        
        Args:
            request: HybridForecastRequest with soil data and planting date
            
        Returns:
            Hybrid forecast response
        """
        # Extract parameters from request
        if hasattr(request, 'current_soil_data'):
            current_soil_data = self._extract_soil_data(request.current_soil_data)
            planting_date = getattr(request, 'planting_date', None)
            forecast_horizon_days = getattr(request, 'forecast_horizon_days', 90)
            forecast_interval_days = getattr(request, 'forecast_interval_days', 7)
        elif isinstance(request, dict):
            current_soil_data = self._extract_soil_data(request.get('current_soil_data', request))
            planting_date = request.get('planting_date')
            forecast_horizon_days = request.get('forecast_horizon_days', 90)
            forecast_interval_days = request.get('forecast_interval_days', 7)
        else:
            raise ValueError(f"Invalid request format: {type(request)}")
        
        logger.info(f"Generating hybrid forecast with soil data: {current_soil_data}")
        logger.info(f"Planting date: {planting_date}, Horizon: {forecast_horizon_days} days")
        
        parsed_planting_date = None
        if planting_date:
            if isinstance(planting_date, str):
                parsed_planting_date = datetime.strptime(planting_date, "%Y-%m-%d")
            else:
                parsed_planting_date = planting_date
        else:
            parsed_planting_date = datetime.now()
        
        historical_data = self._convert_current_to_historical(current_soil_data)
        
        if self.hybrid_forecast_model:
            forecast_result = self.hybrid_forecast_model.forecast_season(
                historical_data=historical_data,
                planting_date=parsed_planting_date,
                forecast_days=forecast_horizon_days,
                interval_days=forecast_interval_days
            )
        else:
            forecast_result = self._generate_fallback_forecast(
                parsed_planting_date, forecast_horizon_days
            )
        
        return {
            "planting_date": forecast_result.get('planting_date', parsed_planting_date.strftime('%Y-%m-%d')),
            "forecast_end_date": forecast_result.get('forecast_end_date', ''),
            "forecast_interval_days": forecast_interval_days,
            "approach": "hybrid",
            "detailed_forecast": forecast_result.get('detailed_forecast', []),
            "weekly_summary": forecast_result.get('weekly_summary', []),
            "model_version": self.hybrid_forecast_model.version if self.hybrid_forecast_model else "1.0",
            "generated_at": datetime.now().isoformat()
        }
    
    async def realign_forecast(
        self,
        request: Any
    ) -> Dict[str, Any]:
        """
        Realign an existing forecast with new sensor data.
        
        Args:
            request: RealignForecastRequest or dict with current_data, existing_forecast, current_week
            
        Returns:
            Realigned forecast
        """
        from apps.soil_service.services.forecast_realigner import ForecastRealignmentService
        
        # Extract parameters from request
        if hasattr(request, 'current_data'):
            current_data = request.current_data
            existing_forecast = request.existing_forecast
            current_week = request.current_week
        elif isinstance(request, dict):
            current_data = request.get('current_data', {})
            existing_forecast = request.get('existing_forecast', {})
            current_week = request.get('current_week', 1)
        else:
            raise ValueError(f"Invalid request format: {type(request)}")
        
        # Normalize current_data
        current_data = self._extract_soil_data({'soil_data': current_data}) if isinstance(current_data, dict) else current_data
        
        logger.info(f"Realigning forecast at week {current_week} with data: {current_data}")
        
        realigner = ForecastRealignmentService()
        return realigner.realign_forecast(
            original_forecast=existing_forecast,
            current_data=current_data,
            current_week=current_week
        )
    
    def _validate_soil_data(self, soil_data: Dict[str, Any]) -> tuple:
        """Validate soil sensor data."""
        errors = []
        
        if soil_data is None:
            return False, ["soil_data is required"]
        
        required_params = ["nitrogen", "phosphorus", "potassium", "ph"]
        for param in required_params:
            if param not in soil_data or soil_data[param] is None:
                errors.append(f"Missing required parameter: {param}")
        
        # Validate ranges
        for param, value in soil_data.items():
            if param in SOIL_OPTIMAL_RANGES and value is not None:
                ranges = SOIL_OPTIMAL_RANGES[param]
                if value < ranges.get("critical_low", 0) or value > ranges.get("critical_high", 999):
                    errors.append(f"{param} value {value} is outside valid range")
        
        return len(errors) == 0, errors
    
    def _convert_current_to_historical(self, soil_dict: Dict) -> Dict[str, List[float]]:
        """Convert current soil readings to historical format for hybrid model."""
        param_mapping = {
            'nitrogen': 'nitrogen_ppm',
            'phosphorus': 'phosphorus_ppm',
            'potassium': 'potassium_meq',
            'ph': 'pH',
            'moisture': 'soil_moisture_pct',
            'organic_matter': 'organic_matter_pct'
        }
        
        historical = {}
        for current_name, ml_name in param_mapping.items():
            if current_name in soil_dict and soil_dict[current_name] is not None:
                base_val = soil_dict[current_name]
                
                # Unit Check/Conversion
                if current_name == 'potassium':
                    # If value is > 20, assume it's in PPM/kg-ha range and convert to meq/100g
                    # Conversion: meq = ppm / 391 (approx for K)
                    if base_val > 10:
                        base_val = base_val / 391.0
                
                historical[ml_name] = list(
                    base_val + np.random.normal(0, base_val * 0.05, 30)
                )
        
        return historical
    
    def _generate_fallback_forecast(
        self,
        planting_date: datetime,
        horizon_days: int
    ) -> Dict[str, Any]:
        """Generate fallback forecast using rule-based only."""
        from datetime import timedelta
        
        default_baseline = {
            'dry': {
                'nitrogen_ppm': {'mean': 45, 'std': 10},
                'phosphorus_ppm': {'mean': 20, 'std': 5},
                'potassium_meq': {'mean': 0.8, 'std': 0.2},
                'pH': {'mean': 6.2, 'std': 0.3},
                'soil_moisture_pct': {'mean': 25, 'std': 8},
                'organic_matter_pct': {'mean': 3.5, 'std': 0.5}
            },
            'wet': {
                'nitrogen_ppm': {'mean': 50, 'std': 12},
                'phosphorus_ppm': {'mean': 22, 'std': 6},
                'potassium_meq': {'mean': 0.9, 'std': 0.25},
                'pH': {'mean': 6.0, 'std': 0.35},
                'soil_moisture_pct': {'mean': 40, 'std': 10},
                'organic_matter_pct': {'mean': 3.8, 'std': 0.6}
            }
        }
        
        forecasts = []
        for day_offset in range(0, horizon_days + 1, 3):
            forecast_date = planting_date + timedelta(days=day_offset)
            month = forecast_date.month
            season = 'dry' if month in [12, 1, 2, 3, 4, 5] else 'wet'
            
            row = {
                'date': forecast_date.strftime('%Y-%m-%d'),
                'week_number': (day_offset // 7) + 1,
                'season': season
            }
            
            for param in ['nitrogen_ppm', 'phosphorus_ppm', 'potassium_meq', 
                         'pH', 'soil_moisture_pct', 'organic_matter_pct']:
                baseline_val = default_baseline[season][param]['mean']
                row[param] = round(baseline_val, 2)
            
            row['soil_health_score'] = 70.0
            row['health_category'] = 'Good'
            
            # Add default status fields for fallback consistency
            row['nitrogenStatus'] = 'good'
            row['phosphorusStatus'] = 'good'
            row['potassiumStatus'] = 'good'
            row['phStatus'] = 'good'
            
            forecasts.append(row)
        
        return {
            'planting_date': planting_date.strftime('%Y-%m-%d'),
            'forecast_end_date': (planting_date + timedelta(days=horizon_days)).strftime('%Y-%m-%d'),
            'detailed_forecast': forecasts,
            'weekly_summary': []
        }
    
    def _interpret_score(self, score: float) -> str:
        """Get human-readable interpretation of overall score."""
        if score >= 80:
            return "Excellent soil health. Optimal conditions for rice cultivation."
        elif score >= 60:
            return "Good soil health. Minor improvements may enhance yield."
        elif score >= 40:
            return "Fair soil health. Several parameters need attention."
        elif score >= 20:
            return "Poor soil health. Significant improvements required before planting."
        else:
            return "Critical soil condition. Major intervention needed."
    
    def _interpret_parameter(self, parameter: str, value: float, score: float) -> str:
        """Get interpretation for a specific parameter."""
        interpretations = {
            "ph": f"Soil pH of {value} is {'optimal' if score >= 70 else 'suboptimal'} for rice.",
            "nitrogen": f"Nitrogen level is {'adequate' if score >= 70 else 'insufficient'} for healthy growth.",
            "phosphorus": f"Phosphorus is {'sufficient' if score >= 70 else 'low'} for root development.",
            "potassium": f"Potassium level is {'good' if score >= 70 else 'needs improvement'} for grain filling.",
            "organic_matter": f"Organic matter content is {'healthy' if score >= 70 else 'below optimal'}.",
            "moisture": f"Soil moisture is {'adequate' if score >= 70 else 'needs adjustment'}."
        }
        return interpretations.get(
            parameter,
            f"{parameter} score of {score:.1f} indicates {'good' if score >= 70 else 'needs attention'}."
        )
