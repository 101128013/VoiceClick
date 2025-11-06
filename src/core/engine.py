"""
Core transcription and recording engine for VoiceClick.

This module handles audio capture, processing, and transcription using the
Whisper model. It is designed to be run in a separate thread to avoid
blocking the main UI.
"""

import logging
import threading
import time
import queue
from typing import Optional, Callable

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from src.config.settings import Settings

logger = logging.getLogger(__name__)

class VoiceClickEngine:
    """
    The core engine for voice-to-text transcription.

    This class encapsulates all the logic for audio recording, silence detection,
    and transcription using the `faster-whisper` library. It is designed to be
    thread-safe and provides callbacks for UI updates.
    """

    def __init__(self, config: Settings):
        """
        Initializes the VoiceClick Engine.

        Args:
            config: A Settings object containing model and recording parameters.
        """
        self.config = config
        self.model: Optional[WhisperModel] = None
        self.is_recording = False
        self.is_initialized = False

        # Audio recording state
        self.stream: Optional[sd.InputStream] = None
        self.audio_data: list[np.ndarray] = []
        self.recording_start_time: Optional[float] = None

        # Status tracking
        self.current_rms = 0.0
        self.silence_start_time: Optional[float] = None

        # Threading
        self.recording_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.model_lock = threading.Lock()

        # Callbacks for UI updates
        self.on_volume_change: Optional[Callable[[int], None]] = None
        self.on_status_change: Optional[Callable[[str], None]] = None

        logger.info(f"VoiceClickEngine initialized with model '{config.whisper_model}'")

    def initialize(self) -> bool:
        """
        Loads the Whisper model. This can be time-consuming and should be
        called before starting any recording.

        Returns:
            True if the model was loaded successfully, False otherwise.
        """
        if self.is_initialized:
            return True

        with self.model_lock:
            if self.model is not None:
                self.is_initialized = True
                return True
            try:
                logger.info(
                    f"Loading Whisper model '{self.config.whisper_model}' on "
                    f"device '{self.config.whisper_device}' with compute type "
                    f"'{self.config.whisper_compute_type}'..."
                )
                self.model = WhisperModel(
                    self.config.whisper_model,
                    device=self.config.whisper_device,
                    compute_type=self.config.whisper_compute_type,
                )
                self.is_initialized = True
                logger.info("Whisper model loaded successfully.")
                if self.on_status_change:
                    self.on_status_change("Model loaded, ready to transcribe.")
                return True
            except Exception as e:
                logger.exception(f"Failed to load Whisper model: {e}")
                if self.on_status_change:
                    self.on_status_change(f"Error: Failed to load model. {e}")
                return False

    def start_recording(self) -> bool:
        """
        Starts capturing audio from the default microphone in a background thread.

        Returns:
            True if recording started successfully, False otherwise.
        """
        if self.is_recording:
            logger.warning("Recording is already in progress.")
            return False

        if not self.is_initialized:
            logger.error("Engine not initialized. Call initialize() first.")
            if self.on_status_change:
                self.on_status_change("Error: Engine not initialized.")
            return False

        try:
            self.is_recording = True
            self.audio_data = []
            self.recording_start_time = time.time()
            self.silence_start_time = None
            self.stop_event.clear()

            self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
            self.recording_thread.start()

            logger.info("Recording started.")
            if self.on_status_change:
                self.on_status_change("Recording...")
            return True
        except Exception as e:
            logger.exception(f"Failed to start recording: {e}")
            self.is_recording = False
            if self.on_status_change:
                self.on_status_change(f"Error: Could not start recording. {e}")
            return False

    def stop_recording(self) -> Optional[str]:
        """
        Stops the recording, transcribes the captured audio, and returns the text.

        Returns:
            The transcribed text as a string, or None if transcription failed or
            no audio was recorded.
        """
        if not self.is_recording:
            logger.warning("No recording in progress to stop.")
            return None

        self.stop_event.set()
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)

        self.is_recording = False
        if self.on_status_change:
            self.on_status_change("Processing audio...")

        if not self.audio_data:
            logger.warning("No audio data was recorded.")
            if self.on_status_change:
                self.on_status_change("Ready.")
            return None

        audio_array = np.concatenate(self.audio_data, axis=0).astype(np.float32)
        
        # Normalize audio to the range [-1, 1]
        max_abs = np.max(np.abs(audio_array))
        if max_abs > 0:
            audio_array = audio_array / max_abs

        logger.info(f"Transcribing {len(audio_array) / 16000:.2f} seconds of audio.")
        result = self._transcribe_audio(audio_array)
        logger.info(f"Transcription result: '{result}'")

        if self.on_status_change:
            self.on_status_change("Ready.")
        
        return result

    def _record_audio(self):
        """
        The main audio recording loop, run in a background thread.
        
        Captures audio from the microphone and puts it into a queue. Also handles
        auto-stop logic for silence and maximum recording time.
        """
        try:
            sample_rate = 16000  # Whisper's required sample rate
            channels = 1
            blocksize = 4096  # 256ms of audio per block

            def audio_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                self.audio_data.append(indata.copy())
                self._update_volume(indata)

            self.stream = sd.InputStream(
                samplerate=sample_rate,
                channels=channels,
                blocksize=blocksize,
                callback=audio_callback,
                dtype=np.float32,
                device=self.config.microphone_device,
            )
            with self.stream:
                while not self.stop_event.is_set():
                    self._check_recording_limits()
                    time.sleep(0.1)
        except Exception as e:
            logger.exception(f"Error in audio recording thread: {e}")
            if self.on_status_change:
                self.on_status_change(f"Error: Audio recording failed. {e}")
        finally:
            if self.stream:
                self.stream.close()
                self.stream = None
            self.stop_event.set()

    def _update_volume(self, audio_chunk: np.ndarray):
        """
        Calculates the root mean square (RMS) of the audio chunk to estimate volume
        and triggers the on_volume_change callback.
        """
        self.current_rms = np.sqrt(np.mean(audio_chunk**2))
        
        # Convert RMS to a more intuitive 0-100 scale.
        # The formula is a logarithmic conversion to decibels, adjusted to the scale.
        volume_db = 20 * np.log10(self.current_rms + 1e-10)
        # Clamp and scale to 0-100 range
        scaled_volume = int(np.clip((volume_db + 60) * 2, 0, 100))

        if self.on_volume_change:
            self.on_volume_change(scaled_volume)

    def _check_recording_limits(self):
        """Checks for silence or max recording time to auto-stop recording."""
        if self.config.enable_silence_auto_stop and self._is_silent():
            logger.info("Silence detected, stopping recording.")
            self.stop_event.set()

        if self.config.enable_manual_stop and self.recording_start_time:
            elapsed = time.time() - self.recording_start_time
            if elapsed > self.config.max_recording_time:
                logger.info(f"Max recording time of {self.config.max_recording_time}s reached.")
                self.stop_event.set()

    def _is_silent(self) -> bool:
        """
        Determines if the audio has been silent for longer than the configured duration.

        Returns:
            True if the silence duration has been exceeded, False otherwise.
        """
        # A reasonable threshold for silence
        silence_threshold = 0.01

        if self.current_rms < silence_threshold:
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
        Transcribes an audio array using the loaded Whisper model.

        Args:
            audio: A NumPy array containing the audio data.

        Returns:
            The transcribed text as a string, or None on error.
        """
        if not self.is_initialized or self.model is None:
            logger.error("Transcription attempted before model was initialized.")
            return None
        
        try:
            with self.model_lock:
                segments, info = self.model.transcribe(
                    audio,
                    language=self.config.language if self.config.language != "auto" else None,
                    beam_size=5,
                )
                
                text = " ".join(segment.text for segment in segments).strip()
                return text if text else None
        except Exception as e:
            logger.exception(f"Transcription failed: {e}")
            return None

    def get_status(self) -> dict:
        """
        Returns a dictionary with the current status of the engine.
        """
        elapsed = 0
        if self.is_recording and self.recording_start_time:
            elapsed = time.time() - self.recording_start_time
        
        return {
            "is_recording": self.is_recording,
            "is_initialized": self.is_initialized,
            "model_name": self.config.whisper_model,
            "device": self.config.whisper_device,
            "recording_time": elapsed,
        }
