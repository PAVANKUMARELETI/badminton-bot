"""
Data preprocessing and feature engineering.

This module transforms raw weather data into ML-ready features with:
- Lag features for wind speed and other variables
- Cyclical time encodings (hour of day, day of week)
- Pressure tendency
- Gap filling for missing data
"""

import logging
from typing import List

import numpy as np
import pandas as pd

from src.config import (
    LAG_HOURS,
    MAX_GAP_FILL_HOURS,
    PRESSURE_TENDENCY_HOURS,
    RANDOM_SEED,
    TARGET_COLUMN,
)

logger = logging.getLogger(__name__)


def resample_to_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resample data to hourly frequency, taking the mean for numeric columns.

    Args:
        df: Input DataFrame with datetime index

    Returns:
        pd.DataFrame: Resampled to hourly frequency
    """
    logger.info("Resampling data to hourly frequency")

    # Ensure index is datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame must have a DatetimeIndex")

    # Resample to hourly, taking mean of numeric columns
    df_hourly = df.resample("1H").mean()

    logger.info(f"Resampled from {len(df)} to {len(df_hourly)} hourly records")
    return df_hourly


def fill_small_gaps(df: pd.DataFrame, max_gap_hours: int = MAX_GAP_FILL_HOURS) -> pd.DataFrame:
    """
    Fill small gaps in data using linear interpolation.

    Only gaps up to max_gap_hours are filled. Larger gaps are left as NaN
    to avoid unrealistic interpolation.

    Args:
        df: Input DataFrame
        max_gap_hours: Maximum gap size to fill (hours)

    Returns:
        pd.DataFrame: DataFrame with small gaps filled
    """
    logger.info(f"Filling gaps up to {max_gap_hours} hours")

    # Interpolate with limit to avoid filling large gaps
    df_filled = df.interpolate(method="linear", limit=max_gap_hours, limit_area="inside")

    # Count how many values were filled
    n_filled = df_filled.notna().sum().sum() - df.notna().sum().sum()
    logger.info(f"Filled {n_filled} missing values")

    return df_filled


def create_lag_features(df: pd.DataFrame, column: str, lags: List[int]) -> pd.DataFrame:
    """
    Create lag features for a given column.

    Args:
        df: Input DataFrame
        column: Column name to create lags for
        lags: List of lag hours (e.g., [1, 2, 3, 6, 12, 24])

    Returns:
        pd.DataFrame: Original df with additional lag columns
    """
    for lag in lags:
        df[f"{column}_lag_{lag}h"] = df[column].shift(lag)

    logger.info(f"Created {len(lags)} lag features for {column}")
    return df


def create_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create cyclical time features using sine/cosine encoding.

    This preserves the cyclical nature of time (e.g., 23:00 is close to 00:00).

    Args:
        df: Input DataFrame with datetime index

    Returns:
        pd.DataFrame: Original df with cyclical time features
    """
    # Hour of day (0-23)
    df["hour_sin"] = np.sin(2 * np.pi * df.index.hour / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df.index.hour / 24)

    # Day of week (0-6)
    df["dow_sin"] = np.sin(2 * np.pi * df.index.dayofweek / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df.index.dayofweek / 7)

    # Day of year (1-365/366) - captures seasonality
    day_of_year = df.index.dayofyear
    days_in_year = 365 + df.index.is_leap_year.astype(int)
    df["doy_sin"] = np.sin(2 * np.pi * day_of_year / days_in_year)
    df["doy_cos"] = np.cos(2 * np.pi * day_of_year / days_in_year)

    logger.info("Created cyclical time features (hour, day of week, day of year)")
    return df


