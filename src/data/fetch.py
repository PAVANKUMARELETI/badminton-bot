"""
Data fetching and loading utilities.

This module handles loading sample data and optionally fetching from external APIs.
If API keys are not available, it gracefully falls back to sample/synthetic data.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import SAMPLE_DATA_PATH

logger = logging.getLogger(__name__)


def load_sample() -> pd.DataFrame:
    """
    Load the sample station data from CSV.

    Returns:
        pd.DataFrame: DataFrame with columns:
            - timestamp: datetime index
            - wind_m_s: wind speed in m/s
            - wind_gust_m_s: wind gust speed in m/s
            - wind_dir_deg: wind direction in degrees
            - pressure: atmospheric pressure in hPa
            - temp: temperature in °C
            - humidity: relative humidity in %
            - precip_mm: precipitation in mm

    Raises:
        FileNotFoundError: If sample_station.csv doesn't exist
    """
    if not SAMPLE_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Sample data not found at {SAMPLE_DATA_PATH}. "
            "Run 'python scripts/make_sample_data.py' to generate it."
        )

    logger.info(f"Loading sample data from {SAMPLE_DATA_PATH}")
    df = pd.read_csv(SAMPLE_DATA_PATH, parse_dates=["timestamp"])
    df = df.set_index("timestamp")
    df = df.sort_index()

    logger.info(f"Loaded {len(df)} records from {df.index.min()} to {df.index.max()}")
    return df


def fetch_metar_data(
    station_code: str, start_date: str, end_date: str, api_key: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    Fetch METAR weather data from an external API (optional).

    This is a placeholder function. If you have access to a METAR API,
    implement the actual fetching logic here. The function gracefully
    handles missing API keys.

    Args:
        station_code: ICAO station code (e.g., 'KJFK')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        api_key: API key for the weather service (optional)

    Returns:
        pd.DataFrame or None: Weather data if successful, None otherwise
    """
    # Check for API key in environment or parameter
    api_key = api_key or os.getenv("WEATHER_API_KEY")

    if not api_key:
        logger.warning(
            "No WEATHER_API_KEY found in environment. "
            "Skipping METAR fetch. Use sample data instead."
        )
        return None

    logger.warning(
        "METAR fetching is not implemented. This is a placeholder. "
        "Implement your own API integration or use sample data."
    )

    # TODO: Implement actual METAR API fetching
    # Example structure:
    # import requests
    # response = requests.get(API_ENDPOINT, params={...}, headers={...})
    # data = response.json()
    # df = pd.DataFrame(data)
    # return df

    return None


def load_data(source: str = "sample", **kwargs) -> pd.DataFrame:
    """
    Universal data loader that handles different sources.

    Args:
        source: Data source ('sample', 'metar', or path to CSV file)
        **kwargs: Additional arguments passed to specific loaders

    Returns:
        pd.DataFrame: Loaded weather data

    Examples:
        >>> df = load_data('sample')
        >>> df = load_data('metar', station_code='KJFK', start_date='2025-01-01', end_date='2025-01-31')
        >>> df = load_data('path/to/custom_data.csv')
    """
    if source == "sample":
        return load_sample()

    elif source == "metar":
        df = fetch_metar_data(**kwargs)
        if df is None:
            logger.warning("METAR fetch failed, falling back to sample data")
            return load_sample()
        return df

    elif Path(source).exists():
        logger.info(f"Loading data from custom path: {source}")
        df = pd.read_csv(source, parse_dates=["timestamp"])
        df = df.set_index("timestamp")
        df = df.sort_index()
        return df

    else:
        raise ValueError(
            f"Unknown data source: {source}. Use 'sample', 'metar', or a valid file path."
        )
