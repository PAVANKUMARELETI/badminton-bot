"""
Decision rules for determining whether it's safe to play badminton.

This module implements the logic to convert wind forecasts into actionable
play/don't play recommendations based on configurable thresholds.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from src.config import DECISION_THRESHOLDS_PATH, DEFAULT_THRESHOLDS

logger = logging.getLogger(__name__)


def load_thresholds(path: Optional[Path] = None) -> Dict:
    """
    Load decision thresholds from JSON file.

    Args:
        path: Path to thresholds JSON (uses default if None)

    Returns:
        Dict: Threshold configuration
    """
    path = path or DECISION_THRESHOLDS_PATH

    if path.exists():
        with open(path, "r") as f:
            thresholds = json.load(f)
        logger.info(f"Loaded thresholds from {path}")
    else:
        thresholds = DEFAULT_THRESHOLDS.copy()
        logger.warning(f"Thresholds file not found at {path}, using defaults")

    return thresholds


def decide_play(
    median_forecast: Dict[str, float],
    q90_forecast: Dict[str, float],
    thresholds: Optional[Dict] = None,
    prob_over_threshold: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Determine whether it's safe to play badminton based on wind forecasts.

    Decision rules:
    1. Median wind speed must be below threshold for all horizons
    2. 90th percentile wind speed must be below threshold for all horizons
    3. (Optional) Probability of exceeding 3 m/s must be below threshold

    Args:
        median_forecast: Dict mapping horizon to median wind speed (m/s)
        q90_forecast: Dict mapping horizon to 90th percentile wind speed (m/s)
        thresholds: Threshold configuration (loads default if None)
        prob_over_threshold: Dict mapping horizon to probability of exceeding 3 m/s

    Returns:
        Dict with:
            - decision: "PLAY" or "DON'T PLAY"
            - reason: Explanation of decision
            - details: Per-horizon breakdown
    """
    # Load thresholds
    if thresholds is None:
        thresholds = load_thresholds()

    play_thresholds = thresholds["play"]

    # Extract threshold values
    median_max = play_thresholds["median_max_m_s"]
    q90_max = play_thresholds["q90_max_m_s"]
    prob_max = play_thresholds.get("prob_over_3m_s_max", 1.0)

    # Check conditions for each horizon
    violations = []
    horizon_details = {}

    for horizon_key in median_forecast.keys():
        median_wind = median_forecast[horizon_key]
        q90_wind = q90_forecast[horizon_key]

        # Extract horizon number from key (e.g., "horizon_1h" -> "1h")
        horizon = horizon_key.replace("horizon_", "")

        # Initialize horizon details
        horizon_details[horizon] = {
            "median_wind_m_s": median_wind,
            "q90_wind_m_s": q90_wind,
            "passes": True,
            "violations": [],
        }

        # Check median threshold
        if median_wind > median_max:
            violation = f"{horizon}: median wind {median_wind:.2f} m/s > {median_max} m/s"
            violations.append(violation)
            horizon_details[horizon]["passes"] = False
            horizon_details[horizon]["violations"].append("median_too_high")

        # Check q90 threshold
        if q90_wind > q90_max:
            violation = f"{horizon}: q90 wind {q90_wind:.2f} m/s > {q90_max} m/s"
            violations.append(violation)
            horizon_details[horizon]["passes"] = False
            horizon_details[horizon]["violations"].append("q90_too_high")

        # Check probability threshold (if provided)
        if prob_over_threshold is not None and horizon_key in prob_over_threshold:
            prob = prob_over_threshold[horizon_key]
            horizon_details[horizon]["prob_over_3m_s"] = prob

            if prob > prob_max:
                violation = f"{horizon}: probability of >3 m/s is {prob:.2%} > {prob_max:.2%}"
                violations.append(violation)
                horizon_details[horizon]["passes"] = False
                horizon_details[horizon]["violations"].append("prob_too_high")

    # Make decision
    if len(violations) == 0:
        decision = "PLAY"
        reason = (
            f"All horizons pass safety criteria: "
            f"median ≤ {median_max} m/s, q90 ≤ {q90_max} m/s"
        )
    else:
        decision = "DON'T PLAY"
        reason = f"Safety violations detected: {'; '.join(violations)}"

    result = {
        "decision": decision,
        "reason": reason,
        "details": horizon_details,
        "thresholds": play_thresholds,
    }

    logger.info(f"Decision: {decision} - {reason}")
    return result


def compute_safety_score(
    median_forecast: Dict[str, float],
    q90_forecast: Dict[str, float],
    thresholds: Optional[Dict] = None,
) -> float:
    """
    Compute a safety score from 0 (very unsafe) to 1 (very safe).

    This provides a continuous measure of how safe conditions are,
    as opposed to the binary PLAY/DON'T PLAY decision.

    Args:
        median_forecast: Dict mapping horizon to median wind speed
        q90_forecast: Dict mapping horizon to 90th percentile wind speed
        thresholds: Threshold configuration

    Returns:
        float: Safety score between 0 and 1
    """
    if thresholds is None:
        thresholds = load_thresholds()

    play_thresholds = thresholds["play"]
    median_max = play_thresholds["median_max_m_s"]
    q90_max = play_thresholds["q90_max_m_s"]

    # Compute worst-case (highest wind) across all horizons
    worst_median = max(median_forecast.values())
    worst_q90 = max(q90_forecast.values())

    # Compute score for each criterion (1.0 = perfect, 0.0 = at/above threshold)
    median_score = max(0, 1 - worst_median / median_max)
    q90_score = max(0, 1 - worst_q90 / q90_max)

    # Overall safety score (average of criteria)
    safety_score = (median_score + q90_score) / 2

    logger.info(f"Safety score: {safety_score:.2f}")
    return safety_score


def suggest_alternative_times(
    forecasts_by_time: Dict[str, Dict],
    thresholds: Optional[Dict] = None,
) -> List[str]:
    """
    Suggest alternative times when conditions might be better.

    Args:
        forecasts_by_time: Dict mapping timestamp to forecast dict
        thresholds: Threshold configuration

    Returns:
        List[str]: Suggested alternative times (timestamps)
    """
    if thresholds is None:
        thresholds = load_thresholds()

    safe_times = []

    for timestamp, forecast in forecasts_by_time.items():
        median = forecast.get("median", {})
        q90 = forecast.get("q90", {})

        # Check if this time passes safety criteria
        decision = decide_play(median, q90, thresholds)

        if decision["decision"] == "PLAY":
            safe_times.append(timestamp)

    logger.info(f"Found {len(safe_times)} safe alternative times")
    return safe_times
