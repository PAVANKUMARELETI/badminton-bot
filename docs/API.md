# API Reference

Comprehensive API documentation for the Badminton Wind Forecasting System.

## Table of Contents

- [Bot Modules](#bot-modules)
- [Data Processing](#data-processing)
- [Model Training](#model-training)
- [Decision Engine](#decision-engine)
- [Weather Integration](#weather-integration)

---

## Bot Modules

### `bot_formatters.py`

Message formatting utilities for Telegram bot.

#### `format_welcome_message(location: str, lat: float, lon: float) -> str`

Formats the welcome message for `/start` command.

**Parameters:**
- `location` (str): Location name
- `lat` (float): Latitude
- `lon` (float): Longitude

**Returns:** Markdown-formatted welcome message

**Example:**
```python
msg = format_welcome_message("IIIT Lucknow", 26.8467, 80.9462)
```

#### `format_help_message() -> str`

Formats the help message for `/help` command.

**Returns:** Markdown-formatted help text

#### `format_current_weather_response(can_play: bool, current_weather: dict, ...) -> str`

Formats current weather conditions response.

**Parameters:**
- `can_play` (bool): BWF compliance decision
- `current_weather` (dict): Weather data with wind_speed, gust, temp, etc.
- `data_source` (str): "live" or "fallback"
- `location` (str): Location name
- `weather_data_time` (datetime): Weather observation time
- `safe_median_wind` (float): BWF median threshold (3.33 m/s)
- `safe_gust_wind` (float): BWF gust threshold (5.0 m/s)

**Returns:** Markdown-formatted weather report

#### `format_forecast_response(decision_result: dict, forecast_result: dict, ...) -> str`

Formats forecast prediction response.

**Parameters:**
- `decision_result` (dict): Decision engine output
- `forecast_result` (dict): LSTM model predictions
- `current_weather` (dict): Current conditions
- `data_source` (str): Data source indicator
- `location` (str): Location name
- `weather_data_time` (datetime): Observation time

**Returns:** Markdown-formatted forecast report

#### `format_location_change_message(name: str, lat: float, lon: float) -> str`

Formats location change confirmation.

**Parameters:**
- `name` (str): New location name
- `lat` (float): Latitude
- `lon` (float): Longitude

**Returns:** Markdown-formatted confirmation message

---

### `bot_weather.py`

Weather data fetching and processing for bot.

#### `fetch_current_weather(lat: float, lon: float, location: str) -> tuple`

Fetches current weather from OpenWeatherMap API.

**Parameters:**
- `lat` (float): Latitude
- `lon` (float): Longitude
- `location` (str): Location name for logging

**Returns:** Tuple of (weather_dict, data_source, timestamp)

**Side Effects:** Logs weather data to `data/collected/weather_observations.csv`

**Example:**
```python
weather, source, time = fetch_current_weather(26.8467, 80.9462, "IIIT Lucknow")
if source == "live":
    print(f"Wind: {weather['wind_speed']} m/s")
```

#### `fetch_forecast_data(lat: float, lon: float, location: str) -> tuple`

Fetches 5-day/3-hour forecast from OpenWeatherMap.

**Parameters:**
- `lat` (float): Latitude
- `lon` (float): Longitude
- `location` (str): Location name

**Returns:** Tuple of (forecast_list, data_source)

**Side Effects:** Logs forecast data to weather_observations.csv

#### `prepare_forecast_dataframe(weather_data: list) -> pd.DataFrame`

Converts API forecast data to pandas DataFrame.

**Parameters:**
- `weather_data` (list): Raw API forecast response

**Returns:** DataFrame with columns: dt, temp, pressure, humidity, wind_speed, wind_deg, clouds, rain_3h

#### `make_play_decision(current_weather: dict) -> bool`

Makes BWF-compliant play decision based on current conditions.

**Parameters:**
- `current_weather` (dict): Must contain 'wind_speed' and 'gust' keys

**Returns:** True if conditions meet BWF standards, False otherwise

**Decision Logic:**
- Median wind ≤ 3.33 m/s (12 km/h) **AND**
- Gust wind ≤ 5.0 m/s (18 km/h)

#### `get_bwf_thresholds() -> tuple`

Returns BWF wind speed thresholds.

**Returns:** Tuple of (median_threshold, gust_threshold) = (3.33, 5.0)

---

### `bot_keyboards.py`

Inline keyboard button layouts for Telegram bot.

#### `get_main_menu_keyboard() -> InlineKeyboardMarkup`

Returns main menu keyboard with "Play Now?" and "Forecast" buttons.

#### `get_now_action_keyboard() -> InlineKeyboardMarkup`

Returns action keyboard after /now command (Forecast, Help, Main Menu).

#### `get_forecast_action_keyboard() -> InlineKeyboardMarkup`

Returns action keyboard after /forecast (Check Now, Help, Main Menu).

#### `get_help_keyboard() -> InlineKeyboardMarkup`

Returns keyboard for help screen (Main Menu button).

---

### `bot_location.py`

Location parsing and management utilities.

#### `parse_location(location_text: str) -> tuple`

Parses location text to coordinates.

**Parameters:**
- `location_text` (str): City name (e.g., "Delhi", "Mumbai")

**Returns:** Tuple of (lat, lon, name) or (None, None, "Unknown Location")

**Supported Locations:**
- IIIT Lucknow (26.8467, 80.9462)
- Lucknow (26.8467, 80.9462)
- Delhi (28.6139, 77.2090)
- Mumbai (19.0760, 72.8777)
- Bangalore (12.9716, 77.5946)
- Hyderabad (17.3850, 78.4867)
- Chennai (13.0827, 80.2707)
- Kolkata (22.5726, 88.3639)

#### `get_default_location() -> tuple`

Returns default location (IIIT Lucknow).

**Returns:** Tuple of (26.8467, 80.9462, "IIIT Lucknow")

#### `format_coordinates(lat: float, lon: float) -> str`

Formats coordinates for display.

**Returns:** String like "26.85°N, 80.95°E"

---

## Data Processing

### `src.data.preprocess`

#### `build_features(df: pd.DataFrame) -> pd.DataFrame`

Builds engineered features from raw weather data.

**Features Created:**
- Lag features (1h, 3h, 6h, 12h, 24h for wind_speed)
- Cyclical time encoding (hour_sin, hour_cos, month_sin, month_cos)
- Pressure tendency (pressure_change_1h)
- Wind components (wind_u, wind_v from speed & direction)
- Rolling statistics (mean_3h, std_3h, min_3h, max_3h)

**Parameters:**
- `df` (pd.DataFrame): Must have columns: dt, temp, pressure, humidity, wind_speed, wind_deg

**Returns:** DataFrame with 29 feature columns

---

## Model Training

### `src.cli.train`

#### `train_lstm(data_df: pd.DataFrame, config: dict) -> keras.Model`

Trains LSTM model for wind forecasting.

**Architecture:**
- Input: 24 timesteps × 29 features
- LSTM layers: 64 → 32 units
- Output: 3 quantiles (median, q10, q90)

**Parameters:**
- `data_df` (pd.DataFrame): Preprocessed feature DataFrame
- `config` (dict): Training configuration

**Returns:** Trained Keras model

**Usage:**
```bash
python -m src.cli.train --model lstm --epochs 50 --batch-size 32
```

---

## Decision Engine

### `src.decision.rules`

#### `decide_play(median_forecast: float, q90_forecast: float) -> dict`

Makes play decision based on LSTM forecast.

**Parameters:**
- `median_forecast` (float): Predicted median wind speed (m/s)
- `q90_forecast` (float): Predicted 90th percentile wind (m/s)

**Returns:** Dictionary with keys:
- `can_play` (bool): Decision
- `median_wind` (float): Median forecast
- `gust_wind` (float): Q90 forecast
- `safe_median` (float): 3.33 m/s
- `safe_gust` (float): 5.0 m/s
- `message` (str): Human-readable explanation

**Example:**
```python
result = decide_play(median_forecast=2.5, q90_forecast=4.2)
if result["can_play"]:
    print("✅ Safe to play!")
```

---

## Weather Integration

### `src.data.weather_logger`

#### `log_weather_data(weather_data: dict, location: str, data_type: str) -> None`

Logs weather observations to CSV for model retraining.

**Parameters:**
- `weather_data` (dict): Weather data from API
- `location` (str): Location name
- `data_type` (str): "current" or "forecast"

**Output:** Appends to `data/collected/weather_observations.csv`

**CSV Columns:**
- timestamp, location, data_type, dt, temp, pressure, humidity, wind_speed, wind_deg, clouds, rain_3h, gust

**Usage:** Automatically called by `fetch_current_weather()` and `fetch_forecast_data()`

---

## Environment Variables

### Required

- `TELEGRAM_BOT_TOKEN`: Token from @BotFather
- `OPENWEATHER_API_KEY`: API key from OpenWeatherMap

### Optional

- `SENTRY_DSN`: Sentry error tracking DSN
- `LOG_LEVEL`: Logging level (default: INFO)

---

## CLI Commands

### Training
```bash
python -m src.cli.train --model lstm --epochs 50 --data sample
```

### Inference
```bash
python -m src.cli.infer --model experiments/latest/model.keras
```

### Testing
```bash
pytest tests/ -v --cov=src --cov-report=html
```

### Bot
```bash
python -m src.integrations.telegram_bot_refactored
```

---

## Error Codes

- `ValueError("TELEGRAM_BOT_TOKEN required")`: Missing bot token
- `ValueError("OPENWEATHER_API_KEY required")`: Missing weather API key
- `FileNotFoundError`: Model file not found
- `requests.exceptions.RequestException`: API connection error

---

## BWF Standards Reference

**Badminton World Federation Wind Thresholds:**

- **Median Wind**: ≤ 3.33 m/s (12 km/h)
- **Gust Wind**: ≤ 5.0 m/s (18 km/h)

**Source:** BWF Tournament Regulations

**Implementation:** See `docs/BWF_STANDARDS.md` for full details.
