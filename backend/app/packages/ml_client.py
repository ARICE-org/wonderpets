import httpx
from typing import Dict, Optional, Any, List
from datetime import date, datetime
from pydantic import BaseModel
from app.config.settings import settings
import logging

from urllib.parse import urlparse

logger = logging.getLogger("uvicorn")


def _normalize_base_url(raw_url: str) -> str:
    url = (raw_url or "").strip()
    if not url:
        return url

    # Common typo: "http:/host" or "https:/host" (missing one slash)
    if url.startswith("http:/") and not url.startswith("http://"):
        url = "http://" + url[len("http:/"):]
    elif url.startswith("https:/") and not url.startswith("https://"):
        url = "https://" + url[len("https:/"):]

    # If scheme is missing, default to http://
    if "://" not in url:
        url = "http://" + url

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported ML base URL scheme in: {raw_url}")
    if not parsed.netloc:
        raise ValueError(f"Invalid ML base URL (missing host): {raw_url}")

    return url.rstrip("/")


# ============================================================================
# Response Models
# ============================================================================

class MLForecastResponse(BaseModel):
    """Response from ML service forecast endpoints."""
    planting_date: str
    forecast_end_date: str
    forecast_interval_days: int
    approach: str = "hybrid"
    detailed_forecast: List[Dict[str, Any]]
    weekly_summary: List[Dict[str, Any]]
    model_version: str = "1.0"
    generated_at: str
    
    @property
    def forecast(self) -> Dict[str, Any]:
        """Provide forecast dict for backward compatibility."""
        return {
            "weekly_summary": self.weekly_summary,
            "detailed_forecast": self.detailed_forecast
        }
    
    @property
    def health_score(self) -> float:
        """Calculate health score from weekly summary."""
        if self.weekly_summary:
            scores = [w.get("soil_health_score", 70) for w in self.weekly_summary]
            return sum(scores) / len(scores) if scores else 70.0
        return 70.0
    
    @property
    def health_category(self) -> str:
        """Get health category from first week."""
        if self.weekly_summary:
            return self.weekly_summary[0].get("health_category", "Good")
        return "Good"


class MLHealthScoreResponse(BaseModel):
    """Response from ML service health score endpoint."""
    health_score: float
    health_category: str
    parameter_scores: Dict[str, float]


# ============================================================================
# Base ML Client
# ============================================================================

class BaseMLClient:
    """Base class for ML service clients with common functionality."""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = _normalize_base_url(base_url)
        self.timeout = timeout
        logger.info(f"[MLClient] Using base_url={self.base_url}")
    
    async def health_check(self) -> bool:
        """Check if ML service is available and healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False


# ============================================================================
# Soil ML Client
# ============================================================================

class SoilMLClient(BaseMLClient):
    """Client for Soil ML Service (port 8001)."""
    
    def __init__(self, base_url: Optional[str] = None):
        # Use SOIL_ML_URL if set, otherwise fall back to ML_SERVICE_URL
        url = base_url or settings.SOIL_ML_URL or settings.ML_SERVICE_URL
        super().__init__(url)
    
    async def generate_forecast(
        self,
        current_data: Dict,
        planting_date: date,
        forecast_horizon_days: int = 90,
        forecast_interval_days: int = 7
    ) -> MLForecastResponse:
        """
        Call ML service to generate new forecast.
        
        Args:
            current_data: Aggregated sensor data with summary statistics
            planting_date: Date when rice was planted
            forecast_horizon_days: How many days to forecast (default 90 = 3 months)
            forecast_interval_days: Interval between forecast points (default 7 = weekly)
            
        Returns:
            MLForecastResponse with forecast data
        """
        url = f"{self.base_url}/api/v1/soil/hybrid-forecast"
        payload = {
            "current_soil_data": self._format_current_data(current_data),
            "planting_date": planting_date.isoformat() if isinstance(planting_date, date) else planting_date,
            "forecast_horizon_days": forecast_horizon_days,
            "forecast_interval_days": forecast_interval_days,
        }
        logger.info(f"[SoilML] POST {url}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                logger.info(f"[SoilML] Response {response.status_code} from {url}")
                response.raise_for_status()
                return MLForecastResponse(**response.json())
            except Exception as exc:
                logger.exception(f"[SoilML] Failed calling {url}: {exc}")
                raise
    
    async def realign_forecast(
        self,
        current_data: Dict,
        existing_forecast: Dict,
        current_week: int
    ) -> MLForecastResponse:
        """
        Call ML service to realign existing forecast based on new data.
        
        Args:
            current_data: New aggregated sensor data
            existing_forecast: The current forecast data to realign
            current_week: Which week of the planting cycle we're in
            
        Returns:
            MLForecastResponse with realigned forecast
        """
        url = f"{self.base_url}/api/v1/soil/realign-forecast"
        payload = {
            "current_data": current_data,
            "existing_forecast": existing_forecast,
            "current_week": current_week,
        }
        logger.info(f"[SoilML] POST {url}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                logger.info(f"[SoilML] Response {response.status_code} from {url}")
                response.raise_for_status()
                return MLForecastResponse(**response.json())
            except Exception as exc:
                logger.exception(f"[SoilML] Failed calling {url}: {exc}")
                raise
    
    async def calculate_health_score(
        self,
        soil_data: Dict
    ) -> MLHealthScoreResponse:
        """
        Call ML service to calculate current soil health score.
        
        Args:
            soil_data: Current soil data (can be raw or aggregated)
            
        Returns:
            MLHealthScoreResponse with health score and category
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/soil/analyze",
                json={"soil_data": soil_data}
            )
            response.raise_for_status()
            return MLHealthScoreResponse(**response.json())
    
    def _format_current_data(self, current_data: Dict) -> Dict:
        """
        Format current data for ML service consumption.
        
        Ensures the data structure matches what the ML model expects.
        """
        formatted = {}
        
        for param, values in current_data.items():
            if values is None:
                continue
            
            if isinstance(values, dict):
                # Already aggregated with statistics
                formatted[param] = values
            else:
                # Simple value, wrap it
                formatted[param] = {
                    "mean": values,
                    "std": 0.0,
                    "min": values,
                    "max": values,
                    "count": 1,
                    "latest": values,
                    "trend": "stable"
                }
        
        return formatted


