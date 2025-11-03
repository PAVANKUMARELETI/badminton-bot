# Script to remove exposed API key from git history
# WARNING: This rewrites git history. Make sure you have a backup!

Write-Host "⚠️  WARNING: This will rewrite git history!" -ForegroundColor Yellow
Write-Host "This will remove the exposed OpenWeather API key from all commits." -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Type 'YES' to continue"

if ($confirm -ne "YES") {
    Write-Host "Cancelled." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 1: Using git filter-repo to remove sensitive data..." -ForegroundColor Cyan

# Install git-filter-repo if needed
if (-not (Get-Command git-filter-repo -ErrorAction SilentlyContinue)) {
    Write-Host "Installing git-filter-repo..." -ForegroundColor Yellow
    pip install git-filter-repo
}

# Replace the API key with placeholder in all history
Write-Host "Replacing API key in git history..." -ForegroundColor Cyan
git filter-repo --replace-text <(echo "c9bff12eb91b0e17f64594137bbd16fd==>YOUR_API_KEY_HERE") --force

Write-Host ""
Write-Host "✅ Git history cleaned!" -ForegroundColor Green
Write-Host ""
Write-Host "Step 2: Force push to GitHub (this will rewrite remote history)" -ForegroundColor Yellow
Write-Host "Run: git push --force-with-lease origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "Step 3: IMPORTANT - Regenerate your OpenWeather API key!" -ForegroundColor Red
Write-Host "1. Go to https://home.openweathermap.org/api_keys" -ForegroundColor Yellow
Write-Host "2. Delete the old key: c9bff12e..." -ForegroundColor Yellow
Write-Host "3. Create a new API key" -ForegroundColor Yellow
Write-Host "4. Update .env file and Railway environment variables" -ForegroundColor Yellow
