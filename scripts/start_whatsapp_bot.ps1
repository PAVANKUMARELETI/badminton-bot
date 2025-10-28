# Quick start script for WhatsApp bot
# Usage: .\scripts\start_whatsapp_bot.ps1

Write-Host "💬 Starting Badminton Wind Forecast WhatsApp Bot..." -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "📝 Creating .env from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "⚠️  Please edit .env file and add your Twilio credentials" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "How to get credentials:" -ForegroundColor Cyan
    Write-Host "1. Sign up at https://www.twilio.com"
    Write-Host "2. Get Account SID and Auth Token from console"
    Write-Host "3. Set up WhatsApp sandbox"
    Write-Host "4. Add credentials to .env file"
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

# Check if credentials are set
if (-not $env:TWILIO_ACCOUNT_SID -or $env:TWILIO_ACCOUNT_SID -like "*your*") {
    Write-Host "❌ Twilio credentials not configured in .env" -ForegroundColor Red
    Write-Host "Please edit .env and add your actual Twilio credentials" -ForegroundColor Yellow
    exit 1
}

# Activate conda environment
Write-Host "🐍 Activating conda environment..." -ForegroundColor Green
conda activate badminton-wind

# Check if dependencies are installed
Write-Host "📦 Checking dependencies..." -ForegroundColor Green
$twilioInstalled = pip list | Select-String "twilio"
if (-not $twilioInstalled) {
    Write-Host "📥 Installing WhatsApp bot dependencies..." -ForegroundColor Yellow
    pip install twilio flask python-dotenv
}

# Start the bot
Write-Host ""
Write-Host "🚀 Starting bot on http://localhost:5000..." -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Don't forget to:" -ForegroundColor Yellow
Write-Host "1. Expose port 5000 with ngrok: ngrok http 5000"
Write-Host "2. Configure webhook URL in Twilio Console"
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python -m src.integrations.whatsapp_bot
