"""
Location utilities for Telegram bot.

This module handles location parsing, geocoding, and management.
"""
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Default location configuration for IIIT Lucknow
DEFAULT_LOCATION = "IIIT Lucknow"
DEFAULT_LAT = 26.7984  # IIIT Lucknow latitude
DEFAULT_LON = 81.0241  # IIIT Lucknow longitude

# Preset locations for quick access
PRESET_LOCATIONS = {
    "iiit lucknow": (26.7984, 81.0241, "IIIT Lucknow"),
    "lucknow": (26.8467, 80.9462, "Lucknow"),
    "delhi": (28.6139, 77.2090, "Delhi"),
    "mumbai": (19.0760, 72.8777, "Mumbai"),
    "bangalore": (12.9716, 77.5946, "Bangalore"),
    "hyderabad": (17.3850, 78.4867, "Hyderabad"),
    "chennai": (13.0827, 80.2707, "Chennai"),
    "kolkata": (22.5726, 88.3639, "Kolkata"),
}


def parse_location(location_text: str) -> Tuple[Optional[float], Optional[float], str]:
    """
    Parse location text and return coordinates.
    
    Args:
        location_text: Location name or city
        
    Returns:
        Tuple of (latitude, longitude, formatted_name)
        Returns (None, None, location_text) if not found
    """
    location_lower = location_text.lower().strip()
    
    # Check if it's a preset location
    if location_lower in PRESET_LOCATIONS:
        lat, lon, name = PRESET_LOCATIONS[location_lower]
        logger.info(f"Found preset location: {name} ({lat}, {lon})")
        return lat, lon, name
    
    # Check if user wants to return to default
    if "iiit" in location_lower and "lucknow" in location_lower:
        logger.info("Returning to default location: IIIT Lucknow")
        return DEFAULT_LAT, DEFAULT_LON, DEFAULT_LOCATION
    
    # TODO: Implement geocoding API (Google Maps, OpenStreetMap Nominatim)
    # For now, return None if not in presets
    logger.warning(f"Location '{location_text}' not found in presets")
    return None, None, location_text


def get_default_location() -> Tuple[float, float, str]:
    """
    Get default location coordinates.
    
    Returns:
        Tuple of (latitude, longitude, name)
    """
    return DEFAULT_LAT, DEFAULT_LON, DEFAULT_LOCATION


def format_coordinates(lat: float, lon: float) -> str:
    """
    Format coordinates for display.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Formatted string like "26.7984°N, 81.0241°E"
    """
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"
    return f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}"
