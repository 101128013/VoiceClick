# VoiceClick - Professional Voice-to-Text Application

VoiceClick is an advanced Windows 11 application that enables users to transcribe speech to text in real-time using OpenAI's Whisper model with GPU acceleration.

## Features

- **Advanced ML Integration**: Uses OpenAI Whisper large-v3 model with GPU acceleration
- **Smart Detection**: Multi-method text field detection (cursor type, class names, window focus)
- **Accessibility Features**: Auto-start on focus, left-click, middle-click toggle
- **Robust Error Handling**: Comprehensive logging, fallback methods for text insertion
- **Performance Monitoring**: Real-time volume monitoring with visual feedback
- **Data Persistence**: Transcription history with JSON storage
- **Modern UI**: Native Windows 11 PyQt6 interface with system tray integration

## System Requirements

- Windows 11
- Python 3.9+ (if running from source)
- 4GB RAM minimum (8GB recommended)
- NVIDIA GPU with CUDA support (optional, but recommended)

## Installation

### From Installer (Recommended)

1. Download `Voice-Click-Setup.exe` from the latest release
2. Run the installer
3. Follow the setup wizard
4. VoiceClick will appear in your Start Menu and Desktop

### From Source

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python src/main.py`

## Usage

1. Launch VoiceClick from Start Menu or Desktop
2. Configure settings (model, device, hotkeys)
3. Use middle-click to toggle recording in any text field
4. Speak clearly and naturally
5. Transcribed text will be automatically inserted

## Configuration

Settings are saved in `~/.voice_click/config.json` and can be modified through the Settings tab in the application.

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for developer setup and contribution guidelines.

## License

MIT License - See LICENSE file for details

## Support

For issues, feature requests, or questions, please open an issue on GitHub.
