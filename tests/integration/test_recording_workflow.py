"""
Integration tests for VoiceClick recording workflow
"""
import pytest
import tempfile
import time
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.core.engine import VoiceClickEngine
from src.core.history import TranscriptionHistory
from src.config.settings import Settings


@pytest.fixture
def mock_settings():
    """Create a mock Settings object"""
    settings = Settings()
    settings.whisper_model = 'tiny'
    settings.whisper_device = 'cpu'
    settings.whisper_compute_type = 'float32'
    settings.language = 'en'
    settings.enable_silence_auto_stop = False
    settings.enable_manual_stop = False
    return settings


@pytest.fixture
def mock_whisper_model():
    """Create a mock WhisperModel"""
    mock_model = MagicMock()
    mock_segment = Mock()
    mock_segment.text = "Hello world"
    mock_model.transcribe.return_value = ([mock_segment], Mock())
    return mock_model


@pytest.fixture
def temp_history_file():
    """Create a temporary history file"""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
    yield temp_path
    if temp_path.exists():
        temp_path.unlink()


class TestRecordingWorkflow:
    """Test complete recording workflow"""
    
    @patch('src.core.engine.WhisperModel')
    @patch('src.core.engine.sd.InputStream')
    def test_complete_recording_workflow(self, mock_stream_class, mock_whisper_class, mock_settings, mock_whisper_model, temp_history_file):
        """Test complete workflow: initialize -> start -> stop -> transcribe"""
        # Setup mocks
        mock_whisper_class.return_value = mock_whisper_model
        
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        # Create engine
        engine = VoiceClickEngine(mock_settings)
        
        # Initialize
        assert engine.initialize() == True
        assert engine.is_initialized == True
        
        # Mock audio callback to simulate recording
        audio_chunks = []
        def mock_callback(indata, frames, time_info, status):
            audio_chunks.append(np.random.randn(frames).astype(np.float32))
        
        # Start recording
        assert engine.start_recording() == True
        assert engine.is_recording == True
        
        # Simulate some audio data being added
        for _ in range(5):
            engine.audio_data.put_nowait(np.random.randn(1000).astype(np.float32))
        
        # Stop recording
        result = engine.stop_recording()
        
        assert result == "Hello world"
        assert engine.is_recording == False
    
    @patch('src.core.engine.WhisperModel')
    def test_recording_with_history_integration(self, mock_whisper_class, mock_settings, mock_whisper_model, temp_history_file):
        """Test recording workflow with history integration"""
        mock_whisper_class.return_value = mock_whisper_model
        
        engine = VoiceClickEngine(mock_settings)
        history = TranscriptionHistory(history_file=temp_history_file)
        
        # Initialize and start recording
        engine.initialize()
        engine.start_recording()
        
        # Add some audio data
        for _ in range(3):
            engine.audio_data.put_nowait(np.random.randn(1000).astype(np.float32))
        
        # Stop and get transcription
        transcription = engine.stop_recording()
        
        if transcription:
            # Add to history
            record = history.add_record(
                text=transcription,
                duration_seconds=engine.get_status().get("recording_time", 0),
                model_used=mock_settings.whisper_model,
                language=mock_settings.language
            )
            
            assert record.text == transcription
            assert len(history.records) == 1
    
    @patch('src.core.engine.WhisperModel')
    @patch('src.core.engine.sd.InputStream')
    def test_recording_with_empty_audio(self, mock_stream_class, mock_whisper_class, mock_settings, mock_whisper_model):
        """Test recording workflow with no audio data"""
        mock_whisper_class.return_value = mock_whisper_model
        
        engine = VoiceClickEngine(mock_settings)
        engine.initialize()
        engine.start_recording()
        
        # Stop without adding any audio
        result = engine.stop_recording()
        
        assert result is None
        assert engine.is_recording == False
    
    @patch('src.core.engine.WhisperModel')
    def test_recording_error_handling(self, mock_whisper_class, mock_settings):
        """Test error handling during recording"""
        mock_whisper_class.side_effect = Exception("Model load error")
        
        engine = VoiceClickEngine(mock_settings)
        result = engine.initialize()
        
        assert result == False
        assert engine.is_initialized == False
    
    @patch('src.core.engine.WhisperModel')
    @patch('src.core.engine.sd.InputStream')
    def test_recording_transcription_failure(self, mock_stream_class, mock_whisper_class, mock_settings, mock_whisper_model):
        """Test handling transcription failure"""
        mock_whisper_class.return_value = mock_whisper_model
        mock_whisper_model.transcribe.side_effect = Exception("Transcription error")
        
        engine = VoiceClickEngine(mock_settings)
        engine.initialize()
        engine.start_recording()
        
        # Add audio data
        for _ in range(3):
            engine.audio_data.put_nowait(np.random.randn(1000).astype(np.float32))
        
        result = engine.stop_recording()
        
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

