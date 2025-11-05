"""
VoiceClick Settings Management - Application configuration persistence
Handles loading, saving, and managing all application settings
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Settings:
    """Application settings with defaults."""
    
    # Model Settings
    whisper_model: str = "large-v3"
    whisper_device: str = "cuda"
    whisper_compute_type: str = "float16"
    
    # Recording Settings
    auto_start_on_focus: bool = True
    auto_start_on_left_click: bool = True
    enable_silence_auto_stop: bool = True
    silence_duration: float = 8.0
    enable_manual_stop: bool = True
    max_recording_time: int = 300
    
    # UI Settings
    start_minimized: bool = False
    show_notification_on_transcription: bool = True
    window_width: int = 800
    window_height: int = 600
    
    # Accessibility
    ignore_password_fields: bool = True
    ignore_fullscreen_games: bool = True
    
    # Advanced
    debug_mode: bool = False
    history_size: int = 50
    language: str = "en"
    
    # Internal paths
    _config_dir: Path = field(default_factory=lambda: Path.home() / ".voice_click")
    _config_file: Path = field(default_factory=lambda: Path.home() / ".voice_click" / "config.json")
    
    @property
    def config_file(self) -> Path:
        """Get config file path."""
        return self._config_file
    
    @property
    def config_dir(self) -> Path:
        """Get config directory path."""
        return self._config_dir

    def validate(self) -> bool:
        """
        Validate settings values.
        
        Returns:
            bool: True if all settings valid
        """
        # Validate model
        valid_models = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
        if self.whisper_model not in valid_models:
            logger.warning(f"Invalid model: {self.whisper_model}, using default")
            self.whisper_model = "large-v3"
        
        # Validate device
        valid_devices = ["cuda", "cpu", "auto"]
        if self.whisper_device not in valid_devices:
            logger.warning(f"Invalid device: {self.whisper_device}, using default")
            self.whisper_device = "cuda"
        
        # Validate compute type
        valid_types = ["auto", "float16", "float32", "int8"]
        if self.whisper_compute_type not in valid_types:
            logger.warning(f"Invalid compute type: {self.whisper_compute_type}, using default")
            self.whisper_compute_type = "float16"
        
        # Validate numeric ranges
        if self.silence_duration < 1.0:
            self.silence_duration = 1.0
        if self.silence_duration > 60.0:
            self.silence_duration = 60.0
        
        if self.max_recording_time < 10:
            self.max_recording_time = 10
        if self.max_recording_time > 3600:
            self.max_recording_time = 3600
        
        if self.history_size < 10:
            self.history_size = 10
        if self.history_size > 1000:
            self.history_size = 1000
        
        if self.window_width < 400:
            self.window_width = 400
        if self.window_height < 300:
            self.window_height = 300
        
        return True

    def save(self) -> bool:
        """
        Save settings to JSON file.
        
        Returns:
            bool: True if successful
        """
        try:
            # Validate before saving
            self.validate()
            
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for serialization (exclude Path objects)
            settings_dict = asdict(self)
            # Remove internal path fields
            del settings_dict['_config_dir']
            del settings_dict['_config_file']
            
            # Write to JSON
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings saved to {self.config_file}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False

    @classmethod
    def load(cls, config_file: Optional[Path] = None) -> "Settings":
        """
        Load settings from JSON file, fall back to defaults if not found.
        
        Args:
            config_file: Optional custom config file path
            
        Returns:
            Settings: Loaded settings or defaults
        """
        if config_file is None:
            config_file = Path.home() / ".voice_click" / "config.json"
        
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Create settings instance with loaded data
                settings = cls(**{k: v for k, v in data.items() if k not in ['_config_dir', '_config_file']})
                settings._config_file = config_file
                settings._config_dir = config_file.parent
                
                # Validate loaded settings
                settings.validate()
                
                logger.info(f"Settings loaded from {config_file}")
                return settings
            else:
                logger.info("No config file found, using default settings")
                settings = cls()
                settings._config_file = config_file
                settings._config_dir = config_file.parent
                return settings
        
        except Exception as e:
            logger.error(f"Failed to load settings: {e}, using defaults")
            settings = cls()
            settings._config_file = config_file
            settings._config_dir = config_file.parent
            return settings

    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to defaults.
        
        Returns:
            bool: True if successful
        """
        try:
            default_settings = Settings()
            
            # Copy all fields from default
            for field_name in asdict(default_settings):
                if not field_name.startswith('_'):
                    setattr(self, field_name, getattr(default_settings, field_name))
            
            logger.info("Settings reset to defaults")
            return True
        
        except Exception as e:
            logger.error(f"Failed to reset settings: {e}")
            return False

    def to_dict(self) -> dict:
        """
        Convert settings to dictionary (excluding internal fields).
        
        Returns:
            dict: Settings dictionary
        """
        settings_dict = asdict(self)
        del settings_dict['_config_dir']
        del settings_dict['_config_file']
        return settings_dict

    def __str__(self) -> str:
        """Return string representation of settings."""
        data = self.to_dict()
        return json.dumps(data, indent=2)
