# 🚀 Deployment Guide

This guide covers deploying the Badminton Wind Forecast Bot to production using Railway.app.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Railway Deployment](#railway-deployment)
- [Post-Deployment](#post-deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Connected to Railway for auto-deployment
3. **Telegram Bot Token**: From [@BotFather](https://t.me/BotFather)
4. **OpenWeatherMap API Key**: From [openweathermap.org](https://openweathermap.org/api)
5. **Sentry Account** (Optional): For error tracking at [sentry.io](https://sentry.io)

---

## Environment Variables

Set these in Railway's dashboard under **Variables**:

### Required Variables

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Weather API
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Python Environment
PYTHONUNBUFFERED=1
```

### Optional Variables

```bash
# Error Tracking (Highly Recommended)
SENTRY_DSN=your_sentry_dsn_here
SENTRY_ENVIRONMENT=production

# Model Configuration
MODEL_PATH=experiments/latest/model.keras

# Logging
LOG_LEVEL=INFO
```

---

## Railway Deployment

### Option 1: Automatic Deployment (Recommended)

1. **Connect GitHub Repository**
   - Go to Railway dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `badminton-bot` repository
   - Railway auto-detects Python project

2. **Set Environment Variables**
   - Go to project settings → Variables
   - Add all required variables from above

3. **Deploy**
   - Railway automatically deploys on push to `main` branch
   - Monitor deployment logs in Railway dashboard

### Option 2: Manual Deployment via CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Set environment variables
railway variables set TELEGRAM_BOT_TOKEN=your_token_here
railway variables set OPENWEATHER_API_KEY=your_key_here
railway variables set SENTRY_DSN=your_dsn_here

# Deploy
railway up
```

---

## Deployment Configuration

### Files Used

- **`railway.toml`**: Railway deployment configuration
  ```toml
  [build]
  builder = "NIXPACKS"

  [deploy]
  startCommand = "python -m src.integrations.telegram_bot_refactored"
  restartPolicyType = "ALWAYS"
  restartPolicyMaxRetries = 10
  ```

- **`start.sh`**: Startup script that:
  1. Checks for trained model
  2. Trains model if missing (using sample data)
  3. Starts the refactored bot with Sentry integration

- **`Procfile`**: For Heroku-style deployments
  ```
  web: bash start.sh
  ```

---

## Post-Deployment

### 1. Verify Bot is Running

Send `/start` to your bot on Telegram. You should receive:
```
🏸 Welcome to Badminton Wind Forecast Bot! 🌬️

I help you decide if it's safe to play badminton based on wind conditions.

📍 Current Location: IIIT Lucknow
🌍 Coordinates: 26.7984°N, 81.0241°E

🎯 What do you want to know?
```

### 2. Test Commands

- `/now` - Check current conditions
- `/forecast` - Get 6-hour predictions
- `/location Delhi` - Change location
- `/help` - Show help

### 3. Monitor Logs

**Railway Dashboard:**
- Go to Deployments → View Logs
- Look for:
  ```
  🤖 Starting Telegram bot (refactored with Sentry)...
  INFO: Bot started successfully
  INFO: Polling for updates...
  ```

### 4. Check Sentry (if configured)

- Go to [sentry.io](https://sentry.io)
- Select your project
- Verify connection (you'll see initialization event)

---

## Monitoring

### Health Checks

The bot should:
1. ✅ Respond to `/start` within 2 seconds
2. ✅ Fetch live weather data (if API key is valid)
3. ✅ Log errors to Sentry (if configured)
4. ✅ Auto-restart on crashes (Railway handles this)

### Logs to Monitor

```bash
# Check Railway logs
railway logs --follow

# Look for:
# - "Bot started successfully"
# - "Fetching current weather for [location]"
# - "Current weather: Wind X.X m/s"
# - Sentry initialization messages
```

### Data Collection

The bot automatically logs weather data for future model training:
- **Location**: `data/logged_weather/`
- **Files**: Daily CSV files (e.g., `weather_2025-11-11.csv`)
- **Purpose**: After 30 days, retrain model on real data

Monitor collection:
```bash
python scripts/check_data_collection.py
```

---

## Troubleshooting

### Issue: Bot Not Responding

**Symptoms:**
- No response to `/start`
- Bot appears offline

**Solutions:**
1. Check Railway logs for errors:
   ```bash
   railway logs
   ```

2. Verify environment variables:
   ```bash
   railway variables
   ```

3. Check Telegram bot token:
   - Ensure `TELEGRAM_BOT_TOKEN` is set correctly
   - Test token: Send message to bot on Telegram

### Issue: Weather API Errors

**Symptoms:**
- "Sample Data" instead of "Live Weather Data"
- Missing wind/temperature information

**Solutions:**
1. Verify OpenWeatherMap API key:
   ```bash
   railway variables get OPENWEATHER_API_KEY
   ```

2. Check API key status at [openweathermap.org](https://home.openweathermap.org/api_keys)

3. Ensure API calls aren't rate-limited (60 calls/min for free tier)

### Issue: Model Not Found

**Symptoms:**
```
⚠️ Model not found. Training a new model...
```

**Expected Behavior:**
- On first deployment, `start.sh` trains a model using sample data
- Takes ~2-5 minutes
- Model saved to `experiments/latest/model.keras`

**If it fails:**
1. Check logs for training errors
2. Verify Python dependencies installed (TensorFlow, Keras)
3. May need to increase Railway memory allocation

### Issue: Sentry Not Working

**Symptoms:**
- No errors in Sentry dashboard
- Initialization message missing

**Solutions:**
1. Check `SENTRY_DSN` is set:
   ```bash
   railway variables get SENTRY_DSN
   ```

2. Verify DSN format:
   ```
   https://<key>@<organization>.ingest.sentry.io/<project>
   ```

3. Check Sentry project settings → Client Keys (DSN)

### Issue: Auto-Restart Loop

**Symptoms:**
- Bot keeps restarting
- Railway shows continuous deployments

**Solutions:**
1. Check logs for crash reason:
   ```bash
   railway logs | grep -i error
   ```

2. Common causes:
   - Missing environment variables
   - Invalid Telegram token
   - Model training failure

3. Disable auto-restart temporarily:
   ```toml
   # In railway.toml
   restartPolicyType = "NEVER"
   ```

---

## Rollback

If the refactored bot has issues, you can quickly rollback:

### Option 1: Revert Deployment Files

```bash
# Update railway.toml
startCommand = "python -m src.integrations.telegram_bot"

# Update start.sh
python -m src.integrations.telegram_bot

# Push changes
git add railway.toml start.sh
git commit -m "Rollback to original bot"
git push
```

### Option 2: Use Railway Dashboard

1. Go to Deployments
2. Find previous working deployment
3. Click "Redeploy"

---

## Production Checklist

Before going live:

- [ ] All environment variables set
- [ ] Sentry DSN configured for error tracking
- [ ] Bot responds to `/start` command
- [ ] Weather API returns live data
- [ ] Location change works (`/location Delhi`)
- [ ] Forecast command works (`/forecast`)
- [ ] Logs show no errors
- [ ] Auto-restart policy configured
- [ ] Data logging enabled (for future training)
- [ ] README updated with production bot link

---

## Performance Optimization

### Railway Plan Recommendations

**Free Plan:**
- Suitable for testing
- 500 hours/month
- $5 credit included

**Hobby Plan ($5/month):**
- Recommended for production
- Always-on deployment
- Better performance

### Resource Monitoring

Check Railway metrics:
- **CPU Usage**: Should be <30% normally
- **Memory**: ~500MB typical (includes TensorFlow)
- **Network**: Depends on user activity

### Scaling Considerations

As user base grows:
1. **API Rate Limits**: Upgrade OpenWeatherMap plan
2. **Database**: Add PostgreSQL for user preferences
3. **Caching**: Implement Redis for weather data
4. **Load Balancing**: Consider multiple instances

---

## Security Best Practices

1. **Never commit secrets**
   - Use environment variables only
   - Add `.env` to `.gitignore`

2. **Rotate API keys regularly**
   - Telegram bot token
   - OpenWeatherMap API key

3. **Monitor Sentry alerts**
   - Set up email notifications
   - Review errors weekly

4. **Keep dependencies updated**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

## Support

- **Issues**: [GitHub Issues](https://github.com/PAVANKUMARELETI/badminton-bot/issues)
- **Documentation**: [Main README](../README.md)
- **Development**: [DEVELOPMENT.md](./DEVELOPMENT.md)

---

**Last Updated**: November 11, 2025
**Bot Version**: Refactored (Phase 1 Complete)
**Deployment**: Railway.app
