"""
The Status Tab for the VoiceClick application.

This module defines the `StatusTab` class, which provides a real-time view of
the application's status, including recording state, microphone volume, and
transcription engine details.
"""

import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QGridLayout, QFrame
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect, QSize

from src.core.engine import VoiceClickEngine

logger = logging.getLogger(__name__)

class StatusTab(QWidget):
    """
    The StatusTab widget displays real-time information about the recording
    and transcription process.
    """
    start_recording_clicked = pyqtSignal()
    stop_recording_clicked = pyqtSignal()
    toggle_full_ui_clicked = pyqtSignal() # New signal to toggle full UI

    def __init__(self, engine: VoiceClickEngine, icon_dir: Path):
        """
        Initializes the StatusTab.

        Args:
            engine: An instance of VoiceClickEngine to get status updates from.
            icon_dir: Path to the icon directory.
        """
        super().__init__()
        self.engine = engine
        self.icon_dir = icon_dir
        
        # Initialize cache variables before setup_ui() is called
        self._last_status_text = ""
        self._last_is_recording = False
        self._is_processing = False
        self._last_volume = -1  # Track volume changes
        
        self.setup_ui()
        self.update_model_info()
        
        # Timer to periodically update dynamic status info
        # Reduced frequency for better performance (1000ms when not recording)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # Update every 1000ms when not recording

    def setup_ui(self):
        """Sets up the user interface for the status tab."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Horizontal layout for controls and status
        h_layout = QHBoxLayout()
        h_layout.setSpacing(10)

        # Start Button (Icon Button)
        self.start_button = QPushButton("") # No text, will use icon
        self.start_button.setIcon(QIcon(str(self.icon_dir / 'recording_icon.png')))
        self.start_button.setIconSize(QSize(24, 24))
        self.start_button.setFixedSize(40, 40)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #B0B0B0;
            }
        """)
        self.start_button.clicked.connect(self.start_recording_clicked.emit)

        # Stop Button (Icon Button)
        self.stop_button = QPushButton("") # No text, will use icon
        self.stop_button.setIcon(QIcon(str(self.icon_dir / 'stop_icon.png')))
        self.stop_button.setIconSize(QSize(24, 24))
        self.stop_button.setFixedSize(40, 40)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #C62828;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #B0B0B0;
            }
        """)
        self.stop_button.clicked.connect(self.stop_recording_clicked.emit)
        
        h_layout.addWidget(self.start_button)
        h_layout.addWidget(self.stop_button)

        # Volume Meter (simplified)
        self.volume_bar = QProgressBar()
        self.volume_bar.setRange(0, 100)
        self.volume_bar.setTextVisible(False) # Hide text for minimal view
        self.volume_bar.setFixedSize(100, 10)
        self.volume_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3e4451;
                border-radius: 5px;
                background-color: #21252b;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #50fa7b, stop:1 #ffb86c);
                border-radius: 4px;
            }
        """)
        h_layout.addWidget(self.volume_bar)
        
        # Status Text & Loading Indicator
        self.status_text = QLabel("Ready")
        self.status_text.setStyleSheet("color: #ABB2BF; font-size: 10pt;")
        h_layout.addWidget(self.status_text)

        self.loading_label = QLabel()
        self.loading_label.setFixedSize(16, 16)
        self.loading_label.setStyleSheet("background-color: transparent;")
        self.loading_label.hide()
        h_layout.addWidget(self.loading_label)
        
        h_layout.addStretch()
        # Front-face info label to show extra context on the compact/front face
        self.front_face_info = QLabel("")
        self.front_face_info.setStyleSheet("color: #ABB2BF; font-size: 9pt;")
        h_layout.addWidget(self.front_face_info)
        
        # Toggle Full UI Button (Icon Button)
        self.toggle_ui_button = QPushButton("")
        self.toggle_ui_button.setIcon(QIcon(str(self.icon_dir / 'settings_icon.png')))
        self.toggle_ui_button.setIconSize(QSize(20, 20))
        self.toggle_ui_button.setFixedSize(30, 30)
        self.toggle_ui_button.setStyleSheet("""
            QPushButton {
                background-color: #3e4451;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #4b5263;
            }
            QPushButton:pressed {
                background-color: #282c34;
            }
        """)
        self.toggle_ui_button.clicked.connect(self.toggle_full_ui_clicked.emit)
        h_layout.addWidget(self.toggle_ui_button)

        layout.addLayout(h_layout)
        layout.addStretch() # Push everything to the top

    def update_front_face_info(self, text: str):
        """Updates the extra front-face information label."""
        if hasattr(self, 'front_face_info'):
            self.front_face_info.setText(text)

    def _create_label(self, text: str, color: str = "#ABB2BF", size: int = 10, bold: bool = False) -> QLabel:
        """Helper function to create a styled QLabel."""
        label = QLabel(text)
        font = QFont("Segoe UI", size)
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
        # Safety check - ensure _is_processing exists
        if not hasattr(self, '_is_processing'):
            self._is_processing = False
        
        self.start_button.setEnabled(not is_recording and not self._is_processing)
        self.stop_button.setEnabled(is_recording)
        self._last_is_recording = is_recording
        
        if self._is_processing:
            return  # Don't override processing state
        
        if is_recording:
            status_text = "Recording..."
            status_style = "color: #98C379;"
            self._show_loading_indicator(is_recording=True)
        else:
            status_text = "Ready"
            status_style = "color: #ABB2BF;"
            self._hide_loading_indicator()
        
        # Only update if changed
        if self.status_text.text() != status_text:
            self.status_text.setText(status_text)
            self.status_text.setStyleSheet(status_style)

    def set_processing_state(self, is_processing: bool):
        """
        Updates the UI to show processing/transcription state.
        
        Args:
            is_processing: True if transcription is in progress, False otherwise.
        """
        self._is_processing = is_processing
        self.start_button.setEnabled(not is_processing and not self._last_is_recording)
        self.stop_button.setEnabled(False) # Disable stop button during processing
        
        if is_processing:
            self.status_text.setText("Processing...")
            self.status_text.setStyleSheet("color: #E5C07B;")
            self._show_loading_indicator(is_recording=False)
        else:
            self._hide_loading_indicator()
            self.set_recording_state(self._last_is_recording)

    def _show_loading_indicator(self, is_recording: bool):
        """
        Shows an animated loading indicator, adapting style for recording or processing.
        """
        self.loading_label.show()
        if is_recording:
            # Pulsating circle for recording
            self.loading_label.setStyleSheet("""
                QLabel {
                    background-color: #E06C75;
                    border-radius: 8px;
                    min-width: 16px;
                    min-height: 16px;
                    max-width: 16px;
                    max-height: 16px;
                    animation: pulse 1s infinite alternate;
                }
                @keyframes pulse {
                    0% { background-color: #E06C75; }
                    100% { background-color: #C24A54; }
                }
            """)
            # QPropertyAnimation for actual pulsing if CSS animation is not fully supported or desired
            if not hasattr(self, '_pulse_animation'):
                self._pulse_animation = QPropertyAnimation(self.loading_label, b"geometry")
                self._pulse_animation.setDuration(1000)
                self._pulse_animation.setLoopCount(-1)
                self._pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
                start_rect = QRect(0, 0, 16, 16)
                end_rect = QRect(0, 0, 18, 18) # Slightly larger
                self._pulse_animation.setStartValue(start_rect)
                self._pulse_animation.setEndValue(end_rect)
                self._pulse_animation.start()
        else:
            # Spinner for processing
            self.loading_label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: 2px solid #5C6370;
                    border-top: 2px solid #61afef;
                    border-radius: 8px;
                    min-width: 16px;
                    min-height: 16px;
                    max-width: 16px;
                    max-height: 16px;
                }
            """)
            if not hasattr(self, '_loading_timer'):
                self._loading_timer = QTimer(self)
                self._loading_timer.timeout.connect(self._animate_loading)
                self._loading_timer.start(100)
                self._loading_angle = 0
    
    def _animate_loading(self):
        """
        Animates the loading indicator for processing state.
        """
        if not self._is_processing:
            if hasattr(self, '_loading_timer'):
                self._loading_timer.stop()
            return
        
        # Rotate effect for spinner
        colors = ["#61afef", "#98c379", "#e5c07b", "#e06c75"]
        color_index = (self._loading_angle // 90) % len(colors)
        top_color = colors[color_index]
        
        self.loading_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                border: 2px solid #5C6370;
                border-top: 2px solid {top_color};
                border-radius: 8px;
                min-width: 16px;
                min-height: 16px;
                max-width: 16px;
                max-height: 16px;
            }}
        """)
        self._loading_angle = (self._loading_angle + 30) % 360
    
    def _hide_loading_indicator(self):
        """Hides the loading indicator."""
        self.loading_label.hide()
        if hasattr(self, '_loading_timer'):
            self._loading_timer.stop()
            del self._loading_timer
        if hasattr(self, '_pulse_animation'):
            self._pulse_animation.stop()
            del self._pulse_animation

    def _animate_button_hover(self, button: QPushButton, base_color: str, hover_color: str):
        """
        Adds smooth color transition animation to button hover.
        (Not directly used with current icon-button styling, but kept for potential future use)
        """
        pass

    def update_volume(self, volume: int):
        """
        Updates the volume progress bar.

        Args:
            volume: The current volume level (0-100).
        """
        # Only update if value changed significantly (>2% threshold) to reduce repaints
        if abs(self._last_volume - volume) > 2 or self._last_volume == -1:
            self.volume_bar.setValue(volume)
            self._last_volume = volume

    def update_model_info(self):
        """
        Updates the displayed information about the model and device.
        (No longer displayed in minimal UI, but kept for logic if needed elsewhere)
        """
        pass

    def update_status(self):
        """Periodically updates the status text, e.g., with recording duration."""
        is_recording = self.engine.is_recording
        
        # Don't update if processing
        if self._is_processing:
            return
        
        # Only update if recording state changed or if recording (to show duration)
        if is_recording != self._last_is_recording:
            self.set_recording_state(is_recording)
            # Adjust timer frequency based on state
            if is_recording:
                self.timer.start(500)  # Update more frequently when recording
            else:
                self.timer.start(1000)  # Update less frequently when idle
            return
        
        if is_recording:
            status = self.engine.get_status()
            duration = status.get("recording_time", 0) if status else 0
            new_text = f"Recording ({duration:.1f}s)"
            
            if self.status_text.text() != new_text:
                self.status_text.setText(new_text)
                self.status_text.setStyleSheet("color: #98C379;") # Recording color
        else:
            # If not recording and not processing, set to Ready
            if not self._is_processing and self.status_text.text() != "Ready":
                self.status_text.setText("Ready")
                self.status_text.setStyleSheet("color: #ABB2BF;")

