"""
Weather service API dependencies.
"""

from functools import lru_cache

from apps.weather_service.services.weather_service import WeatherService


@lru_cache()
def get_weather_service() -> WeatherService:
    """Get or create weather service singleton."""
    return WeatherService()
