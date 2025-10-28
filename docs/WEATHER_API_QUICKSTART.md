# Weather API Integration - Quick Start Guide

## 🚀 Get Started in 5 Minutes!

### Step 1: Get API Key

1. Go to https://openweathermap.org/api
2. Click "Sign Up" (free)
3. Verify your email
4. Go to **API keys** in your account
5. Copy your API key

### Step 2: Add to Environment

**Option A: Add to .env file (recommended)**
```bash
# Edit .env file
OPENWEATHER_API_KEY=your_api_key_here
```

**Option B: Set environment variable**
```powershell
# PowerShell
$env:OPENWEATHER_API_KEY = "your_api_key_here"
```

### Step 3: Install Dependencies

```powershell
conda activate badminton-wind
pip install requests
```

### Step 4: Test It!

```powershell
# Test current weather
python -c "from src.data.weather_api import get_weather_for_location; print(get_weather_for_location('Delhi'))"
```

---

## 📊 Usage Examples

### Get Current Weather

```python
from src.data.weather_api import OpenWeatherMapAPI

api = OpenWeatherMapAPI()

# By coordinates
current = api.get_current_weather(lat=28.6139, lon=77.2090)
print(f"Wind: {current['wind_m_s'].values[0]:.1f} m/s")

# By location name
from src.data.weather_api import get_weather_for_location
weather = get_weather_for_location("Delhi")
print(weather)
```

### Get Forecast

```python
# 6-hour forecast
forecast = api.get_hourly_forecast(lat=28.6139, lon=77.2090, hours=6)
print(forecast[['wind_m_s', 'temp', 'weather']])
```

### Use with Bot

Update your bot to use real weather:

```python
# In telegram_bot.py, replace:
# df = load_sample()

# With:
from src.data.weather_api import get_weather_for_location
df = get_weather_for_location("bits_pilani", hours=6)
```

---

## 🔄 Automated Data Collection

### Collect Once

```powershell
python -m src.data.data_collector --location "Delhi" --collect-once
```

### Continuous Collection (Every Hour)

```powershell
python -m src.data.data_collector --location "bits_pilani" --interval 3600
```

This will:
- Fetch weather every hour
- Store in `data/weather.db`
- Build historical dataset
- Enable model retraining

---

## 📈 Analysis Scripts

### View Collected Data

```python
from src.data.data_collector import WeatherDataCollector

collector = WeatherDataCollector()
historical = collector.get_historical_data("Delhi", days=7)

print(f"Collected {len(historical)} observations")
print(historical[['wind_m_s', 'temp', 'weather']].describe())
```

### Retrain Model on Real Data

After collecting 2+ weeks:

```powershell
# Train on real data
python -m src.cli.train --model lstm --data data/weather.db --epochs 50
```

---

## 🎯 Campus Locations

Predefined coordinates for quick access:

```python
CAMPUS_LOCATIONS = {
    "bits_pilani": (28.3636, 75.5861),
    "iit_delhi": (28.5449, 77.1926),
    "iit_bombay": (19.1334, 72.9133),
    "iit_madras": (12.9916, 80.2337),
    "delhi": (28.6139, 77.2090),
    "bangalore": (12.9716, 77.5946),
    # ... more locations
}

# Use them:
weather = get_weather_for_location("bits_pilani")
```

---

## 🔧 Configuration

### Multiple API Providers

```python
# OpenWeatherMap (default)
weather = get_weather_for_location("Delhi", api_provider="openweather")

# WeatherAPI.com (more free calls)
weather = get_weather_for_location("Delhi", api_provider="weatherapi")
```

### Custom Location

```python
from src.data.weather_api import get_location_coordinates

# Get coordinates for any location
lat, lon = get_location_coordinates("Pilani, Rajasthan, India")
```

---

## 📊 Next Steps

1. **Week 1**: Collect data
   ```powershell
   python -m src.data.data_collector --location "your_campus" --interval 3600
   ```

2. **Week 2-3**: Analyze patterns
   - See `notebooks/real_data_analysis.ipynb` (create this)
   - Identify best play times
   - Compare API vs sample data

3. **Week 4**: Retrain & deploy
   - Train on real data
   - Update bot to use real forecasts
   - Share results!

---

## 🆘 Troubleshooting

**API key not working?**
```bash
# Check if key is set
echo $env:OPENWEATHER_API_KEY  # PowerShell

# Test directly
curl "http://api.openweathermap.org/data/2.5/weather?q=Delhi&appid=YOUR_KEY"
```

**"No module named 'requests'"**
```bash
pip install requests
```

**Rate limit errors?**
- Free tier: 60 calls/minute, 1000/day
- Solution: Use `--interval 3600` (hourly collection)

**Database locked?**
- Close any programs accessing `data/weather.db`
- Or specify different path: `--db-path data/weather2.db`

---

## 📚 Full Documentation

See **[docs/REAL_DATA_INTEGRATION.md](REAL_DATA_INTEGRATION.md)** for:
- Complete implementation plan
- Analysis strategies
- Advanced features
- Best practices

---

**Ready to use real weather data!** 🌤️📊
