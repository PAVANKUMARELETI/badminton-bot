"""
Central configuration for the badminton wind predictor.

This module contains all paths, hyperparameters, and settings used throughout the project.
All random operations use RANDOM_SEED for reproducibility.
"""

from pathlib import Path

# ============================================================================
# PATHS
# ============================================================================

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
SAMPLE_DATA_PATH = DATA_DIR / "sample_station.csv"

# Model and experiment directories
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"
LATEST_MODEL_DIR = EXPERIMENTS_DIR / "latest"

# Source directories
SRC_DIR = PROJECT_ROOT / "src"
DECISION_THRESHOLDS_PATH = SRC_DIR / "decision" / "thresholds.json"

# ============================================================================
# REPRODUCIBILITY
# ============================================================================

RANDOM_SEED = 42

# ============================================================================
# DATA GENERATION
# ============================================================================

# Sample data size (number of hourly records)
SAMPLE_DATA_SIZE = 2000

# Synthetic data parameters (mean values for random walk)
SYNTH_WIND_MEAN = 1.8  # m/s
SYNTH_WIND_STD = 0.8
SYNTH_GUST_MULTIPLIER = 1.4  # Gusts are ~1.4x mean wind
SYNTH_PRESSURE_MEAN = 1013.25  # hPa
SYNTH_PRESSURE_STD = 10.0
SYNTH_TEMP_MEAN = 20.0  # °C
SYNTH_TEMP_STD = 5.0
SYNTH_HUMIDITY_MEAN = 60.0  # %
SYNTH_HUMIDITY_STD = 15.0

# ============================================================================
# PREPROCESSING
# ============================================================================

# Target variable
TARGET_COLUMN = "wind_m_s"

# Feature engineering
LAG_HOURS = [1, 2, 3, 6, 12, 24]  # Lag features to create
PRESSURE_TENDENCY_HOURS = 3  # Hours for pressure tendency calculation

# Maximum allowed gap for interpolation (hours)
MAX_GAP_FILL_HOURS = 3

# ============================================================================
# FORECASTING
# ============================================================================

# Forecast horizons (hours ahead)
HORIZONS = [1, 3, 6]

# Sequence length for LSTM (how many hours of history to use)
SEQUENCE_LENGTH = 24

# Train/validation split
TRAIN_VAL_SPLIT = 0.8  # 80% train, 20% validation

# ============================================================================
# MODEL HYPERPARAMETERS
# ============================================================================

# LSTM Model
LSTM_CONFIG = {
    "units": [32, 16],  # LSTM layer units (small for fast training)
    "dropout": 0.2,
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 5,  # Default for quick training; increase for better performance
    "patience": 5,  # Early stopping patience
}

# Quantile estimation
N_BOOTSTRAP_SAMPLES = 10  # Number of bootstrap samples for uncertainty (small for speed)
QUANTILE_LEVELS = [0.1, 0.5, 0.9]  # Quantiles to compute (10th, 50th, 90th percentile)

# ============================================================================
# EVALUATION
# ============================================================================

# Rolling window backtest
BACKTEST_WINDOW_SIZE = 168  # Hours (1 week)
BACKTEST_STEP_SIZE = 24  # Hours (1 day)

# ============================================================================
# DECISION THRESHOLDS
# ============================================================================

# BWF (Badminton World Federation) AirBadminton Recommendations:
# - Optimal wind: 6-12 km/h (1.67-3.33 m/s)
# - Maximum safe: 12 km/h (3.33 m/s)
# 
# These are defaults; the actual values are loaded from thresholds.json
DEFAULT_THRESHOLDS = {
    "speed_unit": "m/s",
    "play": {
        "median_max_m_s": 3.33,  # 12 km/h - BWF maximum for AirBadminton
        "q90_max_m_s": 5.0,       # ~18 km/h - Allow some gusts above median
        "prob_over_3m_s_max": 0.1,
    },
}

# ============================================================================
# LOGGING
# ============================================================================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
