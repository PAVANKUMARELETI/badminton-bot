"""
Rolling-window backtesting for model evaluation.

This module implements time-series cross-validation to assess model performance
on out-of-sample data while respecting temporal order.
"""

import logging
from typing import Dict, List

import numpy as np
import pandas as pd

from src.config import BACKTEST_STEP_SIZE, BACKTEST_WINDOW_SIZE, HORIZONS, TARGET_COLUMN
from src.eval.metrics import evaluate_forecast, mae, rmse

logger = logging.getLogger(__name__)


def rolling_window_split(
    df: pd.DataFrame,
    window_size: int = BACKTEST_WINDOW_SIZE,
    step_size: int = BACKTEST_STEP_SIZE,
    min_train_size: int = 168,  # Minimum 1 week of training data
) -> List[Dict[str, pd.DataFrame]]:
    """
    Create rolling window train/test splits for backtesting.

    Args:
        df: Input DataFrame
        window_size: Size of test window (hours)
        step_size: Step size between windows (hours)
        min_train_size: Minimum training set size (hours)

    Returns:
        List of dicts with 'train' and 'test' DataFrames
    """
    splits = []

    # Start from min_train_size and create windows
    start_idx = min_train_size

    while start_idx + window_size <= len(df):
        train_df = df.iloc[:start_idx]
        test_df = df.iloc[start_idx : start_idx + window_size]

        splits.append({"train": train_df, "test": test_df})

        start_idx += step_size

    logger.info(f"Created {len(splits)} rolling window splits")
    return splits


def backtest_model(
    model,
    df: pd.DataFrame,
    horizons: List[int] = HORIZONS,
    window_size: int = BACKTEST_WINDOW_SIZE,
    step_size: int = BACKTEST_STEP_SIZE,
) -> Dict[int, Dict[str, float]]:
    """
    Perform rolling-window backtest of a model.

    Args:
        model: Model instance with fit() and predict() methods
        df: Full dataset
        horizons: Forecast horizons to evaluate
        window_size: Test window size (hours)
        step_size: Step between windows (hours)

    Returns:
        Dict mapping horizon to metrics dict
    """
    logger.info("Starting rolling window backtest")

    # Create rolling splits
    splits = rolling_window_split(df, window_size, step_size)

    # Store predictions and actuals for each horizon
    horizon_results = {h: {"y_true": [], "y_pred": []} for h in horizons}

    for i, split in enumerate(splits):
        logger.info(f"Backtest fold {i+1}/{len(splits)}")

        train_df = split["train"]
        test_df = split["test"]

        # Train model on this fold
        try:
            model.fit(train_df)
        except Exception as e:
            logger.warning(f"Training failed for fold {i+1}: {e}")
            continue

        # Predict on test set
        try:
            predictions = model.predict(test_df)
        except Exception as e:
            logger.warning(f"Prediction failed for fold {i+1}: {e}")
            continue

        # Collect results for each horizon
        for h in horizons:
            if h in predictions:
                # Get corresponding actuals (shifted by horizon)
                y_true = test_df[TARGET_COLUMN].iloc[h:].values
                y_pred = predictions[h][: len(y_true)]

                # Ensure same length
                min_len = min(len(y_true), len(y_pred))
                if min_len > 0:
                    horizon_results[h]["y_true"].extend(y_true[:min_len])
                    horizon_results[h]["y_pred"].extend(y_pred[:min_len])

    # Compute metrics for each horizon
    metrics_by_horizon = {}

    for h in horizons:
        y_true = np.array(horizon_results[h]["y_true"])
        y_pred = np.array(horizon_results[h]["y_pred"])

        if len(y_true) > 0:
            metrics_by_horizon[h] = evaluate_forecast(
                y_true, y_pred, model_name=f"Horizon {h}h"
            )
        else:
            logger.warning(f"No predictions for horizon {h}h")
            metrics_by_horizon[h] = {}

    logger.info("Backtest complete")
    return metrics_by_horizon


def compare_models(
    model_a,
    model_b,
    df: pd.DataFrame,
    model_a_name: str = "Model A",
    model_b_name: str = "Model B",
    **backtest_kwargs,
) -> pd.DataFrame:
    """
    Compare two models using backtesting.

    Args:
        model_a: First model
        model_b: Second model (e.g., baseline)
        df: Dataset
        model_a_name: Name of first model
        model_b_name: Name of second model
        **backtest_kwargs: Additional arguments for backtest_model

    Returns:
        pd.DataFrame: Comparison table
    """
    logger.info(f"Comparing {model_a_name} vs {model_b_name}")

    # Backtest both models
    results_a = backtest_model(model_a, df, **backtest_kwargs)
    results_b = backtest_model(model_b, df, **backtest_kwargs)

    # Create comparison table
    comparison_data = []

    for h in results_a.keys():
        if h in results_b:
            row = {
                "horizon": f"{h}h",
                f"{model_a_name}_mae": results_a[h].get("mae", np.nan),
                f"{model_b_name}_mae": results_b[h].get("mae", np.nan),
                f"{model_a_name}_rmse": results_a[h].get("rmse", np.nan),
                f"{model_b_name}_rmse": results_b[h].get("rmse", np.nan),
            }

            # Compute skill score
            mae_a = results_a[h].get("mae", np.nan)
            mae_b = results_b[h].get("mae", np.nan)

            if not np.isnan(mae_a) and not np.isnan(mae_b) and mae_b > 0:
                row["skill_score"] = 1 - (mae_a / mae_b)
            else:
                row["skill_score"] = np.nan

            comparison_data.append(row)

    comparison_df = pd.DataFrame(comparison_data)

    logger.info(f"Model comparison:\n{comparison_df}")
    return comparison_df
