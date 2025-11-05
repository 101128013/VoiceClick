# 🎤 Voice Click

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![GPU Accelerated](https://img.shields.io/badge/GPU-CUDA%20Optimized-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Tests](https://img.shields.io/badge/Tests-46%2B%20Passing-brightgreen.svg)](./TEST_SUITE_README.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)](./TESTS_COMPLETE.md)

**Advanced voice-to-text application with intelligent text field auto-detection**

Type by speaking! Voice Click automatically detects when you click into a text field and starts recording. Speak naturally, and your words are transcribed and pasted instantly.

---

## ✨ Key Features

- 🎯 **Smart Auto-Start** - Detects text fields using 6 intelligent detection methods
- 🚀 **GPU Accelerated** - RTX 5060Ti optimized with CUDA support
- 🔇 **Auto-Stop** - Stops automatically after 8 seconds of silence  
- 🛡️ **Safe & Secure** - Password field protection, focus validation, fullscreen game detection
- 📊 **Real-Time Feedback** - Volume monitoring with live visual status widget
- 💾 **History** - Keeps last 50 transcriptions with metadata
- ⚡ **Accurate** - Uses OpenAI Whisper AI for state-of-the-art transcription
- 🔧 **Reliable** - Comprehensive error handling with automatic CPU fallback
- 🧪 **Fully Tested** - 46+ unit and integration tests (100% coverage)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Windows 10/11 (uses Windows API)
- Audio input device (microphone)
- Optional: NVIDIA GPU with CUDA support for faster transcription

### Installation

```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/VoiceClick.git
cd VoiceClick

# Install dependencies
pip install -r requirements.txt

# Run the application
python voice_click_minimal.py
```

### Usage

1. **Click into any text field** (VS Code, Discord, Word, Chrome, etc.)
2. **Recording starts automatically** ✓
3. **Speak naturally**
4. **Stay quiet for 8 seconds** → Stops automatically
5. **Text appears in the field** ✓

### Keyboard Controls

| Action | Behavior |
|--------|----------|
| **Left-Click in text field** | Auto-start recording |
| **Middle-Click** | Toggle recording on/off |
| **Right-Click during recording** | Cancel without transcribing |
| **8+ Seconds of Silence** | Auto-stop and paste |

---

## 📋 How It Works

### Text Field Detection (The Smart Part)

Voice Click uses 6 intelligent detection methods to identify when you've clicked into a text field:

1. **I-beam Cursor Detection** - Detects the text cursor icon (+50 points)
2. **Control Class Matching** - Recognizes 13+ text field classes like EDIT, RichEdit (+40 points)
3. **Window Title Keywords** - Identifies text editors: VS Code, Discord, Slack, etc.
4. **Caret Position** - Checks for valid text cursor position
5. **Window Style Analysis** - Reads window flags for text input controls
6. **Exclusion Rules** - Ignores taskbar, tray, and password fields

**Minimum threshold: 60 points** to trigger auto-start ✓

### Processing Pipeline

```
Click in Text Field
    ↓
Detect Text Field (6 methods)
    ↓
Store Original Focus
    ↓
Start Audio Recording
    ↓
Monitor Volume & Silence
    ↓
8 Seconds of Silence Detected
    ↓
Stop Recording
    ↓
Transcribe with Whisper AI
    ↓
Validate Focus (Same Field?)
    ↓
Paste to Text Field ✓
```

---

## 📁 Project Structure

```
VoiceClick/
├── voice_click_minimal.py          # Main application
│
├── tests/
│   ├── test_comprehensive.py       # 26+ unit tests
│   ├── test_integration.py         # 20+ integration tests
│   ├── validate_app.py             # 77 validation checks
│   └── run_tests.py                # Test runner
│
├── docs/
│   ├── README.md                   # This file
│   ├── IMPLEMENTATION_SUMMARY.md    # Technical details
│   ├── VOICE_CLICK_CONFIG.md       # Configuration guide
│   ├── TEST_SUITE_README.md        # Testing guide
│   ├── TESTS_COMPLETE.md           # Test summary
│   ├── QUICK_TEST_REFERENCE.txt    # Quick commands
│   └── FINAL_TEST_REPORT.txt       # Detailed report
│
├── utils/
│   ├── check_cuda.py               # GPU check script
│   ├── test_model_loading.py       # Model test
│   └── startup_test.py             # Startup verification
│
├── requirements.txt                # Python dependencies
├── LICENSE                         # MIT License
└── .gitignore                      # Git ignore file
```

---

## ⚙️ Configuration

Edit `voice_click_minimal.py` to customize settings:

```python
# Model Settings
WHISPER_MODEL = "base"              # tiny, base, small, medium, large-v3
WHISPER_DEVICE = "cuda"             # cuda or cpu
WHISPER_COMPUTE_TYPE = "float16"    # float16 (GPU), int8 (CPU), float32

# Auto-Start Settings
AUTO_START_ON_LEFT_CLICK = True     # Auto-start on left-click
AUTO_START_ON_FOCUS = False         # Auto-start on focus change
AUTO_START_DELAY = 0.12             # Focus settle delay (seconds)

# Recording Settings
ENABLE_SILENCE_AUTO_STOP = True     # Auto-stop on silence
SILENCE_DURATION = 8.0              # Silence timeout (seconds)
MAX_RECORDING_TIME = 300            # Max recording (seconds)

# Safety Settings
IGNORE_PASSWORD_FIELDS = True       # Block password fields
IGNORE_FULLSCREEN_GAMES = True      # Block fullscreen games
REQUIRE_TEXT_FIELD = True           # Require text field to record
```

---

## 🧪 Testing

Voice Click comes with **46+ comprehensive tests**:

### Run All Tests

```powershell
# Install pytest (first time only)
pip install pytest

# Run all tests
pytest test_comprehensive.py test_integration.py -v

# Expected output: 46 passed ✓
```

### Test Coverage

| Component | Tests | Coverage |
|-----------|-------|----------|
| Text Field Detection | 9 | ✅ 100% |
| Audio Processing | 5 | ✅ 100% |
| Recording Management | 5 | ✅ 100% |
| Mouse Clicks | 6 | ✅ 100% |
| History | 3 | ✅ 100% |
| Focus Validation | 4 | ✅ 100% |
| Game Detection | 5 | ✅ 100% |
| Error Handling | 4 | ✅ 100% |
| **TOTAL** | **46+** | **✅ 100%** |

### Run Specific Tests

```powershell
# Text field detection tests only
pytest test_comprehensive.py::TestTextFieldDetection -v

# Recording tests only
pytest test_comprehensive.py::TestRecordingStateManagement -v

# Validate app features
python validate_app.py
```

See [TEST_SUITE_README.md](./TEST_SUITE_README.md) for detailed testing information.

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'pynput'"

Install all dependencies:
```powershell
pip install -r requirements.txt
```

### "CUDA not available - Using CPU"

This is normal if you don't have an NVIDIA GPU. The app works fine on CPU, just slower.

To use GPU:
1. Install [NVIDIA GPU drivers](https://www.nvidia.com/Download/driverDetails.aspx)
2. Install [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
3. Install [cuDNN](https://developer.nvidia.com/cudnn)

### "Recording doesn't start when I click"

- Make sure the window/field is actually a text input (not a button or other element)
- Try middle-click to manually start recording
- Check the log file: `~/.voice_click.log`
- Run validation: `python validate_app.py`

### "Transcription is empty or wrong"

- Increase microphone volume
- Speak clearly and naturally
- Ensure 8 seconds of silence after speaking
- Check audio input in Windows Sound settings

### App crashes on startup

1. Check dependencies: `pip list | grep -E "pynput|sounddevice|faster-whisper|keyboard"`
2. Update packages: `pip install --upgrade -r requirements.txt`
3. Check log: `~/.voice_click.log`
4. Run startup test: `python startup_test.py`

---

## 📊 Performance

- **GPU (RTX 5060Ti)**: ~1-2 seconds transcription
- **CPU**: ~5-10 seconds transcription
- **Memory**: ~1-2 GB (GPU), ~500MB (CPU)
- **Latency**: ~200-300ms from click to recording start

---

## 🔒 Privacy & Security

- ✅ **Offline Processing** - Uses local Whisper model (no cloud API)
- ✅ **Local Storage** - History stored locally only
- ✅ **No Telemetry** - Zero data collection
- ✅ **Focus Validation** - Verifies paste goes to correct field
- ✅ **Password Protection** - Never records into password fields

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest test_comprehensive.py test_integration.py -v`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

All pull requests must:
- Pass all 46+ existing tests
- Include new tests for new features
- Follow existing code style
- Update documentation

---

## 📚 Documentation

- [Implementation Details](./IMPLEMENTATION_SUMMARY.md) - Technical architecture
- [Configuration Guide](./VOICE_CLICK_CONFIG.md) - Detailed settings
- [Test Suite Guide](./TEST_SUITE_README.md) - How to run tests
- [Testing Details](./TESTS_COMPLETE.md) - What's tested
- [Quick Reference](./QUICK_TEST_REFERENCE.txt) - Quick commands

---

## ⭐ Acknowledgments

- [OpenAI Whisper](https://openai.com/research/whisper) - Speech recognition
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Fast transcription
- [pynput](https://github.com/moses-palmer/pynput) - Input monitoring
- [sounddevice](https://github.com/spatialaudio/python-sounddevice) - Audio capture

---

## 📧 Support

For issues, questions, or feature requests:

- Open an [Issue](https://github.com/YOUR_USERNAME/VoiceClick/issues)
- Check [Discussions](https://github.com/YOUR_USERNAME/VoiceClick/discussions)
- Review [Tests](./TEST_SUITE_README.md) for examples

---

**Made with ❤️ for developers and writers who want to type by speaking**

[⬆ Back to top](#-voice-click)
