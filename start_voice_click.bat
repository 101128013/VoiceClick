@echo off
REM Voice Click Auto-Starter
REM This script starts the Voice Click application

cd /d "C:\Users\SUPER\Downloads\VoiceClick"
start pythonw voice_click_minimal.py

REM pythonw runs Python without showing a console window
REM The widget only appears during recording
