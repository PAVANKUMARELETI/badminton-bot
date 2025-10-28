# 🎉 Your Badminton Wind Forecaster - Now With Bot Integrations!

## ✅ What's New?

I've added **Telegram** and **WhatsApp** bot integrations so your entire college can easily check wind conditions!

### 📱 New Features

1. **Telegram Bot** - 100% free, easy setup, perfect for tech-savvy groups
2. **WhatsApp Bot** - Everyone has it, familiar interface
3. **Quick-start scripts** - One command to launch bots
4. **Comprehensive guide** - Step-by-step setup in `docs/BOT_SETUP.md`

---

## 🚀 Quick Start - Telegram Bot (5 Minutes!)

### Step 1: Create Your Bot

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Name it: `Your College Badminton Bot`
5. Username: `yourcollege_badminton_bot`
6. **Copy the token** (looks like `123456:ABCdef...`)

### Step 2: Install & Run

```powershell
# Activate your environment
conda activate badminton-wind

# Install Telegram bot library
pip install python-telegram-bot python-dotenv

# Set your token
$env:TELEGRAM_BOT_TOKEN = "paste-your-token-here"

# Start the bot!
python -m src.integrations.telegram_bot
```

**OR use the automated script:**
```powershell
# 1. Copy .env.example to .env
Copy-Item .env.example .env

# 2. Edit .env and add your token

# 3. Run the script
.\scripts\start_telegram_bot.ps1
```

### Step 3: Test It!

1. Search for your bot on Telegram
2. Send `/start`
3. Send "Can I play?"
4. Get instant forecast! 🎯

### Step 4: Share With Friends

Share this link in your college group:
```
https://t.me/yourcollege_badminton_bot
```

Everyone can use it immediately!

---

## 💬 WhatsApp Bot Setup (15 Minutes)

### Why WhatsApp?
- Everyone already has it
- Familiar for non-technical users
- Good for broader college community

### Quick Setup

```powershell
# 1. Sign up at https://www.twilio.com (free credits!)
# 2. Get WhatsApp sandbox credentials
# 3. Run the setup script
.\scripts\start_whatsapp_bot.ps1
```

See **[docs/BOT_SETUP.md](docs/BOT_SETUP.md)** for detailed WhatsApp setup.

---

## 🎨 Cool Features Your Friends Will Love

### 1. **Instant Forecasts**
```
You: "Can I play?"
Bot: ✅ PLAY
     Wind: 1.2 m/s (safe!)
     Next 3h: 1.4 m/s
     Next 6h: 1.1 m/s
```

### 2. **Smart Decisions**
The bot automatically decides PLAY/DON'T PLAY based on:
- Wind speed < 1.5 m/s ✅
- Gusts < 3.5 m/s ✅
- Multi-horizon safety ✅

### 3. **User-Friendly**
- No complex commands
- Just ask naturally: "windy?", "weather check", "can we play?"
- Works with any message!

---

## 📚 What You Just Got

### New Files Created

1. **`src/integrations/telegram_bot.py`** - Telegram bot implementation
2. **`src/integrations/whatsapp_bot.py`** - WhatsApp bot via Twilio
3. **`docs/BOT_SETUP.md`** - Complete setup guide (30+ pages!)
4. **`scripts/start_telegram_bot.ps1`** - Quick-start script for Telegram
5. **`scripts/start_whatsapp_bot.ps1`** - Quick-start script for WhatsApp
6. **`.env.example`** - Template for credentials
7. **`requirements-bots.txt`** - Bot dependencies

### Features Included

✅ **Telegram Bot:**
- `/start` - Welcome message
- `/forecast` - Detailed forecast
- `/help` - Help message
- `/settings` - View thresholds
- Any text → instant forecast

✅ **WhatsApp Bot:**
- "forecast" - Get forecast
- "help" - Show help
- Any message → forecast (default)

✅ **Both Support:**
- PLAY/DON'T PLAY decisions
- Multi-horizon forecasts (1h, 3h, 6h)
- Safety thresholds
- User-friendly formatting

---

## 🎓 Ideas for Your College Group

### 1. **Daily Morning Forecast**
Set up scheduled message at 7 AM:
```
🌅 Good morning badminton players!
Today's forecast: ✅ PLAY (perfect conditions)
Best time: 5-7 PM (wind: 0.8 m/s)
```

### 2. **Group Poll Feature**
```
Wind: 1.6 m/s (slightly high)
Play anyway?
👍 Yes (5 votes) | 👎 No (2 votes)
```

### 3. **Leaderboard**
```
🏆 This Week's Top Players
1. 🥇 Raj - 12 games
2. 🥈 Priya - 10 games
3. 🥉 Arjun - 8 games
```

### 4. **Court Booking Integration**
```
✅ PLAY recommended!
🏸 Available courts:
[Book Court A] [Book Court B]
```

### 5. **Location-Based Forecasts**
```
/forecast_main_campus
/forecast_hostel
/forecast_sports_complex
```

See **`docs/BOT_SETUP.md`** for more ideas!

---

## 🚀 Make It 24/7 (Optional)

### For Testing (Run on Your Laptop)
Just keep the script running:
```powershell
python -m src.integrations.telegram_bot
```

