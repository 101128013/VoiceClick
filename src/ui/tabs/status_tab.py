#!/usr/bin/env python3
"""
VoiceClick - Status Tab
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal

class StatusTab(QWidget):
    """Status tab - displays real-time recording info"""
    
    # Signals
    start_recording_clicked = pyqtSignal()
    stop_recording_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup status display UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("VoiceClick Status")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Status section
        status_label = QLabel("Recording Status:")
        status_font = QFont()
        status_font.setBold(True)
        status_label.setFont(status_font)
        layout.addWidget(status_label)

        self.status_text = QLabel("Ready")
        self.status_text.setStyleSheet("color: green; font-size: 12pt;")
        layout.addWidget(self.status_text)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Recording")
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.start_recording_clicked.emit)
        
        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recording_clicked.emit)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        # Volume meter
        volume_label = QLabel("Microphone Volume:")
        volume_label.setFont(status_font)
        layout.addWidget(volume_label)

        self.volume_bar = QProgressBar()
        self.volume_bar.setRange(0, 100)
        self.volume_bar.setValue(0)
        layout.addWidget(self.volume_bar)

        # Model info
        model_label = QLabel("Current Model:")
        model_label.setFont(status_font)
        layout.addWidget(model_label)

        self.model_text = QLabel("Whisper Model: N/A")
        layout.addWidget(self.model_text)

        # Device info
        device_label = QLabel("Compute Device:")
        device_label.setFont(status_font)
        layout.addWidget(device_label)

        self.device_text = QLabel("Device: N/A")
        layout.addWidget(self.device_text)

        # Add stretch to push everything to top
        layout.addStretch()

        self.setLayout(layout)
    
    def set_recording_state(self, is_recording):
        """Update UI based on recording state"""
        self.start_button.setEnabled(not is_recording)
        self.stop_button.setEnabled(is_recording)
