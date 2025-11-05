"""
VoiceClick Main Application Window
PyQt6-based GUI for the VoiceClick voice-to-text application
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QStatusBar, QSystemTrayIcon, QMenu, QMessageBox,
    QSlider, QSpinBox, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap
from PyQt6.QtWidgets import QApplication
import logging

from src.core.engine import VoiceClickEngine
from src.config.settings import Settings
from src.core.history import TranscriptionHistory

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - VoiceClick - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RecordingThread(QThread):
    """Thread for handling audio recording without blocking UI"""
    
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal(str)  # Emits transcribed text
    recording_error = pyqtSignal(str)    # Emits error message
    volume_updated = pyqtSignal(int)     # Emits volume level (0-100)
    
    def __init__(self, engine: VoiceClickEngine):
        super().__init__()
        self.engine = engine
        self.is_recording = False
    
    def run(self):
        """Start recording"""
        try:
            self.recording_started.emit()
            self.is_recording = True
            
            # Start recording (this is a blocking call)
            transcribed_text = self.engine.start_recording()
            
            self.recording_stopped.emit(transcribed_text)
        except Exception as e:
            self.recording_error.emit(str(e))
            logger.error(f"Recording error: {e}")
        finally:
            self.is_recording = False
    
    def stop(self):
        """Stop recording"""
        self.engine.stop_recording()
        self.is_recording = False


class StatusDisplay(QWidget):
    """Status tab - displays real-time recording info"""
    
    def __init__(self, engine: VoiceClickEngine):
        super().__init__()
        self.engine = engine
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
        
        self.model_text = QLabel(f"Whisper Model: {self.engine.model_size}")
        layout.addWidget(self.model_text)
        
        # Device info
        device_label = QLabel("Compute Device:")
        device_label.setFont(status_font)
        layout.addWidget(device_label)
        
        self.device_text = QLabel(f"Device: {self.engine.compute_device}")
        layout.addWidget(self.device_text)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        self.setLayout(layout)


class SettingsDisplay(QWidget):
    """Settings tab - application configuration"""
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
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
        self.model_combo.addItems(['tiny', 'base', 'small', 'medium', 'large'])
        self.model_combo.setCurrentText(self.settings.model_size)
        layout.addWidget(self.model_combo)
        
        # Silence detection threshold
        silence_label = QLabel("Silence Detection Threshold (seconds):")
        layout.addWidget(silence_label)
        
        self.silence_spinbox = QSpinBox()
        self.silence_spinbox.setRange(1, 30)
        self.silence_spinbox.setValue(int(self.settings.silence_threshold))
        layout.addWidget(self.silence_spinbox)
        
        # Auto-start option
        self.autostart_check = QCheckBox("Auto-start recording on hotkey")
        self.autostart_check.setChecked(self.settings.auto_start_enabled)
        layout.addWidget(self.autostart_check)
        
        # Clipboard insertion option
        self.clipboard_check = QCheckBox("Use clipboard for text insertion")
        self.clipboard_check.setChecked(self.settings.use_clipboard)
        layout.addWidget(self.clipboard_check)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def save_settings(self):
        """Save settings to configuration"""
        self.settings.model_size = self.model_combo.currentText()
        self.settings.silence_threshold = self.silence_spinbox.value()
        self.settings.auto_start_enabled = self.autostart_check.isChecked()
        self.settings.use_clipboard = self.clipboard_check.isChecked()
        self.settings.save()
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")
        logger.info("Settings saved")


class HistoryDisplay(QWidget):
    """History tab - view transcription history"""
    
    def __init__(self, history: TranscriptionHistory):
        super().__init__()
        self.history = history
        self.setup_ui()
    
    def setup_ui(self):
        """Setup history display UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Transcription History")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Create table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "Timestamp", "Duration (s)", "Text", "Model"
        ])
        self.history_table.setColumnWidth(0, 180)
        self.history_table.setColumnWidth(1, 100)
        self.history_table.setColumnWidth(2, 300)
        self.history_table.setColumnWidth(3, 80)
        
        layout.addWidget(self.history_table)
        
        # Load history button
        load_btn = QPushButton("Refresh History")
        load_btn.clicked.connect(self.load_history)
        layout.addWidget(load_btn)
        
        # Load initial history
        self.load_history()
        
        self.setLayout(layout)
    
    def load_history(self):
        """Load and display history from file"""
        try:
            records = self.history.get_all()
            self.history_table.setRowCount(len(records))
            
            for row, record in enumerate(reversed(records)):  # Most recent first
                self.history_table.setItem(row, 0, QTableWidgetItem(record.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
                self.history_table.setItem(row, 1, QTableWidgetItem(f"{record.duration:.2f}"))
                self.history_table.setItem(row, 2, QTableWidgetItem(record.text[:100]))  # First 100 chars
                self.history_table.setItem(row, 3, QTableWidgetItem(record.model))
        except Exception as e:
            logger.error(f"Error loading history: {e}")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceClick - Voice to Text Application")
        self.setGeometry(100, 100, 900, 600)
        
        # Initialize core components
        self.settings = Settings()
        self.engine = VoiceClickEngine()
        self.history = TranscriptionHistory()
        
        # Recording thread
        self.recording_thread = None
        
        # Setup UI
        self.setup_ui()
        self.setup_system_tray()
        
        # Connect signals
        self.connect_signals()
        
        logger.info("VoiceClick main window initialized")
    
    def setup_ui(self):
        """Setup main window UI"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header with app title and record button
        header_layout = QHBoxLayout()
        
        title = QLabel("VoiceClick")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        # Record button (prominent)
        self.record_btn = QPushButton("🎤 START RECORDING")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.record_btn.clicked.connect(self.start_recording)
        header_layout.addStretch()
        header_layout.addWidget(self.record_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tabs for different views
        self.tabs = QTabWidget()
        
        # Status tab
        self.status_display = StatusDisplay(self.engine)
        self.tabs.addTab(self.status_display, "Status")
        
        # Settings tab
        self.settings_display = SettingsDisplay(self.settings)
        self.tabs.addTab(self.settings_display, "Settings")
        
        # History tab
        self.history_display = HistoryDisplay(self.history)
        self.tabs.addTab(self.history_display, "History")
        
        main_layout.addWidget(self.tabs)
        
        central_widget.setLayout(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Tray menu
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show_and_raise)
        
        hide_action = tray_menu.addAction("Hide")
        hide_action.triggered.connect(self.hide)
        
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.close_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def connect_signals(self):
        """Connect application signals"""
        # You can add more signal connections here for real-time updates
        pass
    
    def start_recording(self):
        """Start recording in a separate thread"""
        if self.recording_thread is None or not self.recording_thread.is_running():
            self.record_btn.setText("🎤 RECORDING...")
            self.record_btn.setEnabled(False)
            self.statusBar().showMessage("Recording...")
            
            self.recording_thread = RecordingThread(self.engine)
            self.recording_thread.recording_stopped.connect(self.on_recording_complete)
            self.recording_thread.recording_error.connect(self.on_recording_error)
            self.recording_thread.start()
    
    def on_recording_complete(self, text):
        """Handle recording completion"""
        self.record_btn.setText("🎤 START RECORDING")
        self.record_btn.setEnabled(True)
        self.statusBar().showMessage(f"Transcribed: {text[:50]}...")
        
        # Add to history
        self.history.add_record(
            text=text,
            duration=0,  # Would get actual duration from engine
            model=self.settings.model_size
        )
        
        # Refresh history display
        self.history_display.load_history()
        
        logger.info(f"Recording complete: {text}")
    
    def on_recording_error(self, error):
        """Handle recording error"""
        self.record_btn.setText("🎤 START RECORDING")
        self.record_btn.setEnabled(True)
        self.statusBar().showMessage(f"Error: {error}")
        
        QMessageBox.critical(self, "Recording Error", error)
        logger.error(f"Recording error: {error}")
    
    def show_and_raise(self):
        """Show window and bring to front"""
        self.showNormal()
        self.raise_()
        self.activateWindow()
    
    def close_application(self):
        """Close application properly"""
        self.engine.shutdown()
        self.history.save()
        self.settings.save()
        self.tray_icon.hide()
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.close_application()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
