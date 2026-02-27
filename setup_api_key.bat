@echo off
REM Restaurant Finder MCP - API Key Setup (Windows)

echo.
echo ================================
echo Restaurant Finder MCP - API Key Setup
echo ================================
echo.

set "API_FILE=%USERPROFILE%\.env.googleapi"

REM Check if file already exists
if exist "%API_FILE%" (
    echo WARNING: API key file already exists at: %API_FILE%
    echo.
    set /p "UPDATE=Do you want to update it? (y/n): "
    if /i not "%UPDATE%"=="y" (
        echo Keeping existing API key.
        exit /b 0
    )
)

echo.
echo Please enter your Google Maps API key:
echo (Get one at: https://console.cloud.google.com/)
echo.
set /p "API_KEY=API Key: "

if "%API_KEY%"=="" (
    echo.
    echo ERROR: No API key provided. Exiting.
    exit /b 1
)

REM Save API key
echo %API_KEY%> "%API_FILE%"

echo.
echo SUCCESS: API key saved to: %API_FILE%
echo.
echo Next steps:
echo 1. Restart your MCP server in Kiro
echo 2. Test with: 'Find restaurants near me'
echo.
echo Setup complete!
pause
