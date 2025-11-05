# VoiceClick Developer Documentation

## Architecture Overview

### Project Structure
```
VoiceClick/
├── src/
│   ├── core/              # Core business logic
│   │   ├── engine.py      # Main voice recognition engine
│   │   ├── history.py     # Transcription history management
│   │   └── text_detector.py # Audio detection
│   ├── ui/                # User interface
│   │   ├── main_window.py # Main PyQt6 window
│   │   ├── progress_manager.py # Development progress tracking
│   │   └── tabs/          # UI tabs
│   ├── config/            # Configuration
│   │   ├── settings.py    # User settings management
│   │   └── constants.py   # Application constants
│   └── resources/         # Application resources
│       └── icons/         # Icons and images
├── tests/                 # Unit tests
├── docs/                  # Documentation
└── requirements.txt       # Python dependencies
```

### Core Components

#### 1. VoiceClickEngine (`src/core/engine.py`)
Manages audio recording and speech-to-text transcription using Whisper.

**Key Methods**:
- `start_recording()` - Begin audio capture
- `stop_recording()` - End recording and process audio
- `transcribe()` - Convert audio to text using Whisper model
- `get_supported_devices()` - List available audio devices

**Signals**:
- `recording_started` - Emitted when recording begins
- `recording_stopped` - Emitted when recording ends
- `transcription_complete` - Emitted with transcribed text
- `error_occurred` - Emitted on errors

#### 2. TranscriptionHistory (`src/core/history.py`)
Manages storage and retrieval of transcription records.

**Key Methods**:
- `add_record(text, source)` - Store new transcription
- `get_all()` - Retrieve all records
- `search(keyword)` - Search transcriptions
- `export(format)` - Export records in various formats
- `delete(record_id)` - Remove transcription record

**Storage**: JSON-based, located in `%APPDATA%\VoiceClick\history.json`

#### 3. Settings (`src/config/settings.py`)
Persistent application configuration management.

**Supported Settings**:
- `model` - Whisper model size (tiny, base, small, medium, large)
- `device` - Computation device (auto, cuda, cpu)
- `language` - Default language for transcription
- `audio_device` - Input device selection
- `output_format` - Text output format

**Persistence**: `%APPDATA%\VoiceClick\settings.json`

#### 4. Main Window (`src/ui/main_window.py`)
PyQt6 GUI application main window.

**Features**:
- Tab-based interface (Status, Settings, History)
- System tray integration
- Keyboard shortcuts
- Signal/slot connections to engine

### Development Phases

#### Phase 1: Setup & Architecture (Tasks 1-4)
- Repository initialization
- Requirements definition
- Modular architecture
- Configuration system

#### Phase 2: UI Development (Tasks 5-10)
- Main window design
- Tab implementations
- System tray integration
- Menu and toolbar setup

#### Phase 3: Integration (Tasks 11-14)
- Engine integration
- Icon creation
- Unit testing
- Build configuration

#### Phase 4: Testing & Packaging (Tasks 15-20)
- Executable building
- VM testing
- Installer creation
- Portable packaging

#### Phase 5: Documentation & Release (Tasks 21-30)
- User documentation
- Developer documentation
- CI/CD setup
- Beta testing
- Official release

## Development Setup

### Prerequisites
- Python 3.10+
- pip package manager
- Git for version control

### Installation for Development

```bash
# Clone repository
git clone https://github.com/101128013/VoiceClick.git
cd VoiceClick

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8
```

### Running in Development

```bash
# Run main application
python app.py

# Run tests
pytest tests/ -v --cov=src

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/
```

### Building Distribution

```bash
# Create PyInstaller executable
pyinstaller VoiceClick.spec --clean --noconfirm

# Output: dist/VoiceClick.exe

# Create NSIS installer (Windows only)
makensis.exe installer/VoiceClick-installer.nsi

# Output: VoiceClick-1.0.0-installer.exe
```

## Testing

### Unit Tests
Tests are located in `tests/` directory:
- `test_engine.py` - Engine functionality tests
- `test_history.py` - History management tests
- `test_settings.py` - Settings persistence tests
- `test_progress_manager.py` - Progress tracking tests

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_engine.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Coverage Report
Generated HTML coverage report in `htmlcov/` directory after running with `--cov-report=html`.

### Test Categories

**Unit Tests**: Test individual functions and classes
- Mock external dependencies
- Test error handling
- Validate return values

**Integration Tests**: Test component interactions
- Engine + History
- Settings + UI updates
- Signals/slots connections

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints where applicable
- Maximum line length: 100 characters
- Use black for formatting: `black src/`

### Commit Messages
Format: `<type>: <subject>`

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style changes
- `refactor` - Code refactoring
- `test` - Test additions/changes
- `chore` - Build/dependency changes

Example: `feat: add real-time translation support`

### Pull Request Process
1. Create feature branch: `git checkout -b feature/description`
2. Make changes and commit
3. Run tests: `pytest tests/ -v`
4. Format code: `black src/`
5. Push to GitHub
6. Create pull request with description
7. Wait for CI/CD and code review

## API Reference

### VoiceClickEngine

```python
from src.core.engine import VoiceClickEngine

engine = VoiceClickEngine(model="base", device="auto")

# Start recording
engine.start_recording()

# Stop and transcribe
text = engine.stop_recording()

# Get device information
devices = engine.get_supported_devices()
```

### TranscriptionHistory

```python
from src.core.history import TranscriptionHistory

history = TranscriptionHistory()

# Add transcription
history.add_record("Hello world", source="microphone")

# Search
results = history.search("hello")

# Export
history.export(format="txt", filepath="export.txt")
```

### Settings

```python
from src.config.settings import Settings

settings = Settings()

# Get setting
model = settings.get("model")

# Set and save
settings.set("model", "medium")
settings.save()

# Validate
is_valid = settings.validate()
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**Import Errors**: Ensure Python path includes project root
```python
import sys
sys.path.insert(0, '/path/to/VoiceClick')
```

**PyQt6 Issues**: Ensure PyQt6 is properly installed
```bash
pip install --upgrade PyQt6
```

**Whisper Model Issues**: Check model cache
```bash
# Windows
%APPDATA%\VoiceClick\models

# Linux
~/.local/share/VoiceClick/models

# Mac
~/Library/Application Support/VoiceClick/models
```

## Performance Optimization

### Recommended Settings by Use Case

**Fastest Performance**:
- Model: `tiny`
- Device: `cuda` (if available)
- Language: Specific language only

**Best Accuracy**:
- Model: `large`
- Device: `cuda` (if available)
- Pre-process audio before recording

**Balanced**:
- Model: `base`
- Device: `auto`
- Standard usage patterns

### Memory Profiling

```bash
pip install memory-profiler
python -m memory_profiler src/core/engine.py
```

## CI/CD Pipeline

### GitHub Actions
- Automated testing on push
- Code coverage reporting
- Automated builds
- Release automation

Workflow file: `.github/workflows/ci.yml`

### Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

## Release Process

### Version Numbering
Uses semantic versioning: `MAJOR.MINOR.PATCH`

### Release Steps
1. Update version in `src/config/constants.py`
2. Update CHANGELOG.md
3. Tag release: `git tag v1.0.0`
4. Push tags: `git push --tags`
5. Create GitHub release with notes
6. Upload distribution files

## Support

- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: dev@voiceclick.dev

## License

MIT License - See LICENSE.txt

---

**Last Updated**: November 5, 2025
**VoiceClick Version**: 1.0.0