def create_pressure_tendency(
    df: pd.DataFrame, hours: int = PRESSURE_TENDENCY_HOURS
) -> pd.DataFrame:
    """
    Create pressure tendency feature (rate of change).

    Pressure tendency is a useful predictor of weather changes.

    Args:
        df: Input DataFrame with 'pressure' column
        hours: Hours over which to calculate tendency

    Returns:
        pd.DataFrame: Original df with pressure_tendency column
    """
    if "pressure" in df.columns:
        df["pressure_tendency"] = df["pressure"].diff(hours) / hours
        logger.info(f"Created pressure tendency feature ({hours}h)")
    else:
        logger.warning("No 'pressure' column found, skipping pressure tendency")

    return df


def create_wind_direction_components(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert wind direction (degrees) to u and v components.

    This avoids the discontinuity at 0/360 degrees.

    Args:
        df: Input DataFrame with 'wind_dir_deg' column

    Returns:
        pd.DataFrame: Original df with wind_u and wind_v columns
    """
    if "wind_dir_deg" in df.columns:
        # Convert degrees to radians
        wind_dir_rad = np.deg2rad(df["wind_dir_deg"])

        # Meteorological convention: direction wind is FROM
        # u component: east-west (positive = from west)
        # v component: north-south (positive = from south)
        df["wind_u"] = -df[TARGET_COLUMN] * np.sin(wind_dir_rad)
        df["wind_v"] = -df[TARGET_COLUMN] * np.cos(wind_dir_rad)

        logger.info("Created wind direction components (u, v)")
    else:
        logger.warning("No 'wind_dir_deg' column found, skipping wind components")

    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main feature engineering pipeline.

    Applies all preprocessing steps:
    1. Resample to hourly
    2. Fill small gaps
    3. Create lag features
    4. Create cyclical time features
    5. Create pressure tendency
    6. Create wind direction components

    Args:
        df: Raw weather data with datetime index

    Returns:
        pd.DataFrame: Preprocessed features ready for ML
    """
    logger.info("Starting feature engineering pipeline")

    # Make a copy to avoid modifying original
    df = df.copy()

    # Step 1: Resample to hourly
    df = resample_to_hourly(df)

    # Step 2: Fill small gaps
    df = fill_small_gaps(df)

    # Step 3: Create lag features for wind (main target)
    df = create_lag_features(df, TARGET_COLUMN, LAG_HOURS)

    # Also create lags for wind gusts if available
    if "wind_gust_m_s" in df.columns:
        df = create_lag_features(df, "wind_gust_m_s", LAG_HOURS[:3])  # Fewer lags for gusts

    # Step 4: Create cyclical time features
    df = create_cyclical_features(df)

    # Step 5: Create pressure tendency
    df = create_pressure_tendency(df)

    # Step 6: Create wind direction components
    df = create_wind_direction_components(df)

    # Drop rows with NaN in target column
    initial_len = len(df)
    df = df.dropna(subset=[TARGET_COLUMN])

    # Drop rows with NaN in lag features (from the beginning of the series)
    lag_cols = [col for col in df.columns if "_lag_" in col]
    df = df.dropna(subset=lag_cols)

    logger.info(
        f"Feature engineering complete. "
        f"Dropped {initial_len - len(df)} rows with missing values. "
        f"Final dataset: {len(df)} rows, {len(df.columns)} features"
    )

    return df


def get_feature_columns(df: pd.DataFrame, exclude_target: bool = True) -> List[str]:
    """
    Get list of feature columns (excluding target and metadata).

    Args:
        df: Preprocessed DataFrame
        exclude_target: Whether to exclude the target column

    Returns:
        List[str]: List of feature column names
    """
    # Exclude target and any identifier columns
    exclude_cols = set()

    if exclude_target:
        exclude_cols.add(TARGET_COLUMN)

    # Exclude original wind_dir_deg (we use u/v components instead)
    exclude_cols.add("wind_dir_deg")

    # Also exclude precipitation (often too sparse for hourly forecasting)
    if "precip_mm" in df.columns:
        exclude_cols.add("precip_mm")

    # Get all numeric columns that are not in exclude list
    feature_cols = [col for col in df.columns if col not in exclude_cols]

    return feature_cols
