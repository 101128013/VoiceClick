"""
Unit tests for VoiceClick Settings module
"""
import pytest
import json
import tempfile
from pathlib import Path
from src.config.settings import Settings, SettingsManager
from src.config import constants


class TestSettings:
    """Test Settings class"""
    
    def test_settings_default_initialization(self):
        """Test that settings initializes with defaults"""
        settings = Settings()
        
        # Check default values
        assert settings.whisper_model in ['tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3']
        assert settings.whisper_device in ['cpu', 'cuda', 'auto']
        assert isinstance(settings.auto_start_on_focus, bool)
        assert isinstance(settings.silence_duration, (int, float))
        assert settings.silence_duration > 0
    
    def test_settings_load_save(self):
        """Test settings save and load functionality"""
        # Create temp file for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_config_dir = Path(tmpdir)
            
            # Create settings with custom values using SettingsManager
            manager1 = SettingsManager(config_dir=temp_config_dir)
            manager1.settings.whisper_model = 'medium'
            manager1.settings.whisper_device = 'cpu'
            manager1.settings.silence_duration = 3.0
            manager1.save()
            
            # Load settings using SettingsManager
            manager2 = SettingsManager(config_dir=temp_config_dir)
            
            # Verify loaded values match
            assert manager2.settings.whisper_model == 'medium'
            assert manager2.settings.whisper_device == 'cpu'
            assert manager2.settings.silence_duration == 3.0
    
    def test_settings_validation(self):
        """Test settings value validation"""
        settings = Settings()
        
        # Test valid model
        settings.whisper_model = 'large-v3'
        assert settings.whisper_model == 'large-v3'
        
        # Test valid device
        settings.whisper_device = 'cuda'
        assert settings.whisper_device == 'cuda'
    
    def test_settings_persistence(self):
        """Test that settings persist across instances"""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_config_dir = Path(tmpdir)
            
            # First instance
            manager1 = SettingsManager(config_dir=temp_config_dir)
            manager1.settings.whisper_model = 'small'
            manager1.save()
            
            # Second instance should load saved values
            manager2 = SettingsManager(config_dir=temp_config_dir)
            
            assert manager2.settings.whisper_model == 'small'
    
    def test_to_dict(self):
        """Test to_dict method"""
        settings = Settings()
        settings_dict = settings.to_dict()
        
        assert isinstance(settings_dict, dict)
        assert 'whisper_model' in settings_dict
        assert 'whisper_device' in settings_dict


class TestSettingsManager:
    """Test SettingsManager class"""
    
    def test_settings_manager_initialization(self, temp_config_dir):
        """Test SettingsManager initialization"""
        manager = SettingsManager(config_dir=temp_config_dir)
        
        assert manager.settings is not None
        assert isinstance(manager.settings, Settings)
    
    def test_settings_manager_load_defaults(self, temp_config_dir):
        """Test loading defaults when no config file exists"""
        manager = SettingsManager(config_dir=temp_config_dir)
        
        assert manager.settings.whisper_model == constants.WHISPER_DEFAULT_MODEL
    
    def test_settings_manager_save_load(self, temp_config_dir):
        """Test save and load cycle"""
        manager1 = SettingsManager(config_dir=temp_config_dir)
        manager1.settings.whisper_model = 'medium'
        manager1.save()
        
        manager2 = SettingsManager(config_dir=temp_config_dir)
        
        assert manager2.settings.whisper_model == 'medium'
    
    def test_settings_manager_validation(self, temp_config_dir):
        """Test settings validation"""
        manager = SettingsManager(config_dir=temp_config_dir)
        
        # Set invalid values
        manager.settings.whisper_model = 'invalid_model'
        manager.settings.whisper_device = 'invalid_device'
        manager.settings.silence_duration = -5.0
        
        manager.validate()
        
        # Should be corrected
        assert manager.settings.whisper_model in constants.WHISPER_MODELS
        assert manager.settings.whisper_device in constants.COMPUTE_DEVICES
        assert manager.settings.silence_duration >= 1.0
    
    def test_settings_manager_update_settings(self, temp_config_dir):
        """Test update_settings method"""
        manager = SettingsManager(config_dir=temp_config_dir)
        
        new_settings = {
            'whisper_model': 'small',
            'silence_duration': 10.0
        }
        manager.update_settings(new_settings)
        
        assert manager.settings.whisper_model == 'small'
        assert manager.settings.silence_duration == 10.0
    
    def test_settings_manager_update_settings_invalid_key(self, temp_config_dir):
        """Test update_settings with invalid key"""
        manager = SettingsManager(config_dir=temp_config_dir)
        original_model = manager.settings.whisper_model
        
        new_settings = {
            'invalid_key': 'value',
            'whisper_model': 'small'
        }
        manager.update_settings(new_settings)
        
        # Invalid key should be ignored
        assert manager.settings.whisper_model == 'small'
        assert not hasattr(manager.settings, 'invalid_key')
    
    def test_settings_manager_load_invalid_json(self, temp_config_dir):
        """Test loading invalid JSON"""
        config_file = temp_config_dir / constants.CONFIG_FILENAME
        
        with open(config_file, 'w') as f:
            f.write("invalid json {")
        
        manager = SettingsManager(config_dir=temp_config_dir)
        
        # Should fall back to defaults
        assert manager.settings.whisper_model == constants.WHISPER_DEFAULT_MODEL
    
    def test_settings_manager_load_missing_keys(self, temp_config_dir):
        """Test loading config with missing keys"""
        config_file = temp_config_dir / constants.CONFIG_FILENAME
        
        with open(config_file, 'w') as f:
            json.dump({'whisper_model': 'tiny'}, f)
        
        manager = SettingsManager(config_dir=temp_config_dir)
        
        # Missing keys should use defaults
        assert manager.settings.whisper_model == 'tiny'
        assert manager.settings.whisper_device == constants.DEFAULT_DEVICE
    
    def test_settings_manager_numeric_range_validation(self, temp_config_dir):
        """Test numeric range validation"""
        manager = SettingsManager(config_dir=temp_config_dir)
        
        # Set out-of-range values
        manager.settings.silence_duration = 100.0
        manager.settings.max_recording_time = 10000
        manager.settings.history_size = 5000
        
        manager.validate()
        
        # Should be clamped
        assert manager.settings.silence_duration <= 60.0
        assert manager.settings.max_recording_time <= 3600
        assert manager.settings.history_size <= 1000
    
    def test_settings_manager_get_settings(self, temp_config_dir):
        """Test get_settings method"""
        manager = SettingsManager(config_dir=temp_config_dir)
        
        settings = manager.get_settings()
        
        assert isinstance(settings, Settings)
        assert settings == manager.settings


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
