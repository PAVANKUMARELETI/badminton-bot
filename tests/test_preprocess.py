"""
Tests for data preprocessing and feature engineering.
"""

import numpy as np
import pandas as pd
import pytest

from src.config import LAG_HOURS, RANDOM_SEED, TARGET_COLUMN
from src.data.preprocess import (
    build_features,
    create_cyclical_features,
    create_lag_features,
    create_pressure_tendency,
    fill_small_gaps,
    get_feature_columns,
    resample_to_hourly,
)


@pytest.fixture
def sample_weather_data():
    """Create sample weather data for testing."""
    np.random.seed(RANDOM_SEED)

    # Create 100 hours of data
    timestamps = pd.date_range("2024-01-01", periods=100, freq="1H")

    data = {
        "timestamp": timestamps,
        "wind_m_s": np.random.uniform(0.5, 3.0, 100),
        "wind_gust_m_s": np.random.uniform(1.0, 4.0, 100),
        "wind_dir_deg": np.random.uniform(0, 360, 100),
        "pressure": np.random.uniform(1000, 1020, 100),
        "temp": np.random.uniform(15, 25, 100),
        "humidity": np.random.uniform(40, 80, 100),
        "precip_mm": np.random.exponential(0.5, 100),
    }

    df = pd.DataFrame(data)
    df = df.set_index("timestamp")

    return df


def test_resample_to_hourly(sample_weather_data):
    """Test hourly resampling."""
    df = sample_weather_data

    # Already hourly, so should stay the same size
    df_resampled = resample_to_hourly(df)

    assert len(df_resampled) == len(df)
    assert isinstance(df_resampled.index, pd.DatetimeIndex)


def test_fill_small_gaps(sample_weather_data):
    """Test gap filling."""
    df = sample_weather_data.copy()

    # Introduce some gaps
    df.loc[df.index[10:13], "wind_m_s"] = np.nan  # 3-hour gap
    df.loc[df.index[20], "wind_m_s"] = np.nan  # 1-hour gap

    # Fill gaps
    df_filled = fill_small_gaps(df, max_gap_hours=3)

    # 1-hour gap should be filled
    assert not pd.isna(df_filled.loc[df.index[20], "wind_m_s"])

    # 3-hour gap should be filled (at the limit)
    assert not pd.isna(df_filled.loc[df.index[11], "wind_m_s"])


def test_create_lag_features(sample_weather_data):
    """Test lag feature creation."""
    df = sample_weather_data.copy()

    df_with_lags = create_lag_features(df, "wind_m_s", [1, 2, 3])

    # Check that lag columns were created
    assert "wind_m_s_lag_1h" in df_with_lags.columns
    assert "wind_m_s_lag_2h" in df_with_lags.columns
    assert "wind_m_s_lag_3h" in df_with_lags.columns

    # Check lag values are correct
    assert df_with_lags["wind_m_s_lag_1h"].iloc[1] == df["wind_m_s"].iloc[0]
    assert df_with_lags["wind_m_s_lag_2h"].iloc[2] == df["wind_m_s"].iloc[0]


def test_create_cyclical_features(sample_weather_data):
    """Test cyclical time feature creation."""
    df = sample_weather_data.copy()

    df_with_cyclical = create_cyclical_features(df)

    # Check that cyclical columns were created
    assert "hour_sin" in df_with_cyclical.columns
    assert "hour_cos" in df_with_cyclical.columns
    assert "dow_sin" in df_with_cyclical.columns
    assert "dow_cos" in df_with_cyclical.columns

    # Check values are in valid range [-1, 1]
    assert df_with_cyclical["hour_sin"].min() >= -1
    assert df_with_cyclical["hour_sin"].max() <= 1
    assert df_with_cyclical["hour_cos"].min() >= -1
    assert df_with_cyclical["hour_cos"].max() <= 1


def test_create_pressure_tendency(sample_weather_data):
    """Test pressure tendency calculation."""
    df = sample_weather_data.copy()

    df_with_tendency = create_pressure_tendency(df, hours=3)

    assert "pressure_tendency" in df_with_tendency.columns

    # First few values should be NaN due to differencing
    assert pd.isna(df_with_tendency["pressure_tendency"].iloc[0])


def test_build_features(sample_weather_data):
    """Test full feature engineering pipeline."""
    df = sample_weather_data.copy()

    df_processed = build_features(df)

    # Check that target column exists
    assert TARGET_COLUMN in df_processed.columns

    # Check that lag features exist
    for lag in LAG_HOURS:
        assert f"{TARGET_COLUMN}_lag_{lag}h" in df_processed.columns

    # Check that cyclical features exist
    assert "hour_sin" in df_processed.columns
    assert "dow_sin" in df_processed.columns

    # Check that no NaN in target or lag features
    assert not df_processed[TARGET_COLUMN].isna().any()

    for lag in LAG_HOURS:
        lag_col = f"{TARGET_COLUMN}_lag_{lag}h"
        assert not df_processed[lag_col].isna().any()

    # Check that data was reduced (due to dropna on lags)
    assert len(df_processed) < len(df)


def test_get_feature_columns(sample_weather_data):
    """Test feature column extraction."""
    df = build_features(sample_weather_data)

    feature_cols = get_feature_columns(df, exclude_target=True)

    # Should not include target
    assert TARGET_COLUMN not in feature_cols

    # Should not include wind_dir_deg (we use u/v components instead)
    assert "wind_dir_deg" not in feature_cols

    # Should include lag features
    assert any("_lag_" in col for col in feature_cols)

    # Should include cyclical features
    assert "hour_sin" in feature_cols
    assert "dow_sin" in feature_cols


def test_feature_determinism(sample_weather_data):
    """Test that feature engineering is deterministic."""
    df = sample_weather_data.copy()

    # Process twice
    df1 = build_features(df)
    df2 = build_features(df)

    # Should be identical
    pd.testing.assert_frame_equal(df1, df2)
