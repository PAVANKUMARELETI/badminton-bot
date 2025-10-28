"""
Weather API connector for real-time and forecast data.

Supports multiple weather data providers:
- OpenWeatherMap (recommended)
- WeatherAPI.com
- Visual Crossing
- METAR (aviation weather)

Usage:
    from src.data.weather_api import OpenWeatherMapAPI
    
    api = OpenWeatherMapAPI(api_key="your_key")
    current = api.get_current_weather(lat=28.6139, lon=77.2090)
    forecast = api.get_hourly_forecast(lat=28.6139, lon=77.2090, hours=6)
"""

import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class WeatherAPIBase(ABC):
    """Base class for weather API connectors."""

    @abstractmethod
    def get_current_weather(self, lat: float, lon: float) -> pd.DataFrame:
        """Get current weather observations."""
        pass

    @abstractmethod
    def get_hourly_forecast(
        self, lat: float, lon: float, hours: int = 6
    ) -> pd.DataFrame:
        """Get hourly forecast for next N hours."""
        pass

    def _validate_coordinates(self, lat: float, lon: float):
        """Validate latitude and longitude."""
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")


class OpenWeatherMapAPI(WeatherAPIBase):
    """
    OpenWeatherMap API connector.
    
    Free tier: 1,000 calls/day, 60 calls/minute
    Docs: https://openweathermap.org/api
    
    Args:
        api_key: OpenWeatherMap API key
    """

    BASE_URL = "http://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenWeatherMap API key required. "
                "Set OPENWEATHER_API_KEY environment variable or pass api_key parameter."
            )

    def get_current_weather(self, lat: float, lon: float) -> pd.DataFrame:
        """
        Get current weather conditions.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            DataFrame with single row containing current conditions
        """
        self._validate_coordinates(lat, lon)

        url = f"{self.BASE_URL}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",  # Use metric units
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract relevant fields
            record = {
                "timestamp": pd.Timestamp.utcfromtimestamp(data["dt"]),
                "wind_m_s": data["wind"]["speed"],
                "wind_gust_m_s": data["wind"].get("gust", data["wind"]["speed"] * 1.3),
                "wind_direction": data["wind"].get("deg", 0),
                "temp": data["main"]["temp"],
                "pressure": data["main"]["pressure"],
                "humidity": data["main"]["humidity"],
                "weather": data["weather"][0]["description"],
                "lat": lat,
                "lon": lon,
                "source": "openweathermap",
            }

            df = pd.DataFrame([record])
            df.set_index("timestamp", inplace=True)

            logger.info(
                f"Fetched current weather: {record['wind_m_s']:.1f} m/s at ({lat}, {lon})"
            )
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching current weather: {e}")
            raise

    def get_hourly_forecast(
        self, lat: float, lon: float, hours: int = 6
    ) -> pd.DataFrame:
        """
        Get hourly weather forecast.

        Args:
            lat: Latitude
            lon: Longitude
            hours: Number of hours to forecast (max 48)

        Returns:
            DataFrame with hourly forecasts
        """
        self._validate_coordinates(lat, lon)

        if hours > 48:
            logger.warning(f"Requested {hours}h forecast, limiting to 48h")
            hours = 48

        url = f"{self.BASE_URL}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "cnt": hours,  # Number of timestamps
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract forecast records
            records = []
            for item in data["list"][:hours]:
                record = {
                    "timestamp": pd.Timestamp.utcfromtimestamp(item["dt"]),
                    "wind_m_s": item["wind"]["speed"],
                    "wind_gust_m_s": item["wind"].get(
                        "gust", item["wind"]["speed"] * 1.3
                    ),
                    "wind_direction": item["wind"].get("deg", 0),
                    "temp": item["main"]["temp"],
                    "pressure": item["main"]["pressure"],
                    "humidity": item["main"]["humidity"],
                    "weather": item["weather"][0]["description"],
                    "lat": lat,
                    "lon": lon,
                    "source": "openweathermap_forecast",
                }
                records.append(record)

            df = pd.DataFrame(records)
            df.set_index("timestamp", inplace=True)

            logger.info(f"Fetched {len(df)} hourly forecasts for ({lat}, {lon})")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching forecast: {e}")
            raise


