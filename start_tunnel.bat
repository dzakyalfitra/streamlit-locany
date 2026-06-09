@echo off
title Cloudflare Tunnel - LocateAnything
setlocal

set PROJECT_DIR=%~dp0

echo.
echo  ========================================
echo   Cloudflare Quick Tunnel
echo  ========================================
echo.
echo  Starting tunnel to expose localhost:8501...
echo  A public URL will appear below (e.g. https://xxx-xxx.trycloudflare.com)
echo.
echo  Share this URL + your password with friends!
echo  The URL changes each time you restart this script.
echo.
echo  Press Ctrl+C to stop the tunnel.
echo.

where cloudflared >nul 2>nul
if errorlevel 1 (
    echo  ERROR: cloudflared not found. Install it first:
    echo    winget install Cloudflare.cloudflared
    pause
    exit /b 1
)

cloudflared tunnel --url http://localhost:8501
pause
