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
Write-Host "Setting environment variables..." -ForegroundColor Yellow
railway variables set TELEGRAM_BOT_TOKEN="8463771089:AAElsOdKnkxLXU2Dnyo3WcIof6HzyE4TvTs"
railway variables set OPENWEATHER_API_KEY="c9bff12eb91b0e17f64594137bbd16fd"

# Deploy
Write-Host "Deploying..." -ForegroundColor Yellow
railway up

Write-Host "✅ Deployment complete! Check Railway dashboard" -ForegroundColor Green
Write-Host "View logs: railway logs" -ForegroundColor Cyan
