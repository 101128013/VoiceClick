# VoiceClick

**VoiceClick** is a modern, open-source voice-to-text application for Windows that allows you to transcribe your speech directly into any text field with a simple click. It's built with Python and leverages the power of OpenAI's Whisper for high-quality, real-time transcription.

![VoiceClick Screenshot](docs/screenshot.png) <!--- Placeholder for a screenshot -->

## Features

- **High-Quality Transcription**: Utilizes `faster-whisper`, a highly optimized version of OpenAI's Whisper model, for fast and accurate transcriptions.
- **System-Wide Integration**: Transcribe into any application or text field on Windows.
- **Customizable Models**: Choose from various Whisper model sizes (`tiny`, `base`, `small`, `medium`, `large`) to balance speed and accuracy.
- **Hardware Acceleration**: Supports CUDA for GPU-accelerated transcription, with a fallback to CPU.
- **Silence Detection**: Automatically stops recording after a configurable period of silence.
- **User-Friendly Interface**: A clean, tabbed interface built with PyQt6 to manage settings, view status, and browse transcription history.
- **System Tray Access**: Runs discreetly in the system tray for easy access.
- **Transcription History**: Stores your recent transcriptions for easy review and export.

## Installation

### For End Users (Recommended)

**No Python Required!** VoiceClick comes as a standalone Windows application.

1. **Download the Installer**
   - Download `VoiceClick-Setup-v1.0.0.exe` from the [Releases](https://github.com/your-username/VoiceClick/releases) page
   - Or download the portable ZIP version if you prefer no installation

2. **Run the Installer**
   - Double-click `VoiceClick-Setup-v1.0.0.exe`
   - Follow the installation wizard
   - Choose installation directory (default: `C:\Program Files\VoiceClick\`)
   - Optionally create desktop shortcut and start with Windows

3. **Launch VoiceClick**
   - Find VoiceClick in the Start Menu
   - Or use the desktop shortcut if created
   - First run will download the Whisper model (may take a few minutes)

**System Requirements:**
- Windows 10 or 11 (64-bit)
- 4GB RAM minimum (8GB recommended)
- [NVIDIA GPU with CUDA support](https://developer.nvidia.com/cuda-gpus) (optional, recommended for best performance)
- Internet connection (for initial model download)

### For Developers

If you want to run from source or contribute to development:

**Prerequisites:**
- Windows 10 or 11
- Python 3.9+
- [NVIDIA GPU with CUDA support](https://developer.nvidia.com/cuda-gpus) (recommended)
- [Git](https://git-scm.com/downloads)

**Steps:**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/VoiceClick.git
   cd VoiceClick
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

### Building from Source

To create your own executable, see [docs/build.md](docs/build.md) for detailed instructions.

Quick start:
1. Install PyInstaller: `pip install pyinstaller`
2. Run build script: `python scripts/build.py`
3. Find output in `dist/` directory

## Documentation

- **[User Guide](docs/user-guide.md)** - Complete guide for using VoiceClick
- **[Quick Start](docs/quick-start.md)** - Get started in minutes
- **[Quick Reference](docs/quick-reference.md)** - Quick reference card
- **[Build Guide](docs/build.md)** - Building from source
- **[Deployment Guide](docs/deployment.md)** - Distribution and deployment

## How It Works

VoiceClick runs in the background and can be activated to start recording your voice. When you stop recording (either manually or via silence detection), the captured audio is processed by the Whisper model, and the resulting text is automatically pasted into the currently active text field.

The core components are:
- **`app.py`**: The main entry point that launches the application.
- **`src/core/engine.py`**: The transcription engine that handles audio recording and processing.
- **`src/ui/main_window.py`**: The main application window built with PyQt6.
- **`src/config/settings.py`**: Manages user settings and configurations.

## Contributing

Contributions are welcome! If you have ideas for new features, bug fixes, or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
