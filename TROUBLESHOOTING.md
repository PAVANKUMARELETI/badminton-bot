# Installation Troubleshooting Guide

## ✅ Current Status

The conda environment `badminton-wind` has been created successfully with all packages **except** the pip dependencies (TensorFlow, Gradio, etc.) which failed due to network timeout.

## 🔧 Quick Fix (Currently Running)

TensorFlow is being installed separately with:
```powershell
pip install tensorflow==2.16.1 --default-timeout=100
```

This is downloading ~377 MB and may take a few minutes depending on your internet speed.

## 📦 Remaining Packages to Install

After TensorFlow completes, install the remaining packages:

```powershell
# Make sure badminton-wind is activated
conda activate badminton-wind

# Install remaining packages
pip install gradio==4.26.0 black==24.3.0 isort==5.13.2 flake8==7.0.0
```

## 🚀 Alternative: Install All at Once

If the step-by-step approach is tedious, you can install all pip packages at once:

```powershell
conda activate badminton-wind
pip install -r requirements.txt --default-timeout=100
```

## ✅ Verify Installation

Once all packages are installed, verify everything works:

```powershell
# Check TensorFlow
python -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__} ✓')"

# Check Gradio
python -c "import gradio as gr; print(f'Gradio {gr.__version__} ✓')"

# Check all imports from the project
python -c "from src.models.lstm_model import LSTMForecaster; print('All imports working ✓')"
```

## 🐛 Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'tensorflow'"

**Solution:**
```powershell
conda activate badminton-wind
pip install tensorflow==2.16.1
```

### Issue 2: Network timeout during pip install

**Solution:** Increase timeout and try again:
```powershell
pip install tensorflow==2.16.1 --default-timeout=200 --retries 5
```

Or use a mirror:
```powershell
pip install tensorflow==2.16.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Issue 3: "WARNING: Ignoring invalid distribution"

**Solution:** This is a harmless warning, can be ignored. Or clean up:
```powershell
pip install --upgrade --force-reinstall pip
```

### Issue 4: Conda environment not activating

**Solution:**
```powershell
# Re-initialize conda
conda init powershell

# Close and reopen PowerShell

# Try activating again
conda activate badminton-wind
```

### Issue 5: Multiple Python versions causing conflicts

**Solution:** Use conda's Python explicitly:
```powershell
conda activate badminton-wind
python --version  # Should show Python 3.10.x or 3.11.x
which python     # Should point to anaconda3/envs/badminton-wind/
```

## 🔄 Clean Reinstall (Nuclear Option)

If everything fails, start fresh:

```powershell
# Remove the environment
conda deactivate
conda env remove -n badminton-wind

# Recreate with just conda packages (no pip)
conda create -n badminton-wind python=3.10 numpy pandas scikit-learn matplotlib pytest -y

# Activate and install pip packages separately
conda activate badminton-wind
pip install tensorflow==2.16.1 gradio==4.26.0 black isort flake8
```

## 📝 Manual Installation Checklist

If you prefer manual control:

```powershell
# 1. Create basic environment
conda create -n badminton-wind python=3.10 -y

# 2. Activate
conda activate badminton-wind

# 3. Install conda packages
conda install numpy pandas scikit-learn matplotlib seaborn pyyaml tqdm pytest pytest-cov -y

# 4. Install TensorFlow (largest package, install first)
pip install tensorflow==2.16.1

# 5. Install Gradio
pip install gradio==4.26.0

# 6. Install dev tools
pip install black isort flake8

# 7. Verify
python -c "import tensorflow as tf; import gradio; print('All good ✓')"
```

## 🎯 Minimal Installation (Just to Run)

If you want the absolute minimum to run the project:

```powershell
conda activate badminton-wind

# Core requirements only
pip install tensorflow==2.16.1 gradio==4.26.0

# Skip black, isort, flake8 (only needed for development)
```

This is enough to:
- ✅ Generate data
- ✅ Train models
- ✅ Run inference
- ✅ Launch UI
- ❌ Run code formatting (black/isort)

## 💡 Pro Tips

1. **Install TensorFlow first** - It's the largest package (377 MB)
2. **Use `--default-timeout=100`** - Helps with slow connections
3. **Check your environment** - Always verify with `conda activate badminton-wind` first
4. **Test incrementally** - Install one package, test, then move to next

## 🆘 Still Having Issues?

Check these:

1. **Internet connection** - TensorFlow is 377 MB
2. **Disk space** - Need ~3-4 GB free
3. **Antivirus/Firewall** - May block pip downloads
4. **Corporate proxy** - May need proxy configuration
5. **Python version** - Should be 3.10 or 3.11

---

**Current Status:** TensorFlow is downloading (see terminal for progress)
**Next:** After download completes, install Gradio and other packages
**Then:** You're ready to run the project!
