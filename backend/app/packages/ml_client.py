"""
ML Service Client Module

HTTP client for Backend to communicate with ML Service.
Frontend never uses this directly - all ML communication goes through Backend.
"""

import httpx
from typing import Dict, Optional, Any
from datetime import date, datetime
from pydantic import BaseModel
from app.config.settings import settings


class MLForecastResponse(BaseModel):
    """Response from ML service forecast endpoints."""
    health_score: float
    health_category: str
    forecast: Dict[str, Any]
    weekly_summary: list
    model_info: Optional[Dict[str, Any]] = None


class MLHealthScoreResponse(BaseModel):
    """Response from ML service health score endpoint."""
    health_score: float
    health_category: str
    parameter_scores: Dict[str, float]


class MLServiceClient:
    """
    HTTP client for Backend to communicate with ML Service.
    Frontend never uses this directly.
    
    This client abstracts all communication with the ML service,
    allowing the backend to:
    1. Generate new forecasts
    2. Realign existing forecasts
    3. Calculate health scores
    4. Check ML service health
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the ML service client.
        
        Args:
            base_url: Base URL for ML service. Defaults to ML_SERVICE_URL from settings.
        """
        self.base_url = base_url or getattr(settings, 'ML_SERVICE_URL', 'http://localhost:8001')
        self.timeout = 30.0  # seconds
    
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
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/soil/hybrid-forecast",
                json={
                    "current_soil_data": self._format_current_data(current_data),
                    "planting_date": planting_date.isoformat() if isinstance(planting_date, date) else planting_date,
                    "forecast_horizon_days": forecast_horizon_days,
                    "forecast_interval_days": forecast_interval_days
                }
            )
            response.raise_for_status()
            return MLForecastResponse(**response.json())
    
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
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/soil/realign-forecast",
                json={
                    "current_data": current_data,
                    "existing_forecast": existing_forecast,
                    "current_week": current_week
                }
            )
            response.raise_for_status()
            return MLForecastResponse(**response.json())
    
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
                f"{self.base_url}/api/soil/health-score",
                json={"soil_data": soil_data}
            )
            response.raise_for_status()
            return MLHealthScoreResponse(**response.json())
    
    async def health_check(self) -> bool:
        """
        Check if ML service is available and healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
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


# Factory function for dependency injection
def get_ml_client() -> MLServiceClient:
    """Get ML service client instance."""
    return MLServiceClient()


# Singleton instance for simple use cases
ml_client = MLServiceClient()
