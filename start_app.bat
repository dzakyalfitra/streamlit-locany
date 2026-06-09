@echo off
title LocateAnything-3B Web Interface
setlocal

set VENV_DIR=F:\LocAny\loc_venv
set PROJECT_DIR=%~dp0
set PYTHONPATH=%PROJECT_DIR%..;%PYTHONPATH%

echo.
echo  ========================================
echo   LocateAnything-3B  -  NVIDIA Eagle VLM
echo  ========================================
echo.
echo  Using virtual environment: %VENV_DIR%
echo  Starting Streamlit server...
echo  Access locally: http://localhost:8501
echo.
echo  Press Ctrl+C to stop the server.
echo.

"%VENV_DIR%\Scripts\streamlit.exe" run "%PROJECT_DIR%app.py" --server.port 8501
pause
