"""
Smoke test for model training.

This is a fast integration test that verifies the training pipeline works
end-to-end without extensive training.
"""

import numpy as np
import pandas as pd
import pytest

from src.config import RANDOM_SEED
from src.data.preprocess import build_features
from src.models.baseline import PersistenceModel
from src.models.lstm_model import LSTMForecaster


@pytest.fixture
def sample_training_data():
    """Create minimal sample data for training."""
    np.random.seed(RANDOM_SEED)

    # Create 200 hours of data (enough for LSTM sequence length)
    timestamps = pd.date_range("2024-01-01", periods=200, freq="1H")

    data = {
        "timestamp": timestamps,
        "wind_m_s": np.random.uniform(0.5, 3.0, 200),
        "wind_gust_m_s": np.random.uniform(1.0, 4.0, 200),
        "wind_dir_deg": np.random.uniform(0, 360, 200),
        "pressure": np.random.uniform(1000, 1020, 200),
        "temp": np.random.uniform(15, 25, 200),
        "humidity": np.random.uniform(40, 80, 200),
        "precip_mm": np.random.exponential(0.5, 200),
    }

    df = pd.DataFrame(data)
    df = df.set_index("timestamp")

    return df


@pytest.mark.slow
def test_baseline_training(sample_training_data):
    """Test baseline model training."""
    # Preprocess data
    df = build_features(sample_training_data)

    # Split
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    val_df = df.iloc[split_idx:]

    # Train model
    model = PersistenceModel()
    model.fit(train_df, val_df)

    # Make predictions
    predictions = model.predict(val_df)

    # Check predictions exist and have correct shape
    assert len(predictions) == len(val_df)


@pytest.mark.slow
def test_lstm_training_smoke(sample_training_data):
    """
    Smoke test for LSTM training (1 epoch only).

    This test verifies that the LSTM training pipeline works without
    doing extensive training. Should run in under 30 seconds.
    """
    # Preprocess data
    df = build_features(sample_training_data)

    # Split
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    val_df = df.iloc[split_idx:]

    # Create model
    model = LSTMForecaster()

    # Train for just 1 epoch (smoke test)
    model.fit(train_df, val_df, epochs=1)

    # Make predictions
    predictions = model.predict(val_df)

    # Check predictions exist for all horizons
    assert len(predictions) == len(model.horizons)

    for h in model.horizons:
        assert h in predictions
        assert len(predictions[h]) > 0


@pytest.mark.slow
def test_lstm_predict_latest(sample_training_data):
    """Test LSTM latest prediction after training."""
    df = build_features(sample_training_data)

    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    val_df = df.iloc[split_idx:]

    # Train
    model = LSTMForecaster()
    model.fit(train_df, val_df, epochs=1)

    # Predict latest
    latest_forecast = model.predict_latest(val_df)

    # Check structure
    assert isinstance(latest_forecast, dict)

    for h in model.horizons:
        key = f"horizon_{h}h"
        assert key in latest_forecast
        assert isinstance(latest_forecast[key], float)


@pytest.mark.slow
def test_lstm_save_load(sample_training_data, tmp_path):
    """Test LSTM model save and load."""
    df = build_features(sample_training_data)

    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    val_df = df.iloc[split_idx:]

    # Train model
    model = LSTMForecaster()
    model.fit(train_df, val_df, epochs=1)

    # Get predictions before save
    preds_before = model.predict_latest(val_df)

    # Save
    model_path = tmp_path / "test_model.h5"
    model.save(str(model_path))

    # Load into new model
    model_loaded = LSTMForecaster()
    model_loaded.load(str(model_path))

    # Get predictions after load
    preds_after = model_loaded.predict_latest(val_df)

    # Should be identical
    for key in preds_before.keys():
        assert np.isclose(preds_before[key], preds_after[key], rtol=1e-5)


def test_baseline_predict_latest(sample_training_data):
    """Test baseline latest prediction."""
    df = build_features(sample_training_data)

    model = PersistenceModel()
    model.fit(df)

    # Predict latest
    latest_forecast = model.predict_latest(df)

    # Check structure
    assert isinstance(latest_forecast, dict)

    for h in model.horizons:
        key = f"horizon_{h}h"
        assert key in latest_forecast
        assert isinstance(latest_forecast[key], float)

        # For persistence, all horizons should be the same
        assert np.isclose(latest_forecast[key], df["wind_m_s"].iloc[-1])
