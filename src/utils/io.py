"""
I/O utilities for loading and saving models and data artifacts.

Provides consistent interface for reading/writing various file formats
used throughout the project.
"""

import logging
import pickle
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def save_pickle(obj: Any, path: str) -> None:
    """
    Save an object to pickle file.

    Args:
        obj: Object to save
        path: Path to save to
    """
    save_path = Path(path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with open(save_path, "wb") as f:
        pickle.dump(obj, f)

    logger.info(f"Saved pickle to {save_path}")


def load_pickle(path: str) -> Any:
    """
    Load an object from pickle file.

    Args:
        path: Path to load from

    Returns:
        Any: Loaded object
    """
    with open(path, "rb") as f:
        obj = pickle.load(f)

    logger.info(f"Loaded pickle from {path}")
    return obj


def save_csv(df: pd.DataFrame, path: str, **kwargs) -> None:
    """
    Save DataFrame to CSV.

    Args:
        df: DataFrame to save
        path: Path to save to
        **kwargs: Additional arguments passed to to_csv
    """
    save_path = Path(path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(save_path, **kwargs)
    logger.info(f"Saved CSV to {save_path} ({len(df)} rows)")


def load_csv(path: str, **kwargs) -> pd.DataFrame:
    """
    Load DataFrame from CSV.

    Args:
        path: Path to load from
        **kwargs: Additional arguments passed to read_csv

    Returns:
        pd.DataFrame: Loaded data
    """
    df = pd.read_csv(path, **kwargs)
    logger.info(f"Loaded CSV from {path} ({len(df)} rows)")
    return df


def save_parquet(df: pd.DataFrame, path: str, **kwargs) -> None:
    """
    Save DataFrame to Parquet (more efficient than CSV).

    Args:
        df: DataFrame to save
        path: Path to save to
        **kwargs: Additional arguments passed to to_parquet
    """
    save_path = Path(path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(save_path, **kwargs)
    logger.info(f"Saved Parquet to {save_path} ({len(df)} rows)")


def load_parquet(path: str, **kwargs) -> pd.DataFrame:
    """
    Load DataFrame from Parquet.

    Args:
        path: Path to load from
        **kwargs: Additional arguments passed to read_parquet

    Returns:
        pd.DataFrame: Loaded data
    """
    df = pd.read_parquet(path, **kwargs)
    logger.info(f"Loaded Parquet from {path} ({len(df)} rows)")
    return df


def ensure_dir(path: str) -> Path:
    """
    Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path: Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