# ============================================================================
# Weather ML Client
# ============================================================================

class WeatherMLClient(BaseMLClient):
    """Client for Weather ML Service (port 8002)."""
    
    def __init__(self, base_url: Optional[str] = None):
        # Use WEATHER_ML_URL if set, otherwise fall back to ML_SERVICE_URL
        url = base_url or settings.WEATHER_ML_URL or settings.ML_SERVICE_URL
        super().__init__(url)
    
    async def get_forecast(
        self,
        location: Dict[str, float],
        forecast_days: int = 7
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            location: Dict with 'latitude' and 'longitude'
            forecast_days: Number of days to forecast
            
        Returns:
            Weather forecast data
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/weather/forecast",
                json={
                    "location": location,
                    "forecast_days": forecast_days
                }
            )
            response.raise_for_status()
            return response.json()


# ============================================================================
# Recommendation ML Client
# ============================================================================

class RecommendationMLClient(BaseMLClient):
    """Client for Recommendation ML Service (port 8003)."""
    
    def __init__(self, base_url: Optional[str] = None):
        # Use RECOMMENDATION_ML_URL if set, otherwise fall back to ML_SERVICE_URL
        url = base_url or settings.RECOMMENDATION_ML_URL or settings.ML_SERVICE_URL
        super().__init__(url)
    
    async def get_recommendations(
        self,
        soil_data: Dict[str, Any],
        weather_data: Optional[Dict[str, Any]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get rice variety recommendations.
        
        Args:
            soil_data: Current soil conditions
            weather_data: Optional weather forecast data
            preferences: Optional user preferences
            
        Returns:
            Recommendation results
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/recommendation/varieties",
                json={
                    "soil_data": soil_data,
                    "weather_data": weather_data,
                    "preferences": preferences
                }
            )
            response.raise_for_status()
            return response.json()


# ============================================================================
# Legacy MLServiceClient (backward compatibility)
# ============================================================================

class MLServiceClient(SoilMLClient):
    """
    Legacy ML Service Client for backward compatibility.
    
    This class is an alias for SoilMLClient since the original client
    was soil-specific in practice. New code should use the domain-specific
    clients (SoilMLClient, WeatherMLClient, RecommendationMLClient).
    """
    pass


# ============================================================================
# Factory Functions
# ============================================================================

def get_soil_ml_client() -> SoilMLClient:
    """Get Soil ML service client instance."""
    return SoilMLClient()


def get_weather_ml_client() -> WeatherMLClient:
    """Get Weather ML service client instance."""
    return WeatherMLClient()


def get_recommendation_ml_client() -> RecommendationMLClient:
    """Get Recommendation ML service client instance."""
    return RecommendationMLClient()


# Legacy factory function for backward compatibility
def get_ml_client() -> MLServiceClient:
    """Get ML service client instance (legacy - use domain-specific clients)."""
    return MLServiceClient()


# ============================================================================
# Singleton Instances
# ============================================================================

# Domain-specific clients
soil_ml_client = SoilMLClient()
weather_ml_client = WeatherMLClient()
recommendation_ml_client = RecommendationMLClient()

# Legacy singleton for backward compatibility
ml_client = MLServiceClient()
