@echo off
title LUNA AI Assistant
cd /d "%~dp0"
echo Starting LUNA AI Assistant...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo LUNA encountered an issue. Press any key to exit...
    pause >nul
)
