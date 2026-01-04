from .recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RiceVarietyRecommendation,
    ScheduleRequest,
    ScheduleResponse,
    SoilDataInput,
    WeatherDataInput,
    LocationInput
)
from .weather import (
    WeatherForecastRequest,
    WeatherForecastResponse,
    DailyWeatherForecast
)
from .soil import (
    SoilAnalysisRequest,
    SoilHealthResponse,
    SoilForecastRequest,
    SoilForecastResponse,
    SoilSensorData,
    ParameterScore
)

__all__ = [
    # Recommendation
    "RecommendationRequest",
    "RecommendationResponse",
    "RiceVarietyRecommendation",
    "ScheduleRequest",
    "ScheduleResponse",
    "SoilDataInput",
    "WeatherDataInput",
    "LocationInput",
    # Weather
    "WeatherForecastRequest",
    "WeatherForecastResponse",
    "DailyWeatherForecast",
    # Soil
    "SoilAnalysisRequest",
    "SoilHealthResponse",
    "SoilForecastRequest",
    "SoilForecastResponse",
    "SoilSensorData",
    "ParameterScore"
]
