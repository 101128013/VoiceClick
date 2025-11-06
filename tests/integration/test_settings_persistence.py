"""
Integration tests for VoiceClick settings persistence
"""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from src.config.settings import SettingsManager, Settings
from src.config import constants


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestSettingsPersistence:
    """Test settings persistence and propagation"""
    
    def test_settings_save_load_cycle(self, temp_config_dir):
        """Test complete save/load cycle"""
        # Create first manager and save settings
        manager1 = SettingsManager(config_dir=temp_config_dir)
        manager1.settings.whisper_model = 'medium'
        manager1.settings.whisper_device = 'cpu'
        manager1.settings.silence_duration = 5.0
        manager1.save()
        
        # Create second manager and load
        manager2 = SettingsManager(config_dir=temp_config_dir)
        
        assert manager2.settings.whisper_model == 'medium'
        assert manager2.settings.whisper_device == 'cpu'
        assert manager2.settings.silence_duration == 5.0
    
    def test_settings_validation_on_load(self, temp_config_dir):
        """Test settings validation on load"""
        config_file = temp_config_dir / constants.CONFIG_FILENAME
        
        # Create invalid config file
        invalid_config = {
            'whisper_model': 'invalid_model',
            'whisper_device': 'invalid_device',
            'silence_duration': -5.0  # Invalid negative value
        }
        
        with open(config_file, 'w') as f:
            json.dump(invalid_config, f)
        
        # Load should validate and correct values
        manager = SettingsManager(config_dir=temp_config_dir)
        
        # Should be corrected to valid values
        assert manager.settings.whisper_model in constants.WHISPER_MODELS
        assert manager.settings.whisper_device in constants.COMPUTE_DEVICES
        assert manager.settings.silence_duration >= 1.0
    
    def test_settings_update_propagation(self, temp_config_dir):
        """Test settings update propagation"""
        manager = SettingsManager(config_dir=temp_config_dir)
        
        # Update settings
        new_settings = {
            'whisper_model': 'small',
            'silence_duration': 10.0
        }
        manager.update_settings(new_settings)
        
        # Verify updates
        assert manager.settings.whisper_model == 'small'
        assert manager.settings.silence_duration == 10.0
        
        # Verify persistence
        manager2 = SettingsManager(config_dir=temp_config_dir)
        assert manager2.settings.whisper_model == 'small'
        assert manager2.settings.silence_duration == 10.0
    
    def test_settings_defaults_on_missing_file(self, temp_config_dir):
        """Test default settings when file doesn't exist"""
        manager = SettingsManager(config_dir=temp_config_dir)
        
        # Should use defaults
        assert manager.settings.whisper_model == constants.WHISPER_DEFAULT_MODEL
        assert manager.settings.whisper_device == constants.DEFAULT_DEVICE
    
    def test_settings_invalid_json_handling(self, temp_config_dir):
        """Test handling invalid JSON"""
        config_file = temp_config_dir / constants.CONFIG_FILENAME
        
        # Write invalid JSON
        with open(config_file, 'w') as f:
            f.write("invalid json content {")
        
        # Should fall back to defaults
        manager = SettingsManager(config_dir=temp_config_dir)
        
        assert manager.settings.whisper_model == constants.WHISPER_DEFAULT_MODEL
    
    def test_settings_numeric_range_validation(self, temp_config_dir):
        """Test numeric range validation"""
        manager = SettingsManager(config_dir=temp_config_dir)
        
        # Set out-of-range values
        manager.settings.silence_duration = 100.0  # Too high
        manager.settings.max_recording_time = 10000  # Too high
        manager.settings.history_size = 5000  # Too high
        
        manager.validate()
        
        # Should be clamped to valid ranges
        assert manager.settings.silence_duration <= 60.0
        assert manager.settings.max_recording_time <= 3600
        assert manager.settings.history_size <= 1000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

