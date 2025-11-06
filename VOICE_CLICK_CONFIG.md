# Voice Click - Configuration Guide

## Quick Start Configuration

Edit the top of `voice_click_minimal.py` to customize behavior:

---

## 🎯 **Model Settings (GPU Acceleration)**

```python
WHISPER_MODEL = "medium"       # Options: tiny, base, small, medium, large-v2, large-v3
WHISPER_DEVICE = "cuda"        # "cuda" for GPU, "cpu" for CPU
WHISPER_COMPUTE_TYPE = "float16"  # "float16" (GPU), "int8" (CPU), "float32"
```

### Recommended Configurations:

**High Performance (GPU Required):**
- Model: `medium` or `large-v2`
- Device: `cuda`
- Compute Type: `float16`
- Best accuracy, faster transcription (~2-5x speed)

**Balanced (CPU):**
- Model: `base` or `small`
- Device: `cpu`
- Compute Type: `int8`
- Good accuracy, reasonable speed

**Fast (CPU):**
- Model: `tiny` or `base`
- Device: `cpu`
- Compute Type: `int8`
- Lower accuracy, fastest on CPU

---

## 🚀 **Auto-Start Settings (Accessibility)**

```python
AUTO_START_ON_FOCUS = True          # Auto-start when text field gets focus
AUTO_START_ON_LEFT_CLICK = True     # Auto-start on left-click into text field
AUTO_START_DELAY = 0.12             # Delay (seconds) for focus to settle
IGNORE_PASSWORD_FIELDS = True       # Skip password fields
IGNORE_FULLSCREEN_GAMES = True      # Skip fullscreen games/apps
```

### Use Cases:

**Maximum Accessibility (No Keyboard):**
- `AUTO_START_ON_LEFT_CLICK = True` ← **Recommended for you**
- `AUTO_START_ON_FOCUS = True` (optional, may be too aggressive)
- Just click into a text box and start speaking!

**Conservative (Avoid Accidental Starts):**
- `AUTO_START_ON_LEFT_CLICK = False`
- `AUTO_START_ON_FOCUS = False`
- Use middle-click only

**Gaming Setup:**
- `IGNORE_FULLSCREEN_GAMES = True` ← Prevents recording during games
- `IGNORE_PASSWORD_FIELDS = True` ← Security

---

## ⏹️ **Auto-Stop Settings (When to Stop Recording)**

```python
ENABLE_SILENCE_AUTO_STOP = True     # Auto-stop when you stop speaking
SILENCE_DURATION = 1.5              # Seconds of silence before auto-stop
ENABLE_MANUAL_STOP = True           # Allow middle-click to stop
MAX_RECORDING_TIME = 300            # Max recording (seconds)
```

### Recommended Settings:

**Forgiving Auto-Stop (Best for Natural Speech):**
- `ENABLE_SILENCE_AUTO_STOP = True`
- `SILENCE_DURATION = 1.5` to `2.5` seconds
- `ENABLE_MANUAL_STOP = True` (safety override)

**Auto-Stop Only (No Manual Control):**
- `ENABLE_SILENCE_AUTO_STOP = True`
- `SILENCE_DURATION = 1.0` to `1.5` seconds
- `ENABLE_MANUAL_STOP = False` (forces auto-stop)

**Manual Stop Only (You Control When):**
- `ENABLE_SILENCE_AUTO_STOP = False`
- `ENABLE_MANUAL_STOP = True`
- Middle-click when done speaking

**Both Methods (Most Flexible):** ← **Recommended**
- `ENABLE_SILENCE_AUTO_STOP = True`
- `SILENCE_DURATION = 2.0` seconds (forgiving)
- `ENABLE_MANUAL_STOP = True`
- Auto-stops after pause OR middle-click to stop early

---

## 🔒 **Security & Safety**

```python
IGNORE_PASSWORD_FIELDS = True       # Don't auto-record in password fields
REQUIRE_TEXT_FIELD = True           # Only start in text fields
```

**Important Notes:**
- Password field detection uses heuristics (not 100% reliable)
- Transcribed text is briefly in clipboard (security consideration)
- Focus validation prevents paste into wrong window
- Always review sensitive transcriptions before pasting

---

## 📊 **Detection Thresholds**

```python
VOLUME_THRESHOLD = 0.02             # Minimum volume for speech
```

- **Too many false starts?** Increase to `0.03` or `0.04`
- **Not detecting quiet speech?** Decrease to `0.015` or `0.01`

---

## 🎮 **Advanced Customization**

### Fullscreen Game Detection

The script detects fullscreen apps by:
1. Window size (fullscreen = screen size)
2. Common game engine classes (Unity, Unreal, SDL)
3. Game keywords in window titles

Add your own games to the detection in `is_fullscreen_game()`:
```python
game_keywords = [
    'your_game_name',
    'custom_app',
]
```

### Text Field Detection Score

In `is_text_field()`, change detection threshold:
```python
detected = score >= 40  # Default: 40 points required
```

- **Higher (50-60):** More conservative, fewer false positives
- **Lower (30-35):** More aggressive, catches more fields

