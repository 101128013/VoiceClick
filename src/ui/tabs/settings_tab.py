#!/usr/bin/env python3
"""
VoiceClick - Settings Tab
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QSpinBox, QCheckBox, QPushButton, QMessageBox
from PyQt6.QtGui import QFont

class SettingsTab(QWidget):
    """Settings tab - application configuration"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup settings UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Whisper Model selection
        model_label = QLabel("Whisper Model:")
        layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.addItems(['tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3'])
        layout.addWidget(self.model_combo)

        # Device selection
        device_label = QLabel("Compute Device:")
        layout.addWidget(device_label)

        self.device_combo = QComboBox()
        self.device_combo.addItems(['cpu', 'cuda', 'auto'])
        layout.addWidget(self.device_combo)

        # Silence detection threshold
        silence_label = QLabel("Silence Detection Threshold (seconds):")
        layout.addWidget(silence_label)

        self.silence_spinbox = QSpinBox()
        self.silence_spinbox.setRange(1, 30)
        self.silence_spinbox.setValue(2)
        layout.addWidget(self.silence_spinbox)

        # Auto-start option
        self.autostart_check = QCheckBox("Auto-start recording on hotkey")
        layout.addWidget(self.autostart_check)

        # Clipboard insertion option
        self.clipboard_check = QCheckBox("Use clipboard for text insertion")
        layout.addWidget(self.clipboard_check)

        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()
        self.setLayout(layout)

    def save_settings(self):
        """Save settings to configuration"""
        # This is a placeholder. Integration with settings manager is needed.
        QMessageBox.information(self, "Success", "Settings saved successfully! (Placeholder)")
