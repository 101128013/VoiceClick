"""
The Settings Tab for the VoiceClick application.

This module defines the `SettingsTab` class, which provides a UI for configuring
the application's settings, such as the transcription model, device, and
recording behavior.
"""

import logging

import sounddevice as sd

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QSpinBox,
    QCheckBox, QPushButton, QMessageBox, QFormLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal

from src.config.settings import SettingsManager
from src.config import constants

logger = logging.getLogger(__name__)

class SettingsTab(QWidget):
    """
    The SettingsTab widget allows users to configure application settings.
    
    It interacts with the SettingsManager to load and save configurations.
    """
    settings_saved = pyqtSignal()

    def __init__(self, settings_manager: SettingsManager):
        """
        Initializes the SettingsTab.

        Args:
            settings_manager: An instance of SettingsManager to handle settings persistence.
        """
        super().__init__()
        self.settings_manager = settings_manager
        self.setup_ui()
        self.load_settings()
        self.connect_signals()

    def setup_ui(self):
        """Sets up the user interface for the settings tab."""
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        title = QLabel("Settings")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(title)

        # Model and Device Settings
        self.model_combo = QComboBox()
        self.model_combo.addItems(constants.WHISPER_MODELS)
        form_layout.addRow("Whisper Model:", self.model_combo)

        self.device_combo = QComboBox()
        self.device_combo.addItems(constants.COMPUTE_DEVICES)
        form_layout.addRow("Compute Device:", self.device_combo)

        self.compute_type_combo = QComboBox()
        self.compute_type_combo.addItems(constants.COMPUTE_TYPES)
        form_layout.addRow("Compute Type:", self.compute_type_combo)

        # Language Selection
        self.language_combo = QComboBox()
        languages = [
            ("Auto-detect", "auto"),
            ("English", "en"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de"),
            ("Italian", "it"),
            ("Portuguese", "pt"),
            ("Russian", "ru"),
            ("Japanese", "ja"),
            ("Chinese", "zh"),
            ("Korean", "ko"),
        ]
        for display_name, code in languages:
            self.language_combo.addItem(display_name, code)
        form_layout.addRow("Language:", self.language_combo)

        # Microphone Selection
        self.microphone_combo = QComboBox()
        self._populate_microphones()
        form_layout.addRow("Microphone:", self.microphone_combo)

        # Recording Settings
        self.silence_spinbox = QSpinBox()
        self.silence_spinbox.setRange(1, 60)
        self.silence_spinbox.setSuffix(" s")
        form_layout.addRow("Silence Duration:", self.silence_spinbox)

        self.autostart_focus_check = QCheckBox("Auto-start on text field focus")
        form_layout.addRow(self.autostart_focus_check)
        
        self.autostart_click_check = QCheckBox("Auto-start on left click")
        form_layout.addRow(self.autostart_click_check)

        self.save_button = QPushButton("Save Settings")
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addWidget(self.save_button)

    def _populate_microphones(self):
        """Populates the microphone combo box with available input devices."""
        try:
            devices = sd.query_devices()
            input_devices = []
            device_indices = []
            
            # Add default option
            self.microphone_combo.addItem("Default Microphone", None)
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    device_name = device['name']
                    # Show device index and name
                    display_name = f"{i}: {device_name}"
                    self.microphone_combo.addItem(display_name, i)
                    input_devices.append(display_name)
                    device_indices.append(i)
            
            logger.info(f"Found {len(input_devices)} input devices")
        except Exception as e:
            logger.error(f"Failed to query audio devices: {e}", exc_info=True)
            self.microphone_combo.addItem("Error loading devices", None)

    def connect_signals(self):
        """Connects UI element signals to their respective slots."""
        self.save_button.clicked.connect(self.save_settings)

    def load_settings(self):
        """Loads the current settings from the manager and updates the UI."""
        settings = self.settings_manager.get_settings()
        self.model_combo.setCurrentText(settings.whisper_model)
        self.device_combo.setCurrentText(settings.whisper_device)
        self.compute_type_combo.setCurrentText(settings.whisper_compute_type)
        self.silence_spinbox.setValue(int(settings.silence_duration))
        self.autostart_focus_check.setChecked(settings.auto_start_on_focus)
        self.autostart_click_check.setChecked(settings.auto_start_on_left_click)
        
        # Set language
        language_code = settings.language
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == language_code:
                self.language_combo.setCurrentIndex(i)
                break
        
        # Set microphone device
        microphone_device = settings.microphone_device
        if microphone_device is None:
            self.microphone_combo.setCurrentIndex(0)  # Default
        else:
            # Find the index of the device in the combo box
            for i in range(self.microphone_combo.count()):
                if self.microphone_combo.itemData(i) == microphone_device:
                    self.microphone_combo.setCurrentIndex(i)
                    break
        
        logger.info("Settings loaded into UI.")

    def save_settings(self):
        """Saves the current UI settings to the configuration file."""
        microphone_device = self.microphone_combo.currentData()
        
        language_code = self.language_combo.currentData()
        
        new_settings = {
            "whisper_model": self.model_combo.currentText(),
            "whisper_device": self.device_combo.currentText(),
            "whisper_compute_type": self.compute_type_combo.currentText(),
            "language": language_code,
            "silence_duration": float(self.silence_spinbox.value()),
            "auto_start_on_focus": self.autostart_focus_check.isChecked(),
            "auto_start_on_left_click": self.autostart_click_check.isChecked(),
            "microphone_device": microphone_device,
        }
        self.settings_manager.update_settings(new_settings)
        self.settings_saved.emit()
        
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
        logger.info("Settings saved from UI.")

