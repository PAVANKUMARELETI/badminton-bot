#!/bin/bash

# End-to-end pipeline for badminton wind predictor
# This script runs the full workflow from data generation to inference

set -e  # Exit on error

echo "======================================"
echo "Badminton Wind Predictor - Full Pipeline"
echo "======================================"

# Step 1: Generate sample data
echo ""
echo "[1/5] Generating sample data..."
python scripts/make_sample_data.py

# Step 2: Train baseline model
echo ""
echo "[2/5] Training baseline (persistence) model..."
python -m src.cli.train --model baseline

# Step 3: Train LSTM model (small training for demo)
echo ""
echo "[3/5] Training LSTM model (quick training)..."
python -m src.cli.train --model lstm --epochs 5

# Step 4: Run inference
echo ""
echo "[4/5] Running inference..."
python -m src.cli.infer --model experiments/latest/model.h5

# Step 5: Run tests
echo ""
echo "[5/5] Running tests..."
pytest -v -m "not slow"

echo ""
echo "======================================"
echo "Pipeline complete!"
echo "======================================"
