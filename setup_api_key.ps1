# Restaurant Finder MCP - API Key Setup (Windows PowerShell)

Write-Host "🔑 Restaurant Finder MCP - API Key Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$apiFile = Join-Path $env:USERPROFILE ".env.googleapi"

# Check if file already exists
if (Test-Path $apiFile) {
    Write-Host "⚠️  API key file already exists at: $apiFile" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Do you want to update it? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Keeping existing API key." -ForegroundColor Green
        exit 0
    }
}

Write-Host ""
Write-Host "Please enter your Google Maps API key:"
Write-Host "(Get one at: https://console.cloud.google.com/)" -ForegroundColor Gray
Write-Host ""
$apiKey = Read-Host "API Key"

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "❌ No API key provided. Exiting." -ForegroundColor Red
    exit 1
}

# Save API key
$apiKey | Out-File -FilePath $apiFile -Encoding ASCII -NoNewline

Write-Host ""
Write-Host "✅ API key saved to: $apiFile" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart your MCP server in Kiro"
Write-Host "2. Test with: 'Find restaurants near me'"
Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