---

## 🧪 **Testing Your Configuration**

1. **Test GPU:** Run the script. If it fails to load model:
   - Check CUDA installation: `nvidia-smi` in terminal
   - Try `WHISPER_DEVICE = "cpu"` and `WHISPER_COMPUTE_TYPE = "int8"`

2. **Test Auto-Start:** 
   - Open Notepad
   - Click into the text area
   - Should auto-start recording (if enabled)

3. **Test Auto-Stop:**
   - Start recording
   - Speak, then stay silent for `SILENCE_DURATION` seconds
   - Should auto-stop

4. **Test Fullscreen Detection:**
   - Open a fullscreen game
   - Click anywhere → should NOT start recording

---

## 📝 **Configuration Examples**

### Example 1: Maximum Accessibility (No Keyboard)
```python
# Model
WHISPER_MODEL = "medium"
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"

# Auto-start
AUTO_START_ON_FOCUS = False          # Too aggressive for most
AUTO_START_ON_LEFT_CLICK = True      # ← Main trigger
AUTO_START_DELAY = 0.15
IGNORE_PASSWORD_FIELDS = True
IGNORE_FULLSCREEN_GAMES = True

# Auto-stop
ENABLE_SILENCE_AUTO_STOP = True
SILENCE_DURATION = 2.0               # Forgiving
ENABLE_MANUAL_STOP = False           # Force auto-stop only
```

### Example 2: Conservative (Avoid Accidents)
```python
# Model
WHISPER_MODEL = "base"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

# Auto-start
AUTO_START_ON_FOCUS = False
AUTO_START_ON_LEFT_CLICK = False
AUTO_START_DELAY = 0.12
IGNORE_PASSWORD_FIELDS = True
IGNORE_FULLSCREEN_GAMES = True

# Auto-stop
ENABLE_SILENCE_AUTO_STOP = False
SILENCE_DURATION = 1.5
ENABLE_MANUAL_STOP = True            # Manual control only
```

### Example 3: Balanced (Your Use Case)
```python
# Model - GPU for speed
WHISPER_MODEL = "medium"
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"

# Auto-start - Left-click only
AUTO_START_ON_FOCUS = False          # Avoid accidental starts
AUTO_START_ON_LEFT_CLICK = True      # ← Click and speak
AUTO_START_DELAY = 0.12
IGNORE_PASSWORD_FIELDS = True
IGNORE_FULLSCREEN_GAMES = True

# Auto-stop - Both methods
ENABLE_SILENCE_AUTO_STOP = True      # ← Stops when you pause
SILENCE_DURATION = 2.0               # Forgiving (2 seconds)
ENABLE_MANUAL_STOP = True            # Can still middle-click to stop
```

---

## 🚨 **Troubleshooting**

### "Failed to load model" (GPU)
- **Cause:** CUDA not installed or incompatible
- **Fix:** Set `WHISPER_DEVICE = "cpu"` and `WHISPER_COMPUTE_TYPE = "int8"`

### Recording starts accidentally
- **Cause:** Detection too sensitive
- **Fix:** Set `AUTO_START_ON_FOCUS = False`, keep only `AUTO_START_ON_LEFT_CLICK = True`

### Recording doesn't stop automatically
- **Cause:** Silence detection not triggering
- **Fix:** Increase `VOLUME_THRESHOLD` to `0.03` or `0.04`

### Paste goes to wrong window
- **Cause:** Focus changed during transcription
- **Fix:** Focus validation already implemented - text will be in clipboard, paste manually with Ctrl+V

### Doesn't detect my text editor
- **Cause:** Uncommon class name or window title
- **Fix:** Check logs for window details, add to `text_classes` or `apps_and_keywords` in `is_text_field()`

---

## 📌 **Your Recommended Setup**

Based on your needs (no keyboard access, frequent use):

```python
# GPU for speed (if available)
WHISPER_MODEL = "medium"
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"

# Left-click to start (most accessible)
AUTO_START_ON_FOCUS = False
AUTO_START_ON_LEFT_CLICK = True
AUTO_START_DELAY = 0.15
IGNORE_PASSWORD_FIELDS = True
IGNORE_FULLSCREEN_GAMES = True

# Auto-stop after pause (forgiving)
ENABLE_SILENCE_AUTO_STOP = True
SILENCE_DURATION = 2.0
ENABLE_MANUAL_STOP = True

# Safety
REQUIRE_TEXT_FIELD = True
VOLUME_THRESHOLD = 0.02
MAX_RECORDING_TIME = 300
```

**Workflow:**
1. Click into any text field → Recording starts automatically
2. Speak naturally
3. Pause for 2 seconds → Auto-stops and pastes
4. Or middle-click to stop early if needed

---

## 💡 **Tips**

- Start with default settings, adjust based on experience
- Check console logs to see detection details
- Test in different apps (browser, Word, Discord, etc.)
- Adjust `SILENCE_DURATION` based on your speaking pace
- Use `ENABLE_MANUAL_STOP = True` as a safety override

