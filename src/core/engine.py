"""
VoiceClick Core Engine - Main transcription and recording engine
Handles audio capture, Whisper transcription, and text field detection
"""

import logging
import threading
import time
import queue
from typing import Optional, Dict, Callable
from pathlib import Path

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from ..config.settings import Settings


logger = logging.getLogger(__name__)


class VoiceClickEngine:
    """
    Core transcription engine - encapsulates all voice-to-text logic.
    Handles Whisper model loading, audio recording, and transcription.
    """

    def __init__(self, config: Settings):
        """
        Initialize the VoiceClick Engine.
        
        Args:
            config: Settings object containing model and recording parameters
        """
        self.config = config
        self.model = None
        self.is_recording = False
        self.is_initialized = False
        
        # Audio recording state
        self.stream = None
        self.audio_queue = queue.Queue()
        self.audio_data = []
        self.recording_start_time = None
        
        # Status tracking
        self.current_volume = 0
        self.current_rms = 0
        self.silence_start_time = None
        
        # Threading
        self.recording_thread = None
        self.stop_event = threading.Event()
        self.model_lock = threading.Lock()
        
        # Callbacks
        self.on_volume_change = None
        self.on_status_change = None
        
        logger.info(f"VoiceClickEngine initialized with model: {config.whisper_model}")

    def initialize(self) -> bool:
        """
        Load Whisper model asynchronously - this can take a few seconds on first run.
        Should be called before start_recording.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        if self.model is not None:
            return True
        
        try:
            with self.model_lock:
                logger.info(
                    f"Loading {self.config.whisper_model} model "
                    f"on device: {self.config.whisper_device}"
                )
                
                self.model = WhisperModel(
                    self.config.whisper_model,
                    device=self.config.whisper_device,
                    compute_type=self.config.whisper_compute_type,
                    num_workers=4
                )
                
                self.is_initialized = True
                logger.info("Model loaded successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return False

    def start_recording(self) -> bool:
        """
        Start audio capture from the default microphone.
        
        Returns:
            bool: True if recording started successfully
        """
        if self.is_recording:
            logger.warning("Recording is already in progress")
            return False
        
        if not self.is_initialized:
            logger.error("Engine not initialized. Call initialize() first.")
            return False
        
        try:
            self.is_recording = True
            self.audio_data = []
            self.recording_start_time = time.time()
            self.silence_start_time = time.time()
            self.stop_event.clear()
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
            self.recording_thread.start()
            
            logger.info("Recording started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.is_recording = False
            return False

    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and return the transcribed text.
        
        Returns:
            str: Transcribed text, or None if transcription failed
        """
        if not self.is_recording:
            logger.warning("No recording in progress")
            return None
        
        try:
            self.stop_event.set()
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=5)
            
            # Close the stream
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            self.is_recording = False
            
            if len(self.audio_data) == 0:
                logger.warning("No audio data recorded")
                return None
            
            # Convert audio to numpy array
            audio_array = np.concatenate(self.audio_data, axis=0).astype(np.float32)
            
            # Normalize audio to [-1, 1] range
            audio_array = audio_array / np.max(np.abs(audio_array)) if np.max(np.abs(audio_array)) > 0 else audio_array
            
            logger.info(f"Transcribing audio ({len(audio_array)} samples)")
            
            # Transcribe with Whisper
            result = self._transcribe_audio(audio_array)
            
            logger.info(f"Transcription complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error during stop_recording: {e}")
            self.is_recording = False
            return None

    def _record_audio(self):
        """
        Internal method: Record audio in background thread.
        """
        try:
            # Audio configuration
            sample_rate = 16000  # Whisper default
            channels = 1
            blocksize = 4096
            
            def audio_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                
                # Store audio chunk
                self.audio_data.append(indata.copy())
                
                # Update volume/RMS
                self._update_volume(indata)
            
            # Open audio stream
            self.stream = sd.InputStream(
                samplerate=sample_rate,
                channels=channels,
                blocksize=blocksize,
                callback=audio_callback,
                dtype=np.float32
            )
            
            with self.stream:
                # Record until stop_event is set or max time reached
                while not self.stop_event.is_set():
                    # Check max recording time
                    if self.config.enable_manual_stop:
                        elapsed = time.time() - self.recording_start_time
                        if elapsed > self.config.max_recording_time:
                            logger.info(f"Max recording time reached ({elapsed:.1f}s)")
                            self.stop_event.set()
                    
                    # Check for silence auto-stop
                    if self.config.enable_silence_auto_stop:
                        if self._check_silence():
                            logger.info("Silence detected, stopping recording")
                            self.stop_event.set()
                    
                    time.sleep(0.1)
        
        except Exception as e:
            logger.error(f"Error in _record_audio: {e}")
            self.stop_event.set()

    def _update_volume(self, audio_chunk: np.ndarray):
        """
        Update current volume/RMS level for UI display.
        
        Args:
            audio_chunk: Audio data chunk
        """
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        self.current_rms = rms
        
        # Convert to dB scale for display (0-100)
        self.current_volume = min(100, int(20 * np.log10(max(rms, 1e-10)) + 100))
        
        # Call volume callback if set
        if self.on_volume_change:
            self.on_volume_change(self.current_volume)

    def _check_silence(self) -> bool:
        """
        Check if recording has been silent long enough to auto-stop.
        
        Returns:
            bool: True if silence threshold exceeded
        """
        if self.current_rms < 0.01:  # Silence threshold
            if self.silence_start_time is None:
                self.silence_start_time = time.time()
            
            silence_duration = time.time() - self.silence_start_time
            if silence_duration > self.config.silence_duration:
                return True
        else:
            self.silence_start_time = None
        
        return False

    def _transcribe_audio(self, audio: np.ndarray) -> Optional[str]:
        """
        Transcribe audio using Whisper model.
        
        Args:
            audio: Audio numpy array
            
        Returns:
            str: Transcribed text
        """
        try:
            with self.model_lock:
                segments, info = self.model.transcribe(
                    audio,
                    language=None,  # Auto-detect language
                    beam_size=5
                )
                
                # Combine all segments
                text = " ".join([segment.text for segment in segments]).strip()
                return text if text else None
        
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    def get_status(self) -> Dict:
        """
        Get current engine status for UI updates.
        
        Returns:
            dict: Status information
        """
        elapsed = 0
        if self.is_recording and self.recording_start_time:
            elapsed = time.time() - self.recording_start_time
        
        return {
            "is_recording": self.is_recording,
            "is_initialized": self.is_initialized,
            "current_volume": self.current_volume,
            "recording_duration": elapsed,
            "model_loaded": self.model is not None,
            "current_model": self.config.whisper_model,
            "current_device": self.config.whisper_device,
        }

    def shutdown(self):
        """
        Gracefully shutdown the engine and release resources.
        """
        if self.is_recording:
            self.stop_recording()
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        logger.info("VoiceClickEngine shutdown complete")
