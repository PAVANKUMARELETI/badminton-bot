# Post-installation script for pip packages
# Run this AFTER creating the conda environment

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Installing Remaining Packages" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if badminton-wind environment is active
$currentEnv = $env:CONDA_DEFAULT_ENV

if ($currentEnv -ne "badminton-wind") {
    Write-Host "ERROR: badminton-wind environment is not active" -ForegroundColor Red
    Write-Host "Please run: conda activate badminton-wind" -ForegroundColor Yellow
    Write-Host "Then run this script again" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Environment 'badminton-wind' is active" -ForegroundColor Green
Write-Host ""

# Install packages one by one with progress
$packages = @(
    @{name="TensorFlow"; package="tensorflow==2.16.1"; size="~377 MB"},
    @{name="Gradio"; package="gradio==4.26.0"; size="~50 MB"},
    @{name="Black"; package="black==24.3.0"; size="~5 MB"},
    @{name="isort"; package="isort==5.13.2"; size="~2 MB"},
    @{name="flake8"; package="flake8==7.0.0"; size="~2 MB"}
)

$total = $packages.Count
$current = 0

foreach ($pkg in $packages) {
    $current++
    Write-Host "[$current/$total] Installing $($pkg.name) ($($pkg.size))..." -ForegroundColor Yellow
    
    pip install $pkg.package --default-timeout=100
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $($pkg.name) installed successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to install $($pkg.name)" -ForegroundColor Red
        Write-Host "  Try manually: pip install $($pkg.package)" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Verify installations
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Verifying Installations" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test TensorFlow
Write-Host "Testing TensorFlow..." -ForegroundColor Yellow
python -c "import tensorflow as tf; print(f'  ✓ TensorFlow {tf.__version__} works!')" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ TensorFlow not working" -ForegroundColor Red
} else {
    Write-Host ""
}

# Test Gradio
Write-Host "Testing Gradio..." -ForegroundColor Yellow
python -c "import gradio as gr; print(f'  ✓ Gradio {gr.__version__} works!')" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Gradio not working" -ForegroundColor Red
} else {
    Write-Host ""
}

# Test project imports
Write-Host "Testing project imports..." -ForegroundColor Yellow
python -c "from src.models.lstm_model import LSTMForecaster; print('  ✓ Project imports work!')" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Project imports not working (this is OK if you haven't generated data yet)" -ForegroundColor Yellow
} else {
    Write-Host ""
}

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Generate data: python scripts/make_sample_data.py" -ForegroundColor White
Write-Host "  2. Train model: python -m src.cli.train --model lstm --epochs 5" -ForegroundColor White
Write-Host "  3. Run inference: python -m src.cli.infer" -ForegroundColor White
Write-Host ""
