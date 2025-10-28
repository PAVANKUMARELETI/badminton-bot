"""
LSTM-based wind forecasting model.

This module implements a small LSTM neural network for multi-horizon wind prediction.
The model is kept intentionally small for fast training on free hardware (Colab, CI).
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from src.config import (
    HORIZONS,
    LSTM_CONFIG,
    RANDOM_SEED,
    SEQUENCE_LENGTH,
    TARGET_COLUMN,
    TRAIN_VAL_SPLIT,
)
from src.data.preprocess import get_feature_columns

logger = logging.getLogger(__name__)

# Set random seeds for reproducibility
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)


class LSTMForecaster:
    """
    LSTM model for multi-horizon wind speed forecasting.

    Architecture:
    - Input: sequences of historical features
    - Multiple LSTM layers with dropout
    - Dense output layer for each horizon
    """

    def __init__(
        self,
        horizons: List[int] = HORIZONS,
        sequence_length: int = SEQUENCE_LENGTH,
        config: Dict = None,
    ):
        """
        Initialize LSTM forecaster.

        Args:
            horizons: List of forecast horizons in hours
            sequence_length: Number of past timesteps to use as input
            config: Model configuration (uses LSTM_CONFIG defaults if None)
        """
        self.horizons = horizons
        self.sequence_length = sequence_length
        self.config = config or LSTM_CONFIG.copy()

        self.model = None
        self.feature_cols = None
        self.scaler_mean = None
        self.scaler_std = None

    def _build_model(self, n_features: int) -> keras.Model:
        """
        Build LSTM architecture.

        Args:
            n_features: Number of input features

        Returns:
            keras.Model: Compiled model
        """
        inputs = keras.Input(shape=(self.sequence_length, n_features), name="input_sequence")

        # LSTM layers
        x = inputs
        for i, units in enumerate(self.config["units"]):
            return_sequences = i < len(self.config["units"]) - 1
            x = layers.LSTM(
                units,
                return_sequences=return_sequences,
                dropout=self.config["dropout"],
                name=f"lstm_{i+1}",
            )(x)

        # Output layer: one neuron per horizon
        outputs = []
        for h in self.horizons:
            out = layers.Dense(1, name=f"horizon_{h}h")(x)
            outputs.append(out)

        # Build model
        model = keras.Model(inputs=inputs, outputs=outputs, name="wind_lstm")

        # Compile
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.config["learning_rate"]),
            loss={f"horizon_{h}h": "mse" for h in self.horizons},
            metrics={f"horizon_{h}h": ["mae"] for h in self.horizons},
        )

        return model

    def _create_sequences(
        self, df: pd.DataFrame, feature_cols: List[str]
    ) -> Tuple[np.ndarray, Dict[int, np.ndarray]]:
        """
        Create sequences for LSTM training/prediction.

        Args:
            df: Input DataFrame with features
            feature_cols: List of feature column names

        Returns:
            Tuple of (X_sequences, y_targets)
                X_sequences: shape (n_samples, sequence_length, n_features)
                y_targets: dict mapping horizon to target arrays
        """
        # Extract feature values
        X_values = df[feature_cols].values
        y_values = df[TARGET_COLUMN].values

        n_samples = len(df) - self.sequence_length - max(self.horizons)
        n_features = len(feature_cols)

        # Initialize arrays
        X_seq = np.zeros((n_samples, self.sequence_length, n_features))
        y_targets = {h: np.zeros(n_samples) for h in self.horizons}

        # Create sequences
        for i in range(n_samples):
            # Input sequence
            X_seq[i] = X_values[i : i + self.sequence_length]

            # Output targets for each horizon
            for h in self.horizons:
                y_targets[h][i] = y_values[i + self.sequence_length + h - 1]

        return X_seq, y_targets

    def fit(
        self,
        train_df: pd.DataFrame,
        val_df: Optional[pd.DataFrame] = None,
        epochs: Optional[int] = None,
    ) -> "LSTMForecaster":
        """
        Train the LSTM model.

        Args:
            train_df: Training data with features
            val_df: Validation data (optional, will split from train if not provided)
            epochs: Number of training epochs (uses config default if None)

        Returns:
            self: The fitted model
        """
        logger.info("Starting LSTM training")

        # Get feature columns (exclude target)
        self.feature_cols = get_feature_columns(train_df, exclude_target=True)
        logger.info(f"Using {len(self.feature_cols)} features: {self.feature_cols[:5]}...")

        # Combine train and val for normalization
        if val_df is not None:
            combined_df = pd.concat([train_df, val_df])
        else:
            combined_df = train_df

        # Fit scaler on training data
        self.scaler_mean = combined_df[self.feature_cols].mean()
        self.scaler_std = combined_df[self.feature_cols].std()
        self.scaler_std = self.scaler_std.replace(0, 1)  # Avoid division by zero

        # Normalize data
        train_df_norm = train_df.copy()
        train_df_norm[self.feature_cols] = (
            train_df[self.feature_cols] - self.scaler_mean
        ) / self.scaler_std

        if val_df is not None:
            val_df_norm = val_df.copy()
            val_df_norm[self.feature_cols] = (
                val_df[self.feature_cols] - self.scaler_mean
            ) / self.scaler_std
        else:
            # Split train into train/val
            split_idx = int(len(train_df_norm) * TRAIN_VAL_SPLIT)
            val_df_norm = train_df_norm.iloc[split_idx:]
            train_df_norm = train_df_norm.iloc[:split_idx]

        # Create sequences
        X_train, y_train = self._create_sequences(train_df_norm, self.feature_cols)
        X_val, y_val = self._create_sequences(val_df_norm, self.feature_cols)

        logger.info(f"Training sequences: {X_train.shape}, Validation sequences: {X_val.shape}")

        # Build model
        self.model = self._build_model(n_features=len(self.feature_cols))
        logger.info(f"Model architecture:\n{self.model.summary()}")

        # Prepare targets as list for multi-output model
        y_train_list = [y_train[h] for h in self.horizons]
        y_val_list = [y_val[h] for h in self.horizons]

        # Training callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=self.config["patience"],
                restore_best_weights=True,
                verbose=1,
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=1
            ),
        ]

        # Train
        epochs = epochs or self.config["epochs"]
        history = self.model.fit(
            X_train,
            y_train_list,
            validation_data=(X_val, y_val_list),
            epochs=epochs,
            batch_size=self.config["batch_size"],
            callbacks=callbacks,
            verbose=1,
        )

        logger.info("LSTM training complete")
        return self

    def predict(self, df: pd.DataFrame) -> Dict[int, np.ndarray]:
        """
        Make predictions for all horizons.

        Args:
            df: Input data with features

        Returns:
            Dict[int, np.ndarray]: Predictions for each horizon
        """
        if self.model is None:
            raise RuntimeError("Model must be fitted or loaded before prediction")

        # Normalize features
        df_norm = df.copy()
        df_norm[self.feature_cols] = (df[self.feature_cols] - self.scaler_mean) / self.scaler_std

        # Create sequences
        X_seq, _ = self._create_sequences(df_norm, self.feature_cols)

        if len(X_seq) == 0:
            raise ValueError(
                f"Not enough data to create sequences. "
                f"Need at least {self.sequence_length + max(self.horizons)} samples."
            )

        # Predict
        predictions_list = self.model.predict(X_seq, verbose=0)

        # Convert to dict
        predictions = {}
        for i, h in enumerate(self.horizons):
            predictions[h] = predictions_list[i].flatten()

        logger.info(f"Made {len(X_seq)} predictions for {len(self.horizons)} horizons")
        return predictions

    def predict_latest(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Predict for the latest possible sequence in the DataFrame.

        Args:
            df: Input data

        Returns:
            Dict[str, float]: Forecasts for each horizon
        """
        if len(df) < self.sequence_length:
            raise ValueError(
                f"Need at least {self.sequence_length} samples for prediction, got {len(df)}"
            )

        # Get predictions for all complete sequences
        all_preds = self.predict(df)

        # Return the latest prediction
        result = {}
        for h in self.horizons:
            result[f"horizon_{h}h"] = float(all_preds[h][-1])

        logger.info(f"Latest forecast: {result}")
        return result

    def save(self, path: str) -> None:
        """
        Save model weights and configuration.

        Args:
            path: Path to save model (.keras file)
        """
        if self.model is None:
            raise RuntimeError("No model to save")

        save_path = Path(path)
        # Ensure path uses .keras extension
        if save_path.suffix == '.h5':
            save_path = save_path.with_suffix('.keras')
        
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Save model weights
        self.model.save(save_path)

        # Save scaler parameters
        scaler_path = save_path.parent / "scaler.npz"
        np.savez(
            scaler_path,
            mean=self.scaler_mean.values,
            std=self.scaler_std.values,
            feature_cols=self.feature_cols,
        )

        logger.info(f"Model saved to {save_path}")

    def load(self, path: str) -> "LSTMForecaster":
        """
        Load model weights and configuration.

        Args:
            path: Path to load model from (.keras or .h5 file)

        Returns:
            self: The loaded model
        """
        load_path = Path(path)
        
        # Support both .h5 and .keras formats
        if not load_path.exists():
            # Try .keras if .h5 was specified
            if load_path.suffix == '.h5':
                keras_path = load_path.with_suffix('.keras')
                if keras_path.exists():
                    load_path = keras_path
                else:
                    raise FileNotFoundError(f"Model file not found: {load_path}")
            else:
                raise FileNotFoundError(f"Model file not found: {load_path}")

        # Load model
        self.model = keras.models.load_model(load_path)

        # Load scaler parameters
        scaler_path = load_path.parent / "scaler.npz"
        if scaler_path.exists():
            scaler_data = np.load(scaler_path, allow_pickle=True)
            self.scaler_mean = pd.Series(scaler_data["mean"], index=scaler_data["feature_cols"])
            self.scaler_std = pd.Series(scaler_data["std"], index=scaler_data["feature_cols"])
            self.feature_cols = scaler_data["feature_cols"].tolist()

        logger.info(f"Model loaded from {load_path}")
        return self

    def __repr__(self) -> str:
        fitted = self.model is not None
        return f"LSTMForecaster(horizons={self.horizons}, fitted={fitted})"
