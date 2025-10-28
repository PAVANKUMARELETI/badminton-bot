"""
Evaluation metrics for forecasting models.

Implements standard regression metrics and probabilistic forecasting scores.
"""

import logging
from typing import Dict

import numpy as np

logger = logging.getLogger(__name__)


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Mean Absolute Error.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        float: MAE score
    """
    return np.mean(np.abs(y_true - y_pred))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Root Mean Squared Error.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        float: RMSE score
    """
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def mape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-10) -> float:
    """
    Mean Absolute Percentage Error.

    Args:
        y_true: True values
        y_pred: Predicted values
        epsilon: Small constant to avoid division by zero

    Returns:
        float: MAPE score (as percentage)
    """
    return np.mean(np.abs((y_true - y_pred) / (y_true + epsilon))) * 100


def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Mean Squared Error.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        float: MSE score
    """
    return np.mean((y_true - y_pred) ** 2)


def quantile_loss(y_true: np.ndarray, y_pred: np.ndarray, quantile: float) -> float:
    """
    Quantile loss (pinball loss) for probabilistic forecasts.

    Args:
        y_true: True values
        y_pred: Predicted quantiles
        quantile: Quantile level (e.g., 0.9 for 90th percentile)

    Returns:
        float: Quantile loss
    """
    errors = y_true - y_pred
    loss = np.where(errors >= 0, quantile * errors, (quantile - 1) * errors)
    return np.mean(loss)


def skill_score(mae_model: float, mae_baseline: float) -> float:
    """
    Skill score: improvement over baseline.

    Skill Score = 1 - (MAE_model / MAE_baseline)

    Positive values indicate improvement over baseline.
    0.0 = same as baseline
    1.0 = perfect predictions

    Args:
        mae_model: MAE of the model
        mae_baseline: MAE of the baseline (e.g., persistence)

    Returns:
        float: Skill score
    """
    if mae_baseline == 0:
        return 0.0
    return 1.0 - (mae_model / mae_baseline)


def evaluate_forecast(
    y_true: np.ndarray, y_pred: np.ndarray, model_name: str = "Model"
) -> Dict[str, float]:
    """
    Compute multiple evaluation metrics.

    Args:
        y_true: True values
        y_pred: Predicted values
        model_name: Name of model (for logging)

    Returns:
        Dict[str, float]: Dictionary of metric names and values
    """
    metrics = {
        "mae": mae(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "mse": mse(y_true, y_pred),
        "mape": mape(y_true, y_pred),
    }

    logger.info(
        f"{model_name} - MAE: {metrics['mae']:.4f}, "
        f"RMSE: {metrics['rmse']:.4f}, "
        f"MAPE: {metrics['mape']:.2f}%"
    )

    return metrics


def evaluate_probabilistic_forecast(
    y_true: np.ndarray,
    y_pred_median: np.ndarray,
    y_pred_q10: np.ndarray,
    y_pred_q90: np.ndarray,
) -> Dict[str, float]:
    """
    Evaluate probabilistic forecasts with quantiles.

    Args:
        y_true: True values
        y_pred_median: Median predictions
        y_pred_q10: 10th percentile predictions
        y_pred_q90: 90th percentile predictions

    Returns:
        Dict[str, float]: Metrics for probabilistic forecast
    """
    metrics = {
        "mae_median": mae(y_true, y_pred_median),
        "quantile_loss_q10": quantile_loss(y_true, y_pred_q10, 0.1),
        "quantile_loss_q90": quantile_loss(y_true, y_pred_q90, 0.9),
        "coverage_80": np.mean((y_true >= y_pred_q10) & (y_true <= y_pred_q90)),
    }

    logger.info(
        f"Probabilistic forecast - MAE: {metrics['mae_median']:.4f}, "
        f"80% Coverage: {metrics['coverage_80']:.2%}"
    )

    return metrics