class WeatherAPIClient(WeatherAPIBase):
    """
    WeatherAPI.com connector.
    
    Free tier: 1 million calls/month
    Docs: https://www.weatherapi.com/docs/
    
    Args:
        api_key: WeatherAPI.com API key
    """

    BASE_URL = "http://api.weatherapi.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("WEATHERAPI_KEY")
        if not self.api_key:
            raise ValueError(
                "WeatherAPI.com API key required. "
                "Set WEATHERAPI_KEY environment variable or pass api_key parameter."
            )

    def get_current_weather(self, lat: float, lon: float) -> pd.DataFrame:
        """Get current weather from WeatherAPI.com."""
        self._validate_coordinates(lat, lon)

        url = f"{self.BASE_URL}/current.json"
        params = {"key": self.api_key, "q": f"{lat},{lon}"}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            record = {
                "timestamp": pd.Timestamp(data["location"]["localtime"]),
                "wind_m_s": data["current"]["wind_kph"] / 3.6,  # Convert km/h to m/s
                "wind_gust_m_s": data["current"]["gust_kph"] / 3.6,
                "wind_direction": data["current"]["wind_degree"],
                "temp": data["current"]["temp_c"],
                "pressure": data["current"]["pressure_mb"],
                "humidity": data["current"]["humidity"],
                "weather": data["current"]["condition"]["text"],
                "lat": lat,
                "lon": lon,
                "source": "weatherapi",
            }

            df = pd.DataFrame([record])
            df.set_index("timestamp", inplace=True)

            logger.info(f"Fetched current weather from WeatherAPI.com")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather from WeatherAPI.com: {e}")
            raise

    def get_hourly_forecast(
        self, lat: float, lon: float, hours: int = 6
    ) -> pd.DataFrame:
        """Get hourly forecast from WeatherAPI.com."""
        self._validate_coordinates(lat, lon)

        # WeatherAPI.com provides up to 3 days (72 hours) of forecast
        days = min((hours // 24) + 1, 3)

        url = f"{self.BASE_URL}/forecast.json"
        params = {"key": self.api_key, "q": f"{lat},{lon}", "days": days, "hour": 24}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            records = []
            for day in data["forecast"]["forecastday"]:
                for hour in day["hour"][:hours]:
                    record = {
                        "timestamp": pd.Timestamp(hour["time"]),
                        "wind_m_s": hour["wind_kph"] / 3.6,
                        "wind_gust_m_s": hour["gust_kph"] / 3.6,
                        "wind_direction": hour["wind_degree"],
                        "temp": hour["temp_c"],
                        "pressure": hour["pressure_mb"],
                        "humidity": hour["humidity"],
                        "weather": hour["condition"]["text"],
                        "lat": lat,
                        "lon": lon,
                        "source": "weatherapi_forecast",
                    }
                    records.append(record)

            df = pd.DataFrame(records[:hours])
            df.set_index("timestamp", inplace=True)

            logger.info(f"Fetched {len(df)} hourly forecasts from WeatherAPI.com")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching forecast from WeatherAPI.com: {e}")
            raise


def get_location_coordinates(location_name: str) -> Tuple[float, float]:
    """
    Get latitude and longitude for a location name.
    
    Args:
        location_name: City name, e.g., "Delhi, India" or "Bangalore"
    
    Returns:
        Tuple of (latitude, longitude)
    """
    # Use OpenWeatherMap's geocoding API (free)
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY required for geocoding")

    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": location_name, "limit": 1, "appid": api_key}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            raise ValueError(f"Location not found: {location_name}")

        lat = data[0]["lat"]
        lon = data[0]["lon"]
        logger.info(f"Found coordinates for {location_name}: ({lat}, {lon})")
        return lat, lon

    except requests.exceptions.RequestException as e:
        logger.error(f"Error geocoding location: {e}")
        raise


# Predefined locations for common campuses
CAMPUS_LOCATIONS = {
    "bits_pilani": (28.3636, 75.5861),
    "iit_delhi": (28.5449, 77.1926),
    "iit_bombay": (19.1334, 72.9133),
    "iit_madras": (12.9916, 80.2337),
    "iit_kanpur": (26.5123, 80.2329),
    "nit_trichy": (10.7591, 78.8148),
    "delhi": (28.6139, 77.2090),
    "bangalore": (12.9716, 77.5946),
    "mumbai": (19.0760, 72.8777),
    "chennai": (13.0827, 80.2707),
    "hyderabad": (17.3850, 78.4867),
}


def get_weather_for_location(
    location: str, hours: int = 6, api_provider: str = "openweather"
) -> pd.DataFrame:
    """
    Convenience function to get weather for a named location.
    
    Args:
        location: Location name (e.g., "Delhi") or campus code (e.g., "iit_delhi")
        hours: Forecast hours
        api_provider: "openweather" or "weatherapi"
    
    Returns:
        DataFrame with current + forecast weather
    """
    # Check if it's a predefined campus
    location_key = location.lower().replace(" ", "_")
    if location_key in CAMPUS_LOCATIONS:
        lat, lon = CAMPUS_LOCATIONS[location_key]
        logger.info(f"Using predefined coordinates for {location}")
    else:
        # Geocode the location
        lat, lon = get_location_coordinates(location)

    # Get weather data
    if api_provider == "openweather":
        api = OpenWeatherMapAPI()
    elif api_provider == "weatherapi":
        api = WeatherAPIClient()
    else:
        raise ValueError(f"Unknown API provider: {api_provider}")

    # Combine current + forecast
    current = api.get_current_weather(lat, lon)
    forecast = api.get_hourly_forecast(lat, lon, hours)

    # Combine
    df = pd.concat([current, forecast])
    df = df[~df.index.duplicated(keep="first")]  # Remove duplicates
    df.sort_index(inplace=True)

    return df
