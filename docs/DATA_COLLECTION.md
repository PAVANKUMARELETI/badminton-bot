# Automatic Weather Data Collection

## Overview

The bot now **automatically collects and saves weather observations** every time you check the weather. This builds a historical dataset for training the LSTM model on real IIIT Lucknow data.

## How It Works

### Automatic Logging
Every time you use the bot:
- `/now` command → Logs current weather
- `/forecast` command → Logs forecast data

Data is saved to: `data/collected/weather_observations.csv`

### What's Logged
- Timestamp
- Wind speed (m/s)
- Wind gusts (m/s)
- Wind direction (degrees)
- Temperature (°C)
- Humidity (%)
- Pressure (hPa)
- Location (lat/lon)
- Data source (current/forecast)

### De-duplication
- Automatically removes duplicate timestamps
- Keeps the most recent observation for each timestamp
- Sorted chronologically

## Monitoring Progress

Check collection status anytime:

```bash
python scripts/check_data_collection.py
```

This shows:
- ✅ Total observations collected
- 📅 Date range of data
- 🎯 Progress toward 30-day goal
- 🚀 Ready for training?

Example output:
```
======================================================================
📊 WEATHER DATA COLLECTION STATUS
======================================================================

✅ Data collection active!

📈 Current Progress:
   • Total observations: 1,250
   • Start date: 2025-10-04 10:30:00
   • End date: 2025-11-03 19:15:00
   • Days of data: 30.4 days

🎯 Progress to training readiness (30 days):
   [████████████████████████████████████████] 100.0%

🎉 READY FOR TRAINING!
   ✅ Sufficient data collected (30.4 days)
   ✅ Sufficient observations (1,250)

🚀 Run: python scripts/check_data_collection.py --retrain
======================================================================
```

## Retraining the Model

### When Ready (After 30 Days)

Once you've collected 30+ days of data:

```bash
python scripts/check_data_collection.py --retrain
```

This will:
1. Load all collected observations
2. Build enhanced features (29 features total)
3. Train LSTM model for 50 epochs
4. Save production-ready model to `experiments/latest/`
5. Create training metadata file

### Deploy Updated Model

```bash
git add experiments/latest/
git commit -m "Update to real-data trained model (30+ days)"
git push origin main
```

Railway will auto-deploy the new model! 🚀

## Requirements for Training

- ✅ **Minimum 30 days** of data collection
- ✅ **Minimum 500 observations** (hourly data)
- ✅ **Covers different weather conditions** (ideal if includes various wind patterns)

## Timeline

### Week 1-2: Bootstrap Phase
- Bot uses live API + synthetic LSTM model
- Collects 300-700 observations
- Not ready for training yet

### Week 3-4: Collection Phase
- 700-1,400 observations
- Approaching readiness
- Can see progress bar filling up

### Day 30+: Training Ready! 🎉
- 1,400+ observations
- Covers full month of weather patterns
- Ready to train on real IIIT Lucknow data

### After Retraining
- LSTM model learns local wind patterns
- Better 1h/3h/6h forecasts
- Improved prediction accuracy

## Benefits of Real Data Training

### Before (Synthetic Data)
- Generic wind patterns
- May not match IIIT Lucknow climate
- Accuracy: ~70-80%

### After (Real Data)
- Location-specific patterns
- Learns daily/weekly cycles
- Knows seasonal variations
- Accuracy: ~85-95% (expected)

## Data Storage

### Location
```
data/
└── collected/
    └── weather_observations.csv
```

### Size Estimates
- 1 month: ~2-5 MB
- 6 months: ~10-30 MB
- 1 year: ~20-60 MB

### Backup Recommendation
Periodically backup `data/collected/` folder:

```bash
# Create backup
cp -r data/collected data/collected_backup_$(date +%Y%m%d)

# Or commit to git (if you want version control)
git add data/collected/
git commit -m "Backup weather data - $(date +%Y-%m-%d)"
```

## Troubleshooting

### "No data collected yet"
- Use the bot at least once (`/now` or `/forecast`)
- Check that bot has internet access
- Verify OPENWEATHER_API_KEY is set

### "Not enough data for training"
- Keep using the bot regularly
- Wait for 30+ days of collection
- Each use adds more observations

### "Training failed"
- Check logs for specific errors
- Ensure at least 500 observations
- Verify data quality (no corruption)

## Advanced Usage

### Force Retrain (if needed)
```bash
python scripts/check_data_collection.py --retrain --force
```

### Manual Data Inspection
```python
from src.data.weather_logger import load_historical_data

df = load_historical_data()
print(df.describe())
print(f"Wind speed range: {df['wind_m_s'].min():.2f} - {df['wind_m_s'].max():.2f} m/s")
```

## Summary

✅ **Automatic**: No manual intervention needed
✅ **Incremental**: Builds dataset over time
✅ **Smart**: De-duplicates and validates data
✅ **Transparent**: Check progress anytime
✅ **Production-ready**: Retrain with one command

**Just use the bot normally, and it takes care of the rest!** 🎉
