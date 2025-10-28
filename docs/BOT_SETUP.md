# 🤖 Messaging Bot Setup Guide

Make your badminton wind forecaster available via **Telegram** or **WhatsApp** so your college mates can easily check if it's safe to play!

## 🎯 Quick Comparison

| Feature | Telegram | WhatsApp |
|---------|----------|----------|
| **Ease of Setup** | ⭐⭐⭐⭐⭐ Very Easy | ⭐⭐⭐ Moderate |
| **Cost** | 100% Free | Free (sandbox) or paid |
| **User Experience** | Native bot commands | SMS-like interface |
| **Best For** | Tech-savvy groups | Everyone |
| **Setup Time** | 5 minutes | 15-30 minutes |

**Recommendation**: Start with **Telegram** - it's easier and completely free!

---

## 📱 Option 1: Telegram Bot (RECOMMENDED)

### Why Telegram?
- ✅ 100% free forever
- ✅ No phone number verification needed
- ✅ Rich bot features (buttons, commands, inline keyboards)
- ✅ Setup in 5 minutes
- ✅ Great for college groups

### Step-by-Step Setup

#### 1. Create Your Bot (2 minutes)

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name: `Badminton Wind Checker` (display name)
4. Choose a username: `your_college_badminton_bot` (must end in 'bot')
5. **Copy the token** you receive (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 2. Install Dependencies

```powershell
conda activate badminton-wind
pip install python-telegram-bot
```

#### 3. Set Your Bot Token

**Windows PowerShell:**
```powershell
$env:TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**Permanent (recommended):**
Create a `.env` file in your project:
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

Then install python-dotenv:
```powershell
pip install python-dotenv
```

#### 4. Start Your Bot

```powershell
python -m src.integrations.telegram_bot
```

You should see:
```
Bot is ready! Press Ctrl+C to stop.
```

#### 5. Test It!

1. Search for your bot username on Telegram
2. Send `/start`
3. Send "Can I play badminton?"
4. Get instant forecast! 🎉

### Usage Examples

Your friends can message the bot:
- `/forecast` - Get detailed wind forecast
- `/help` - Show help
- "Can I play?" - Quick check
- "Is it windy?" - Any text gets forecast

### Sharing with Friends

1. Get your bot link: `https://t.me/your_college_badminton_bot`
2. Share in your college WhatsApp/Telegram groups
3. Everyone can use it instantly!

---

## 💬 Option 2: WhatsApp Bot

### Why WhatsApp?
- ✅ Everyone already has it
- ✅ Familiar SMS-like interface
- ✅ Good for less tech-savvy users
- ⚠️ Requires Twilio account
- ⚠️ Free tier limited (sandbox only)

### Step-by-Step Setup

#### 1. Sign Up for Twilio (Free)

1. Go to https://www.twilio.com/try-twilio
2. Sign up (you get **free credits**)
3. Verify your phone number

#### 2. Get WhatsApp Sandbox

1. In Twilio Console, go to **Messaging** > **Try it out** > **Send a WhatsApp message**
2. Follow instructions to join sandbox:
   - Send a code like `join happy-dog` to the Twilio WhatsApp number
3. Copy these from console:
   - **Account SID**
   - **Auth Token**
   - **WhatsApp Number** (looks like `whatsapp:+14155238886`)

#### 3. Install Dependencies

```powershell
conda activate badminton-wind
pip install twilio flask python-dotenv
```

#### 4. Set Environment Variables

Create `.env` file:
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

Or set manually:
```powershell
$env:TWILIO_ACCOUNT_SID = "ACxxxxx..."
$env:TWILIO_AUTH_TOKEN = "your_token"
$env:TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
```

#### 5. Expose Your Server to Internet

You need a public URL for Twilio webhooks. Two options:

**Option A: ngrok (Easy for testing)**
```powershell
# Download ngrok from https://ngrok.com
ngrok http 5000
```
Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

**Option B: Deploy to Cloud (Production)**
- Heroku (free tier)
- Railway.app
- Render.com
- Your own server

#### 6. Configure Twilio Webhook

1. In Twilio Console, go to your WhatsApp Sandbox settings
2. Set **"When a message comes in"** webhook to:
   ```
   https://your-ngrok-url.ngrok.io/webhook
   ```
3. Method: **POST**
4. Save

#### 7. Start Your Bot

```powershell
python -m src.integrations.whatsapp_bot
```

#### 8. Test It!

1. Send a WhatsApp message to your Twilio number
2. Type "Can I play?"
3. Get instant forecast! 🎉

### Usage Examples

Send to WhatsApp bot:
- "forecast" - Get wind forecast
- "help" - Show help
- Any message - Gets forecast

### Limitations of Free Tier

- **Sandbox**: Only you and people who join sandbox can use it
- **Messages**: Limited free credits (~$15 worth)
- **Production**: Need approved WhatsApp Business Account ($$$)

**For college group**: Telegram is better unless you need enterprise features!

---

## 🎨 Making It More Interesting for College Mates

### Feature Ideas

#### 1. **Group Notifications** (Telegram)
```python
# Send daily forecast to group
bot.send_message(
    chat_id=-123456789,  # Your group ID
    text="🌅 Good morning! Today's badminton conditions..."
)
```

#### 2. **Custom Commands**
- `/subscribe` - Daily 7 AM forecast
- `/weekend` - Weekend forecast
- `/location` - Add weather station near your campus

#### 3. **Fun Responses**
```python
responses = {
    "PLAY": [
        "🏸 Let's smash it! Wind is perfect!",
        "🌟 Game on! Court conditions are ideal!",
        "⚡ Shuttlecock won't stand a chance!",
    ],
    "DON'T PLAY": [
        "🌪️ Too windy mate! Netflix instead?",
        "💨 Wind says no. Gym day? 🏋️",
        "⛈️ Save your energy for tomorrow!",
    ]
}
```

#### 4. **Leaderboard**
Track who plays most and give badges:
```
🏆 Weekly Badminton Kings
1. 🥇 Raj - 12 games
2. 🥈 Priya - 10 games
3. 🥉 Arjun - 8 games
```

#### 5. **Court Booking Integration**
```
✅ PLAY recommended!
Want to book court?
[Book 6-7 PM] [Book 7-8 PM]
```

#### 6. **Weather Alerts**
```
⚠️ ALERT: Wind dropping to safe levels in 30 mins!
Current: 2.1 m/s → Forecast 1.3 m/s @ 6:30 PM
```

#### 7. **Poll Feature**
```
Wind is borderline (1.6 m/s). Play anyway?
👍 Yes, let's risk it (5 votes)
👎 No, too risky (2 votes)
```

### Advanced: Multi-Location Support

```python
# Let users add their location
locations = {
    "main_campus": "Bangalore Station A",
    "hostel": "Bangalore Station B",
    "sports_complex": "Bangalore Station C",
}

# Usage: /forecast sports_complex
```

---

## 🚀 Deployment for College-Wide Use

### Quick Setup (5 users - Telegram Sandbox)
Just run bot on your laptop when needed!

### Medium Setup (50 users - Always Online)
Deploy to free cloud:

**Railway.app** (Recommended):
```bash
# 1. Create account at railway.app
# 2. Connect GitHub repo
# 3. Add start command:
python -m src.integrations.telegram_bot

# 4. Add environment variables in dashboard
# Done! Your bot is 24/7 online
```

**Heroku**:
```bash
# Create Procfile
echo "bot: python -m src.integrations.telegram_bot" > Procfile

# Deploy
heroku create your-badminton-bot
git push heroku main
```

### Large Setup (500+ users - Production)
- Use AWS/GCP/Azure
- Add database for user preferences
- Implement caching (Redis)
- Add monitoring (Sentry)

---

## 🎓 College-Specific Features

### 1. **Academic Calendar Integration**
```python
# No forecasts during exams!
if is_exam_week():
    return "📚 Focus on exams! Check back after finals."
```

### 2. **Hostel-Based Groups**
```python
# Different forecasts for different campus locations
/forecast_boys_hostel
/forecast_girls_hostel
/forecast_sports_complex
```

### 3. **Competition Mode**
```python
# Tournament days - stricter thresholds
if tournament_day:
    threshold = 1.0  # Even lower wind tolerance
```

### 4. **Streak Tracking**
```
🔥 You've played 5 days in a row!
🏆 Unlock "Regular Player" badge
```

---

## 📊 Analytics & Insights

Track usage to improve:
```python
# Log every forecast request
{
    "user": "@john_doe",
    "timestamp": "2024-03-24 18:00",
    "decision": "PLAY",
    "wind": 1.2,
    "did_user_play": True  # Follow-up survey
}
```

Generate insights:
- Most active users
- Peak request times
- Accuracy tracking
- User satisfaction

---

## 🔐 Security & Privacy

### Best Practices

1. **Don't commit tokens to Git**
   ```bash
   # Add to .gitignore
   .env
   config/secrets.py
   ```

2. **Rate limiting**
   ```python
   # Prevent spam
   @rate_limit(max_calls=10, period=60)  # 10 calls/minute
   def forecast_command():
       ...
   ```

3. **User privacy**
   - Don't log personal messages
   - Clear data on request
   - Anonymous usage stats only

---

## 🐛 Troubleshooting

### Telegram Bot Not Responding
```bash
# Check if bot is running
ps aux | grep telegram_bot

# Check logs
tail -f logs/telegram_bot.log

# Test token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### WhatsApp Webhook Not Working
```bash
# Test locally
curl -X POST http://localhost:5000/webhook \
  -d "Body=forecast" \
  -d "From=whatsapp:+1234567890"

# Check ngrok
curl http://127.0.0.1:4040/api/tunnels  # ngrok dashboard
```

### Model Loading Issues
```python
# Preload model on startup
bot = TelegramBot()
bot._load_model()  # Load once
bot.run()  # Then start
```

---

## 💡 Pro Tips

1. **Set up aliases**
   ```bash
   # Quick start
   alias badminton-bot="conda activate badminton-wind && python -m src.integrations.telegram_bot"
   ```

2. **Systemd service** (Linux)
   ```ini
   [Unit]
   Description=Badminton Wind Bot
   
   [Service]
   ExecStart=/path/to/conda/envs/badminton-wind/bin/python -m src.integrations.telegram_bot
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Docker deployment**
   ```dockerfile
   FROM python:3.10
   COPY . /app
   WORKDIR /app
   RUN pip install -r requirements.txt
   CMD ["python", "-m", "src.integrations.telegram_bot"]
   ```

---

## 📱 Ready-to-Share Messages

**For College WhatsApp Group:**
```
🏸 Hey badminton players!

I made a bot that tells us if it's safe to play based on wind conditions 🌬️

Telegram: @your_college_badminton_bot
Just message "Can I play?" and get instant forecast!

Features:
✅ Real-time wind forecasts
✅ Smart PLAY/DON'T PLAY decisions
✅ 1h, 3h, 6h predictions

Try it out! 🎯
```

---

## 🎉 Launch Checklist

- [ ] Bot created and token saved
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Bot tested with yourself
- [ ] Tested with 2-3 friends
- [ ] Deployment set up (if needed)
- [ ] Welcome message customized
- [ ] Shared in college group
- [ ] Monitoring set up
- [ ] Gathered feedback

---

## 🆘 Need Help?

Common issues:
- **Token invalid**: Regenerate from @BotFather
- **Module not found**: Check `pip list` in correct env
- **Webhook failed**: Verify ngrok URL is HTTPS
- **Model not loading**: Check path in code

---

**Your college mates will love this!** 🏸🌟

Start with Telegram (easiest), then expand to WhatsApp if needed.
