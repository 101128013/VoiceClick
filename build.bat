@echo off
REM VoiceClick - Build Script for PyInstaller
REM Creates a standalone Windows executable

echo ========================================
echo VoiceClick Build Script
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo [1/3] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo ✓ Cleaned

echo.
echo [2/3] Building executable with PyInstaller...
python -m PyInstaller VoiceClick.spec --clean --noconfirm
if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)
echo ✓ Build complete

echo.
echo [3/3] Verifying build...
if exist "dist\VoiceClick.exe" (
    echo ✓ Executable created: dist\VoiceClick.exe
    dir "dist\VoiceClick.exe"
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL
    echo ========================================
    echo Executable location: %CD%\dist\VoiceClick.exe
    echo.
) else (
    echo [ERROR] Executable not found
    pause
    exit /b 1
)

pause
