# VoiceClick User Guide

Complete guide for using VoiceClick voice-to-text application.

## Table of Contents

1. [What is VoiceClick?](#what-is-voiceclick)
2. [Installation](#installation)
3. [First Launch](#first-launch)
4. [The Main Window](#the-main-window)
   - [Status Tab](#status-tab)
   - [Settings Tab](#settings-tab)
   - [History Tab](#history-tab)
5. [System Tray Icon](#system-tray-icon)
6. [Basic Usage](#basic-usage)
7. [Features](#features)
8. [Configuration Details](#configuration-details)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Usage](#advanced-usage)

---

## What is VoiceClick?

VoiceClick is a voice-to-text application that allows you to transcribe your speech directly into any text field on Windows. Simply speak, and your words appear in the active text field automatically. It runs in the background and can be easily controlled via its main window or system tray icon.

## Installation

### Option 1: Installer (Recommended)

1. Download `VoiceClick-Setup-v1.0.0.exe` from GitHub Releases
2. Double-click the installer
3. Follow the installation wizard
4. Choose installation directory (default: `C:\Program Files\VoiceClick\`)
5. Optionally create desktop shortcut and start with Windows
6. Launch from Start Menu

### Option 2: Portable Version

1. Download `VoiceClick-Portable-v1.0.0.zip`
2. Extract the ZIP file anywhere
3. Run `VoiceClick.exe`
4. No installation needed!

**System Requirements:**
- Windows 10 or 11 (64-bit)
- 4GB RAM minimum (8GB recommended)
- NVIDIA GPU with CUDA support (optional, recommended for best performance)
- Internet connection (for initial model download)

## First Launch

On first launch, VoiceClick will:
1. Download the Whisper transcription model (2-5 minutes, one-time only)
2. Initialize the application
3. Show "Model loaded successfully"

**Note**: Model download only happens once. Subsequent launches are instant.

## The Main Window

The main window is organized into three tabs, giving you full control over the application.

### Status Tab

This is the default tab you see when you open the application. It provides real-time information about the transcription engine.

- **Status**: Shows the current state of the engine (e.g., `Idle`, `Recording`, `Transcribing`, `Initializing`)
- **Volume Meter**: A progress bar that displays the current input volume from your microphone. This is useful for checking if your microphone is working correctly
- **Start/Stop Recording Button**: Manually start or stop a recording session
- **Model Information**: Displays the currently loaded transcription model and compute device

### Settings Tab

This tab allows you to customize the application's behavior to fit your needs.

- **Transcription Model**:
  - **Model Size**: Choose the Whisper model size. Smaller models (`tiny`, `base`) are faster but less accurate. Larger models (`small`, `medium`, `large-v2`, `large-v3`) are more accurate but require more processing power. The `large-v3` model is the default and recommended for a balance of performance and accuracy
  - **Compute Device**: Select the hardware for running the model. `CUDA` (NVIDIA GPU) is highly recommended for the best performance. If you don't have a compatible GPU, select `CPU`
  - **Language**: Choose the language for transcription, or use "Auto-detect"
- **Recording Settings**:
  - **Silence Duration**: The number of seconds of silence to wait before automatically stopping the recording
  - **Microphone Device**: Select which microphone to use (default uses system default)
- **Auto-Start Options**:
  - **Auto-start on text field focus**: Automatically start recording when a text field gains focus
  - **Auto-start on left click**: Automatically start recording when you click on a text field
- **Save Settings**: Click this to apply and save any changes you make

### History Tab

This tab displays a record of your past transcriptions.

- **Transcription List**: Shows a table with the timestamp, duration, text, and model used for each transcription
- **Search**: Search through your transcription history by text content
- **Export to CSV**: Allows you to save your entire transcription history to a `.csv` file for use in other applications
- **Clear History**: Permanently deletes all saved transcription records

## System Tray Icon

When you minimize the main window, VoiceClick continues to run in the system tray.

- **Left-Click**: Show/hide the main application window
- **Right-Click**: Opens a context menu with options to:
  - **Show**: Brings the main window to the foreground
  - **Hide**: Hides the main window
  - **Quit**: Exits the application completely

## Basic Usage

### Starting Recording

1. Click "Start Recording" button in the Status Tab
2. Or use the hotkey (default: Ctrl+Shift+V)
3. Speak into your microphone
4. Your speech is transcribed in real-time

### Stopping Recording

- Click "Stop Recording" button
- Or use the hotkey (default: Ctrl+Shift+X)
- Or wait for automatic silence detection to stop recording

### Keyboard Shortcuts

- **Start Recording**: Ctrl+Shift+V (default)
- **Stop Recording**: Ctrl+Shift+X (default)
- Customize shortcuts in Settings tab

### How to Transcribe

1. **Open the application**. It will initialize the transcription engine, which may take a moment
2. **Click the "Start Recording" button** in the Status Tab or use the hotkey. The status will change to "Recording"
3. **Position your cursor** in any text field on your computer (e.g., a text editor, web browser, or word processor)
4. **Start speaking**
5. **Stop recording** by either:
   - Clicking the "Stop Recording" button
   - Using the stop hotkey
   - Waiting for the automatic silence detection to kick in
6. The engine will process the audio, and the transcribed text will be automatically typed into the text field where your cursor is positioned

## Features

### Auto-Start Recording

Enable auto-start to automatically begin recording when:
- A text field gains focus
- You click on a text field

Configure in Settings → Auto-Start Options

### Transcription History

View all past transcriptions in the History tab:
- Search by text content
- Export to CSV
- Clear history

### Settings

Customize VoiceClick in the Settings tab:
- Transcription model (tiny, base, small, medium, large-v2, large-v3)
- Compute device (CPU, CUDA, auto)
- Silence detection duration
- Maximum recording time
- Hotkeys
- Auto-start options
- Language selection

## Configuration Details

### Model Settings

- **Model Size**: The choice of model is a trade-off between speed and accuracy. If you find transcriptions are slow, try a smaller model. If accuracy is poor, try a larger one
- **Compute Device**: Using a `CUDA`-enabled GPU will result in significantly faster transcriptions compared to using the `CPU`. The application will automatically detect if you have a compatible GPU

### Recording Settings

- **Silence Duration**: This sets how long the application waits before stopping a recording after it detects silence. A shorter duration means the transcription will be faster, but it might cut you off if you pause while speaking
- **Maximum Recording Time**: Set a limit on how long a single recording can last (prevents accidental long recordings)

## Troubleshooting

### No Audio Input

- Check microphone permissions in Windows Settings
- Ensure microphone is not muted
- Try a different microphone device
- Verify microphone is selected in Settings tab

### "No input device found" error

- Ensure your microphone is properly connected and configured in Windows sound settings
- Check that the microphone is not being used by another application

### Application is slow or unresponsive

- If you are not using a GPU (`CUDA`), transcription can be resource-intensive, especially with larger models. Try using a smaller model size
- Close other resource-intensive applications
- Ensure you have sufficient RAM (8GB+ recommended)

### Poor transcription quality

- Ensure your microphone is close to you and the input volume is adequate
- Try using a larger, more accurate Whisper model
- Minimize background noise
- Speak clearly and at a moderate pace

### Transcription Not Appearing

- Ensure a text field is active/focused
- Check that the application is not blacklisted
- Verify text insertion method in Settings
- Make sure you have a text field selected (i.e., your cursor is active in it) before the transcription finishes

### Model Download Fails

- Check internet connection
- Try again later
- Manually download model if needed

### Text is not being pasted

- Make sure you have a text field selected (i.e., your cursor is active in it) before the transcription finishes
- Check that clipboard access is allowed
- Try restarting the application

## Advanced Usage

### Application Whitelist/Blacklist

Control which applications VoiceClick works with:
- Add apps to whitelist (only these apps will trigger auto-start)
- Add apps to blacklist (exclude these apps from auto-start)

Configure in Settings → Auto-Start Options

### Text Insertion Methods

VoiceClick uses the clipboard method by default:
- Clipboard method: Fast and reliable, temporarily uses clipboard
- Automatic fallback: If clipboard fails, tries keyboard simulation

### Hotkey Customization

Customize global hotkeys in Settings:
- Change start recording hotkey
- Change stop recording hotkey
- Enable/disable hotkeys entirely

## Support

For issues or questions:
- Check the troubleshooting section above
- Open an issue on GitHub
- Review the documentation
- Check the [Quick Start Guide](quick-start.md) for getting started quickly
- See the [Quick Reference](quick-reference.md) for common tasks
