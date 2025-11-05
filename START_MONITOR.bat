@echo off
REM VoiceClick Monitor Quick Start
REM Run this to start the monitor widget immediately

setlocal enabledelayedexpansion

echo.
echo =================================
echo  VoiceClick Development Monitor
echo =================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ ERROR: Python not found in PATH
    echo.
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if PyQt6 is installed
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo Installing PyQt6...
    pip install PyQt6 >nul 2>&1
    if errorlevel 1 (
        echo ✗ Failed to install PyQt6
        echo.
        echo Run this command manually:
        echo   pip install PyQt6
        echo.
        pause
        exit /b 1
    )
    echo ✓ PyQt6 installed
    echo.
)

REM Start the monitor
echo Starting VoiceClick Monitor...
echo.
echo The widget will appear above your taskbar.
echo.
echo Controls:
echo   ↑ / ↓      Navigate tasks
echo   ESC        Hide/show widget
echo   Double-click to toggle
echo.
echo Updating task?
echo   python monitor_control.py set-task 5
echo.

start python monitor.py

echo ✓ Monitor started!
echo.
echo It will continue running in the background.
echo.
