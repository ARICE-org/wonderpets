"""
Soil Analysis Service

Business logic layer for soil health scoring and forecasting.
Provides:
- Health scoring (0-100 scale)
- 3-month seasonal forecasting
- Improvement recommendations
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from app.models.soil import (
    SoilHealthModel,
    SoilForecastModel,
    SoilFeatureEngineer,
    SoilDataPreprocessor
)
from app.schemas.soil import (
    SoilAnalysisRequest,
    SoilHealthResponse,
    SoilForecastRequest,
    SoilForecastResponse,
    ParameterScore
)

logger = logging.getLogger(__name__)


class SoilAnalysisService:
    """
    Service for soil health analysis and forecasting.
    
    Provides comprehensive soil analysis including:
    - Overall health scoring (0-100)
    - Individual parameter scores
    - 3-month forecasts aligned with rice planting seasons
    - Deficiency analysis and recommendations
    """
    
    def __init__(self):
        self.health_model: Optional[SoilHealthModel] = None
        self.forecast_model: Optional[SoilForecastModel] = None
        self.feature_engineer: Optional[SoilFeatureEngineer] = None
        self.preprocessor: Optional[SoilDataPreprocessor] = None
        self._initialized = False
    
    async def initialize(self, model_path: str) -> None:
        """
        Initialize the service with models.
        
        Args:
            model_path: Path to the model files
        """
        try:
            # Initialize health model (rule-based initially)
            self.health_model = SoilHealthModel()
            
            # Initialize forecast model
            self.forecast_model = SoilForecastModel()
            
            # Try to load trained models if available
            try:
                self.health_model.load(f"{model_path}/soil_health_model.pkl")
            except FileNotFoundError:
                logger.warning("Soil health model not found, using rule-based scoring")
            
            try:
                self.forecast_model.load(f"{model_path}/soil_forecast_model.pkl")
            except FileNotFoundError:
                logger.warning("Soil forecast model not found, forecasting will be limited")
            
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
        
        # Generate forecast
        forecast_result = self.forecast_model.forecast_season(
            historical_data=historical_data,
            planting_date=planting_date,
            location=request.location.model_dump() if request.location else None
        )
        
        # Format response
        return self._format_forecast_response(forecast_result)
    
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
    
    def is_ready(self) -> bool:
        """Check if service is ready to handle requests."""
        return self._initialized
