@echo off
title Claude Web Chat
echo ==================================
echo   Claude Web Chat
echo ==================================
echo.

if "%ANTHROPIC_AUTH_TOKEN%"=="" if "%ANTHROPIC_API_KEY%"=="" (
    echo [ERROR] ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY not set
    pause
    exit /b 1
)

cd /d "%~dp0"

echo [1/2] Starting Flask server on port 5000...
start /B python app.py
timeout /t 2 /nobreak >nul

echo [2/2] Starting cloudflared tunnel...
echo.
echo   Your public URL will appear below:
echo   =================================
echo.

cloudflared tunnel --url http://127.0.0.1:5000
