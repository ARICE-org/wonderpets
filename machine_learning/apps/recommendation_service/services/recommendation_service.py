"""
Recommendation Service

Business logic layer for rice variety recommendations.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from apps.recommendation_service.models.rice_variety_model import RiceVarietyRecommendationModel
from apps.recommendation_service.core.constants import (
    RICE_VARIETIES,
    VARIETY_REQUIREMENTS,
    PLANTING_SEASONS,
)
from apps.common.utils.logging_utils import logger


class RecommendationService:
    """
    Service for rice variety recommendations.
    
    Handles the full pipeline from input validation to
    formatted recommendation output.
    """
    
    def __init__(self):
        self.model: Optional[RiceVarietyRecommendationModel] = None
        self._initialized = False
        self._auto_initialize()
    
    def _auto_initialize(self) -> None:
        """Auto-initialize with fallback models."""
        try:
            self.model = RiceVarietyRecommendationModel()
            self._initialized = True
            logger.info("Recommendation service auto-initialized")
        except Exception as e:
            logger.error(f"Failed to auto-initialize recommendation service: {e}")
    
    def is_ready(self) -> bool:
        """Check if service is ready."""
        return self._initialized
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        if self.model:
            return {
                "name": self.model.model_name,
                "version": self.model.version,
                "is_trained": self.model.is_trained
            }
        return {"status": "not_loaded"}
    
    async def initialize(self, model_path: str) -> None:
        """Initialize the service with trained models."""
        try:
            self.model = RiceVarietyRecommendationModel()
            try:
                self.model.load(model_path)
                logger.info("Recommendation model loaded successfully")
            except FileNotFoundError:
                logger.warning("Recommendation model not found, using rule-based")
            
            self._initialized = True
            logger.info("Recommendation service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize recommendation service: {e}")
            raise
    
    async def get_recommendations(
        self,
        soil_data: Optional[Dict[str, Any]] = None,
        weather_data: Optional[Dict[str, Any]] = None,
        location: Optional[Dict[str, Any]] = None,
        season: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Get rice variety recommendations based on conditions.
        
        Args:
            soil_data: Soil conditions
            weather_data: Weather conditions
            location: Farm location
            season: Planting season
            top_k: Number of recommendations
            
        Returns:
            Recommendations with scores
        """
        is_valid, errors = self._validate_input(soil_data, location)
        if not is_valid:
            raise ValueError(f"Invalid input: {', '.join(errors)}")
        
        if self.model and self.model.is_trained:
            input_features = self._prepare_features(
                soil_data, weather_data, location, season
            )
            predictions = self.model.get_top_recommendations(input_features, top_k=top_k)
        else:
            predictions = self._rule_based_recommendations(
                soil_data, weather_data, location, season, top_k
            )
        
        return {
            "recommendations": predictions,
            "input_summary": {
                "soil_health_score": self._calculate_soil_score(soil_data) if soil_data else None,
                "weather_outlook": self._get_weather_outlook(weather_data) if weather_data else None,
                "season": season,
                "location_region": location.get("region") if location else None
            },
            "total_varieties_considered": len(RICE_VARIETIES),
            "generated_at": datetime.now().isoformat()
        }
    
    async def get_planting_schedule(
        self,
        location: Optional[Dict[str, Any]] = None,
        variety: Optional[str] = None,
        target_harvest_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get optimal planting schedule."""
        current_month = datetime.now().month
        
        # Determine recommended season
        if current_month in [10, 11, 12, 1, 2]:
            season = "dry_season"
            season_info = PLANTING_SEASONS["dry_season"]
        else:
            season = "wet_season"
            season_info = PLANTING_SEASONS["wet_season"]
        
        # Calculate planting window
        if target_harvest_date:
            harvest = datetime.strptime(target_harvest_date, "%Y-%m-%d")
            maturity_days = 115  # Default
            if variety and variety in RICE_VARIETIES:
                maturity_days = RICE_VARIETIES[variety].get("maturity_days", 115)
            
            optimal_plant_date = harvest - timedelta(days=maturity_days)
            start_date = optimal_plant_date - timedelta(days=14)
            end_date = optimal_plant_date + timedelta(days=14)
        else:
            # Use seasonal defaults
            now = datetime.now()
            month = season_info["months"][0]
            start_date = datetime(now.year if month >= now.month else now.year + 1, month, 1)
            end_date = start_date + timedelta(days=45)
            optimal_plant_date = start_date + timedelta(days=15)
        
        return {
            "location": location,
            "variety": variety,
            "recommended_planting_window": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "optimal_date": optimal_plant_date.strftime("%Y-%m-%d")
            },
            "season_type": season,
            "recommendations": season_info.get("considerations", "").split(", ") if isinstance(season_info.get("considerations"), str) else [],
            "generated_at": datetime.now().isoformat()
        }
    
    def get_available_varieties(self) -> List[Dict[str, Any]]:
        """Get list of all available varieties."""
        return [
            {
                "id": variety_id,
                "name": variety["name"],
                "maturity_days": variety["maturity_days"],
                "yield_potential": variety["yield_potential_tha"],
                "quality": variety.get("grain_quality", "Good")
            }
            for variety_id, variety in RICE_VARIETIES.items()
        ]
    
    def get_variety_details(self, variety_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific variety."""
        if variety_id in RICE_VARIETIES:
            variety = RICE_VARIETIES[variety_id].copy()
            variety["id"] = variety_id
            if variety_id in VARIETY_REQUIREMENTS:
                variety["requirements"] = VARIETY_REQUIREMENTS[variety_id]
            return variety
        return None
    
    def _validate_input(
        self,
        soil_data: Optional[Dict],
        location: Optional[Dict]
    ) -> tuple:
        """Validate input parameters."""
        errors = []
        
        # At least some data should be provided
        if not soil_data and not location:
            errors.append("At least soil_data or location is required")
        
        return len(errors) == 0, errors
    
    def _prepare_features(
        self,
        soil_data: Optional[Dict],
        weather_data: Optional[Dict],
        location: Optional[Dict],
        season: Optional[str]
    ) -> Dict[str, Any]:
        """Prepare features for model prediction."""
        features = {}
        
        if soil_data:
            features.update({f"soil_{k}": v for k, v in soil_data.items()})
        
        if weather_data:
            features.update({f"weather_{k}": v for k, v in weather_data.items()})
        
        if location:
            features.update({f"location_{k}": v for k, v in location.items()})
        
        features["season"] = season or "unknown"
        
        return features
    
    def _rule_based_recommendations(
        self,
        soil_data: Optional[Dict],
        weather_data: Optional[Dict],
        location: Optional[Dict],
        season: Optional[str],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Rule-based recommendations when model not available."""
        scores = []
        
        for variety_id, variety in RICE_VARIETIES.items():
            score = self._calculate_variety_score(
                variety_id, variety, soil_data, weather_data, season
            )
            scores.append({
                "variety_id": variety_id,
                "variety_name": variety["name"],
                "score": score,
                "variety_info": variety
            })
        
        # Sort by score descending
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Format top-k results
        recommendations = []
        for rank, item in enumerate(scores[:top_k], 1):
            recommendations.append({
                "rank": rank,
                "variety_id": item["variety_id"],
                "variety_name": item["variety_name"],
                "confidence_score": round(item["score"] / 100, 2),
                "match_score": round(item["score"], 1),
                "maturity_days": item["variety_info"]["maturity_days"],
                "yield_potential_tha": item["variety_info"]["yield_potential_tha"],
                "grain_quality": item["variety_info"].get("grain_quality", "Good"),
                "strengths": self._get_variety_strengths(item["variety_info"]),
                "recommendation_reason": self._get_recommendation_reason(
                    item["variety_id"], soil_data, weather_data, season
                )
            })
        
        return recommendations
    
    def _calculate_variety_score(
        self,
        variety_id: str,
        variety: Dict,
        soil_data: Optional[Dict],
        weather_data: Optional[Dict],
        season: Optional[str]
    ) -> float:
        """Calculate match score for a variety."""
        score = 50  # Base score
        
        requirements = VARIETY_REQUIREMENTS.get(variety_id, {})
        
        # Soil matching
        if soil_data and requirements:
            ph_range = requirements.get("ph_range", (5.5, 7.0))
            ph = soil_data.get("ph", 6.5)
            if ph_range[0] <= ph <= ph_range[1]:
                score += 15
            elif abs(ph - sum(ph_range)/2) < 1:
                score += 8
        
        # Weather matching
        if weather_data and requirements:
            temp_range = requirements.get("temperature_range", (20, 35))
            temp = weather_data.get("temperature_avg", 28)
            if temp_range[0] <= temp <= temp_range[1]:
                score += 10
            
            # Flood/drought tolerance
            if weather_data.get("is_flood_prone") and variety.get("submergence_tolerance"):
                score += 15
            if weather_data.get("is_drought_prone") and variety.get("drought_tolerance"):
                score += 15
        
        # Season matching
        if season:
            season_key = f"{season}_season" if not season.endswith("_season") else season
            if season_key in PLANTING_SEASONS:
                recommended = PLANTING_SEASONS[season_key].get("recommended_varieties", [])
                if variety_id in recommended:
                    score += 10
        
        # Quality bonus
        if variety.get("grain_quality") == "Premium":
            score += 5
        
        return min(100, score)
    
    def _calculate_soil_score(self, soil_data: Dict) -> float:
        """Calculate overall soil health score."""
        score = 70  # Base score
        
        ph = soil_data.get("ph", 6.5)
        if 5.5 <= ph <= 7.0:
            score += 10
        
        return min(100, score)
    
    def _get_weather_outlook(self, weather_data: Dict) -> str:
        """Get weather outlook description."""
        if weather_data.get("is_flood_prone"):
            return "Flood risk present"
        if weather_data.get("is_drought_prone"):
            return "Drought risk present"
        return "Favorable"
    
    def _get_variety_strengths(self, variety: Dict) -> List[str]:
        """Get list of variety strengths."""
        strengths = []
        
        if variety.get("yield_potential_tha", 0) >= 7:
            strengths.append("High yield potential")
        if variety.get("grain_quality") == "Premium":
            strengths.append("Premium grain quality")
        if variety.get("maturity_days", 120) <= 100:
            strengths.append("Early maturity")
        if variety.get("drought_tolerance"):
            strengths.append("Drought tolerant")
        if variety.get("submergence_tolerance"):
            strengths.append("Flood tolerant")
        if variety.get("disease_resistance"):
            strengths.append(f"Resistant to: {', '.join(variety['disease_resistance'][:2])}")
        
        return strengths[:4]  # Limit to 4 strengths
    
    def _get_recommendation_reason(
        self,
        variety_id: str,
        soil_data: Optional[Dict],
        weather_data: Optional[Dict],
        season: Optional[str]
    ) -> str:
        """Generate recommendation reason."""
        variety = RICE_VARIETIES.get(variety_id, {})
        reasons = []
        
        if variety.get("yield_potential_tha", 0) >= 7:
            reasons.append("high yield potential")
        
        if weather_data:
            if weather_data.get("is_drought_prone") and variety.get("drought_tolerance"):
                reasons.append("suited for drought conditions")
            if weather_data.get("is_flood_prone") and variety.get("submergence_tolerance"):
                reasons.append("flood tolerant")
        
        if soil_data:
            soil_type = soil_data.get("soil_type")
            requirements = VARIETY_REQUIREMENTS.get(variety_id, {})
            if soil_type and soil_type in requirements.get("soil_type", []):
                reasons.append(f"well-suited for {soil_type} soil")
        
        if not reasons:
            reasons.append("general good performance")
        
        return f"Recommended for {', '.join(reasons)}"
