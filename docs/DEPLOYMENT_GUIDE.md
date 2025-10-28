# 🚀 Deployment Guide - Run Your Bot 24/7

## Quick Comparison of Free Options

| Platform | Free Tier | Setup Time | Best For |
|----------|-----------|------------|----------|
| **Railway** ⭐ | $5 credit/month | 5 min | Easiest, recommended |
| **Render** | 750 hrs/month | 10 min | Reliable, auto-deploy |
| **Fly.io** | 3 small VMs free | 15 min | Most powerful |
| **PythonAnywhere** | Always free tier | 10 min | Simple Python apps |

---

## 🌟 Option 1: Railway.app (RECOMMENDED)

**Why Railway?**
- ✅ Easiest setup (literally 3 clicks)
- ✅ $5 free credit/month (enough for small bot)
- ✅ Auto-deploys from GitHub
- ✅ Free database included

### Setup Steps:

1. **Push code to GitHub** (if not already)
   ```powershell
   git init
   git add .
   git commit -m "Initial commit - badminton wind predictor bot"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/badminton-wind-bot.git
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to https://railway.app
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python and deploys!

3. **Add environment variables**
   - In Railway dashboard, go to your project
   - Click "Variables" tab
   - Add:
     ```
     TELEGRAM_BOT_TOKEN=your_bot_token_here
     OPENWEATHER_API_KEY=your_api_key_here
     ```

4. **Done!** ✅
   - Bot runs 24/7
   - Auto-restarts on crash
   - Free monitoring included

---

## 🎨 Option 2: Render.com

**Why Render?**
- ✅ 750 hours/month free (enough for 24/7)
- ✅ Very reliable
- ✅ Auto-deploys from GitHub

### Setup Steps:

1. **Create `render.yaml`** (already done - see below)

2. **Deploy**
   - Go to https://render.com
   - Sign in with GitHub
   - Click "New" → "Blueprint"
   - Connect your repository
   - Render auto-deploys!

3. **Add environment variables**
   - In dashboard, go to your service
   - Environment → Add variables
   - Same as Railway

---

## ✈️ Option 3: Fly.io

**Why Fly.io?**
- ✅ 3 free VMs (most generous)
- ✅ Global deployment
- ✅ Great for scaling

### Setup Steps:

1. **Install Fly CLI**
   ```powershell
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Deploy**
   ```powershell
   fly auth login
   fly launch
   # Follow prompts, choose region closest to users
   ```

3. **Set secrets**
   ```powershell
   fly secrets set TELEGRAM_BOT_TOKEN=your_bot_token_here
   fly secrets set OPENWEATHER_API_KEY=your_api_key_here
   ```

4. **Deploy**
   ```powershell
   fly deploy
   ```

---

## 🐍 Option 4: PythonAnywhere

**Why PythonAnywhere?**
- ✅ Forever free tier
- ✅ No credit card needed
- ✅ Python-focused

### Setup Steps:

1. **Sign up** at https://www.pythonanywhere.com

2. **Upload code**
   - Use "Files" tab
   - Or clone from GitHub

3. **Create always-on task**
   - Go to "Tasks" tab
   - Add: `python3 -m src.integrations.telegram_bot`
   - Set to run every hour

4. **Set environment variables**
   - In bash console:
     ```bash
     export TELEGRAM_BOT_TOKEN=your_bot_token_here
     export OPENWEATHER_API_KEY=your_api_key_here
     ```

⚠️ **Note**: Free tier has some limitations (CPU time)

---

## 📦 Quick Deploy - Railway (Step by Step)

### Step 1: Prepare Your Code

```powershell
# Make sure you have a requirements.txt
pip freeze > requirements.txt

# Create .gitignore (if not exists)
echo "data/" >> .gitignore
echo "*.db" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore

# Commit everything
git add .
git commit -m "Ready for deployment"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create new repository (e.g., "badminton-wind-bot")
3. Don't initialize with README (you have code already)

```powershell
git remote add origin https://github.com/YOUR_USERNAME/badminton-wind-bot.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Railway

1. **Sign up**: https://railway.app/login
2. **New Project** → Deploy from GitHub
3. **Select** your repository
4. **Add variables**:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENWEATHER_API_KEY`
5. **Deploy** ✅

Railway will:
- Auto-detect Python
- Install dependencies from `requirements.txt`
- Run your bot
- Keep it running 24/7

---

## 🔧 Alternative: Keep Running on Your PC

If you want to keep it running locally (free but requires PC on):

### Windows Service Setup

```powershell
# Create a scheduled task to start bot on boot
$action = New-ScheduledTaskAction -Execute "python" -Argument "-m src.integrations.telegram_bot" -WorkingDirectory "G:\PROJECTS\badminton"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
Register-ScheduledTask -TaskName "BadmintonBot" -Action $action -Trigger $trigger -Principal $principal
```

### Or Use `nohup` Alternative (PowerShell)

```powershell
# Start in background (keeps running even if you close terminal)
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m","src.integrations.telegram_bot" -WorkingDirectory "G:\PROJECTS\badminton"
```

---

## 📊 Monitoring Your Bot

### Check if bot is running:

**Railway/Render/Fly.io:**
- Check dashboard logs
- Look for "Bot is ready!" message

**Test the bot:**
```
Open Telegram → Search for your bot → Send /start
```

### View logs:

**Railway:**
```
Dashboard → Your project → Logs tab
```

**Render:**
```
Dashboard → Your service → Logs
```

**Fly.io:**
```powershell
fly logs
```

---

## 💰 Cost Comparison

| Platform | Free Tier | After Free Tier |
|----------|-----------|-----------------|
| Railway | $5 credit/month | ~$5-10/month |
| Render | 750 hrs/month | $7/month for always-on |
| Fly.io | 3 VMs free | ~$2/month for extras |
| PythonAnywhere | Forever free* | $5/month for always-on |

**For a small bot**: All free tiers are enough! 🎉

---

## 🎯 Recommendation

**For beginners**: Use **Railway** ⭐
- Easiest setup (< 5 minutes)
- Best developer experience
- Free $5 credit is plenty for small bot

**For long-term free**: Use **Fly.io**
- Most generous free tier
- Great performance
- Slightly more setup

**For zero commitment**: Use **PythonAnywhere**
- No credit card needed
- Forever free (with limitations)

---

## 🚀 Next Steps

1. Choose your platform (I recommend Railway)
2. Follow the setup steps above
3. Test your bot on Telegram
4. Share with your college friends!

**Ready to deploy?** Let me know which platform you want to use and I'll help you through it! 🎉
