#!/usr/bin/env python3
"""
VoiceClick - Main Application Window
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QStatusBar, QLabel, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QTimer
from src.ui.tabs.status_tab import StatusTab
from src.ui.tabs.settings_tab import SettingsTab
from src.ui.tabs.history_tab import HistoryTab
from src.core.engine import VoiceClickEngine
from src.config.settings import Settings

class MainWindow(QMainWindow):
    """Main application window for VoiceClick."""

    def __init__(self):
        super().__init__()
        
        # Get icon paths
        self.icon_dir = Path(__file__).parent.parent / 'resources' / 'icons'
        
        # Initialize engine and settings
        self.settings = Settings()
        self.engine = VoiceClickEngine(self.settings)
        
        # Setup UI
        self.setup_ui()
        self.setup_system_tray()
        
        # Connect engine to UI
        self.connect_engine()
        
        # Initialize engine in background
        QTimer.singleShot(100, self.initialize_engine)

    def setup_ui(self):
        """Set up the main window's UI."""
        self.setWindowTitle("VoiceClick")
        self.setMinimumSize(800, 600)
        
        # Set window icon
        icon_path = self.icon_dir / 'voiceclick.ico'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Add tabs and pass engine reference
        self.status_tab = StatusTab()
        self.settings_tab = SettingsTab()
        self.history_tab = HistoryTab()

        self.tab_widget.addTab(self.status_tab, "Status")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.tab_widget.addTab(self.history_tab, "History")

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Menu bar
        self.create_menu_bar()
        
        # Setup update timer for real-time status
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(100)  # Update every 100ms

    def create_menu_bar(self):
        """Create the main menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        # Add actions for Edit menu later

        # View menu
        view_menu = menu_bar.addMenu("&View")
        # Add actions for View menu later

        # Tools menu
        tools_menu = menu_bar.addMenu("&Tools")
        # Add actions for Tools menu later

        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("&About", self)
        # about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set tray icon
        tray_icon_path = self.icon_dir / 'tray_icon.png'
        if tray_icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(tray_icon_path)))
        
        # Set tooltip
        self.tray_icon.setToolTip("VoiceClick - Voice to Text")
        
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

    def show_and_raise(self):
        """Show window and bring to front"""
        self.showNormal()
        self.raise_()
        self.activateWindow()
    
    def close_application(self):
        """Close application properly"""
        # Shutdown engine
        if hasattr(self, 'engine'):
            self.engine.shutdown()
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        """Handle window close"""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.close_application()
    
    def connect_engine(self):
        """Connect engine callbacks to UI updates"""
        # Set volume callback
        self.engine.on_volume_change = self.on_volume_update
        self.engine.on_status_change = self.on_status_update
        
        # Connect recording buttons
        self.status_tab.start_recording_clicked.connect(self.start_recording)
        self.status_tab.stop_recording_clicked.connect(self.stop_recording)
    
    def initialize_engine(self):
        """Initialize the engine asynchronously"""
        self.status_bar.showMessage("Loading Whisper model...")
        success = self.engine.initialize()
        if success:
            self.status_bar.showMessage("Model loaded successfully")
            self.status_tab.model_text.setText(f"Whisper Model: {self.settings.whisper_model}")
            self.status_tab.device_text.setText(f"Device: {self.settings.whisper_device}")
        else:
            self.status_bar.showMessage("Failed to load model")
    
    def update_status(self):
        """Update UI with current engine status"""
        status = self.engine.get_status()
        
        # Update status tab
        if status['is_recording']:
            duration = int(status['recording_duration'])
            self.status_tab.status_text.setText(f"Recording... ({duration}s)")
            self.status_tab.status_text.setStyleSheet("color: red; font-size: 12pt;")
            self.status_tab.set_recording_state(True)
        elif status['is_initialized']:
            self.status_tab.status_text.setText("Ready")
            self.status_tab.status_text.setStyleSheet("color: green; font-size: 12pt;")
            self.status_tab.set_recording_state(False)
        else:
            self.status_tab.status_text.setText("Initializing...")
            self.status_tab.status_text.setStyleSheet("color: orange; font-size: 12pt;")
            self.status_tab.set_recording_state(False)
    
    def start_recording(self):
        """Start recording audio"""
        if self.engine.start_recording():
            self.status_bar.showMessage("Recording started")
        else:
            self.status_bar.showMessage("Failed to start recording")
    
    def stop_recording(self):
        """Stop recording and get transcription"""
        self.status_bar.showMessage("Processing transcription...")
        transcription = self.engine.stop_recording()
        if transcription:
            self.status_bar.showMessage(f"Transcribed: {transcription[:50]}...")
            # TODO: Add to history
        else:
            self.status_bar.showMessage("No transcription available")
    
    def on_volume_update(self, volume):
        """Update volume meter when engine reports volume change"""
        self.status_tab.volume_bar.setValue(volume)
    
    def on_status_update(self, status_message):
        """Update status bar when engine reports status change"""
        self.status_bar.showMessage(status_message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
