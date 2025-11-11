# Developer Guide

Comprehensive guide for contributing to and extending the Badminton Wind Forecasting System.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Development Setup](#development-setup)
- [Code Organization](#code-organization)
- [Testing Guidelines](#testing-guidelines)
- [Adding Features](#adding-features)
- [Code Quality](#code-quality)
- [Deployment](#deployment)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interfaces                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Telegram    │  │   Gradio     │  │     CLI      │      │
│  │     Bot      │  │   Web UI     │  │   Interface  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Bot Integration Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ bot_formatters  bot_weather  bot_keyboards  bot_loc │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core ML Pipeline                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐      │
│  │   Data     │→ │  Feature   │→ │  LSTM Model      │      │
│  │ Collection │  │ Engineering│  │  Training/Infer  │      │
│  └────────────┘  └────────────┘  └──────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Decision Engine                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   BWF Threshold Rules (3.33 m/s median, 5.0 m/s gust)│   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input**: User requests weather forecast via bot/UI/CLI
2. **Weather API**: Fetch data from OpenWeatherMap
3. **Logging**: Automatic data collection to CSV
4. **Feature Engineering**: Build 29 features from raw data
5. **LSTM Inference**: Predict wind speeds (median, q10, q90)
6. **Decision**: Apply BWF rules to make play/no-play decision
7. **Output**: Formatted response to user

---

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- OpenWeatherMap API key (free tier)
- Telegram bot token (for bot development)

### Quick Setup

```powershell
# Clone repository
git clone https://github.com/PAVANKUMARELETI/badminton-bot.git
cd badminton-bot

# Create conda environment
conda env create -f environment.yml
conda activate badminton-wind

# Install development dependencies
pip install pytest pytest-cov black isort flake8 mypy

# Set environment variables
$env:OPENWEATHER_API_KEY = "your-key-here"
$env:TELEGRAM_BOT_TOKEN = "your-token-here"

# Run tests
pytest tests/ -v
```

### Environment Variables

Create a `.env` file in the project root:

```env
OPENWEATHER_API_KEY=your_openweather_key
TELEGRAM_BOT_TOKEN=your_telegram_token
SENTRY_DSN=your_sentry_dsn  # Optional
LOG_LEVEL=INFO
```

---

## Code Organization

### Directory Structure

```
badminton/
├── src/
│   ├── cli/                 # Command-line interfaces
│   │   ├── train.py         # Model training CLI
│   │   └── infer.py         # Inference CLI
│   ├── data/                # Data processing
│   │   ├── preprocess.py    # Feature engineering
│   │   └── weather_logger.py # Automatic data collection
│   ├── decision/            # Decision engine
│   │   └── rules.py         # BWF threshold rules
│   ├── integrations/        # Bot & UI integrations
│   │   ├── telegram_bot_refactored.py  # Main bot
│   │   ├── bot_formatters.py           # Message templates
│   │   ├── bot_weather.py              # Weather handling
│   │   ├── bot_keyboards.py            # UI buttons
│   │   └── bot_location.py             # Location utils
│   └── models/              # ML models
│       └── lstm.py          # LSTM implementation
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── scripts/                 # Utility scripts
│   ├── make_sample_data.py
│   └── check_data_collection.py
├── data/
│   ├── collected/           # Automatic data collection
│   └── sample_station.csv   # Synthetic training data
├── experiments/             # Model checkpoints
├── docs/                    # Documentation
└── deployment/              # Deployment configs
```

### Module Responsibilities

#### `src/cli/`
- **Purpose**: Command-line tools for training and inference
- **Key Files**: `train.py`, `infer.py`
- **Testing**: Covered by integration tests

#### `src/data/`
- **Purpose**: Data collection and preprocessing
- **Key Files**: `preprocess.py` (feature engineering), `weather_logger.py` (auto-collection)
- **Testing**: Unit tests for feature engineering

#### `src/decision/`
- **Purpose**: Play/no-play decision logic
- **Key Files**: `rules.py`
- **Testing**: `tests/integration/test_bwf_thresholds.py`

#### `src/integrations/`
- **Purpose**: Bot and UI integrations
- **Key Files**: Refactored bot modules
- **Testing**: Unit tests for each module

#### `src/models/`
- **Purpose**: ML model implementations
- **Key Files**: `lstm.py`
- **Testing**: Model architecture tests

---

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/integration/test_bwf_thresholds.py -v

# Run specific test
pytest tests/integration/test_bwf_thresholds.py::test_very_calm_conditions -v
```

### Writing Tests

#### Unit Test Example

```python
# tests/unit/test_bot_formatters.py
import pytest
from src.integrations.bot_formatters import format_welcome_message

def test_format_welcome_message():
    msg = format_welcome_message("Delhi", 28.6139, 77.2090)
    
    assert "Delhi" in msg
    assert "28.61" in msg
    assert "77.21" in msg
    assert "Play Now" in msg
```

#### Integration Test Example

```python
# tests/integration/test_bwf_thresholds.py
from src.integrations.bot_weather import make_play_decision

def test_optimal_conditions():
    current_weather = {
        "wind_speed": 2.0,  # Below 3.33 m/s
        "gust": 3.5         # Below 5.0 m/s
    }
    
    result = make_play_decision(current_weather)
    assert result is True
```

### Test Coverage Goals

- **Overall**: ≥80%
- **Critical Paths**: 100%
  - Decision engine (`src/decision/rules.py`)
  - BWF threshold logic (`bot_weather.py`)
  - Feature engineering (`src/data/preprocess.py`)

---

## Adding Features

### Adding a New Bot Command

1. **Add handler to `telegram_bot_refactored.py`**:

```python
async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command."""
    # Your logic here
    await update.message.reply_text("Statistics here...")
```

2. **Register handler in `run()` method**:

```python
self.application.add_handler(CommandHandler("stats", self.stats_command))
```

3. **Add tests**:

```python
# tests/integration/test_bot_commands.py
def test_stats_command():
    # Test implementation
    pass
```

### Adding a New Location

Edit `src/integrations/bot_location.py`:

```python
PRESET_LOCATIONS = {
    # ... existing locations
    "pune": (18.5204, 73.8567, "Pune"),
}
```

### Adding a New Feature

1. **Implement in `src/data/preprocess.py`**:

```python
def build_features(df):
    # ... existing features
    
    # Add new feature
    df["temperature_change_1h"] = df["temp"].diff(1)
    
    return df
```

2. **Update feature count** (29 → 30)
3. **Retrain model** with new features
4. **Add tests** for new feature

---

## Code Quality

### Code Formatting

```bash
# Format code
black src/ tests/ scripts/

# Sort imports
isort src/ tests/ scripts/

# Lint
flake8 src/ tests/ scripts/
```

### Type Checking

```bash
# Run mypy
mypy src/ --ignore-missing-imports
```

### Pre-commit Checks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

Install hooks:
```bash
pip install pre-commit
pre-commit install
```

### Code Review Checklist

- [ ] Tests added for new features
- [ ] Type hints added
- [ ] Code formatted with black
- [ ] Imports sorted with isort
- [ ] No flake8 violations
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

---

## Deployment

### Railway.app (Current)

Automatic deployment from `main` branch.

**Configuration**: `railway.json`

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python -m src.integrations.telegram_bot_refactored",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Hugging Face Spaces

Gradio UI deployment.

**Files**: `deployment/hf_space/`

```bash
cd deployment/hf_space
python app.py
```

### Docker (Local)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "src.integrations.telegram_bot_refactored"]
```

Build and run:
```bash
docker build -t badminton-bot .
docker run -e TELEGRAM_BOT_TOKEN=$env:TELEGRAM_BOT_TOKEN badminton-bot
```

---

## Performance Optimization

### Model Inference

- **Current**: ~100ms per prediction
- **Optimization**: Use TFLite for faster inference
- **Target**: <50ms per prediction

### API Caching

Cache OpenWeatherMap responses for 5 minutes:

```python
import functools
from datetime import datetime, timedelta

@functools.lru_cache(maxsize=128)
def fetch_weather_cached(lat, lon, timestamp_bucket):
    # timestamp_bucket rounds to nearest 5 minutes
    return fetch_weather(lat, lon)
```

### Database Migration

Current: CSV file (`weather_observations.csv`)
Future: PostgreSQL for better query performance

---

## Monitoring & Logging

### Logging Levels

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.debug("Debug info")      # Detailed diagnostic
logger.info("User action")      # Normal operations
logger.warning("Unusual event") # Recoverable issues
logger.error("Error occurred")  # Failures
logger.critical("Critical!")    # System-level failures
```

### Sentry Integration

```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
)
```

---

## Contributing

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch
- `feature/xyz`: Feature branches
- `fix/xyz`: Bug fix branches

### Pull Request Process

1. Create feature branch from `develop`
2. Make changes with tests
3. Ensure all tests pass
4. Format code (black, isort)
5. Submit PR to `develop`
6. Wait for review
7. Merge after approval

---

## Resources

- **API Documentation**: `docs/API.md`
- **User Guide**: `docs/USER_GUIDE.md`
- **BWF Standards**: `docs/BWF_STANDARDS.md`
- **Data Collection**: `docs/DATA_COLLECTION.md`
- **Setup Guide**: `docs/SETUP.md`

---

## FAQ

**Q: How do I add support for a new city?**  
A: Edit `src/integrations/bot_location.py` and add to `PRESET_LOCATIONS`.

**Q: How often should I retrain the model?**  
A: Weekly or when you have 1000+ new observations.

**Q: Can I use a different weather API?**  
A: Yes, implement a new provider in `bot_weather.py` with the same interface.

**Q: How do I debug bot issues?**  
A: Set `LOG_LEVEL=DEBUG` and check logs. Use Sentry for production errors.

**Q: What's the model accuracy?**  
A: Currently ~75% on synthetic data. Will improve with real data collection.

---

## Version History

- **v2.0.0** (Nov 2025): Refactored modular architecture, BWF compliance
- **v1.5.0** (Oct 2025): Automatic data collection system
- **v1.0.0** (Sep 2025): Initial release with Telegram bot
