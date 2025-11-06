"""
The Status Tab for the VoiceClick application.

This module defines the `StatusTab` class, which provides a real-time view of
the application's status, including recording state, microphone volume, and
transcription engine details.
"""

import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal, QTimer

from src.core.engine import VoiceClickEngine

logger = logging.getLogger(__name__)

class StatusTab(QWidget):
    """
    The StatusTab widget displays real-time information about the recording
    and transcription process.
    """
    start_recording_clicked = pyqtSignal()
    stop_recording_clicked = pyqtSignal()

    def __init__(self, engine: VoiceClickEngine):
        """
        Initializes the StatusTab.

        Args:
            engine: An instance of VoiceClickEngine to get status updates from.
        """
        super().__init__()
        self.engine = engine
        self.setup_ui()
        self.update_model_info()

        # Timer to periodically update dynamic status info
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(200)  # Update every 200ms

    def setup_ui(self):
        """Sets up the user interface for the status tab."""
        layout = QVBoxLayout(self)
        grid_layout = QGridLayout()

        title = QLabel("Real-Time Status")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Recording Status
        grid_layout.addWidget(self._create_label("Recording Status:"), 0, 0)
        self.status_text = self._create_label("Initializing...", "orange", 12)
        grid_layout.addWidget(self.status_text, 0, 1)

        # Control Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Recording")
        self.stop_button = QPushButton("Stop Recording")
        self.start_button.clicked.connect(self.start_recording_clicked.emit)
        self.stop_button.clicked.connect(self.stop_recording_clicked.emit)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        # Volume Meter
        grid_layout.addWidget(self._create_label("Microphone Volume:"), 1, 0)
        self.volume_bar = QProgressBar()
        self.volume_bar.setRange(0, 100)
        self.volume_bar.setTextVisible(False)
        grid_layout.addWidget(self.volume_bar, 1, 1)

        # Model Info
        grid_layout.addWidget(self._create_label("Transcription Model:"), 2, 0)
        self.model_text = self._create_label("N/A")
        grid_layout.addWidget(self.model_text, 2, 1)

        # Device Info
        grid_layout.addWidget(self._create_label("Compute Device:"), 3, 0)
        self.device_text = self._create_label("N/A")
        grid_layout.addWidget(self.device_text, 3, 1)

        layout.addLayout(grid_layout)
        layout.addStretch()
        self.set_recording_state(False)

    def _create_label(self, text: str, color: str = "black", size: int = 10, bold: bool = False) -> QLabel:
        """Helper function to create a styled QLabel."""
        label = QLabel(text)
        font = QFont("Arial", size)
        font.setBold(bold)
        label.setFont(font)
        label.setStyleSheet(f"color: {color};")
        return label

    def set_recording_state(self, is_recording: bool):
        """
        Updates the UI to reflect the current recording state.

        Args:
            is_recording: True if recording is active, False otherwise.
        """
        self.start_button.setEnabled(not is_recording)
        self.stop_button.setEnabled(is_recording)
        if is_recording:
            self.status_text.setText("Recording...")
            self.status_text.setStyleSheet("color: red; font-size: 12pt;")
        else:
            self.status_text.setText("Ready")
            self.status_text.setStyleSheet("color: green; font-size: 12pt;")

    def update_volume(self, volume: int):
        """
        Updates the volume progress bar.

        Args:
            volume: The current volume level (0-100).
        """
        self.volume_bar.setValue(volume)

    def update_model_info(self):
        """Updates the displayed information about the model and device."""
        config = self.engine.config
        self.model_text.setText(f"{config.whisper_model}")
        self.device_text.setText(f"{config.whisper_device.upper()} ({config.whisper_compute_type})")

    def update_status(self):
        """Periodically updates the status text, e.g., with recording duration."""
        if self.engine.is_recording:
            duration = self.engine.get_status().get("recording_time", 0)
            self.status_text.setText(f"Recording... ({duration:.1f}s)")

