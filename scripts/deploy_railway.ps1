# Quick deployment script for Railway (PowerShell)

Write-Host "🚀 Deploying Badminton Wind Bot to Railway" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "📦 Initializing git repository..." -ForegroundColor Yellow
    git init
    git add .
    git commit -m "Initial commit - Badminton wind predictor bot"
}

# Check if Railway CLI is installed
$railwayInstalled = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayInstalled) {
    Write-Host "❌ Railway CLI not found" -ForegroundColor Red
    Write-Host "Installing Railway CLI..." -ForegroundColor Yellow
    
    # Install Railway CLI via npm (requires Node.js)
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        npm install -g @railway/cli
    } else {
        Write-Host "Please install Railway CLI manually:" -ForegroundColor Red
        Write-Host "1. Install Node.js from https://nodejs.org" -ForegroundColor Yellow
        Write-Host "2. Run: npm install -g @railway/cli" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "OR use the web dashboard:" -ForegroundColor Yellow
        Write-Host "https://railway.app" -ForegroundColor Cyan
        exit 1
    }
}

Write-Host "✅ Railway CLI installed" -ForegroundColor Green

# Login to Railway
Write-Host "🔐 Logging in to Railway..." -ForegroundColor Yellow
railway login

# Initialize project
Write-Host "📦 Creating Railway project..." -ForegroundColor Yellow
railway init

# Set environment variables
Write-Host "🔧 Setting environment variables..." -ForegroundColor Yellow
$TELEGRAM_BOT_TOKEN = "8463771089:AAElsOdKnkxLXU2Dnyo3WcIof6HzyE4TvTs"
$OPENWEATHER_API_KEY = "c9bff12eb91b0e17f64594137bbd16fd"

railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
railway variables set OPENWEATHER_API_KEY="$OPENWEATHER_API_KEY"

# Deploy
Write-Host "🚀 Deploying to Railway..." -ForegroundColor Yellow
railway up

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Your bot is now running 24/7 on Railway!" -ForegroundColor Green
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  railway logs        - View bot logs" -ForegroundColor Cyan
Write-Host "  railway status      - Check deployment status" -ForegroundColor Cyan
Write-Host "  railway open        - Open Railway dashboard" -ForegroundColor Cyan
Write-Host "  railway down        - Stop the bot" -ForegroundColor Cyan
