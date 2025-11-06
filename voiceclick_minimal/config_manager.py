from pathlib import Path
import json
import logging
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger('VoiceClick')

# --- Configuration Schema (Pydantic) ---

class VoiceClickConfig(BaseModel):
    """Defines the structure and default values for VoiceClick settings."""
    
    # Mouse Shake Detection
    mouse_shake_threshold_px: int = Field(50, description="Total distance in pixels for mouse shake detection.")
    mouse_shake_time_ms: int = Field(100, description="Time window in milliseconds for mouse shake detection.")
    
    # Core Functionality
    require_text_field: bool = Field(True, description="Require text field focus to start recording.")
    volume_threshold: float = Field(0.02, description="Minimum volume (RMS) to consider as speech.")
    enable_audio_feedback: bool = Field(True, description="Enable audio beeps for start, stop, and status pulses.")
    
    # Whisper Model Configuration
    whisper_model: str = Field("base", description="Whisper model size (tiny, base, small, medium, large-v2, large-v3).")
    whisper_device: str = Field("cpu", description="Device for Whisper (cuda or cpu).")
    whisper_compute_type: str = Field("int8", description="Compute type (float16, int8, float32).")
    transcription_language: str = Field("en", description="Language for transcription (e.g., en, tr, de).")
    
    # Auto-start options
    auto_start_on_focus: bool = Field(False, description="Start recording automatically when a text field receives focus.")
    auto_start_on_left_click: bool = Field(True, description="Start recording when user left-clicks into a text field.")
    auto_start_delay: float = Field(0.12, description="Delay (s) after focus/click to allow caret/focus to settle.")
    ignore_password_fields: bool = Field(True, description="Do not auto-start on password fields.")
    ignore_fullscreen_games: bool = Field(True, description="Do not auto-start during fullscreen games.")
    
    # Auto-stop Configuration
    enable_silence_auto_stop: bool = Field(True, description="Auto-stop when user stops speaking.")
    silence_duration: float = Field(8.0, description="Seconds of silence before auto-stop.")
    enable_manual_stop: bool = Field(True, description="Allow middle-click to manually stop recording.")
    max_recording_time: int = Field(300, description="Max recording duration in seconds (5 minutes).")
    
    # History Configuration
    max_history: int = Field(100, description="Maximum number of transcriptions to keep in history.")

# --- Config Manager Class ---

class ConfigManager:
    CONFIG_FILE = Path.home() / ".voice_click_config.json"
    
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> VoiceClickConfig:
        """Loads configuration from file or returns defaults."""
        if self.CONFIG_FILE.exists():
            try:
                data = json.loads(self.CONFIG_FILE.read_text())
                # Validate and load existing data, filling missing fields with defaults
                config = VoiceClickConfig.model_validate(data)
                logger.info(f"Configuration loaded from {self.CONFIG_FILE}")
                return config
            except (json.JSONDecodeError, ValidationError, Exception) as e:
                logger.warning(f"Failed to load or validate config file: {e}. Using default settings.")
                return VoiceClickConfig()
        else:
            logger.info("Config file not found. Using default settings.")
            return VoiceClickConfig()

    def save_config(self):
        """Saves the current configuration to file."""
        try:
            # Use model_dump to get a dictionary representation of the config
            data = self.config.model_dump(mode='json')
            self.CONFIG_FILE.write_text(json.dumps(data, indent=2))
            logger.info(f"Configuration saved to {self.CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def get(self, key: str):
        """Retrieves a configuration value by key."""
        return getattr(self.config, key)

    def set(self, key: str, value):
        """Sets a configuration value by key and saves it."""
        if hasattr(self.config, key):
            try:
                # Use model_validate to ensure the new value conforms to the schema type
                # We create a temporary dictionary to validate the single field
                temp_data = self.config.model_dump()
                temp_data[key] = value
                
                # Validate the entire model with the updated value
                validated_config = VoiceClickConfig.model_validate(temp_data)
                
                # If validation passes, update the internal config object
                setattr(self.config, key, getattr(validated_config, key))
                self.save_config()
                return True
            except ValidationError as e:
                logger.error(f"Validation error for setting '{key}' to '{value}': {e}")
                return False
            except Exception as e:
                logger.error(f"Error setting configuration value for '{key}': {e}")
                return False
        else:
            logger.warning(f"Attempted to set unknown configuration key: {key}")
            return False

    def get_descriptions(self) -> dict:
        """Retrieves descriptions for all configuration fields."""
        descriptions = {}
        for field_name, field in VoiceClickConfig.model_fields.items():
            descriptions[field_name] = field.description
        return descriptions

# Global instance for easy access
config_manager = ConfigManager()