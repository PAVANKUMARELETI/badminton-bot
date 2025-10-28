# Experiments Directory

This directory stores trained model artifacts and experiment results.

## Structure

```
experiments/
├── latest/              # Latest trained model (gitignored)
│   ├── model.h5        # LSTM model weights
│   ├── scaler.npz      # Feature scaling parameters
│   └── baseline.txt    # Baseline model marker
├── run_001/            # Example: timestamped experiments
├── run_002/
└── ...
```

## Model Artifacts

### LSTM Model

- **model.h5**: Keras model in HDF5 format
- **scaler.npz**: NumPy archive with:
  - `mean`: Feature means for normalization
  - `std`: Feature standard deviations
  - `feature_cols`: List of feature column names

### Baseline Model

- **baseline.txt**: Marker file (persistence model has no learned parameters)

## Loading Models

```python
from src.models.lstm_model import LSTMForecaster

model = LSTMForecaster()
model.load("experiments/latest/model.h5")
```

## Experiment Tracking

For production use, consider:

- [MLflow](https://mlflow.org/) for experiment tracking
- [Weights & Biases](https://wandb.ai/) for visualization
- Version control model artifacts with [DVC](https://dvc.org/)

## Storage Notes

- The `experiments/` directory is gitignored to avoid committing large model files
- For deployment, copy model artifacts to the deployment directory
- Consider cloud storage (S3, GCS) for production model versioning
