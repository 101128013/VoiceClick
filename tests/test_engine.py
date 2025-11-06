"""
Unit tests for VoiceClick Engine module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.engine import VoiceClickEngine
from src.config.settings import Settings


class TestVoiceClickEngine:
    """Test VoiceClickEngine class"""
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        settings = Settings()
        engine = VoiceClickEngine(settings)
        
        assert engine.config == settings
        assert engine.is_recording == False
        assert engine.is_initialized == False
        assert engine.model is None
    
    def test_engine_callbacks(self):
        """Test setting callbacks"""
        settings = Settings()
        engine = VoiceClickEngine(settings)
        
        # Set callbacks
        volume_callback = Mock()
        status_callback = Mock()
        
        engine.on_volume_change = volume_callback
        engine.on_status_change = status_callback
        
        assert engine.on_volume_change == volume_callback
        assert engine.on_status_change == status_callback
    
    def test_get_status_not_initialized(self):
        """Test getting status when not initialized"""
        settings = Settings()
        engine = VoiceClickEngine(settings)
        
        status = engine.get_status()
        
        assert status['is_recording'] == False
        assert status['is_initialized'] == False
        assert status['model_name'] == settings.whisper_model
        assert status['device'] == settings.whisper_device
        assert status['recording_time'] == 0
    
    def test_start_recording_not_initialized(self):
        """Test starting recording when not initialized fails"""
        settings = Settings()
        engine = VoiceClickEngine(settings)
        
        result = engine.start_recording()
        
        assert result == False
        assert engine.is_recording == False
    
    def test_stop_recording_not_recording(self):
        """Test stopping recording when not recording"""
        settings = Settings()
        engine = VoiceClickEngine(settings)
        
        result = engine.stop_recording()
        
        assert result is None
    
    @patch('src.core.engine.WhisperModel')
    def test_engine_initialize(self, mock_whisper):
        """Test engine initialization with mocked Whisper"""
        settings = Settings()
        settings.whisper_model = 'tiny'
        settings.whisper_device = 'cpu'
        
        engine = VoiceClickEngine(settings)
        
        # Mock the model
        mock_model = MagicMock()
        mock_whisper.return_value = mock_model
        
        result = engine.initialize()
        
        assert result == True
        assert engine.is_initialized == True
        assert engine.model is not None
    


class TestEngineThreadSafety:
    """Test engine thread safety"""
    
    def test_model_lock_exists(self):
        """Test that model lock exists for thread safety"""
        settings = Settings()
        engine = VoiceClickEngine(settings)
        
        assert hasattr(engine, 'model_lock')
        assert engine.model_lock is not None
    
    def test_stop_event_exists(self):
        """Test that stop event exists for thread control"""
        settings = Settings()
        engine = VoiceClickEngine(settings)
        
        assert hasattr(engine, 'stop_event')
        assert engine.stop_event is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
