"""
External API Connector

Connects to external APIs for weather data and other external data sources.
"""

from typing import Any, Dict, List, Optional
import logging
import httpx
from datetime import datetime, timedelta

from app.config.settings import settings

logger = logging.getLogger(__name__)


class ExternalAPIConnector:
    """
    Connector for external weather and data APIs.
    
    Supports:
    - Weather API integration
    - Geocoding services
    - Other external data sources
    """
    
    def __init__(
        self,
        weather_api_key: Optional[str] = None,
        weather_api_url: Optional[str] = None
    ):
        """
        Initialize external API connector.
        
        Args:
            weather_api_key: API key for weather service
            weather_api_url: Base URL for weather API
        """
        self.weather_api_key = weather_api_key or settings.WEATHER_API_KEY
        self.weather_api_url = weather_api_url or settings.WEATHER_API_URL
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
    
    async def get_current_weather(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """
        Get current weather for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Current weather data or None if unavailable
        """
        if not self.weather_api_key or not self.weather_api_url:
            logger.warning("Weather API not configured")
            return None
        
        try:
            client = await self._get_client()
            
            # Example for OpenWeatherMap API structure
            url = f"{self.weather_api_url}/weather"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.weather_api_key,
                "units": "metric"
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return self._parse_current_weather(data)
            
        except httpx.HTTPError as e:
            logger.error(f"Weather API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return None
    
    async def get_weather_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get weather forecast for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of days to forecast
            
        Returns:
            List of daily forecasts or None if unavailable
        """
        if not self.weather_api_key or not self.weather_api_url:
            logger.warning("Weather API not configured")
            return None
        
        try:
            client = await self._get_client()
            
            # Example for forecast API structure
            url = f"{self.weather_api_url}/forecast"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.weather_api_key,
                "units": "metric",
                "cnt": days * 8  # 3-hour intervals
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return self._parse_forecast(data)
            
        except httpx.HTTPError as e:
            logger.error(f"Forecast API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return None
    
    async def get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get historical weather data for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date
            end_date: End date
            
        Returns:
            List of historical weather data or None
        """
        # Note: Many weather APIs require premium tier for historical data
        # This is a placeholder implementation
        
        logger.info(
            f"Historical weather request: {latitude}, {longitude}, "
            f"{start_date} to {end_date}"
        )
        
        # Return None to indicate data should be fetched from local database
        return None
    
    def _parse_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse current weather response from API.
        
        Args:
            data: Raw API response
            
        Returns:
            Parsed weather data
        """
        # Adjust parsing based on actual API response structure
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})
        
        return {
            "temperature": main.get("temp"),
            "temperature_feels_like": main.get("feels_like"),
            "temperature_min": main.get("temp_min"),
            "temperature_max": main.get("temp_max"),
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "wind_speed": wind.get("speed"),
            "wind_direction": wind.get("deg"),
            "condition": weather.get("main"),
            "description": weather.get("description"),
            "clouds": data.get("clouds", {}).get("all"),
            "visibility": data.get("visibility"),
            "timestamp": datetime.fromtimestamp(
                data.get("dt", datetime.now().timestamp())
            ).isoformat()
        }
    
    def _parse_forecast(
        self, 
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parse forecast response from API.
        
        Args:
            data: Raw API response
            
        Returns:
            List of daily forecasts
        """
        forecasts = []
        daily_data: Dict[str, Dict] = {}
        
        for item in data.get("list", []):
            dt = datetime.fromtimestamp(item.get("dt", 0))
            date_key = dt.strftime("%Y-%m-%d")
            
            main = item.get("main", {})
            weather = item.get("weather", [{}])[0]
            
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "temps": [],
                    "humidity": [],
                    "conditions": [],
                    "rainfall": 0
                }
            
            daily_data[date_key]["temps"].append(main.get("temp", 0))
            daily_data[date_key]["humidity"].append(main.get("humidity", 0))
            daily_data[date_key]["conditions"].append(weather.get("main", ""))
            
            # Add rainfall if present
            rain = item.get("rain", {}).get("3h", 0)
            daily_data[date_key]["rainfall"] += rain
        
        # Aggregate daily data
        for date_key, day in sorted(daily_data.items()):
            forecasts.append({
                "date": day["date"],
                "temperature_max": max(day["temps"]) if day["temps"] else None,
                "temperature_min": min(day["temps"]) if day["temps"] else None,
                "temperature_avg": sum(day["temps"]) / len(day["temps"]) if day["temps"] else None,
                "humidity": sum(day["humidity"]) / len(day["humidity"]) if day["humidity"] else None,
                "rainfall": day["rainfall"],
                "condition": max(set(day["conditions"]), key=day["conditions"].count) if day["conditions"] else None
            })
        
        return forecasts
    
    async def geocode(
        self, 
        location_name: str
    ) -> Optional[Dict[str, float]]:
        """
        Get coordinates for a location name.
        
        Args:
            location_name: Name of location to geocode
            
        Returns:
            Dictionary with latitude and longitude or None
        """
        if not self.weather_api_key or not self.weather_api_url:
            return None
        
        try:
            client = await self._get_client()
            
            # Example for OpenWeatherMap geocoding
            url = f"{self.weather_api_url.replace('/data/2.5', '/geo/1.0')}/direct"
            params = {
                "q": location_name,
                "limit": 1,
                "appid": self.weather_api_key
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data:
                return {
                    "latitude": data[0].get("lat"),
                    "longitude": data[0].get("lon"),
                    "name": data[0].get("name"),
                    "country": data[0].get("country")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Geocoding failed: {e}")
            return None
