"""
Manages application settings, providing a structured and persistent way to
handle user configurations.

This module defines the `Settings` data class, which holds all user-configurable
options. It also includes the `SettingsManager` to load, save, and validate
these settings from a JSON file.
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List

from . import constants

logger = logging.getLogger(__name__)

@dataclass
class Settings:
    """
    A data class holding all application settings with their default values.
    
    This class is designed to be easily serialized to and from JSON.
    """
    
    # Model Settings
    whisper_model: str = constants.WHISPER_DEFAULT_MODEL
    whisper_device: str = constants.DEFAULT_DEVICE
    whisper_compute_type: str = "float16"
    language: str = "en"  # 'auto' for auto-detection
    
    # Recording Settings
    auto_start_on_focus: bool = constants.DEFAULT_AUTO_START_FOCUS
    auto_start_on_left_click: bool = constants.DEFAULT_AUTO_START_LEFT_CLICK
    enable_silence_auto_stop: bool = constants.DEFAULT_ENABLE_SILENCE_AUTO_STOP
    silence_duration: float = constants.DEFAULT_SILENCE_DURATION
    enable_manual_stop: bool = True
    max_recording_time: int = constants.DEFAULT_MAX_RECORDING_TIME
    microphone_device: Optional[int] = None  # None = default device
    
    # Auto-Start Settings
    auto_start_cooldown: float = 2.0  # Seconds between auto-starts
    app_whitelist: List[str] = field(default_factory=list)  # Empty = all apps allowed
    app_blacklist: List[str] = field(default_factory=list)  # Empty = no apps blocked
    
    # UI Settings
    start_minimized: bool = False
    show_notification_on_transcription: bool = True
    window_width: int = constants.DEFAULT_WINDOW_WIDTH
    window_height: int = constants.DEFAULT_WINDOW_HEIGHT
    
    # History Settings
    history_size: int = constants.DEFAULT_HISTORY_SIZE
    
    # Hotkey Settings
    enable_hotkeys: bool = constants.DEFAULT_ENABLE_HOTKEYS
    start_recording_hotkey: str = constants.DEFAULT_START_RECORDING_HOTKEY
    stop_recording_hotkey: str = constants.DEFAULT_STOP_RECORDING_HOTKEY
    
    # Advanced Settings
    debug_mode: bool = False

    def to_dict(self) -> dict:
        """Converts the settings object to a dictionary."""
        return asdict(self)


class SettingsManager:
    """
    Handles loading, saving, and validating application settings.
    
    This manager ensures that settings are persisted across sessions and that
    their values remain within valid ranges.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initializes the SettingsManager.

        Args:
            config_dir: The directory to store configuration files. Defaults to
                        `~/.voice_click`.
        """
        self.config_dir = config_dir or Path.home() / ".voice_click"
        self.config_file = self.config_dir / constants.CONFIG_FILENAME
        self.settings = Settings()
        self.load()

    def load(self) -> Settings:
        """
        Loads settings from the JSON configuration file.
        
        If the file doesn't exist or is invalid, it returns default settings.
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            logger.info("Configuration file not found. Using default settings.")
            self.save()  # Create a default config file
            return self.settings

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update settings with loaded data, ignoring unknown keys
            loaded_settings = Settings(**{k: v for k, v in data.items() if hasattr(Settings, k)})
            self.settings = loaded_settings
            logger.info("Settings loaded successfully.")
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to load or parse settings file: {e}. Using defaults.", exc_info=True)
            self.settings = Settings() # Reset to defaults on error
        
        self.validate()
        return self.settings

    def save(self):
        """
        Saves the current settings to the JSON configuration file.
        """
        self.validate()
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, indent=4)
            logger.info(f"Settings saved to {self.config_file}")
        except IOError as e:
            logger.error(f"Failed to save settings: {e}", exc_info=True)

    def validate(self):
        """
        Ensures that all settings have valid and reasonable values.
        
        This method corrects any out-of-range values to prevent application errors.
        """
        # Validate model
        if self.settings.whisper_model not in constants.WHISPER_MODELS:
            logger.warning(f"Invalid model '{self.settings.whisper_model}', resetting to default.")
            self.settings.whisper_model = constants.WHISPER_DEFAULT_MODEL
        
        # Validate device
        if self.settings.whisper_device not in constants.COMPUTE_DEVICES:
            logger.warning(f"Invalid device '{self.settings.whisper_device}', resetting to default.")
            self.settings.whisper_device = constants.DEFAULT_DEVICE
        
        # Validate compute type
        if self.settings.whisper_compute_type not in constants.COMPUTE_TYPES:
            logger.warning(f"Invalid compute type '{self.settings.whisper_compute_type}', resetting to 'auto'.")
            self.settings.whisper_compute_type = "auto"
        
        # Validate numeric ranges
        self.settings.silence_duration = max(1.0, min(self.settings.silence_duration, 60.0))
        self.settings.max_recording_time = max(10, min(self.settings.max_recording_time, 3600))
        self.settings.history_size = max(10, min(self.settings.history_size, 1000))

    def get_settings(self) -> Settings:
        """Returns the current settings object."""
        return self.settings

    def update_settings(self, new_settings: dict):
        """
        Updates the settings with new values and saves them.
        """
        for key, value in new_settings.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        self.save()
