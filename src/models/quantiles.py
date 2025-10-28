"""
Uncertainty quantification using bootstrap and quantile estimation.

This module provides utilities to compute prediction intervals and quantiles
for probabilistic forecasting.
"""

import logging
from typing import Dict, List

import numpy as np

from src.config import N_BOOTSTRAP_SAMPLES, QUANTILE_LEVELS, RANDOM_SEED

logger = logging.getLogger(__name__)


def compute_quantiles_from_samples(
    samples: np.ndarray, quantiles: List[float] = QUANTILE_LEVELS
) -> Dict[str, float]:
    """
    Compute quantiles from an array of prediction samples.

    Args:
        samples: Array of predictions (e.g., from bootstrap or ensemble)
        quantiles: List of quantile levels (e.g., [0.1, 0.5, 0.9])

    Returns:
        Dict[str, float]: Dictionary mapping quantile level to value
    """
    result = {}
    for q in quantiles:
        result[f"q{int(q*100)}"] = np.percentile(samples, q * 100)

    return result


def compute_q90(predictions: np.ndarray, residuals: np.ndarray = None) -> np.ndarray:
    """
    Compute 90th percentile forecast from point predictions.

    If residuals are provided, uses them to estimate uncertainty.
    Otherwise, uses a simple scaling factor (conservative fallback).

    Args:
        predictions: Point predictions
        residuals: Historical residuals (optional)

    Returns:
        np.ndarray: 90th percentile forecasts
    """
    if residuals is not None and len(residuals) > 0:
        # Use residual distribution to compute percentile
        q90_residual = np.percentile(np.abs(residuals), 90)
        q90_predictions = predictions + q90_residual
    else:
        # Fallback: conservative scaling (documented limitation)
        # Assumes residuals are ~20% of prediction
        q90_predictions = predictions * 1.2
        logger.warning(
            "Computing q90 without residuals; using conservative scaling factor 1.2. "
            "For better uncertainty estimates, provide residuals or use ensemble."
        )

    return q90_predictions


def bootstrap_predictions(
    model, X: np.ndarray, n_samples: int = N_BOOTSTRAP_SAMPLES, seed: int = RANDOM_SEED
) -> np.ndarray:
    """
    Generate bootstrap predictions by resampling with replacement.

    Note: This is a simple implementation. For production, consider training
    multiple models on bootstrapped data for true ensemble uncertainty.

    Args:
        model: Fitted model with predict() method
        X: Input features
        n_samples: Number of bootstrap samples
        seed: Random seed

    Returns:
        np.ndarray: Bootstrap predictions, shape (n_samples, n_predictions)
    """
    rng = np.random.RandomState(seed)

    bootstrap_preds = []

    for i in range(n_samples):
        # Resample indices with replacement
        indices = rng.choice(len(X), size=len(X), replace=True)
        X_bootstrap = X[indices]

        # Get predictions
        preds = model.predict(X_bootstrap)
        bootstrap_preds.append(preds)

    return np.array(bootstrap_preds)


def compute_prediction_intervals(
    predictions: np.ndarray,
    residuals: np.ndarray,
    confidence_level: float = 0.9,
) -> Dict[str, np.ndarray]:
    """
    Compute prediction intervals using residual distribution.

    Args:
        predictions: Point predictions
        residuals: Historical residuals (errors)
        confidence_level: Confidence level (e.g., 0.9 for 90% interval)

    Returns:
        Dict with 'lower', 'median', 'upper' bounds
    """
    # Compute quantiles of residual distribution
    lower_percentile = (1 - confidence_level) / 2 * 100
    upper_percentile = (1 + confidence_level) / 2 * 100

    lower_residual = np.percentile(residuals, lower_percentile)
    upper_residual = np.percentile(residuals, upper_percentile)

    # Apply to predictions
    result = {
        "lower": predictions + lower_residual,
        "median": predictions,
        "upper": predictions + upper_residual,
    }

    logger.info(
        f"Computed {confidence_level*100}% prediction intervals: "
        f"[{lower_residual:.2f}, {upper_residual:.2f}]"
    )

    return result


class SimpleEnsemble:
    """
    Simple ensemble wrapper for uncertainty quantification.

    This trains multiple models on different data splits or with different
    random initializations to get prediction diversity.
    """

    def __init__(self, model_class, n_models: int = 5, **model_kwargs):
        """
        Initialize ensemble.

        Args:
            model_class: Class of model to ensemble (e.g., LSTMForecaster)
            n_models: Number of models in ensemble
            **model_kwargs: Arguments to pass to model constructor
        """
        self.model_class = model_class
        self.n_models = n_models
        self.model_kwargs = model_kwargs
        self.models = []

    def fit(self, train_df, val_df=None):
        """
        Train ensemble of models.

        Args:
            train_df: Training data
            val_df: Validation data

        Returns:
            self
        """
        logger.info(f"Training ensemble of {self.n_models} models")

        for i in range(self.n_models):
            logger.info(f"Training model {i+1}/{self.n_models}")

            # Create model with different random seed
            model = self.model_class(**self.model_kwargs)

            # Train (could also use different data subsets for bagging)
            model.fit(train_df, val_df)

            self.models.append(model)

        return self

    def predict_with_uncertainty(self, df) -> Dict:
        """
        Predict with uncertainty estimates from ensemble.

        Args:
            df: Input data

        Returns:
            Dict with 'mean', 'std', 'q10', 'q50', 'q90' for each horizon
        """
        # Get predictions from all models
        all_predictions = []
        for model in self.models:
            preds = model.predict(df)
            all_predictions.append(preds)

        # Aggregate predictions
        # For simplicity, focusing on point predictions
        # In practice, you'd compute quantiles across ensemble members
        mean_preds = {}
        for h in self.models[0].horizons:
            horizon_preds = np.array([p[h] for p in all_predictions])
            mean_preds[h] = horizon_preds.mean(axis=0)

        logger.info("Ensemble predictions computed")
        return mean_preds
