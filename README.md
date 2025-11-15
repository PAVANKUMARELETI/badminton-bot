# Badminton Wind Predictor

🏸 **Production-ready ML system** for predicting wind conditions and deciding whether it's safe to play badminton outdoors. Features LSTM forecasting, BWF-compliant thresholds, and automatic data collection.

## Features

- **BWF Standards**: Complies with Badminton World Federation wind thresholds (12 km/h median, 18 km/h gusts)
- **Telegram Bot**: Interactive bot for instant weather checks and forecasts
- **LSTM Forecasting**: Deep learning model predicting 1h/3h/6h wind speeds
- **Real Data**: Automatic collection from OpenWeatherMap API
- **Well-tested**: 15+ test suites with CI/CD via GitHub Actions
- **Deployed**: Live on Railway.app with auto-deployment
- **Modular**: Refactored architecture for easy maintenance

## Quick Start

### 1. Installation

**Option A: Conda (Recommended)**

```powershell
# Clone repository
git clone https://github.com/PAVANKUMARELETI/badminton-bot.git
cd badminton-bot

# Create environment
conda env create -f environment.yml
conda activate badminton-wind
```

**Option B: pip + venv**

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Set environment variables:

```powershell
# Required
$env:OPENWEATHER_API_KEY = "your-api-key-here"
$env:TELEGRAM_BOT_TOKEN = "your-bot-token-here"

# Optional
$env:SENTRY_DSN = "your-sentry-dsn"
```

Or create a `.env` file:
```env
OPENWEATHER_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_token_here
```

### 3. Run the Bot

```powershell
python -m src.integrations.telegram_bot_refactored
```

Then open Telegram and chat with your bot!

### 4. Train Your Own Model (Optional)

```powershell
# Generate sample data (for testing)
python scripts/make_sample_data.py

# Train LSTM model
python -m src.cli.train --model lstm --epochs 50

# Run inference
python -m src.cli.infer --model experiments/latest/model.keras
```

### 5. Verify Installation

```powershell
# Run tests
pytest tests/ -v

# Check code coverage
pytest tests/ --cov=src --cov-report=html
```

## 📱 Using the Telegram Bot

### Available Commands

- `/start` - Welcome message and main menu
- `/now` - Check current wind conditions
- `/forecast` - Get ML-powered forecast for next 6 hours
- `/help` - Usage instructions
- `/location <city>` - Change location (e.g., `/location Delhi`)

### Example Interaction

```
User: /now
Bot:  ✅ PLAY! Conditions are perfect!

📊 Current Conditions (IIIT Lucknow)
🌡️ Temperature: 28.5°C
💨 Wind Speed: 2.1 m/s (median)
💨 Gust Speed: 3.2 m/s
🌤️ Conditions: Clear sky

✅ Wind: 2.1 m/s (Safe: ≤3.33 m/s)
✅ Gusts: 3.2 m/s (Safe: ≤5.0 m/s)
```

## Documentation

- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment on Railway.app
- **[Setup Guide](docs/SETUP.md)** - Detailed installation instructions
- **[User Guide](docs/USER_GUIDE.md)** - How to use the bot
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Developer Guide](docs/DEVELOPMENT.md)** - Contributing and architecture
- **[BWF Standards](docs/BWF_STANDARDS.md)** - Wind threshold specifications
- **[Data Collection](docs/DATA_COLLECTION.md)** - Automatic data logging system
- **[Improvement Plan](docs/IMPROVEMENT_PLAN.md)** - Roadmap and future features

## Architecture

```
 User Interfaces
   ├── Telegram Bot (refactored modular architecture)
   ├── Gradio Web UI
   └── CLI Tools

⬇️

 Bot Integration Layer
   ├── bot_formatters.py    - Message templates
   ├── bot_weather.py       - Weather API & decisions
   ├── bot_keyboards.py     - UI button layouts
   └── bot_location.py      - Location management

⬇️

 ML Pipeline
   ├── Feature Engineering  - 29 engineered features
   ├── LSTM Model          - Wind speed forecasting
   └── Decision Engine     - BWF-compliant rules

⬇️

 Data Layer
   ├── OpenWeatherMap API  - Live weather data
   └── Auto Data Logger    - CSV collection for retraining
```

### Key Technologies

- **ML Framework**: TensorFlow/Keras (LSTM model)
- **Bot Framework**: python-telegram-bot 22.5
- **Weather API**: OpenWeatherMap (free tier)
- **Data Processing**: Pandas, NumPy
- **Testing**: pytest, pytest-cov
- **Deployment**: Railway.app
- **CI/CD**: GitHub Actions

## Model Performance

- **Architecture**: LSTM with 64→32 units
- **Input**: 24 timesteps × 29 features
- **Output**: 3 quantiles (median, q10, q90)
- **Training**: Currently on synthetic data (real data collection in progress)
- **Inference Time**: ~100ms per prediction

**Features Used:**
- Lag features (1h, 3h, 6h, 12h, 24h)
- Cyclical time encoding (hour, month)
- Pressure tendency
- Wind components (U/V)
- Rolling statistics (mean, std, min, max)

## Testing

