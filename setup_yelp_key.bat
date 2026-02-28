@echo off
REM Setup script for Yelp API key (Windows)

echo === Yelp API Key Setup ===
echo.
echo This script will help you set up your Yelp Fusion API key.
echo.
echo To get your API key:
echo 1. Go to https://www.yelp.com/developers/v3/manage_app
echo 2. Sign in or create a Yelp account (free)
echo 3. Create a new app or use an existing one
echo 4. Copy your API Key
echo.
set /p api_key="Enter your Yelp API key: "

if "%api_key%"=="" (
    echo Error: API key cannot be empty
    exit /b 1
)

REM Save to %USERPROFILE%\.env.yelpapi
echo %api_key%> "%USERPROFILE%\.env.yelpapi"

echo.
echo [OK] API key saved to %USERPROFILE%\.env.yelpapi
echo.
echo You're all set! The Yelp Finder MCP server will now use this API key.
echo.
echo Note: Yelp Fusion API free tier includes:
echo   - 500 API calls per day
echo   - No credit card required
echo   - Access to business search, details, and reviews
echo.
pause
