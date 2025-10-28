# Quick start script for Telegram bot
# Usage: .\scripts\start_telegram_bot.ps1

Write-Host "🤖 Starting Badminton Wind Forecast Telegram Bot..." -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "📝 Creating .env from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "⚠️  Please edit .env file and add your TELEGRAM_BOT_TOKEN" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "How to get token:" -ForegroundColor Cyan
    Write-Host "1. Open Telegram and search for @BotFather"
    Write-Host "2. Send /newbot and follow instructions"
    Write-Host "3. Copy the token to .env file"
    Write-Host ""
    exit 1
}

# Load environment variables
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$name" -Value $value
    }
}

# Check if token is set
if (-not $env:TELEGRAM_BOT_TOKEN -or $env:TELEGRAM_BOT_TOKEN -like "*your*") {
    Write-Host "❌ TELEGRAM_BOT_TOKEN not configured in .env" -ForegroundColor Red
    Write-Host "Please edit .env and add your actual bot token" -ForegroundColor Yellow
    exit 1
}

# Activate conda environment
Write-Host "🐍 Activating conda environment..." -ForegroundColor Green
conda activate badminton-wind

# Check if python-telegram-bot is installed
Write-Host "📦 Checking dependencies..." -ForegroundColor Green
$telegramBotInstalled = pip list | Select-String "python-telegram-bot"
if (-not $telegramBotInstalled) {
    Write-Host "📥 Installing python-telegram-bot..." -ForegroundColor Yellow
    pip install python-telegram-bot python-dotenv
}

# Start the bot
Write-Host ""
Write-Host "🚀 Starting bot..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python -m src.integrations.telegram_bot
