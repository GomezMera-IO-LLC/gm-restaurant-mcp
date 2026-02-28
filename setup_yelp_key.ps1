# Setup script for Yelp API key (Windows PowerShell)

Write-Host "=== Yelp API Key Setup ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will help you set up your Yelp Fusion API key."
Write-Host ""
Write-Host "To get your API key:"
Write-Host "1. Go to https://www.yelp.com/developers/v3/manage_app"
Write-Host "2. Sign in or create a Yelp account (free)"
Write-Host "3. Create a new app or use an existing one"
Write-Host "4. Copy your API Key"
Write-Host ""

$api_key = Read-Host "Enter your Yelp API key"

if ([string]::IsNullOrWhiteSpace($api_key)) {
    Write-Host "Error: API key cannot be empty" -ForegroundColor Red
    exit 1
}

# Save to ~/.env.yelpapi
$env_file = Join-Path $env:USERPROFILE ".env.yelpapi"
$api_key | Out-File -FilePath $env_file -Encoding ASCII -NoNewline

Write-Host ""
Write-Host "[OK] API key saved to $env_file" -ForegroundColor Green
Write-Host ""
Write-Host "You're all set! The Yelp Finder MCP server will now use this API key."
Write-Host ""
Write-Host "Note: Yelp Fusion API free tier includes:"
Write-Host "  - 500 API calls per day"
Write-Host "  - No credit card required"
Write-Host "  - Access to business search, details, and reviews"
Write-Host ""
