"""
Tests for evaluation metrics.
"""

import numpy as np
import pytest

from src.eval.metrics import (
    mae,
    mape,
    mse,
    quantile_loss,
    rmse,
    skill_score,
    evaluate_forecast,
)


def test_mae():
    """Test Mean Absolute Error."""
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y_pred = np.array([1.1, 2.1, 2.9, 4.2, 4.8])

    result = mae(y_true, y_pred)

    expected = np.mean([0.1, 0.1, 0.1, 0.2, 0.2])
    assert np.isclose(result, expected)


def test_rmse():
    """Test Root Mean Squared Error."""
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    result = rmse(y_true, y_pred)
    assert np.isclose(result, 0.0)

    # Test with errors
    y_pred = np.array([2.0, 3.0, 4.0, 5.0, 6.0])
    result = rmse(y_true, y_pred)
    assert np.isclose(result, 1.0)


def test_mse():
    """Test Mean Squared Error."""
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.0, 2.0, 3.0])

    result = mse(y_true, y_pred)
    assert np.isclose(result, 0.0)

    # Test with errors
    y_pred = np.array([2.0, 3.0, 4.0])
    result = mse(y_true, y_pred)
    assert np.isclose(result, 1.0)


def test_mape():
    """Test Mean Absolute Percentage Error."""
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([110.0, 190.0, 300.0])

    result = mape(y_true, y_pred)

    # (10/100 + 10/200 + 0/300) / 3 * 100 = (0.1 + 0.05 + 0) / 3 * 100 = 5%
    assert np.isclose(result, 5.0)


def test_quantile_loss():
    """Test quantile loss."""
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    # Test 50th percentile (median) - symmetric loss
    y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    result = quantile_loss(y_true, y_pred, quantile=0.5)
    assert np.isclose(result, 0.0)

    # Test 90th percentile - should penalize under-prediction more
    y_pred = np.array([0.5, 1.5, 2.5, 3.5, 4.5])  # Under-predicting
    result_90 = quantile_loss(y_true, y_pred, quantile=0.9)

    # Should be positive (loss from under-prediction)
    assert result_90 > 0


def test_skill_score():
    """Test skill score calculation."""
    # Perfect model vs baseline
    mae_model = 0.0
    mae_baseline = 1.0
    result = skill_score(mae_model, mae_baseline)
    assert np.isclose(result, 1.0)

    # Same as baseline
    mae_model = 1.0
    mae_baseline = 1.0
    result = skill_score(mae_model, mae_baseline)
    assert np.isclose(result, 0.0)

    # Worse than baseline
    mae_model = 2.0
    mae_baseline = 1.0
    result = skill_score(mae_model, mae_baseline)
    assert np.isclose(result, -1.0)

    # 50% improvement
    mae_model = 0.5
    mae_baseline = 1.0
    result = skill_score(mae_model, mae_baseline)
    assert np.isclose(result, 0.5)


def test_evaluate_forecast():
    """Test comprehensive forecast evaluation."""
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y_pred = np.array([1.1, 2.1, 2.9, 4.2, 4.8])

    metrics = evaluate_forecast(y_true, y_pred, model_name="TestModel")

    # Check that all metrics are returned
    assert "mae" in metrics
    assert "rmse" in metrics
    assert "mse" in metrics
    assert "mape" in metrics

    # Check that values are reasonable
    assert metrics["mae"] > 0
    assert metrics["rmse"] >= metrics["mae"]  # RMSE is always >= MAE
    assert metrics["mape"] > 0


def test_metrics_with_perfect_predictions():
    """Test metrics with perfect predictions (all zeros)."""
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y_pred = y_true.copy()

    assert np.isclose(mae(y_true, y_pred), 0.0)
    assert np.isclose(rmse(y_true, y_pred), 0.0)
    assert np.isclose(mse(y_true, y_pred), 0.0)


def test_metrics_with_negative_values():
    """Test metrics handle negative values correctly."""
    y_true = np.array([-1.0, -2.0, -3.0])
    y_pred = np.array([-1.5, -2.5, -2.5])

    result_mae = mae(y_true, y_pred)
    result_rmse = rmse(y_true, y_pred)

    assert result_mae > 0
    assert result_rmse > 0
