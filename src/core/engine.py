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
from PyQt6.QtCore import QThread, pyqtSignal

from src.config.settings import Settings

logger = logging.getLogger(__name__)


class TranscriptionWorker(QThread):
    """
    Worker thread for asynchronous audio transcription.
    
    This class handles transcription in a separate thread to avoid blocking
    the main UI thread during long transcription operations.
    """
    
    # Signals for thread-safe communication with UI
    transcription_complete = pyqtSignal(str)  # Emitted with transcription result
    transcription_failed = pyqtSignal(str)  # Emitted with error message
    transcription_progress = pyqtSignal(str)  # Emitted with progress updates
    
    def __init__(self, model: WhisperModel, audio: np.ndarray, config: Settings, model_lock: threading.Lock):
        """
        Initializes the transcription worker.
        
        Args:
            model: The WhisperModel instance to use for transcription
            audio: The audio array to transcribe
            config: Settings object containing transcription parameters
            model_lock: Thread lock for model access
        """
        super().__init__()
        self.model = model
        self.audio = audio
        self.config = config
        self.model_lock = model_lock
        
    def run(self):
        """Executes the transcription in the worker thread."""
        try:
            self.transcription_progress.emit("Transcribing audio...")
            
            with self.model_lock:
                # First pass: enable VAD to remove non-speech and improve quality
                segments, info = self.model.transcribe(
                    self.audio,
                    language=self.config.language if self.config.language != "auto" else None,
                    beam_size=5,
                    vad_filter=True,
                )
                text = " ".join(segment.text for segment in segments).strip()

            if text:
                self.transcription_complete.emit(text)
            else:
                # Fallback pass: retry with different decoding params
                with self.model_lock:
                    segments, info = self.model.transcribe(
                        self.audio,
                        language=self.config.language if self.config.language != "auto" else None,
                        beam_size=1,
                        vad_filter=False,
                        temperature=0.7,
                        condition_on_previous_text=False,
                    )
                    text_retry = " ".join(segment.text for segment in segments).strip()

                if text_retry:
                    self.transcription_complete.emit(text_retry)
                else:
                    self.transcription_failed.emit("Transcription returned empty result")
                
        except Exception as e:
            logger.exception(f"Transcription failed in worker thread: {e}")
            self.transcription_failed.emit(str(e))

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
        self.audio_data: queue.Queue = queue.Queue()
        self.recording_start_time: Optional[float] = None

        # Status tracking
        self.current_rms = 0.0
        self.silence_start_time: Optional[float] = None

        # Threading
        self.recording_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.model_lock = threading.Lock()
        self.transcription_worker: Optional[TranscriptionWorker] = None

        # Callbacks for UI updates
        self.on_volume_change: Optional[Callable[[int], None]] = None
        self.on_status_change: Optional[Callable[[str], None]] = None
        self.on_transcription_complete: Optional[Callable[[str], None]] = None
        self.on_transcription_failed: Optional[Callable[[str], None]] = None
        self.on_transcription_progress: Optional[Callable[[str], None]] = None

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
            # Clear the queue for new recording
            while not self.audio_data.empty():
                try:
                    self.audio_data.get_nowait()
                except queue.Empty:
                    break
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

    def stop_recording(self) -> bool:
        """
        Stops the recording and starts asynchronous transcription.
        
        This method returns immediately after stopping the recording and
        preparing the audio. Transcription happens in a background thread,
        and results are communicated via callbacks.

        Returns:
            True if recording was stopped and transcription started, False otherwise.
        """
        if not self.is_recording:
            logger.warning("No recording in progress to stop.")
            return False

        self.stop_event.set()
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=5.0)  # Increased timeout
            if self.recording_thread.is_alive():
                logger.warning("Recording thread did not stop within timeout")

        self.is_recording = False
        if self.on_status_change:
            self.on_status_change("Processing audio...")

        # Collect all audio data from queue
        audio_chunks = []
        while not self.audio_data.empty():
            try:
                audio_chunks.append(self.audio_data.get_nowait())
            except queue.Empty:
                break

        if not audio_chunks:
            logger.warning("No audio data was recorded.")
            if self.on_status_change:
                self.on_status_change("Ready.")
            if self.on_transcription_failed:
                self.on_transcription_failed("No audio data was recorded.")
            return False

        audio_array = np.concatenate(audio_chunks, axis=0).astype(np.float32)
        
        # Normalize audio to the range [-1, 1]
        max_abs = np.max(np.abs(audio_array))
        if max_abs > 0:
            audio_array = audio_array / max_abs

        logger.info(f"Starting transcription for {len(audio_array) / 16000:.2f} seconds of audio.")
        
        # Start transcription in background thread
        if not self.is_initialized or self.model is None:
            logger.error("Transcription attempted before model was initialized.")
            if self.on_status_change:
                self.on_status_change("Error: Model not initialized.")
            if self.on_transcription_failed:
                self.on_transcription_failed("Model not initialized.")
            return False
        
        # Clean up any existing worker
        if self.transcription_worker and self.transcription_worker.isRunning():
            self.transcription_worker.terminate()
            self.transcription_worker.wait()
        
        # Create and start new worker
        self.transcription_worker = TranscriptionWorker(
            self.model, audio_array, self.config, self.model_lock
        )
        
        # Connect worker signals to callbacks
        if self.on_transcription_complete:
            self.transcription_worker.transcription_complete.connect(self._on_transcription_complete)
        if self.on_transcription_failed:
            self.transcription_worker.transcription_failed.connect(self._on_transcription_failed)
        if self.on_transcription_progress:
            self.transcription_worker.transcription_progress.connect(self.on_transcription_progress)
        
        self.transcription_worker.start()
        return True
    
    def _on_transcription_complete(self, text: str):
        """Internal handler for transcription completion."""
        logger.info(f"Transcription result: '{text}'")
        if self.on_transcription_complete:
            self.on_transcription_complete(text)
    
    def _on_transcription_failed(self, error: str):
        """Internal handler for transcription failure."""
        logger.error(f"Transcription failed: {error}")
        if self.on_transcription_failed:
            self.on_transcription_failed(error)

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
                try:
                    if indata.ndim > 1:
                        # If stereo, take only the first channel
                        indata = indata[:, 0]
                    self.audio_data.put_nowait(indata.copy())
                except queue.Full:
                    logger.warning("Audio data queue full, dropping chunk")
                self._update_volume(indata)

            try:
                self.stream = sd.InputStream(
                    samplerate=sample_rate,
                    channels=channels,
                    blocksize=blocksize,
                    callback=audio_callback,
                    dtype=np.float32,
                    device=self.config.microphone_device,
                )
            except sd.PortAudioError as e:
                logger.error(f"Failed to open audio device: {e}")
                if self.on_status_change:
                    self.on_status_change(f"Error: Audio device unavailable. {e}")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize audio stream: {e}")
                if self.on_status_change:
                    self.on_status_change(f"Error: Could not initialize audio. {e}")
                raise

            with self.stream:
                while not self.stop_event.is_set():
                    self._check_recording_limits()
                    time.sleep(0.1)
        except sd.PortAudioError as e:
            logger.exception(f"Audio device error: {e}")
            if self.on_status_change:
                self.on_status_change(f"Error: Audio device failed. {e}")
        except Exception as e:
            logger.exception(f"Error in audio recording thread: {e}")
            if self.on_status_change:
                self.on_status_change(f"Error: Audio recording failed. {e}")
        finally:
            if self.stream:
                try:
                    self.stream.close()
                except Exception as e:
                    logger.warning(f"Error closing audio stream: {e}")
                finally:
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
    
    def cleanup(self):
        """
        Ensures all resources are properly cleaned up.
        Should be called when the engine is no longer needed.
        """
        logger.info("Cleaning up VoiceClickEngine resources...")
        
        # Stop recording if active
        if self.is_recording:
            self.stop_event.set()
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=5.0)
            self.is_recording = False
        
        # Stop transcription worker if running
        if self.transcription_worker and self.transcription_worker.isRunning():
            self.transcription_worker.terminate()
            self.transcription_worker.wait(timeout=2.0)
            self.transcription_worker = None
        
        # Close audio stream
        if self.stream:
            try:
                self.stream.close()
            except Exception as e:
                logger.warning(f"Error closing stream during cleanup: {e}")
            finally:
                self.stream = None
        
        # Clear audio data queue
        while not self.audio_data.empty():
            try:
                self.audio_data.get_nowait()
            except queue.Empty:
                break
        
        logger.info("VoiceClickEngine cleanup complete.")
