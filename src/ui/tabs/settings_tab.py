"""
The Settings Tab for the VoiceClick application.

This module defines the `SettingsTab` class, which provides a UI for configuring
the application's settings, such as the transcription model, device, and
recording behavior.
"""

import logging
from pathlib import Path

import sounddevice as sd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QSpinBox,
    QCheckBox, QPushButton, QMessageBox, QFormLayout, QFrame, QHBoxLayout
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import pyqtSignal, QSize

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
        # Icon directory (relative to repo root)
        self.icon_dir = Path(__file__).resolve().parents[4] / 'resources' / 'icons'
        self.setup_ui()
        self.load_settings()
        self.connect_signals()

    def setup_ui(self):
        """Sets up the user interface for the settings tab."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #61afef; margin-bottom: 15px;")
        main_layout.addWidget(title)

        # Settings Card
        settings_card = QFrame()
        settings_card.setStyleSheet("""
            QFrame {
                background-color: #21252b;
                border: 1px solid #3e4451;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QFormLayout(settings_card)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(10, 10, 10, 10)

        # Model and Device Settings
        self.model_combo = QComboBox()
        self.model_combo.addItems(constants.WHISPER_MODELS)
        self.model_combo.setStyleSheet(self._get_combo_style())
        form_layout.addRow(self._create_form_label("Whisper Model:"), self.model_combo)

        self.device_combo = QComboBox()
        self.device_combo.addItems(constants.COMPUTE_DEVICES)
        self.device_combo.setStyleSheet(self._get_combo_style())
        form_layout.addRow(self._create_form_label("Compute Device:"), self.device_combo)

        self.compute_type_combo = QComboBox()
        self.compute_type_combo.addItems(constants.COMPUTE_TYPES)
        self.compute_type_combo.setStyleSheet(self._get_combo_style())
        form_layout.addRow(self._create_form_label("Compute Type:"), self.compute_type_combo)

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
        self.language_combo.setStyleSheet(self._get_combo_style())
        form_layout.addRow(self._create_form_label("Language:"), self.language_combo)

        # Microphone Selection
        self.microphone_combo = QComboBox()
        self._populate_microphones()
        self.microphone_combo.setStyleSheet(self._get_combo_style())
        form_layout.addRow(self._create_form_label("Microphone:"), self.microphone_combo)

        # Recording Settings
        self.silence_spinbox = QSpinBox()
        self.silence_spinbox.setRange(1, 60)
        self.silence_spinbox.setSuffix(" s")
        self.silence_spinbox.setStyleSheet(self._get_spinbox_style())
        form_layout.addRow(self._create_form_label("Silence Duration:"), self.silence_spinbox)

        self.autostart_focus_check = QCheckBox("Auto-start on text field focus")
        self.autostart_focus_check.setStyleSheet(self._get_checkbox_style())
        form_layout.addRow("", self.autostart_focus_check)
        
        self.autostart_click_check = QCheckBox("Auto-start on left click")
        self.autostart_click_check.setStyleSheet(self._get_checkbox_style())
        form_layout.addRow("", self.autostart_click_check)

        main_layout.addWidget(settings_card)
        main_layout.addStretch()

        # Save Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #98C379;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #83AD6B;
            }
            QPushButton:pressed {
                background-color: #729B5C;
            }
        """)
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

    def _create_form_label(self, text: str) -> QLabel:
        """Creates a styled label for form fields."""
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal))
        label.setStyleSheet("color: #ABB2BF; padding: 5px;") # Dark theme text color
        return label

    def _get_combo_style(self) -> str:
        """Returns style sheet for combo boxes."""
        chevron_path = str(self.icon_dir / 'chevron-down.svg')
        return f"""
            QComboBox {{
                background-color: #21252b;
                border: 1px solid #5C6370;
                border-radius: 4px;
                padding: 5px;
                font-size: 10pt;
                min-width: 200px;
                color: #ABB2BF;
            }}
            QComboBox:hover {{
                border-color: #61afef;
            }}
            QComboBox:focus {{
                border-color: #61afef;
                background-color: #282c34;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: url("{chevron_path}");
                width: 12px;
                height: 12px;
            }}
        """

    def _get_spinbox_style(self) -> str:
        """
        Returns style sheet for spin boxes.
        """
        up_path = str(self.icon_dir / 'arrow-up.svg')
        down_path = str(self.icon_dir / 'arrow-down.svg')
        css_template = """
            QSpinBox {{
                background-color: #21252b;
                border: 1px solid #5C6370;
                border-radius: 4px;
                padding: 5px;
                font-size: 10pt;
                min-width: 100px;
                color: #ABB2BF;
            }}
            QSpinBox:hover {{
                border-color: #61afef;
            }}
            QSpinBox:focus {{
                border-color: #61afef;
                background-color: #282c34;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                border: none;
                background-color: #3e4451;
                width: 18px;
                border-radius: 2px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: #4b5263;
            }}
            QSpinBox::up-arrow {{
                image: url("{up_path}");
                width: 10px;
                height: 10px;
            }}
            QSpinBox::down-arrow {{
                image: url("{down_path}");
                width: 10px;
                height: 10px;
            }}
        """
        return css_template.format(up_path=up_path, down_path=down_path)

    def _get_checkbox_style(self) -> str:
        """
        Returns style sheet for checkboxes.
        """
        return """
            QCheckBox {
                font-size: 10pt;
                color: #ABB2BF;
                spacing: 6px;
                padding: 4px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #5C6370;
                border-radius: 3px;
                background-color: #21252b;
            }
            QCheckBox::indicator:hover {
                border-color: #61afef;
            }
            QCheckBox::indicator:checked {
                background-color: #98C379;
                border-color: #98C379;
                image: none;
            }
        """

