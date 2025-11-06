"""
Test configuration and utilities for VoiceClick tests.

Provides shared fixtures, mock objects, and test utilities.
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
import tempfile
import shutil

from src.config.settings import Settings
from src.core.text_field_monitor import TextFieldInfo


# Test Settings
def get_test_settings() -> Settings:
    """Returns a Settings object configured for testing."""
    settings = Settings()
    settings.whisper_model = "tiny"  # Use smallest model for tests
    settings.whisper_device = "cpu"  # Use CPU for CI/CD compatibility
    settings.silence_duration = 2.0
    settings.auto_start_on_focus = False  # Disable for most tests
    settings.auto_start_on_left_click = False
    settings.enable_hotkeys = False  # Disable global hotkeys in tests
    settings.check_for_updates = False
    return settings


# Mock Fixtures
@pytest.fixture
def mock_text_field_info():
    """Returns a mock TextFieldInfo object for testing."""
    return TextFieldInfo(
        is_text_field=True,
        control_type="Edit",
        application_name="notepad.exe",
        window_title="Untitled - Notepad",
        is_password_field=False,
        is_readonly=False,
        bounds=(100, 100, 200, 50)
    )


@pytest.fixture
def temp_config_dir():
    """Creates a temporary directory for test configuration."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_whisper_model():
    """Returns a mock WhisperModel for testing."""
    mock_model = Mock()
    mock_model.transcribe = Mock(return_value=(
        [Mock(text="Test transcription")],
        Mock(language="en")
    ))
    return mock_model


@pytest.fixture
def mock_audio_stream():
    """Returns a mock audio stream for testing."""
    mock_stream = Mock()
    mock_stream.start = Mock()
    mock_stream.stop = Mock()
    mock_stream.close = Mock()
    return mock_stream


# Test Utilities
def create_test_audio_data(duration_seconds: float = 1.0, sample_rate: int = 16000):
    """
    Creates dummy audio data for testing.
    
    Args:
        duration_seconds: Duration of audio in seconds
        sample_rate: Sample rate in Hz
        
    Returns:
        numpy array of audio data
    """
    import numpy as np
    samples = int(duration_seconds * sample_rate)
    return np.random.randn(samples).astype(np.float32) * 0.1


def assert_file_exists(file_path: Path, message: str = None):
    """
    Asserts that a file exists.
    
    Args:
        file_path: Path to check
        message: Optional error message
    """
    if not file_path.exists():
        msg = message or f"File does not exist: {file_path}"
        raise AssertionError(msg)


def assert_file_not_empty(file_path: Path, message: str = None):
    """
    Asserts that a file exists and is not empty.
    
    Args:
        file_path: Path to check
        message: Optional error message
    """
    assert_file_exists(file_path, message)
    if file_path.stat().st_size == 0:
        msg = message or f"File is empty: {file_path}"
        raise AssertionError(msg)

