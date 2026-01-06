"""
Soil Analysis Service

Business logic layer for soil health scoring and forecasting.
Provides:
- Health scoring (0-100 scale)
- 3-month seasonal forecasting
- Hybrid forecasting (Rule-Based + ML)
- Improvement recommendations
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from app.models.soil import (
    SoilHealthModel,
    HybridSoilForecastModel,
    SoilFeatureEngineer,
    SoilDataPreprocessor
)
from app.schemas.soil import (
    SoilAnalysisRequest,
    SoilHealthResponse,
    SoilForecastRequest,
    SoilForecastResponse,
    ParameterScore,
    HybridForecastRequest,
    HybridForecastResponse
)

logger = logging.getLogger(__name__)


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
        self.feature_engineer: Optional[SoilFeatureEngineer] = None
        self.preprocessor: Optional[SoilDataPreprocessor] = None
        self._initialized = False
        
        # Auto-initialize with default/fallback models
        self._auto_initialize()
    
    def _auto_initialize(self) -> None:
        """
        Auto-initialize with rule-based fallback models.
        This ensures the service is always usable even without trained models.
        """
        try:
            # Initialize with rule-based models (no external files needed)
            self.health_model = SoilHealthModel()
            self.hybrid_forecast_model = HybridSoilForecastModel()
            self.feature_engineer = SoilFeatureEngineer()
            self.preprocessor = SoilDataPreprocessor()
            self._initialized = True
            logger.info("Soil analysis service auto-initialized with rule-based models")
        except Exception as e:
            logger.error(f"Failed to auto-initialize soil analysis service: {e}")
            # Service will still work but with limited functionality
    
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
            # Initialize health model (rule-based initially)
            self.health_model = SoilHealthModel()
            
            # Try to load trained health model if available
            try:
                self.health_model.load(f"{model_path}/soil_health_model.pkl")
            except FileNotFoundError:
                logger.warning("Soil health model not found, using rule-based scoring")
            
            # Initialize hybrid forecast model
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
            
            self.feature_engineer = SoilFeatureEngineer()
            self.preprocessor = SoilDataPreprocessor()
            
            self._initialized = True
            logger.info("Soil analysis service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize soil analysis service: {e}")
            raise
    
    async def analyze_health(
        self,
        request: SoilAnalysisRequest
    ) -> SoilHealthResponse:
        """
        Analyze soil health and generate health score.
        
        Args:
            request: Soil analysis request with sensor data
            
        Returns:
            SoilHealthResponse with overall score and parameter breakdown
        """
        # Ensure service is ready
        if not self.is_ready():
            self._auto_initialize()
            if not self.is_ready():
                raise ValueError("Soil analysis service is not ready. Models failed to initialize.")
        
        # Validate input
        is_valid, errors = self._validate_soil_data(request.soil_data)
        if not is_valid:
            logger.warning(f"Soil data validation warnings: {errors}")
        
        # Prepare data for scoring
        soil_data = self._prepare_soil_data(request)
        
        # Get health score
        health_result = self.health_model._calculate_health_score(soil_data)
        
        # Format response
        return self._format_health_response(health_result, request)
    
    async def get_detailed_score(
        self,
        request: SoilAnalysisRequest
    ) -> Dict[str, Any]:
        """
        Get detailed health scoring with parameter breakdown.
        
        Args:
            request: Soil analysis request
            
        Returns:
            Detailed scoring with explanations
        """
        health_response = await self.analyze_health(request)
        
        # Add detailed explanations
        detailed_scores = {
            "overall_score": health_response.overall_score,
            "overall_status": health_response.overall_status,
            "score_interpretation": self._interpret_score(health_response.overall_score),
            "parameter_details": []
        }
        
        for param_score in health_response.parameter_scores:
            detailed_scores["parameter_details"].append({
                "parameter": param_score.parameter,
                "value": param_score.value,
                "score": param_score.score,
                "status": param_score.status,
                "optimal_range": param_score.optimal_range,
                "interpretation": self._interpret_parameter(
                    param_score.parameter,
                    param_score.value,
                    param_score.score
                )
            })
        
        detailed_scores["deficiencies"] = health_response.deficiencies
        detailed_scores["recommendations"] = health_response.recommendations
        
        return detailed_scores
    
    async def forecast_season(
        self,
        request: SoilForecastRequest
    ) -> SoilForecastResponse:
        """
        Generate 3-month soil condition forecast for planting season.
        Uses the hybrid forecast model.
        
        Args:
            request: Forecast request with historical data and planting date
            
        Returns:
            SoilForecastResponse with seasonal predictions
        """
        # Parse planting date
        planting_date = None
        if request.planting_date:
            planting_date = datetime.strptime(request.planting_date, "%Y-%m-%d")
        
        # Prepare historical data
        historical_data = self._prepare_historical_data(request)
        
        # Generate forecast using hybrid model
        forecast_result = self.hybrid_forecast_model.forecast_season(
            historical_data=historical_data,
            planting_date=planting_date,
            interval_days=7  # Weekly forecasts
        )
        
        # Format response
        return self._format_forecast_response(forecast_result)
    
    async def hybrid_forecast(
        self,
        request: HybridForecastRequest
    ) -> HybridForecastResponse:
        """
        Generate hybrid soil forecast combining Rule-Based and ML approaches.
        
        This is the core thesis contribution - a hybrid approach that:
        1. Uses soil science rules for baseline predictions (explainability)
        2. Applies ML to learn residuals/corrections (accuracy)
        3. Combines both for robust and interpretable forecasts
        
        Args:
            request: Hybrid forecast request with soil data and parameters
            
        Returns:
            HybridForecastResponse with predictions from all approaches
        """
        # Parse planting date
        planting_date = None
        if request.planting_date:
            planting_date = datetime.strptime(request.planting_date, "%Y-%m-%d")
        else:
            planting_date = datetime.now()
        
        # Prepare historical data from request
        historical_data = None
        if request.historical_data:
            historical_data = request.historical_data
        elif request.current_soil_data:
            # Convert current readings to historical format
            soil_dict = request.current_soil_data.model_dump()
            historical_data = self._convert_current_to_historical(soil_dict)
        
        # Generate hybrid forecast
        if self.hybrid_forecast_model:
            forecast_result = self.hybrid_forecast_model.forecast_season(
                historical_data=historical_data,
                planting_date=planting_date,
                forecast_days=request.forecast_horizon_days,
                interval_days=request.forecast_interval_days
            )
        else:
            # Fallback to rule-based only
            forecast_result = self._generate_fallback_forecast(
                planting_date, request.forecast_horizon_days
            )
        
        # Format response (simplified - only hybrid values)
        return HybridForecastResponse(
            planting_date=forecast_result.get('planting_date', planting_date.strftime('%Y-%m-%d')),
            forecast_end_date=forecast_result.get('forecast_end_date', ''),
            forecast_interval_days=request.forecast_interval_days,
            approach="hybrid",
            detailed_forecast=forecast_result.get('detailed_forecast', []),
            weekly_summary=forecast_result.get('weekly_summary', []),
            model_version=self.hybrid_forecast_model.version if self.hybrid_forecast_model else "1.0",
            generated_at=datetime.now().isoformat()
        )
    
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
                # Create pseudo-historical with slight variations
                base_val = soil_dict[current_name]
                # Simulate 30 days of historical data
                import numpy as np
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
        
        forecasts = []
        rules = self.hybrid_forecast_model.rules if self.hybrid_forecast_model else None
        
        # Default baselines if no model
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
        
        for day_offset in range(0, horizon_days + 1, 3):
            forecast_date = planting_date + timedelta(days=day_offset)
            month = forecast_date.month
            season = 'dry' if month in [12, 1, 2, 3, 4, 5] else 'wet'
            
            row = {
                'date': forecast_date.strftime('%Y-%m-%d'),
                'week_number': (day_offset // 7) + 1,
                'season': season
            }
            
            # Use baseline values (hybrid values only)
            for param in ['nitrogen_ppm', 'phosphorus_ppm', 'potassium_meq', 
                         'pH', 'soil_moisture_pct', 'organic_matter_pct']:
                baseline_val = default_baseline[season][param]['mean']
                row[param] = round(baseline_val, 2)
            
            row['soil_health_score'] = 70.0
            row['health_category'] = 'Good'
            forecasts.append(row)
        
        return {
            'planting_date': planting_date.strftime('%Y-%m-%d'),
            'forecast_end_date': (planting_date + timedelta(days=horizon_days)).strftime('%Y-%m-%d'),
            'detailed_forecast': forecasts,
            'weekly_summary': []
        }
    
    async def get_seasonal_forecast(
        self,
        request: SoilForecastRequest
    ) -> Dict[str, Any]:
        """
        Get forecast aligned with rice growth stages.
        
        Args:
            request: Forecast request
            
        Returns:
            Forecast with growth stage alignment
        """
        forecast = await self.forecast_season(request)
        
        return {
            "planting_date": forecast.planting_date,
            "forecast_end_date": forecast.forecast_end_date,
            "growth_stage_timeline": forecast.growth_stage_timeline,
            "weekly_summary": forecast.weekly_summary,
            "stage_alerts": forecast.stage_alerts,
            "overall_outlook": forecast.overall_outlook,
            "recommendations_by_stage": self._get_stage_recommendations(
                forecast.growth_stage_timeline,
                forecast.stage_alerts
            )
        }
    
    async def get_recommendations(
        self,
        request: SoilAnalysisRequest
    ) -> Dict[str, Any]:
        """
        Get soil improvement recommendations.
        
        Args:
            request: Soil analysis request
            
        Returns:
            Prioritized recommendations
        """
        health_result = await self.analyze_health(request)
        
        # Prioritize recommendations by severity
        prioritized_recommendations = []
        
        for i, rec in enumerate(health_result.recommendations):
            priority = "high" if health_result.parameter_scores[i].score < 40 else \
                       "medium" if health_result.parameter_scores[i].score < 60 else "low"
            
            prioritized_recommendations.append({
                "recommendation": rec,
                "priority": priority,
                "expected_improvement": self._estimate_improvement(
                    health_result.parameter_scores[i].parameter
                )
            })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        prioritized_recommendations.sort(key=lambda x: priority_order[x["priority"]])
        
        return {
            "current_health_score": health_result.overall_score,
            "recommendations": prioritized_recommendations,
            "estimated_score_after_improvements": self._estimate_improved_score(
                health_result.overall_score,
                prioritized_recommendations
            )
        }
    
    def _validate_soil_data(self, soil_data: Any) -> tuple:
        """Validate soil sensor data."""
        errors = []
        
        if soil_data is None:
            return False, ["soil_data is required"]
        
        # Use preprocessor validation if available
        if self.preprocessor:
            data_dict = soil_data.model_dump() if hasattr(soil_data, 'model_dump') else soil_data
            return self.preprocessor.validate_sensor_reading(data_dict)
        
        return True, errors
    
    def _prepare_soil_data(self, request: SoilAnalysisRequest) -> Dict[str, float]:
        """Prepare soil data for analysis."""
        data = request.soil_data.model_dump() if hasattr(request.soil_data, 'model_dump') else request.soil_data
        
        if self.preprocessor:
            return self.preprocessor.prepare_for_health_scoring(data)
        
        return data
    
    def _prepare_historical_data(self, request: SoilForecastRequest) -> Dict[str, Any]:
        """Prepare historical data for forecasting."""
        if request.historical_data:
            return request.historical_data
        
        # If no historical data, use current readings
        if request.current_soil_data:
            return {
                param: [value]
                for param, value in request.current_soil_data.model_dump().items()
            }
        
        return {}
    
    def _format_health_response(
        self,
        health_result: Dict[str, Any],
        request: SoilAnalysisRequest
    ) -> SoilHealthResponse:
        """Format health result into response schema."""
        parameter_scores = [
            ParameterScore(
                parameter=param,
                value=data["value"],
                score=data["score"],
                status=data["status"],
                optimal_range=data["optimal_range"]
            )
            for param, data in health_result.get("parameter_scores", {}).items()
        ]
        
        return SoilHealthResponse(
            overall_score=health_result.get("overall_score", 0),
            overall_status=health_result.get("overall_status", "Unknown"),
            parameter_scores=parameter_scores,
            deficiencies=health_result.get("deficiencies", []),
            recommendations=health_result.get("recommendations", []),
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _format_forecast_response(
        self,
        forecast_result: Dict[str, Any]
    ) -> SoilForecastResponse:
        """Format forecast result into response schema."""
        return SoilForecastResponse(
            planting_date=forecast_result.get("planting_date"),
            forecast_end_date=forecast_result.get("forecast_end_date"),
            location=forecast_result.get("location"),
            growth_stage_timeline=forecast_result.get("growth_stage_timeline", []),
            parameter_forecasts=forecast_result.get("parameter_forecasts", {}),
            weekly_summary=forecast_result.get("weekly_summary", []),
            stage_alerts=forecast_result.get("stage_alerts", []),
            overall_outlook=forecast_result.get("overall_outlook", {})
        )
    
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
    
    def _interpret_parameter(
        self,
        parameter: str,
        value: float,
        score: float
    ) -> str:
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
    
    def _get_stage_recommendations(
        self,
        timeline: List[Dict],
        alerts: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for each growth stage."""
        recommendations = []
        
        for stage in timeline:
            stage_name = stage.get("stage")
            stage_alerts = next(
                (a for a in alerts if a.get("stage") == stage_name),
                {"alerts": []}
            )
            
            recommendations.append({
                "stage": stage_name,
                "period": f"{stage.get('start_date')} to {stage.get('end_date')}",
                "focus_parameters": stage.get("critical_parameters", []),
                "alerts": stage_alerts.get("alerts", []),
                "actions": self._get_stage_actions(stage_name)
            })
        
        return recommendations
    
    def _get_stage_actions(self, stage: str) -> List[str]:
        """Get recommended actions for each growth stage."""
        actions = {
            "seedling": [
                "Maintain adequate moisture levels",
                "Monitor nitrogen availability",
                "Check for pest damage"
            ],
            "tillering": [
                "Apply nitrogen fertilizer if deficient",
                "Ensure proper water management",
                "Monitor for diseases"
            ],
            "panicle_initiation": [
                "Apply phosphorus and potassium",
                "Maintain consistent water levels",
                "Watch for nutrient deficiency symptoms"
            ],
            "flowering": [
                "Avoid water stress",
                "Protect from extreme temperatures",
                "Monitor potassium levels"
            ],
            "grain_filling": [
                "Maintain moisture for grain development",
                "Reduce nitrogen to prevent lodging",
                "Prepare for harvest timing"
            ]
        }
        
        return actions.get(stage, ["Monitor soil conditions regularly"])
    
    def _estimate_improvement(self, parameter: str) -> str:
        """Estimate expected improvement from recommendation."""
        improvements = {
            "ph": "5-15% score improvement in 2-4 weeks",
            "nitrogen": "10-20% score improvement in 1-2 weeks",
            "phosphorus": "5-10% score improvement in 2-3 weeks",
            "potassium": "5-10% score improvement in 1-2 weeks",
            "organic_matter": "2-5% score improvement in 4-8 weeks",
            "moisture": "Immediate improvement with proper irrigation"
        }
        
        return improvements.get(parameter, "Varies based on implementation")
    
    def _estimate_improved_score(
        self,
        current_score: float,
        recommendations: List[Dict]
    ) -> float:
        """Estimate overall score after implementing recommendations."""
        improvement = 0
        
        for rec in recommendations:
            if rec["priority"] == "high":
                improvement += 10
            elif rec["priority"] == "medium":
                improvement += 5
            else:
                improvement += 2
        
        return min(100, current_score + improvement)
