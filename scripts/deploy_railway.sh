#!/bin/bash
# Quick deployment script for Railway

echo "🚀 Deploying Badminton Wind Bot to Railway"
echo "=========================================="

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Badminton wind predictor bot"
fi

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo "Installing Railway CLI..."
    
    # Install Railway CLI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install railwayapp/railway/railway
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        bash <(curl -fsSL https://railway.app/install.sh)
    else
        echo "Please install Railway CLI manually:"
        echo "https://docs.railway.app/develop/cli#install"
        exit 1
    fi
fi

echo "✅ Railway CLI installed"

# Login to Railway
echo "🔐 Logging in to Railway..."
railway login

# Initialize project
echo "📦 Creating Railway project..."
railway init

# Set environment variables
echo "🔧 Setting environment variables..."
echo "Please enter your Telegram Bot Token:"
read TELEGRAM_BOT_TOKEN
railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"

echo "Please enter your OpenWeather API Key:"
read OPENWEATHER_API_KEY
railway variables set OPENWEATHER_API_KEY="$OPENWEATHER_API_KEY"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo ""
echo "🎉 Your bot is now running 24/7 on Railway!"
echo ""
echo "To view logs:"
echo "  railway logs"
echo ""
echo "To check status:"
echo "  railway status"
echo ""
echo "To open dashboard:"
echo "  railway open"
