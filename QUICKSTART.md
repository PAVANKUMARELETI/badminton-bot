# Badminton Wind Predictor - Quick Start

## ✅ Installation Complete!

Your badminton wind forecasting project is now fully operational!

## 🚀 Quick Commands

### Activate Environment
```powershell
conda activate badminton-wind
```

### Generate Sample Data
```powershell
python scripts/make_sample_data.py
```

### Train a Model
```powershell
# Quick training (2 epochs for testing)
python -m src.cli.train --model lstm --data sample --epochs 2

# Full training (default 50 epochs)
python -m src.cli.train --model lstm --data sample
```

### Run Inference
```powershell
python -m src.cli.infer --model experiments/latest/model.keras --data sample
```

### Run Tests
```powershell
pytest tests/ -v
```

### Code Formatting
```powershell
black src/ tests/ scripts/
isort src/ tests/ scripts/
flake8 src/ tests/ scripts/
```

## 📊 What Just Worked

Your system successfully:
1. ✅ Loaded 2000 hours of synthetic weather data
2. ✅ Built 22 engineered features (lag features, cyclical time, pressure tendency, wind components)
3. ✅ Trained an LSTM neural network with 10,227 parameters
4. ✅ Made multi-horizon forecasts (1h, 3h, 6h ahead)
5. ✅ Applied safety thresholds and decision rules
6. ✅ Output a PLAY/DON'T PLAY recommendation

## 📁 Key Files

- **`src/config.py`** - Central configuration (thresholds, model params)
- **`src/models/lstm_model.py`** - LSTM forecaster implementation
- **`src/cli/train.py`** - Training CLI
- **`src/cli/infer.py`** - Inference CLI
- **`experiments/latest/model.keras`** - Trained model
- **`data/sample_station.csv`** - Generated sample data

## 🎯 Example Output

The inference CLI just gave you:
```json
{
  "decision": "DON'T PLAY",
  "forecast": {
    "median": {
      "horizon_1h": 1.68,
      "horizon_3h": 1.63,
      "horizon_6h": 1.51
    }
  },
  "reason": "Safety violations detected: median wind > 1.5 m/s"
}
```

## 🔧 Customize Thresholds

Edit `src/decision/thresholds.json` to adjust safety limits:
```json
{
  "median_max_m_s": 1.5,
  "q90_max_m_s": 3.5
}
```

## 📚 Next Steps

1. **Use Real Data**: Replace `data/sample_station.csv` with actual weather station CSV
2. **Tune Model**: Adjust hyperparameters in `src/config.py`
3. **Deploy Web UI**: Run `python deployment/hf_space/app.py` (Gradio interface)
4. **Add More Features**: Extend `src/data/preprocess.py` with domain knowledge

## 🐛 Troubleshooting

If you encounter issues:
- Check `TROUBLESHOOTING.md` for common solutions
- Ensure conda environment is activated: `conda activate badminton-wind`
- Verify TensorFlow/Gradio versions: `pip list | findstr tensorflow gradio`

## 📖 Full Documentation

- **README.md** - Project overview and architecture
- **SETUP.md** - Detailed installation guide
- **GETTING_STARTED.md** - Step-by-step tutorials
- **docs/design.md** - Technical design decisions

---

**Status**: 🟢 All systems operational!

You're ready to forecast wind conditions for badminton! 🏸
