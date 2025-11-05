@echo off
REM Enable VoiceClick Monitor auto-start on Windows login
REM Run this batch file once to enable auto-start

cd /d "%~dp0"
python monitor.py --autostart

echo.
echo VoiceClick Monitor auto-start ENABLED
echo The widget will now start automatically when you log in.
echo.
pause
