# 🚀 Quick Start - After Installation

## ✅ What's Installed

Your `badminton-wind` conda environment has been created with:
- ✅ Python 3.10/3.11
- ✅ NumPy, Pandas, Scikit-learn (via conda)
- ✅ Matplotlib, Seaborn (via conda)
- ✅ Pytest (via conda)
- ⏳ **TensorFlow** - Currently downloading (47/377 MB)
- ⏳ Gradio, Black, isort, flake8 - To be installed next

## 📋 Complete Installation Steps

### Step 1: Wait for TensorFlow ⏳
The terminal is currently downloading TensorFlow (377 MB). This will take a few minutes.

### Step 2: Install Remaining Packages

Once TensorFlow finishes, run:

```powershell
# Make sure environment is active
conda activate badminton-wind

# Quick install of remaining packages
pip install gradio==4.26.0 black==24.3.0 isort==5.13.2 flake8==7.0.0
```

**OR** use the automated script:
```powershell
conda activate badminton-wind
.\install_pip_packages.ps1
```

### Step 3: Verify Installation

```powershell
# Test TensorFlow
python -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__} ✓')"

# Test Gradio
python -c "import gradio; print('Gradio ✓')"

# Test project imports
python -c "from src import config; print('Project ready ✓')"
```

## 🎯 First Run - Your Next Commands

Once installation is complete:

```powershell
# 1. Generate sample data (takes ~5 seconds)
python scripts/make_sample_data.py

# 2. Train baseline model (instant)
python -m src.cli.train --model baseline

# 3. Train LSTM model (1-2 minutes for 5 epochs)
python -m src.cli.train --model lstm --epochs 5

# 4. Run inference and get decision
python -m src.cli.infer --model experiments/latest/model.h5

# 5. Launch the web UI
cd deployment/hf_space
python app.py
```

## 📊 Expected Output

### After Data Generation:
```
Generating 2000 hours of synthetic weather data...
Random seed: 42
✓ Saved to G:\PROJECTS\badminton\data\sample_station.csv
```

### After Training:
```
Training LSTM model
Train size: 1437, Val size: 360
...
LSTM training complete
LSTM model saved to experiments/latest/model.h5
```

### After Inference:
```json
{
  "timestamp": "2024-03-23 07:00:00",
  "forecast": {
    "median": {
      "horizon_1h": 1.23,
      "horizon_3h": 1.45,
      "horizon_6h": 1.67
    }
  },
  "decision": "PLAY",
  "reason": "All horizons pass safety criteria..."
}
```

## ⚠️ If Something Goes Wrong

Check `TROUBLESHOOTING.md` for solutions to common issues.

**Quick fixes:**
- TensorFlow fails: `pip install tensorflow==2.16.1 --default-timeout=200`
- Import errors: Make sure `conda activate badminton-wind` is active
- Module not found: Reinstall with `pip install -r requirements.txt`

## 🎓 Learning Resources

- **README.md** - Full project documentation
- **docs/design.md** - Technical architecture details  
- **notebooks/00_quickstart_colab.ipynb** - Interactive tutorial
- **SETUP.md** - Detailed conda setup guide

## 💡 Pro Tips

1. **Always activate first:** `conda activate badminton-wind`
2. **Check environment:** `conda env list` (should see `*` next to badminton-wind)
3. **Verify Python:** `python --version` (should be 3.10.x or 3.11.x)
4. **List packages:** `conda list` or `pip list`

---

**Current Status:**  
✅ Conda environment created  
⏳ TensorFlow downloading (47/377 MB)  
⏸️ Waiting for remaining packages  

**Next:** After download completes, install Gradio and dev tools, then you're ready to go! 🚀
