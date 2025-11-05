"""VoiceClick Application Constants"""

# Application Info
APP_NAME = "VoiceClick"
APP_VERSION = "1.0.0"
APP_AUTHOR = "VoiceClick Development Team"

# UI Defaults
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
DEFAULT_TAB_HEIGHT = 400

# Whisper Model Options
WHISPER_MODELS = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
WHISPER_DEFAULT_MODEL = "large-v3"

# Device Options
COMPUTE_DEVICES = ["cuda", "cpu", "auto"]
COMPUTE_TYPES = ["auto", "float16", "float32"]
DEFAULT_DEVICE = "cuda"

# Recording Settings
DEFAULT_SILENCE_DURATION = 8.0
DEFAULT_MAX_RECORDING_TIME = 300
DEFAULT_AUTO_START_FOCUS = True
DEFAULT_AUTO_START_LEFT_CLICK = True
DEFAULT_ENABLE_SILENCE_AUTO_STOP = True

# History
DEFAULT_HISTORY_SIZE = 50

# Paths
CONFIG_FILENAME = "config.json"
HISTORY_FILENAME = "history.json"
