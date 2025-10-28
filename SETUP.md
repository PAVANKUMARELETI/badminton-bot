# Quick Setup Guide - Badminton Wind Predictor

## 🚀 Using Conda (Recommended for Windows)

### One-Command Setup
```powershell
# Run the automated setup script
.\setup_conda.ps1
```

### Manual Setup
```powershell
# 1. Create environment
conda env create -f environment.yml

# 2. Activate environment
conda activate badminton-wind

# 3. Verify installation
python -c "import tensorflow as tf; import pandas as pd; print('✓ All packages installed')"
```

## 📦 What Gets Installed

The `badminton-wind` conda environment includes:

- **Python 3.10** - Base interpreter
- **NumPy 1.26.4** - Numerical computing
- **Pandas 2.2.1** - Data manipulation
- **Scikit-learn 1.4.1** - ML utilities
- **TensorFlow 2.16.1** - Deep learning (LSTM)
- **Matplotlib 3.8.3** - Plotting
- **Gradio 4.26.0** - Web UI
- **Pytest 8.1.1** - Testing
- **Black, isort, flake8** - Code formatting

Total environment size: ~2-3 GB

## 🎯 After Setup - Quick Commands

```powershell
# Always activate first!
conda activate badminton-wind

# Generate data
python scripts/make_sample_data.py

# Train baseline model
python -m src.cli.train --model baseline

# Train LSTM (quick)
python -m src.cli.train --model lstm --epochs 5

# Run inference
python -m src.cli.infer --model experiments/latest/model.h5

# Run tests
pytest -v

# Launch UI
cd deployment/hf_space
python app.py
```

## 🔧 Troubleshooting

### "conda: command not found"
- Install Anaconda: https://www.anaconda.com/download
- Or Miniconda: https://docs.conda.io/en/latest/miniconda.html
- Restart PowerShell after installation

### TensorFlow installation issues
```powershell
# If TensorFlow fails, install separately:
conda activate badminton-wind
pip install tensorflow==2.16.1
```

### Environment already exists
```powershell
# Remove old environment
conda env remove -n badminton-wind

# Create fresh environment
conda env create -f environment.yml
```

## 📝 Environment Management

```powershell
# List all conda environments
conda env list

# Activate this environment
conda activate badminton-wind

# Deactivate environment
conda deactivate

# Export environment (after changes)
conda env export > environment.yml

# Remove environment
conda env remove -n badminton-wind
```

## 🆚 Conda vs pip/venv

**Use Conda if:**
- ✅ You're on Windows
- ✅ You want easier TensorFlow installation
- ✅ You use Anaconda/Miniconda already
- ✅ You want binary package management

**Use pip/venv if:**
- ✅ You prefer lightweight environments
- ✅ You're deploying to cloud (Colab, HF Spaces)
- ✅ You don't have conda installed

Both methods work perfectly - choose what you prefer!

## 💡 Pro Tips

1. **Always activate before working:**
   ```powershell
   conda activate badminton-wind
   ```

2. **Check what's installed:**
   ```powershell
   conda list
   ```

3. **Update packages:**
   ```powershell
   conda update --all
   ```

4. **Create requirements.txt from conda env:**
   ```powershell
   pip list --format=freeze > requirements.txt
   ```

## 🎓 Next Steps

After environment setup:

1. ✅ Read `README.md` for project overview
2. ✅ Generate sample data: `python scripts/make_sample_data.py`
3. ✅ Open Jupyter: `jupyter notebook notebooks/00_quickstart_colab.ipynb`
4. ✅ Train your first model!

---

**Questions?** Check `README.md` or `docs/design.md` for detailed documentation.
