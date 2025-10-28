"""
Training CLI for wind forecasting models.

Usage:
    python -m src.cli.train --model lstm --epochs 10
    python -m src.cli.train --model baseline
"""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from src.config import LATEST_MODEL_DIR, LOG_FORMAT, LOG_LEVEL
from src.data.fetch import load_sample
from src.data.preprocess import build_features
from src.models.baseline import PersistenceModel
from src.models.lstm_model import LSTMForecaster
from src.utils.io import ensure_dir

# Setup logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def train_baseline(data_df: pd.DataFrame, save_dir: Path) -> None:
    """
    Train baseline persistence model.

    Args:
        data_df: Preprocessed data
        save_dir: Directory to save model
    """
    logger.info("Training baseline persistence model")

    # Split into train/val (80/20)
    split_idx = int(len(data_df) * 0.8)
    train_df = data_df.iloc[:split_idx]
    val_df = data_df.iloc[split_idx:]

    # Create and fit model
    model = PersistenceModel()
    model.fit(train_df, val_df)

    # Save model (just a marker file for persistence)
    ensure_dir(save_dir)
    model_path = save_dir / "baseline.txt"
    with open(model_path, "w") as f:
        f.write("Baseline persistence model - no state to save\n")

    logger.info(f"Baseline model 'saved' to {model_path}")


def train_lstm(data_df: pd.DataFrame, save_dir: Path, epochs: int = None) -> None:
    """
    Train LSTM forecasting model.

    Args:
        data_df: Preprocessed data
        save_dir: Directory to save model
        epochs: Number of training epochs
    """
    logger.info("Training LSTM model")

    # Split into train/val (80/20)
    split_idx = int(len(data_df) * 0.8)
    train_df = data_df.iloc[:split_idx]
    val_df = data_df.iloc[split_idx:]

    logger.info(f"Train size: {len(train_df)}, Val size: {len(val_df)}")

    # Create and fit model
    model = LSTMForecaster()

    try:
        model.fit(train_df, val_df, epochs=epochs)
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

    # Save model
    ensure_dir(save_dir)
    model_path = save_dir / "model.h5"
    model.save(str(model_path))

    logger.info(f"LSTM model saved to {model_path}")


def main():
    """Main training CLI."""
    parser = argparse.ArgumentParser(description="Train wind forecasting models")

    parser.add_argument(
        "--model",
        type=str,
        choices=["lstm", "baseline"],
        required=True,
        help="Model type to train",
    )

    parser.add_argument(
        "--data",
        type=str,
        default="sample",
        help="Data source: 'sample' or path to CSV file",
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Number of training epochs (LSTM only, uses config default if not specified)",
    )

    parser.add_argument(
        "--save-dir",
        type=str,
        default=None,
        help="Directory to save model (default: experiments/latest/)",
    )

    args = parser.parse_args()

    # Load data
    logger.info(f"Loading data from: {args.data}")
    if args.data == "sample":
        df = load_sample()
    else:
        df = pd.read_csv(args.data, parse_dates=["timestamp"], index_col="timestamp")

    # Preprocess data
    logger.info("Preprocessing data and building features")
    data_df = build_features(df)

    logger.info(f"Preprocessed data shape: {data_df.shape}")
    logger.info(f"Date range: {data_df.index.min()} to {data_df.index.max()}")

    # Determine save directory
    save_dir = Path(args.save_dir) if args.save_dir else LATEST_MODEL_DIR

    # Train model
    if args.model == "baseline":
        train_baseline(data_df, save_dir)
    elif args.model == "lstm":
        train_lstm(data_df, save_dir, epochs=args.epochs)
    else:
        logger.error(f"Unknown model type: {args.model}")
        sys.exit(1)

    logger.info("Training complete!")


if __name__ == "__main__":
    main()
