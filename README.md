# Badminton Wind Predictor

A complete, end-to-end machine learning system for predicting short-term wind conditions (1h/3h/6h) and deciding whether it's safe to play badminton outdoors. Uses synthetic data generation, LSTM forecasting, and a decision engine with configurable thresholds.

## Features

- ⚡ **Fast setup**: Works locally and in Google Colab
- 🆓 **Zero-cost**: Uses synthetic data, runs on free tiers
- 🧪 **Well-tested**: Unit tests and CI with GitHub Actions
- 🚀 **Deployment-ready**: Gradio UI for Hugging Face Spaces
- 📊 **Reproducible**: Deterministic RNG and pinned dependencies
- 🤖 **Bot integrations**: Telegram & WhatsApp bots for easy access

## Quick Start (Local)

### 1. Setup Environment

#### Option A: Conda (Recommended)

```powershell
# Create conda environment from YAML file
conda env create -f environment.yml

# Activate environment
conda activate badminton-wind
```

Or use the automated setup script:
```powershell
.\setup_conda.ps1
```

#### Option B: pip + venv

```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Sample Data

```bash
python scripts/make_sample_data.py
```

### 3. Train Models

```bash
# Train baseline (persistence model)
python -m src.cli.train --model baseline --epochs 0

# Train LSTM (quick training for demo)
python -m src.cli.train --model lstm --epochs 5
```

### 4. Run Inference

```bash
python -m src.cli.infer --model experiments/latest/model.h5
```

This outputs JSON with forecasts for 1h/3h/6h horizons and a PLAY/DON'T PLAY decision.

### 5. Run Tests

```bash
pytest
```

### 6. Launch Gradio UI (Local)

```bash
cd deployment/hf_space
python app.py
```

Open your browser to the URL shown (typically http://127.0.0.1:7860).

## Quick Start (Google Colab)

Open `notebooks/00_quickstart_colab.ipynb` in Colab and run all cells. It will:
1. Generate sample data
2. Preprocess features
3. Train a tiny LSTM for 1 epoch
4. Show forecast and decision

## Project Structure

```
badminton-wind-predictor/
├── data/
│   ├── raw/                    # Gitignored, for real data
│   └── sample_station.csv      # Synthetic hourly data (2000 rows)
├── src/
│   ├── config.py               # Central configuration
│   ├── data/
│   │   ├── fetch.py            # Data loading
│   │   └── preprocess.py       # Feature engineering
│   ├── models/
│   │   ├── baseline.py         # Persistence model
│   │   ├── lstm_model.py       # LSTM forecaster
│   │   └── quantiles.py        # Uncertainty quantification
│   ├── eval/
│   │   ├── metrics.py          # MAE, RMSE, quantile loss
│   │   └── backtest.py         # Rolling-window validation
│   ├── decision/
│   │   ├── rules.py            # Play/Don't Play logic
│   │   └── thresholds.json     # Decision thresholds
│   ├── utils/
│   │   └── io.py               # I/O helpers
│   └── cli/
│       ├── train.py            # Training CLI
│       └── infer.py            # Inference CLI
├── scripts/
│   ├── make_sample_data.py     # Generate synthetic data
│   └── run_all.sh              # End-to-end pipeline
├── tests/
│   ├── test_preprocess.py      # Feature engineering tests
│   ├── test_metrics.py         # Metric calculation tests
│   ├── test_decision.py        # Decision logic tests
│   └── test_smoke_train.py     # Fast training smoke test
├── deployment/
│   └── hf_space/
│       ├── app.py              # Gradio app
│       └── requirements.txt    # HF Space dependencies
├── experiments/
│   └── latest/                 # Model artifacts (gitignored)
├── notebooks/
│   └── 00_quickstart_colab.ipynb
├── docs/
│   └── design.md               # Design decisions
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI
├── requirements.txt
├── pyproject.toml
├── Makefile
├── .gitignore
└── LICENSE
```

## Using the Makefile

```bash
# Setup environment and install dependencies
make setup

# Generate sample data
make data

# Train models
make train

# Run all tests
make test

# Run inference
make infer

# Launch Gradio UI
make ui
```

## Deployment to Hugging Face Spaces

1. Create a new Space at https://huggingface.co/new-space
2. Choose "Gradio" as the SDK
3. Clone the Space repository:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
   ```
4. Copy deployment files:
   ```bash
   cp deployment/hf_space/* YOUR_SPACE_NAME/
   cp -r experiments/latest YOUR_SPACE_NAME/experiments/
   cp -r src YOUR_SPACE_NAME/
   ```
