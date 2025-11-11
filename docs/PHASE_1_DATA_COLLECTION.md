# 📊 PHASE 1: Real Data Collection (30 Days)

**Status:** ✅ ACTIVE  
**Start Date:** November 11, 2025  
**Expected Completion:** December 11, 2025

---

## 🎯 Objective

Collect **30 days of real weather data** from IIIT Lucknow to:
1. Replace synthetic training data with actual observations
2. Improve model accuracy for local weather patterns
3. Validate BWF safety thresholds with real-world data

---

## 🤖 Automatic Data Collection

Your bot is now **automatically logging weather data every hour**!

### What's Being Logged
- **Location:** IIIT Lucknow (26.7984°N, 81.0241°E)
- **Frequency:** Every 1 hour
- **Expected Data Points:** ~720 (24 hours × 30 days)
- **Data Saved To:** `data/logged_weather/weather_YYYY-MM-DD.csv`

### Data Fields
Each hourly record contains:
- `timestamp` - When data was collected
- `temperature_c` - Temperature in Celsius
- `humidity_percent` - Relative humidity
- `pressure_hpa` - Atmospheric pressure
- `wind_m_s` - **Wind speed in m/s (BWF standard)**
- `wind_gust_m_s` - **Wind gust speed in m/s**
- `data_source` - Always "live" for real data

---

## 📈 Monitoring Progress

### Quick Check (Anytime)
```bash
python scripts/quick_progress.py
```

**Output Example:**
```
==================================================
📊 PHASE 1: DATA COLLECTION PROGRESS
==================================================
📅 Days collected: 5/30 (16.7%)
📈 Total data points: 120
⏳ Days remaining: 25

[████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

💡 Keep bot running to collect data!
==================================================
```

### Detailed Analysis
```bash
python scripts/check_data_collection.py
```

Shows:
- Date range of collected data
- Data quality metrics
- File sizes and point counts
- Estimated completion date

---

## ✅ What You Need to Do

### Keep Bot Running on Railway
Your bot is deployed on Railway and will collect data automatically. Just verify:

1. **Check Railway Dashboard**
   - Visit: https://railway.app
   - Project: badminton-bot
   - Status should be: **Active** ✅

2. **Monitor Logs (Optional)**
   - Look for: `✅ Weather data logged to data/logged_weather/weather_YYYY-MM-DD.csv`
   - Appears every hour

3. **Test Bot Works (Daily)**
   - Send `/now` to your bot in Telegram
   - Confirms bot is alive and API is working

### What NOT to Do
- ❌ Don't stop the Railway deployment
- ❌ Don't delete `data/logged_weather/` folder
- ❌ Don't change location during collection period

---

## 📅 Timeline

| Milestone | Date | Status |
|-----------|------|--------|
| Data collection starts | Nov 11, 2025 | ✅ Complete |
| 1 week checkpoint | Nov 18, 2025 | ⏳ Pending |
| 2 week checkpoint | Nov 25, 2025 | ⏳ Pending |
| 3 week checkpoint | Dec 2, 2025 | ⏳ Pending |
| **30 days complete** | **Dec 11, 2025** | ⏳ Pending |
| Model retraining | Dec 12, 2025 | ⏳ Pending |
| Deploy improved model | Dec 13, 2025 | ⏳ Pending |

---

## 🔄 After 30 Days

When collection completes, run the retrain script:

```bash
python scripts/check_data_collection.py --retrain
```

This will:
1. ✅ Validate 30+ days of data collected
2. ✅ Preprocess data with proper feature engineering
3. ✅ Train new LSTM model on real data
4. ✅ Save improved model to `experiments/real_data_v1/`
5. ✅ Generate performance comparison report

Then update Railway to use the new model!

---

## 🚨 Troubleshooting

### No data being collected?

**Check bot is running:**
```bash
# Railway logs should show:
✅ Weather logging job scheduled (every 1 hour)
✅ Weather data logged to data/logged_weather/...
```

**If bot stopped:**
1. Check Railway dashboard for errors
2. Verify TELEGRAM_BOT_TOKEN is set
3. Check API quota limits (Open-Meteo: unlimited free tier)

### Data files too small?

Each hourly log creates ~150 bytes. Daily file = ~3.6 KB.
If files are empty, check for:
- API connection errors in Railway logs
- Location coordinates correct (26.7984, 81.0241)

### Want to check specific day's data?

```bash
# View today's weather log
cat data/logged_weather/weather_2025-11-11.csv
```

---

## 💡 Pro Tips

1. **Set up monitoring alerts** (optional)
   - Railway can send email if bot crashes
   - Set up in Railway dashboard → Settings → Notifications

2. **Weekly verification**
   - Every Monday, run `python scripts/quick_progress.py`
   - Ensures data collection is on track

3. **Test before deadline**
   - After 25 days, test the retrain script with partial data
   - Ensures no surprises on day 30

---

## 📊 Expected Data Volume

- **Per hour:** 1 data point (~150 bytes)
- **Per day:** 24 data points (~3.6 KB)
- **30 days:** 720 data points (~108 KB)
- **File count:** 30 CSV files (one per day)

All data fits easily in Railway's free tier storage! 🎉

---

## 🎯 Success Criteria

✅ **Minimum:** 600 data points (25 days @ 24/day)  
🎯 **Target:** 720 data points (30 days @ 24/day)  
⭐ **Ideal:** 750+ data points (extra buffer for analysis)

Even with some missed hours, you'll have enough data for meaningful improvement!

---

## 📞 Need Help?

- Check Railway logs for errors
- Review bot code: `src/integrations/telegram_bot_refactored.py`
- Logger function: `_log_weather_data()` method
- Data directory: `data/logged_weather/`

---

**🏸 Happy Data Collecting! Your model will thank you in 30 days! 🚀**
