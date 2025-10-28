"""
Baseline persistence model for wind forecasting.

The persistence model assumes that future conditions will be the same as current conditions.
This is a strong baseline for short-term forecasting (especially 1-3 hours).
"""

import logging
from typing import Dict, List

import numpy as np
import pandas as pd

from src.config import HORIZONS, TARGET_COLUMN

logger = logging.getLogger(__name__)


class PersistenceModel:
    """
    Persistence (naive) forecaster.

    Predicts that the wind speed at time t+h equals the wind speed at time t.
    Despite its simplicity, this is hard to beat for very short horizons.
    """

    def __init__(self, horizons: List[int] = HORIZONS):
        """
        Initialize persistence model.

        Args:
            horizons: List of forecast horizons in hours
        """
        self.horizons = horizons
        self.is_fitted = False

    def fit(self, train_df: pd.DataFrame, val_df: pd.DataFrame = None) -> "PersistenceModel":
        """
        Fit the persistence model (no actual training needed).

        Args:
            train_df: Training data (not used, but kept for API consistency)
            val_df: Validation data (not used)

        Returns:
            self: The fitted model
        """
        # Persistence model has no parameters to learn
        # We just verify that the target column exists
        if TARGET_COLUMN not in train_df.columns:
            raise ValueError(f"Target column '{TARGET_COLUMN}' not found in training data")

        self.is_fitted = True
        logger.info("Persistence model 'fitted' (no training required)")
        return self

    def predict(self, df: pd.DataFrame, horizon: int = 1) -> np.ndarray:
        """
        Make predictions for a specific horizon.

        Args:
            df: Input data with current conditions
            horizon: Forecast horizon in hours

        Returns:
            np.ndarray: Predictions (same as current wind speed)
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before prediction")

        if TARGET_COLUMN not in df.columns:
            raise ValueError(f"Target column '{TARGET_COLUMN}' not found in data")

        # Persistence: future = current
        predictions = df[TARGET_COLUMN].values

        logger.debug(f"Made {len(predictions)} persistence predictions for horizon {horizon}h")
        return predictions

    def predict_all_horizons(self, df: pd.DataFrame) -> Dict[int, np.ndarray]:
        """
        Make predictions for all configured horizons.

        Args:
            df: Input data with current conditions

        Returns:
            Dict[int, np.ndarray]: Dictionary mapping horizon to predictions
        """
        predictions = {}
        for h in self.horizons:
            predictions[h] = self.predict(df, horizon=h)

        logger.info(f"Made persistence predictions for horizons {self.horizons}")
        return predictions

    def predict_latest(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Predict for the latest timestamp in the DataFrame.

        Args:
            df: Input data

        Returns:
            Dict[str, float]: Dictionary with forecasts for each horizon
        """
        if len(df) == 0:
            raise ValueError("Input DataFrame is empty")

        # Get the latest wind speed
        latest_wind = df[TARGET_COLUMN].iloc[-1]

        # For persistence, all horizons have the same prediction
        result = {f"horizon_{h}h": float(latest_wind) for h in self.horizons}

        logger.info(f"Latest persistence forecast: {latest_wind:.2f} m/s for all horizons")
        return result

    def save(self, path: str) -> None:
        """
        Save model (persistence model has no state to save).

        Args:
            path: Path to save model (ignored, but kept for API consistency)
        """
        logger.info("Persistence model has no state to save")

    def load(self, path: str) -> "PersistenceModel":
        """
        Load model (persistence model has no state to load).

        Args:
            path: Path to load model from (ignored)

        Returns:
            self: The model instance
        """
        self.is_fitted = True
        logger.info("Persistence model 'loaded' (no state to restore)")
        return self

    def __repr__(self) -> str:
        return f"PersistenceModel(horizons={self.horizons}, fitted={self.is_fitted})"