### For Production (Always Online)

#### Option 1: Railway.app (Easiest, Free)
```bash
# 1. Sign up at railway.app
# 2. Connect GitHub repo
# 3. Add environment variable: TELEGRAM_BOT_TOKEN
# 4. Deploy! (automatic)
```

#### Option 2: Heroku
```bash
# Create Procfile
echo "bot: python -m src.integrations.telegram_bot" > Procfile

# Deploy
heroku create your-badminton-bot
git push heroku main
```

#### Option 3: Your Own Server
```bash
# Use systemd, PM2, or Docker
# See docs/BOT_SETUP.md for details
```

---

## 🔒 Security & Best Practices

### Protect Your Credentials

✅ **Do:**
- Use `.env` file for secrets
- Add `.env` to `.gitignore` (already done!)
- Never commit tokens to Git

❌ **Don't:**
- Share bot tokens publicly
- Hardcode credentials in code
- Commit `.env` file

### Rate Limiting

Add to prevent spam:
```python
# 10 requests per minute per user
@rate_limit(max_calls=10, period=60)
```

---

## 📊 Bot Comparison

| Feature | Telegram | WhatsApp |
|---------|----------|----------|
| **Setup Time** | 5 min | 15-30 min |
| **Cost** | FREE | Free sandbox |
| **User Limit** | Unlimited | Sandbox limited |
| **Commands** | Rich (buttons, inline) | Text only |
| **Best For** | Tech groups | Everyone |
| **24/7 Hosting** | Easy | Need webhook |

**Recommendation**: Start with **Telegram** (easier, free, feature-rich)!

---

## 🎯 Usage Examples

### Telegram Examples

**User Messages:**
```
User: "Can I play?"
Bot: ✅ PLAY - Wind is perfect! (1.2 m/s)

User: "/forecast"
Bot: [Detailed forecast with 1h/3h/6h predictions]

User: "Is it windy today?"
Bot: ❌ DON'T PLAY - Too windy (2.3 m/s)
     Forecast: Wind dropping to 1.4 m/s by 6 PM
```

### WhatsApp Examples

```
You: forecast
Bot: ✅ PLAY
     📅 2024-03-24 18:00
     
     Wind Forecast:
     ✅ 1h: 1.3 m/s
     ✅ 3h: 1.4 m/s
     ⚠️ 6h: 1.6 m/s
```

---

## 🐛 Troubleshooting

### Bot Not Responding?

**Check 1: Token Correct?**
```powershell
# Verify token
$env:TELEGRAM_BOT_TOKEN
```

**Check 2: Bot Running?**
```powershell
# See if process is running
Get-Process python
```

**Check 3: Test Token**
```powershell
# In browser, visit:
https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### Dependencies Issue?

```powershell
# Reinstall bot dependencies
conda activate badminton-wind
pip install --upgrade python-telegram-bot python-dotenv
```

### Model Not Loading?

```powershell
# Verify model exists
Test-Path experiments/latest/model.keras

# Retrain if needed
python -m src.cli.train --model lstm --data sample --epochs 2
```

---

## 📖 Full Documentation

- **[docs/BOT_SETUP.md](docs/BOT_SETUP.md)** - Complete bot setup guide (recommended reading!)
  - Step-by-step Telegram setup
  - Step-by-step WhatsApp setup
  - Advanced features
  - Deployment options
  - Feature ideas for college
  - Security best practices

- **[README.md](README.md)** - Main project docs
- **[QUICKSTART.md](QUICKSTART.md)** - Quick commands reference

---

## 💡 Next Steps

### Immediate (5 minutes)
1. ✅ Set up Telegram bot
2. ✅ Test with yourself
3. ✅ Share with 2-3 friends

### Short-term (1 day)
1. ✅ Share in college group
2. ✅ Gather feedback
3. ✅ Customize welcome message
4. ✅ Adjust thresholds if needed

### Long-term (1 week)
1. ✅ Deploy 24/7 (Railway/Heroku)
2. ✅ Add scheduled daily forecasts
3. ✅ Integrate real weather API
4. ✅ Add location support
5. ✅ Build leaderboard/stats

---

## 🎉 Summary

You now have:

✅ **Working ML model** (LSTM forecaster)
✅ **Telegram bot** (ready to deploy)
✅ **WhatsApp bot** (via Twilio)
✅ **Quick-start scripts** (one command!)
✅ **Complete documentation** (30+ pages)
✅ **Feature ideas** (for college groups)
✅ **Deployment guides** (24/7 hosting)

**Your entire college can now check wind conditions just by messaging a bot!** 🏸🌬️

---

## 🆘 Need Help?

1. Check **[docs/BOT_SETUP.md](docs/BOT_SETUP.md)** (very detailed!)
2. Read troubleshooting section above
3. Check bot logs for errors
4. Verify environment variables are set

---

## 🎊 Ready to Launch?

```powershell
# 1. Activate environment
conda activate badminton-wind

# 2. Set your token
$env:TELEGRAM_BOT_TOKEN = "your-token-here"

# 3. Launch!
python -m src.integrations.telegram_bot
```

**Share with friends and enjoy!** 🏸✨
