# Voice Click - Voice-to-Text Application

**Advanced voice transcription with auto-start, auto-stop, and GPU acceleration**

---

## 🚀 Quick Start

1. **Run the application:**
   ```powershell
   python voice_click_minimal.py
   ```

2. **Usage:**
   - Left-click into any text field → Recording starts automatically
   - Speak naturally
   - Pause for 8 seconds → Auto-stops and pastes text
   - Or middle-click to stop manually
   - Right-click to cancel

---

## 📁 Files in This Folder

### Main Application
- **`voice_click_minimal.py`** - Main application (run this!)

### Test & Verification Scripts
- **`test_voice_click.py`** - Unit tests (13 tests)
- **`final_validation.py`** - Integration tests (10 tests)
- **`startup_test.py`** - Startup verification
- **`check_cuda.py`** - GPU/CUDA check
- **`test_model_loading.py`** - Model download test

### Documentation
- **`README.md`** - This file
- **`VOICE_CLICK_CONFIG.md`** - Configuration guide
- **`IMPLEMENTATION_SUMMARY.md`** - Technical documentation

---

## ⚙️ Configuration

Current settings (optimized for RTX 5060Ti):

```python
# Model (edit voice_click_minimal.py to change)
WHISPER_MODEL = "large-v3"          # Best quality
WHISPER_DEVICE = "cuda"             # GPU (auto-fallback to CPU)
WHISPER_COMPUTE_TYPE = "float16"    # RTX-optimized

# Auto-stop
SILENCE_DURATION = 8.0              # Seconds of silence before auto-stop
ENABLE_SILENCE_AUTO_STOP = True     # Auto-stop enabled
ENABLE_MANUAL_STOP = True           # Middle-click also works

# Safety
IGNORE_FULLSCREEN_GAMES = True      # Skip games
IGNORE_PASSWORD_FIELDS = True       # Skip passwords
```

---

## 🧪 Testing

Run tests to verify everything works:

```powershell
# Quick validation
python final_validation.py

# Full unit tests
python test_voice_click.py

# Check GPU
python check_cuda.py
```

All tests should pass (23/23).

---

## 📝 Logs & History

- **Log file**: `C:\Users\SUPER\.voice_click.log`
- **History file**: `C:\Users\SUPER\.voice_click_history.json`

These files are stored in your home directory (outside this folder).

---

## 🔧 Troubleshooting

**Script won't start?**
- Check the log file: `C:\Users\SUPER\.voice_click.log`
- Run: `python final_validation.py`

**Slow transcription?**
- Model is running on CPU (CUDA unavailable)
- Quality is still excellent, just slower

**Recording won't stop?**
- Wait 8 seconds of silence
- Or middle-click to stop manually
- Or right-click to cancel

---

## 📊 Features

✅ GPU acceleration (RTX 5060Ti optimized)
✅ Large-v3 model (best quality)
✅ 8-second auto-stop on silence
✅ Focus validation (paste safety)
✅ Fullscreen game detection
✅ Password field avoidance
✅ Comprehensive error handling
✅ Enhanced logging system
✅ Auto-fallback to CPU
✅ Recording history
✅ Volume monitoring
✅ Multiple auto-start methods

---

## 🎯 System Requirements

- Windows 10/11
- Python 3.8+
- NVIDIA GPU (optional, auto-fallback to CPU)
- Microphone
- Required packages (auto-installed):
  - faster-whisper
  - numpy
  - sounddevice
  - pynput
  - keyboard
  - pyperclip
  - pywin32

---

## 📞 Support

For issues:
1. Check console output
2. Check log file: `C:\Users\SUPER\.voice_click.log`
3. Run diagnostic: `python final_validation.py`
4. Run tests: `python test_voice_click.py`

---

**Version**: 2.0 (2025-11-05)
**Status**: Production Ready ✅
**Tests**: 23/23 Passing ✅
