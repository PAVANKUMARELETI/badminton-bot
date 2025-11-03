# Project Structure

```
badminton/
├── 📁 .github/              # GitHub Actions workflows
├── 📁 data/                 # Sample data files
├── 📁 deployment/           # Deployment configurations (Hugging Face, etc.)
├── 📁 docs/                 # 📚 Documentation
│   ├── ENHANCED_FEATURES_SUMMARY.md
│   ├── GETTING_STARTED.md
│   ├── IMPLEMENTATION_CHECKLIST.md
│   ├── QUICKSTART.md
│   ├── REAL_DATA_INTEGRATION.md
│   ├── SETUP.md
│   ├── TROUBLESHOOTING.md
│   ├── WEATHER_API_QUICKSTART.md
│   └── 📁 security/        # Security documentation
│       └── SECURITY_ALERT.md
│
├── 📁 experiments/          # Trained models and artifacts
│   └── latest/
│       ├── model.keras      # LSTM model (29 features)
│       └── scaler.npz       # Feature scaler
│
├── 📁 notebooks/            # Jupyter notebooks for exploration
├── 📁 scripts/              # 🔧 Utility scripts
│   ├── deploy_now.ps1
│   ├── deploy_railway.ps1
│   ├── install_pip_packages.ps1
│   ├── make_sample_data.py
│   ├── remove_api_key_from_history.ps1
│   ├── retrain_enhanced_model.py
│   ├── setup_conda.ps1
│   └── test_weather_api.py
│
├── 📁 src/                  # 💻 Main source code
│   ├── cli/                 # Command-line interface
│   ├── data/                # Data fetching & preprocessing
│   ├── decision/            # Play/don't play decision logic
│   ├── eval/                # Model evaluation
│   ├── integrations/        # 🤖 Telegram/WhatsApp bots
│   ├── models/              # ML models (LSTM)
│   └── utils/               # Utility functions
│
├── 📁 tests/                # 🧪 Test files
│   ├── integration/         # Integration tests
│   │   ├── README.md
│   │   ├── check_current_weather.py
│   │   ├── debug_bot.py
│   │   ├── test_api_key.py
│   │   ├── test_bot_forecast.py
│   │   ├── test_enhanced_features.py
│   │   ├── test_final_integration.py
│   │   ├── test_forecast_flow.py
│   │   ├── test_real_weather.py
│   │   └── test_weather_api.py
│   ├── test_decision.py
│   ├── test_metrics.py
│   └── test_preprocess.py
│
├── 📄 .env                  # Environment variables (NOT in git)
├── 📄 .env.example          # Example environment file
├── 📄 .gitignore
├── 📄 environment.yml       # Conda environment
├── 📄 LICENSE
├── 📄 Makefile
├── 📄 Procfile             # Railway/Heroku process file
├── 📄 pyproject.toml       # Python project metadata
├── 📄 README.md            # Main README
├── 📄 requirements.txt     # Python dependencies
├── 📄 runtime.txt          # Python version for deployment
└── 📄 start.sh             # Startup script for Railway
```

## Key Directories

### `/src` - Source Code
Main application code organized by functionality:
- `cli/` - Command-line tools (train, infer)
- `data/` - Weather API integration, data preprocessing
- `integrations/` - Telegram & WhatsApp bot implementations
- `models/` - LSTM forecasting model
- `decision/` - Decision rules for play/don't play

### `/tests` - Testing
- `integration/` - End-to-end integration tests
- Unit tests for individual components

### `/docs` - Documentation
All project documentation including setup guides, troubleshooting, and security alerts

### `/scripts` - Utility Scripts
Setup, deployment, and maintenance scripts

### `/experiments` - Model Artifacts
Trained models and scalers for production use

## Configuration Files

- **`.env`** - Local environment variables (secrets, API keys)
- **`.env.example`** - Template for environment variables
- **`requirements.txt`** - Python dependencies
- **`Procfile`** - Railway deployment configuration
- **`start.sh`** - Startup script (trains model if missing)

## Running the Project

See `/docs/QUICKSTART.md` for quick start instructions.
