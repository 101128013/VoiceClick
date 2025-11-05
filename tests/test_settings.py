"""
Unit tests for VoiceClick Settings module
"""
import pytest
import json
import tempfile
from pathlib import Path
from src.config.settings import Settings


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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Create settings with custom values
            settings1 = Settings()
            settings1._config_file = temp_path
            settings1.whisper_model = 'medium'
            settings1.whisper_device = 'cpu'
            settings1.silence_duration = 3.0
            
            # Save settings
            settings1.save()
            
            # Load settings using classmethod
            settings2 = Settings.load(temp_path)
            
            # Verify loaded values match
            assert settings2.whisper_model == 'medium'
            assert settings2.whisper_device == 'cpu'
            assert settings2.silence_duration == 3.0
            
        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()
    
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # First instance
            settings1 = Settings()
            settings1._config_file = temp_path
            settings1.whisper_model = 'small'
            settings1.save()
            
            # Second instance should load saved values
            settings2 = Settings.load(temp_path)
            
            assert settings2.whisper_model == 'small'
            
        finally:
            if temp_path.exists():
                temp_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