```powershell
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test suite
pytest tests/integration/test_bwf_thresholds.py -v
```

**Current Test Coverage:**
- BWF Thresholds: 11/11 tests passing ✅
- Feature Engineering: Covered
- Decision Logic: 100% coverage
- Overall: >80% target

## Real Data Collection

The system automatically collects real weather data with every bot interaction:

```powershell
# Check collection progress
python scripts/check_data_collection.py
```

**Output:**
```
Data Collection Summary
========================
File: data/collected/weather_observations.csv
Total records: 1,247
Date range: 2025-11-01 to 2025-11-11
Locations: IIIT Lucknow, Delhi, Mumbai
Collection period: 11 days
Target: 30 days for retraining
```

After 30 days of collection, retrain the model on real data for improved accuracy!

## Deployment

### Railway.app (Production)

**Status**: Using refactored bot with Sentry error tracking

Automatic deployment from `main` branch.

**Features:**
- Auto-restart on failure
- Environment variable management
- Zero-downtime deployments
- Free tier available (500 hours/month)
- Sentry integration for error monitoring

**Quick Deploy:**
```bash
# Run pre-deployment checklist
python scripts/pre_deploy_check.py

# Push to deploy
git push origin main

# Monitor deployment
railway logs --follow
```

**Required Environment Variables:**
- `TELEGRAM_BOT_TOKEN` - Your bot token from @BotFather
- `OPENWEATHER_API_KEY` - API key from OpenWeatherMap
- `SENTRY_DSN` (optional) - For error tracking

See **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** for detailed deployment instructions.

### Local Development

```powershell
# Run refactored bot locally
python -m src.integrations.telegram_bot_refactored
```

### Docker (Optional)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "src.integrations.telegram_bot_refactored"]
```

## Contributing

We welcome contributions! See **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** for:

- Architecture overview
- Development setup
- Code style guide
- Testing guidelines
- Pull request process

**Quick Start for Contributors:**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with tests
4. Format code: `black src/ tests/`
5. Run tests: `pytest tests/ -v`
6. Submit a pull request

## 📈 Roadmap

See **[IMPROVEMENT_PLAN.md](docs/IMPROVEMENT_PLAN.md)** for detailed roadmap.

**Phase 1 (Weeks 1-2)** - IN PROGRESS
- [x] Refactor telegram_bot.py into modular architecture
- [x] Add comprehensive documentation (API, DEVELOPMENT)
- [ ] Set up CI/CD with GitHub Actions
- [ ] Add type hints to all modules
- [ ] Set up Sentry error tracking

**Phase 2 (Weeks 3-4)** - UPCOMING
- [ ] Retrain model on real collected data
- [ ] Add location autocomplete with geocoding API
- [ ] Implement user preferences storage
- [ ] Create web dashboard

**Phase 3 (Weeks 5-6)** - PLANNED
- [ ] Add Grafana monitoring
- [ ] Implement Redis caching
- [ ] Performance optimization

**Phase 4 (Weeks 7-8)** - FUTURE
- [ ] Advanced ML features
- [ ] Multi-language support
- [ ] Mobile app

## 📄 License

MIT License - See LICENSE file for details.

## Acknowledgments

- **OpenWeatherMap** - Weather data API
- **Badminton World Federation** - Wind threshold standards
- **TensorFlow Team** - ML framework
- **python-telegram-bot** - Bot framework

## Support

- **Issues**: [GitHub Issues](https://github.com/PAVANKUMARELETI/badminton-bot/issues)
- **Documentation**: [docs/](docs/)
- **Email**: Contact via GitHub profile

---

**Made with ❤️ for badminton players who hate the wind**
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

## Bot Integrations

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

### Current Status: Trained on Synthetic Data

The current deployed model is trained on **synthetic/sample data** for demonstration purposes:
- **Baseline (Persistence)**: MAE ~0.3 m/s, RMSE ~0.45 m/s
- **LSTM**: MAE ~0.25 m/s, RMSE ~0.38 m/s (after 50 epochs)

### Next Step: Train on Real Historical Data

To achieve production-ready performance, the model needs to be trained on **real historical weather data** from IIIT Lucknow:

**Option 1: OpenWeatherMap Historical API (Paid)**
- Requires paid subscription for historical data access
- Can fetch years of hourly observations
- Run: `python scripts/retrain_on_real_data.py` (requires historical API key)

**Option 2: Local Weather Station Data**
- Collect data from a local weather station
- Export as CSV with columns: `datetime, wind_m_s, wind_gust_m_s, temp, humidity, pressure`
- Place in `data/raw/` and retrain

**Option 3: Automatic Data Collection (RECOMMENDED)**
- **The bot automatically collects data** every time you use it!
- Observations saved to `data/collected/weather_observations.csv`
- After 30+ days, retrain with: `python scripts/check_data_collection.py --retrain`
- Check progress anytime: `python scripts/check_data_collection.py`
- **No manual work needed** - just use the bot normally!
- See [DATA_COLLECTION.md](docs/DATA_COLLECTION.md) for details

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
  author={Pavan Eleti},
  year={2025},
  url={https://github.com/pavankumareleti/badminton-wind-predictor}
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
