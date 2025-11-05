@echo off
REM Disable VoiceClick Monitor auto-start

cd /d "%~dp0"
python monitor.py --disable-autostart

echo.
echo VoiceClick Monitor auto-start DISABLED
echo The widget will no longer start automatically.
echo.
pause
