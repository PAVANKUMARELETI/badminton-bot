# Setup script for Badminton Wind Predictor (Windows PowerShell)
# This script creates a conda environment and installs all dependencies

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Badminton Wind Predictor Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if conda is available
Write-Host "Checking for conda..." -ForegroundColor Yellow
$condaExists = Get-Command conda -ErrorAction SilentlyContinue

if (-not $condaExists) {
    Write-Host "ERROR: Conda not found in PATH" -ForegroundColor Red
    Write-Host "Please install Anaconda or Miniconda first:" -ForegroundColor Red
    Write-Host "  https://www.anaconda.com/download" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Conda found" -ForegroundColor Green
Write-Host ""

# Create conda environment from environment.yml
Write-Host "Creating conda environment 'badminton-wind'..." -ForegroundColor Yellow
conda env create -f environment.yml

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create conda environment" -ForegroundColor Red
    Write-Host "You can try manually with: conda env create -f environment.yml" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Environment created successfully" -ForegroundColor Green
Write-Host ""

# Instructions
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To activate the environment, run:" -ForegroundColor Yellow
Write-Host "  conda activate badminton-wind" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Activate the environment: conda activate badminton-wind" -ForegroundColor White
Write-Host "  2. Generate sample data: python scripts/make_sample_data.py" -ForegroundColor White
Write-Host "  3. Train models: python -m src.cli.train --model lstm --epochs 5" -ForegroundColor White
Write-Host "  4. Run inference: python -m src.cli.infer" -ForegroundColor White
Write-Host ""
