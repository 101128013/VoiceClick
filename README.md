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

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the progress monitor (optional)
python monitor.py

# Start development
python app.py
```

## Project Status

- **Phase 1**: Setup & Architecture ✓ Complete (4/4)
- **Phase 2**: UI Development ⏳ In Progress (Task 5: Main Window)
- **Phase 3**: Testing & Packaging ⏹️ Pending
- **Phase 4**: Documentation & Release ⏹️ Pending

**Overall**: 4/30 tasks complete (13%)

See `PROJECT_ROADMAP.md` for complete roadmap and `docs/` for detailed documentation.

## Project Structure

```
VoiceClick/
├── app.py                   # Main application entry point
├── monitor.py              # Development progress widget
├── requirements.txt        # Python dependencies
├── PROJECT_ROADMAP.md      # 30-task development roadmap
├── src/
│   ├── core/              # Core modules (engine, detection, history)
│   ├── ui/                # UI components (main window, tabs, widgets)
│   ├── config/            # Configuration system
│   └── resources/         # Icons and assets
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── examples/              # Example code
└── .github/               # CI/CD workflows
```

## System Requirements

- Windows 11
- Python 3.9+ (if running from source)
- 4GB RAM minimum (8GB recommended)
- NVIDIA GPU with CUDA support (optional, but recommended)

## Installation from Source

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python app.py`

## Development Guide

1. Read `PROJECT_ROADMAP.md` - understand the 30-task plan
2. Review `docs/` - architecture and setup guides
3. Check `src/core/` - core modules
4. Start Phase 2 - UI development tasks

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, see documentation in the `docs/` folder.