5. Commit and push:
   ```bash
   cd YOUR_SPACE_NAME
   git add .
   git commit -m "Initial deployment"
   git push
   ```

The Space will automatically build and deploy your Gradio app.

## 🤖 Bot Integrations

Make your forecaster available via messaging apps! Perfect for college groups.

### Quick Setup - Telegram Bot (Recommended, 100% Free)

```powershell
# 1. Install dependencies
pip install python-telegram-bot python-dotenv

# 2. Create bot via @BotFather on Telegram and get token

# 3. Set token
$env:TELEGRAM_BOT_TOKEN = "your-token-here"

# 4. Start bot
python -m src.integrations.telegram_bot

# OR use the quick-start script
.\scripts\start_telegram_bot.ps1
```

Your friends can now message the bot:
- `/start` - Get welcome message
- `/forecast` - Get wind forecast & play decision
- "Can I play?" - Any text gets instant forecast!

### WhatsApp Bot Setup

```powershell
# 1. Sign up at https://www.twilio.com (free tier)
# 2. Get WhatsApp sandbox credentials
# 3. Set environment variables
# 4. Start bot
.\scripts\start_whatsapp_bot.ps1
```

### Detailed Setup Guide

See **[docs/BOT_SETUP.md](docs/BOT_SETUP.md)** for:
- Step-by-step Telegram/WhatsApp setup
- Feature ideas for college groups
- Deployment options (24/7 online)
- Advanced features (notifications, polls, leaderboards)

## Configuration

Edit `src/config.py` to change:
- **Forecast horizons**: `[1, 3, 6]` hours by default
- **Random seed**: `42` for reproducibility
- **Model hyperparameters**: LSTM units, layers, dropout
- **Training parameters**: epochs, batch size, learning rate

Edit `src/decision/thresholds.json` to adjust play/don't play criteria:
- `median_max_m_s`: Maximum median wind speed (m/s)
- `q90_max_m_s`: Maximum 90th percentile wind speed
- `prob_over_3m_s_max`: Maximum probability of wind > 3 m/s

## API Keys (Optional)

If you have access to weather APIs (e.g., METAR, OpenWeather), set environment variables:

```bash
# PowerShell
$env:WEATHER_API_KEY = "your_key_here"
```

The system will gracefully fall back to synthetic data if keys are missing.

## Development

### Code Style

```bash
# Format code
black src tests scripts

# Sort imports
isort src tests scripts
```

### Running Specific Tests

```bash
# Run only fast tests
pytest -m "not slow"

# Run with coverage
pytest --cov=src --cov-report=html
```

## Model Performance

### Current Status: ⚠️ Trained on Synthetic Data

The current deployed model is trained on **synthetic/sample data** for demonstration purposes:
- **Baseline (Persistence)**: MAE ~0.3 m/s, RMSE ~0.45 m/s
- **LSTM**: MAE ~0.25 m/s, RMSE ~0.38 m/s (after 50 epochs)

### 🎯 Next Step: Train on Real Historical Data

To achieve production-ready performance, the model needs to be trained on **real historical weather data** from IIIT Lucknow:

**Option 1: OpenWeatherMap Historical API (Paid)**
- Requires paid subscription for historical data access
- Can fetch years of hourly observations
- Run: `python scripts/retrain_on_real_data.py` (requires historical API key)

**Option 2: Local Weather Station Data**
- Collect data from a local weather station
- Export as CSV with columns: `datetime, wind_m_s, wind_gust_m_s, temp, humidity, pressure`
- Place in `data/raw/` and retrain

**Option 3: Accumulate Forecast Data Over Time**
- The bot saves current weather observations automatically
- After 30+ days of operation, retrain on accumulated real data
- This will provide location-specific patterns

### Expected Real-World Performance
Once trained on real IIIT Lucknow data:
- **MAE**: 0.4-0.6 m/s (1.4-2.2 km/h) for 1h forecasts
- **RMSE**: 0.6-0.8 m/s (2.2-2.9 km/h) for 1h forecasts
- Performance degrades for longer horizons (3h, 6h)

> **Note**: The bot currently works with live OpenWeatherMap forecasts for decision-making. The LSTM model provides additional context but isn't strictly required for the NOW mode, which uses current weather conditions directly.

## Citation

If you use this project, please cite:

```bibtex
@software{badminton_wind_predictor,
  title={Badminton Wind Predictor},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/badminton-wind-predictor}
}
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure `pytest` passes
5. Submit a pull request

## Support

For issues or questions, please open a GitHub issue.
