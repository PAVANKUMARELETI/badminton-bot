"""
Tests for decision-making logic.
"""

import pytest

from src.decision.rules import (
    compute_safety_score,
    decide_play,
    load_thresholds,
)


def test_decide_play_safe_conditions():
    """Test decision when conditions are safe."""
    median_forecast = {
        "horizon_1h": 1.0,
        "horizon_3h": 1.2,
        "horizon_6h": 1.3,
    }

    q90_forecast = {
        "horizon_1h": 1.5,
        "horizon_3h": 1.8,
        "horizon_6h": 2.0,
    }

    result = decide_play(median_forecast, q90_forecast)

    assert result["decision"] == "PLAY"
    assert "details" in result
    assert len(result["details"]) == 3  # Three horizons


def test_decide_play_unsafe_median():
    """Test decision when median wind is too high (BWF standard: 3.33 m/s)."""
    median_forecast = {
        "horizon_1h": 3.5,  # Above BWF threshold of 3.33
        "horizon_3h": 3.6,
        "horizon_6h": 3.4,
    }

    q90_forecast = {
        "horizon_1h": 4.5,
        "horizon_3h": 4.8,
        "horizon_6h": 4.0,
    }

    result = decide_play(median_forecast, q90_forecast)

    assert result["decision"] == "DON'T PLAY"
    assert "median wind" in result["reason"].lower()


def test_decide_play_unsafe_q90():
    """Test decision when q90 wind is too high (BWF standard: 5.0 m/s for gusts)."""
    median_forecast = {
        "horizon_1h": 2.0,
        "horizon_3h": 2.2,
        "horizon_6h": 2.3,
    }

    q90_forecast = {
        "horizon_1h": 4.5,
        "horizon_3h": 5.5,  # Above BWF threshold of 5.0
        "horizon_6h": 4.8,
    }

    result = decide_play(median_forecast, q90_forecast)

    assert result["decision"] == "DON'T PLAY"
    assert "q90" in result["reason"].lower()


def test_decide_play_custom_thresholds():
    """Test decision with custom thresholds."""
    median_forecast = {
        "horizon_1h": 1.8,
        "horizon_3h": 1.9,
        "horizon_6h": 2.0,
    }

    q90_forecast = {
        "horizon_1h": 2.8,
        "horizon_3h": 2.9,
        "horizon_6h": 3.0,
    }

    # Stricter thresholds - should not play
    strict_thresholds = {
        "speed_unit": "m/s",
        "play": {
            "median_max_m_s": 1.0,
            "q90_max_m_s": 2.0,
            "prob_over_3m_s_max": 0.1,
        },
    }

    result = decide_play(median_forecast, q90_forecast, thresholds=strict_thresholds)
    assert result["decision"] == "DON'T PLAY"

    # Looser thresholds - should play
    loose_thresholds = {
        "speed_unit": "m/s",
        "play": {
            "median_max_m_s": 2.5,
            "q90_max_m_s": 4.0,
            "prob_over_3m_s_max": 0.5,
        },
    }

    result = decide_play(median_forecast, q90_forecast, thresholds=loose_thresholds)
    assert result["decision"] == "PLAY"


def test_decide_play_with_probabilities():
    """Test decision with probability threshold."""
    median_forecast = {
        "horizon_1h": 1.0,
        "horizon_3h": 1.2,
    }

    q90_forecast = {
        "horizon_1h": 1.5,
        "horizon_3h": 1.8,
    }

    prob_over_threshold = {
        "horizon_1h": 0.05,  # Low probability - should pass
        "horizon_3h": 0.15,  # High probability - should fail
    }

    result = decide_play(median_forecast, q90_forecast, prob_over_threshold=prob_over_threshold)

    assert result["decision"] == "DON'T PLAY"
    assert "prob" in result["reason"].lower()


def test_decision_details():
    """Test that decision details are complete."""
    median_forecast = {
        "horizon_1h": 1.0,
        "horizon_3h": 1.2,
        "horizon_6h": 1.3,
    }

    q90_forecast = {
        "horizon_1h": 1.5,
        "horizon_3h": 1.8,
        "horizon_6h": 2.0,
    }

    result = decide_play(median_forecast, q90_forecast)

    # Check details structure
    assert "details" in result
    assert "1h" in result["details"]
    assert "3h" in result["details"]
    assert "6h" in result["details"]

    # Check detail fields
    for horizon, details in result["details"].items():
        assert "median_wind_m_s" in details
        assert "q90_wind_m_s" in details
        assert "passes" in details
        assert "violations" in details

        # Safe conditions should pass
        assert details["passes"] is True
        assert len(details["violations"]) == 0


def test_compute_safety_score():
    """Test safety score computation."""
    # Very safe conditions
    median_forecast = {
        "horizon_1h": 0.5,
        "horizon_3h": 0.6,
    }

    q90_forecast = {
        "horizon_1h": 0.8,
        "horizon_3h": 1.0,
    }

    score = compute_safety_score(median_forecast, q90_forecast)

    # Should be high (close to 1.0)
    assert 0.5 < score <= 1.0

    # Unsafe conditions
    median_forecast = {
        "horizon_1h": 2.0,
        "horizon_3h": 2.5,
    }

    q90_forecast = {
        "horizon_1h": 3.0,
        "horizon_3h": 3.5,
    }

    score = compute_safety_score(median_forecast, q90_forecast)

    # Should be low (close to 0.0)
    assert 0.0 <= score < 0.5


def test_load_thresholds():
    """Test threshold loading."""
    thresholds = load_thresholds()

    # Should have required fields
    assert "speed_unit" in thresholds
    assert "play" in thresholds
    assert "median_max_m_s" in thresholds["play"]
    assert "q90_max_m_s" in thresholds["play"]
