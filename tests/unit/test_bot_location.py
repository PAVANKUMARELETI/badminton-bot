"""Unit tests for bot_location module."""
import pytest

from src.integrations.bot_location import (
    parse_location,
    get_default_location,
    format_coordinates,
    PRESET_LOCATIONS,
    DEFAULT_LOCATION,
    DEFAULT_LAT,
    DEFAULT_LON,
)


class TestBotLocation:
    """Test location parsing and management functions."""

    def test_get_default_location(self):
        """Test getting default location."""
        lat, lon, name = get_default_location()
        
        assert lat == DEFAULT_LAT
        assert lon == DEFAULT_LON
        assert name == DEFAULT_LOCATION
        assert isinstance(lat, float)
        assert isinstance(lon, float)
        assert isinstance(name, str)

    def test_parse_location_iiit_lucknow(self):
        """Test parsing IIIT Lucknow location."""
        lat, lon, name = parse_location("IIIT Lucknow")
        
        assert lat == 26.7984
        assert lon == 81.0241
        assert name == "IIIT Lucknow"

    def test_parse_location_case_insensitive(self):
        """Test that location parsing is case-insensitive."""
        # Test various cases
        for location_text in ["delhi", "DELHI", "Delhi", "DeLhI"]:
            lat, lon, name = parse_location(location_text)
            assert lat == 28.6139
            assert lon == 77.2090
            assert name == "Delhi"

    def test_parse_location_with_whitespace(self):
        """Test parsing location with extra whitespace."""
        lat, lon, name = parse_location("  mumbai  ")
        
        assert lat == 19.0760
        assert lon == 72.8777
        assert name == "Mumbai"

    def test_parse_all_preset_locations(self):
        """Test parsing all preset locations."""
        for location_key, (expected_lat, expected_lon, expected_name) in PRESET_LOCATIONS.items():
            lat, lon, name = parse_location(location_key)
            
            assert lat == expected_lat
            assert lon == expected_lon
            assert name == expected_name

    def test_parse_location_unknown(self):
        """Test parsing unknown location."""
        lat, lon, name = parse_location("Unknown City")

        assert lat is None
        assert lon is None
        assert name == "Unknown City"  # Returns original text, not "Unknown Location"    def test_parse_location_empty_string(self):
        """Test parsing empty string."""
        lat, lon, name = parse_location("")

        assert lat is None
        assert lon is None
        assert name == ""  # Returns original text (empty string)

    def test_format_coordinates_north_east(self):
        """Test formatting coordinates for northern/eastern location."""
        formatted = format_coordinates(28.6139, 77.2090)

        # Uses 4 decimal places
        assert "28.6139" in formatted
        assert "77.2090" in formatted
        assert "°N" in formatted
        assert "°E" in formatted

    def test_format_coordinates_south_west(self):
        """Test formatting coordinates for southern/western location."""
        formatted = format_coordinates(-33.8688, -151.2093)  # Sydney

        # Uses 4 decimal places
        assert "33.8688" in formatted
        assert "151.2093" in formatted
        assert "°S" in formatted
        assert "°W" in formatted

    def test_format_coordinates_precision(self):
        """Test coordinate formatting precision."""
        formatted = format_coordinates(26.846789, 80.946234)

        # Uses 4 decimal places
        assert "26.8468" in formatted
        assert "80.9462" in formatted

    def test_format_coordinates_zero(self):
        """Test formatting coordinates at equator/prime meridian."""
        formatted = format_coordinates(0.0, 0.0)
        
        assert "0.00" in formatted
        # Could be N or S, E or W for zero

    def test_preset_locations_structure(self):
        """Test that PRESET_LOCATIONS has correct structure."""
        assert isinstance(PRESET_LOCATIONS, dict)
        assert len(PRESET_LOCATIONS) > 0
        
        for key, value in PRESET_LOCATIONS.items():
            assert isinstance(key, str)
            assert isinstance(value, tuple)
            assert len(value) == 3
            assert isinstance(value[0], float)  # latitude
            assert isinstance(value[1], float)  # longitude
            assert isinstance(value[2], str)    # name

    def test_all_preset_locations_valid_coordinates(self):
        """Test that all preset locations have valid coordinates."""
        for _, (lat, lon, name) in PRESET_LOCATIONS.items():
            # Latitude: -90 to 90
            assert -90 <= lat <= 90
            # Longitude: -180 to 180
            assert -180 <= lon <= 180
            # Name not empty
            assert len(name) > 0

    def test_default_location_in_presets(self):
        """Test that default location exists in presets."""
        default_key = DEFAULT_LOCATION.lower()
        assert default_key in PRESET_LOCATIONS
        
        preset_lat, preset_lon, _ = PRESET_LOCATIONS[default_key]
        assert preset_lat == DEFAULT_LAT
        assert preset_lon == DEFAULT_LON

    def test_parse_location_returns_tuple(self):
        """Test that parse_location always returns a tuple of 3 items."""
        # Valid location
        result = parse_location("delhi")
        assert isinstance(result, tuple)
        assert len(result) == 3
        
        # Invalid location
        result = parse_location("invalid")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_major_indian_cities_present(self):
        """Test that major Indian cities are in presets."""
        major_cities = ["delhi", "mumbai", "bangalore", "hyderabad", "chennai", "kolkata"]
        
        for city in major_cities:
            lat, lon, name = parse_location(city)
            assert lat is not None
            assert lon is not None
            assert name != "Unknown Location"
