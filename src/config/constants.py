"""
VoiceClick Application Constants.

This module defines static constant values used throughout the application,
such as application metadata, UI defaults, and configuration options.
"""

# --- Application Information ---
APP_NAME = "VoiceClick"
APP_VERSION = "1.0.0"
APP_AUTHOR = "VoiceClick Development Team"

# --- UI Defaults ---
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
DEFAULT_TAB_HEIGHT = 400

# --- Whisper Model Options ---
# Available models for transcription.
WHISPER_MODELS = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
WHISPER_DEFAULT_MODEL = "large-v3"

# --- Device and Compute Options ---
# Hardware acceleration options for the Whisper model.
COMPUTE_DEVICES = ["cuda", "cpu", "auto"]
COMPUTE_TYPES = ["auto", "float16", "float32", "int8"]
DEFAULT_DEVICE = "cuda"

# --- Recording Settings ---
# Default values for audio recording behavior.
DEFAULT_SILENCE_DURATION = 8.0  # Seconds of silence before auto-stopping.
DEFAULT_MAX_RECORDING_TIME = 300  # Maximum recording duration in seconds.
DEFAULT_AUTO_START_FOCUS = True  # Start recording when a text field is focused.
DEFAULT_AUTO_START_LEFT_CLICK = True  # Start recording on left click.
DEFAULT_ENABLE_SILENCE_AUTO_STOP = True  # Enable auto-stop on silence.

# --- History Settings ---
# Default number of transcription records to store.
DEFAULT_HISTORY_SIZE = 50

# --- Hotkey Settings ---
# Default global hotkey combinations
DEFAULT_START_RECORDING_HOTKEY = "ctrl+shift+v"
DEFAULT_STOP_RECORDING_HOTKEY = "ctrl+shift+x"
DEFAULT_ENABLE_HOTKEYS = True

# --- File Paths ---
# Default filenames for configuration and history data.
CONFIG_FILENAME = "config.json"
HISTORY_FILENAME = "history.json"
LOG_FILENAME = "voiceclick.log"
