"""
Weather data handlers for Telegram bot.

This module handles all weather API interactions and data processing
for the bot, including current weather, forecasts, and data logging.
"""
import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import pandas as pd

logger = logging.getLogger(__name__)

# BWF (Badminton World Federation) thresholds
BWF_MEDIAN_WIND_THRESHOLD = 3.33  # 12 km/h - BWF maximum
BWF_GUST_WIND_THRESHOLD = 5.0     # ~18 km/h - Allow some margin for gusts


def fetch_current_weather(lat: float, lon: float, location: str) -> Tuple[Optional[Dict], str, Optional[datetime]]:
    """
    Fetch current weather data from OpenWeatherMap API.
    
    Args:
        lat: Latitude
        lon: Longitude
        location: Location name for logging
        
    Returns:
        Tuple of (weather_dict, data_source, timestamp)
        - weather_dict: Dictionary with weather data or None
        - data_source: "live" or "sample"
        - timestamp: When data was observed or None
    """
    try:
        from src.data.weather_api import OpenWeatherMapAPI
        
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            logger.warning("No OPENWEATHER_API_KEY found")
            return None, "sample", None
        
        if not (lat and lon):
            logger.warning("No coordinates provided")
            return None, "sample", None
        
        logger.info(f"Fetching current weather for {location}")
        weather_api = OpenWeatherMapAPI(api_key)
        
        current_weather_df = weather_api.get_current_weather(lat=lat, lon=lon)
        
        if current_weather_df is not None and not current_weather_df.empty:
            current_weather = current_weather_df.iloc[0].to_dict()
            weather_data_time = current_weather_df.index[0]
            logger.info(f"Current weather: Wind {current_weather.get('wind_m_s', 0):.1f} m/s")
            
            # 📊 LOG DATA FOR FUTURE TRAINING
            try:
                from src.data.weather_logger import log_weather_data
                log_weather_data(current_weather_df, source="current")
            except Exception as log_error:
                logger.warning(f"Failed to log weather data: {log_error}")
            
            return current_weather, "live", weather_data_time
        else:
            logger.warning("Could not fetch current weather")
            return None, "sample", None
            
    except Exception as e:
        logger.error(f"Weather API error: {e}", exc_info=True)
        return None, "sample", None


def fetch_forecast_data(lat: float, lon: float, location: str, hours: int = 48):
    """
    Fetch forecast data from OpenWeatherMap API.
    
    Args:
        lat: Latitude
        lon: Longitude
        location: Location name for logging
        hours: Number of hours to forecast
        
    Returns:
        Tuple of (dataframe, data_source)
        - dataframe: Weather forecast DataFrame or None
        - data_source: "live" or "sample"
    """
    try:
        from src.data.weather_api import OpenWeatherMapAPI
        from src.data.fetch import load_sample
        
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key or not (lat and lon):
            logger.warning("No API key or coordinates, using sample data")
            return load_sample(), "sample"
        
        logger.info(f"Fetching forecast data for {location}")
        weather_api = OpenWeatherMapAPI(api_key)
        
        weather_data = weather_api.get_hourly_forecast(lat=lat, lon=lon, hours=hours)
        
        if weather_data is not None and not weather_data.empty:
            logger.info(f"✅ Using REAL weather data: {len(weather_data)} hours")
            
            # 📊 LOG FORECAST DATA FOR FUTURE TRAINING
            try:
                from src.data.weather_logger import log_weather_data
                log_weather_data(weather_data, source="forecast")
            except Exception as log_error:
                logger.warning(f"Failed to log forecast data: {log_error}")
            
            return weather_data, "live"
        else:
            logger.warning("Could not fetch forecast data, using sample")
            return load_sample(), "sample"
            
    except Exception as e:
        logger.error(f"Forecast API error: {e}", exc_info=True)
        from src.data.fetch import load_sample
        return load_sample(), "sample"


def prepare_forecast_dataframe(weather_data: List[Dict]) -> pd.DataFrame:
    """
    Prepare weather DataFrame for model input.
    
    Args:
        weather_data: Raw weather data list from API
        
    Returns:
        Processed DataFrame ready for feature engineering
    """
    import numpy as np
    
    df = weather_data.copy()

    # Normalize column names
    if "wind_direction" in df.columns and "wind_dir_deg" not in df.columns:
        df = df.rename(columns={"wind_direction": "wind_dir_deg"})

    # Drop any non-numeric columns to avoid aggregation errors
    df = df.select_dtypes(include=[np.number])

    # Ensure target column exists
    if "wind_m_s" not in df.columns:
        raise ValueError("Weather data missing 'wind_m_s' column")
    
    return df


def make_play_decision(current_weather: Dict) -> bool:
    """
    Decide if it's safe to play based on current weather.
    
    Args:
        current_weather: Dictionary with current weather data
        
    Returns:
        True if safe to play, False otherwise
    """
    wind_speed = current_weather.get('wind_m_s', 0)
    wind_gust = current_weather.get('wind_gust_m_s', 0)
    
    return (wind_speed <= BWF_MEDIAN_WIND_THRESHOLD and 
            wind_gust <= BWF_GUST_WIND_THRESHOLD)


def get_bwf_thresholds() -> Tuple[float, float]:
    """
    Get BWF-compliant wind thresholds.
    
    Returns:
        Tuple of (median_threshold, gust_threshold) in m/s
    """
    return BWF_MEDIAN_WIND_THRESHOLD, BWF_GUST_WIND_THRESHOLD
