"""
Inference CLI for wind forecasting.

Usage:
    python -m src.cli.infer --model experiments/latest/model.h5
    python -m src.cli.infer --model baseline
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import LATEST_MODEL_DIR, LOG_FORMAT, LOG_LEVEL
from src.data.fetch import load_sample
from src.data.preprocess import build_features
from src.decision.rules import decide_play
from src.models.baseline import PersistenceModel
from src.models.lstm_model import LSTMForecaster
from src.models.quantiles import compute_q90

# Setup logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def load_model(model_path: str):
    """
    Load a model from path.

    Args:
        model_path: Path to model file or 'baseline'

    Returns:
        Loaded model instance
    """
    if model_path == "baseline":
        logger.info("Using baseline persistence model")
        model = PersistenceModel()
        model.is_fitted = True
        return model

    model_path = Path(model_path)

    if not model_path.exists():
        # Try default location
        model_path = LATEST_MODEL_DIR / "model.h5"

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    logger.info(f"Loading model from {model_path}")

    # Determine model type from extension
    if model_path.suffix in [".h5", ".keras"]:
        model = LSTMForecaster()
        model.load(str(model_path))
    else:
        raise ValueError(f"Unknown model format: {model_path.suffix}")

    return model


def make_forecast(model, data_df: pd.DataFrame) -> dict:
    """
    Make forecast using the model.

    Args:
        model: Fitted model
        data_df: Preprocessed data

    Returns:
        dict: Forecast results with median and q90
    """
    logger.info("Making forecast")

    # Get latest forecast
    median_forecast = model.predict_latest(data_df)

    # Compute q90 estimates
    # For simplicity, use scaling factor (documented limitation)
    # In production, would use ensemble or residual-based uncertainty
    q90_forecast = {}
    for key, value in median_forecast.items():
        q90_forecast[key] = value * 1.2  # Conservative estimate

    logger.info(f"Median forecast: {median_forecast}")
    logger.info(f"Q90 forecast: {q90_forecast}")

    return {
        "median": median_forecast,
        "q90": q90_forecast,
    }


def main():
    """Main inference CLI."""
    parser = argparse.ArgumentParser(description="Run wind forecast inference")

    parser.add_argument(
        "--model",
        type=str,
        default="experiments/latest/model.h5",
        help="Path to model file or 'baseline'",
    )

    parser.add_argument(
        "--data",
        type=str,
        default="sample",
        help="Data source: 'sample' or path to CSV file",
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save forecast JSON (prints to stdout if not specified)",
    )

    args = parser.parse_args()

    # Load data
    logger.info(f"Loading data from: {args.data}")
    if args.data == "sample":
        df = load_sample()
    else:
        df = pd.read_csv(args.data, parse_dates=["timestamp"], index_col="timestamp")

    # Preprocess data
    logger.info("Preprocessing data")
    data_df = build_features(df)

    # Load model
    try:
        model = load_model(args.model)
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        sys.exit(1)

    # Make forecast
    try:
        forecast = make_forecast(model, data_df)
    except Exception as e:
        logger.error(f"Forecast failed: {e}")
        sys.exit(1)

    # Make decision
    decision = decide_play(forecast["median"], forecast["q90"])

    # Combine results
    result = {
        "timestamp": str(data_df.index[-1]),
        "forecast": forecast,
        "decision": decision["decision"],
        "reason": decision["reason"],
        "details": decision["details"],
    }

    # Output results
    result_json = json.dumps(result, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(result_json)
        logger.info(f"Forecast saved to {output_path}")
    else:
        print(result_json)

    # Also print decision prominently
    print(f"\n{'='*60}")
    print(f"DECISION: {decision['decision']}")
    print(f"REASON: {decision['reason']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
