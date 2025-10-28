# Quick Railway Deployment Script
# Run this after installing Railway CLI: npm install -g @railway/cli

Write-Host "🚀 Deploying to Railway..." -ForegroundColor Green

# Login to Railway
railway login

# Create new project from current directory
railway init

# Link to GitHub repo
railway link

# Set environment variables
Write-Host "🔧 Setting environment variables..." -ForegroundColor Yellow
Write-Host "Please enter your Telegram Bot Token:" -ForegroundColor Cyan
$TELEGRAM_BOT_TOKEN = Read-Host
railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"

Write-Host "Please enter your OpenWeather API Key:" -ForegroundColor Cyan
$OPENWEATHER_API_KEY = Read-Host
railway variables set OPENWEATHER_API_KEY="$OPENWEATHER_API_KEY"

# Deploy
Write-Host "Deploying..." -ForegroundColor Yellow
railway up

Write-Host "✅ Deployment complete! Check Railway dashboard" -ForegroundColor Green
Write-Host "View logs: railway logs" -ForegroundColor Cyan
