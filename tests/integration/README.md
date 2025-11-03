# Integration Tests

This directory contains integration tests for the badminton wind forecasting system.

## Test Files

### Weather API Tests
- `test_weather_api.py` - Tests OpenWeatherMap API integration
- `test_real_weather.py` - Tests real weather data fetching and preprocessing
- `check_current_weather.py` - Quick verification of current weather data

### Model & Forecast Tests
- `test_forecast_flow.py` - End-to-end forecast pipeline test
- `test_enhanced_features.py` - Tests enhanced feature engineering (temp, humidity)
- `test_final_integration.py` - Complete system integration test

### Bot Tests
- `test_bot_forecast.py` - Tests Telegram bot forecast functionality
- `debug_bot.py` - Debugging script for bot issues
- `test_api_key.py` - Validates API key configuration

## Running Tests

```bash
# Run all integration tests
python -m pytest tests/integration/

# Run specific test
python tests/integration/test_final_integration.py
```

## Requirements

All tests require:
- Valid `.env` file with API keys
- OpenWeather API key
- Telegram bot token (for bot tests)
- Python environment with dependencies installed
