"""
Main application window for VoiceClick.

This module defines the `MainWindow` class, which serves as the main entry point
for the VoiceClick user interface. It sets up the window, tabs, system tray icon,
and connects UI elements to the core engine.
"""

import logging
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QStatusBar, QSystemTrayIcon, QMenu, QApplication
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QTimer

from src.ui.tabs.status_tab import StatusTab
from src.ui.tabs.settings_tab import SettingsTab
from src.ui.tabs.history_tab import HistoryTab
from src.core.engine import VoiceClickEngine
from src.config.settings import SettingsManager
from src.core.history import TranscriptionHistory
from src.core.text_detector import TextDetector
from src.core.hotkeys import HotkeyManager
from src.core.focus_monitor import FocusMonitor
from src.core.click_monitor import ClickMonitor
from src.core.text_field_monitor import TextFieldInfo

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    The main application window for VoiceClick.
    
    This class orchestrates the entire UI, including the tabbed interface for
    status, settings, and history, as well as system tray integration.
    """

    def __init__(self):
        """Initializes the MainWindow."""
        super().__init__()

        self.icon_dir = self._get_icon_dir()
        
        # Initialize core components
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.get_settings()
        self.history_manager = TranscriptionHistory(max_size=self.settings.history_size)
        self.engine = VoiceClickEngine(self.settings)
        self.text_detector = TextDetector()
        self.hotkey_manager = HotkeyManager()
        
        # Initialize monitoring systems
        self.focus_monitor = FocusMonitor(self.text_detector.text_field_monitor)
        self.click_monitor = ClickMonitor(self.text_detector.text_field_monitor)

        self.setup_ui()
        self.setup_system_tray()
        self.setup_hotkeys()
        self.setup_auto_start()
        self.connect_signals()

        # Defer engine initialization to prevent blocking the UI
        QTimer.singleShot(100, self.initialize_engine)
        logger.info("MainWindow initialized.")

    def _get_icon_dir(self) -> Path:
        """Determines the path to the icons directory."""
        # This handles running from source and from a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).resolve().parent.parent
        return base_path / 'resources' / 'icons'

    def setup_ui(self):
        """Sets up the main window's user interface."""
        self.setWindowTitle("VoiceClick")
        self.setWindowIcon(QIcon(str(self.icon_dir / 'voiceclick.ico')))
        self.resize(self.settings.window_width, self.settings.window_height)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Initialize tabs and pass core components
        self.status_tab = StatusTab(self.engine)
        self.settings_tab = SettingsTab(self.settings_manager)
        self.history_tab = HistoryTab(self.history_manager)

        self.tab_widget.addTab(self.status_tab, "Status")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.tab_widget.addTab(self.history_tab, "History")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready.")

        self.create_menu_bar()

    def create_menu_bar(self):
        """Creates the main menu bar with file and help menus."""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("&About", self)
        # about_action.triggered.connect(self.show_about_dialog) # Placeholder
        help_menu.addAction(about_action)

    def setup_system_tray(self):
        """Initializes the system tray icon and its context menu."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(str(self.icon_dir / 'tray_icon.png')))
        self.tray_icon.setToolTip("VoiceClick - Voice to Text")

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

    def setup_hotkeys(self):
        """Sets up global keyboard shortcuts."""
        if self.settings.enable_hotkeys:
            self.hotkey_manager.register_hotkey(
                self.settings.start_recording_hotkey,
                self.start_recording
            )
            self.hotkey_manager.register_hotkey(
                self.settings.stop_recording_hotkey,
                self.stop_recording
            )
            self.hotkey_manager.start()
            logger.info("Global hotkeys registered and started")

    def setup_auto_start(self):
        """Sets up automatic recording start based on focus and click events."""
        # Configure cooldown periods
        self.focus_monitor.set_cooldown_period(self.settings.auto_start_cooldown)
        self.click_monitor.set_cooldown_period(self.settings.auto_start_cooldown)
        
        # Register callbacks for auto-start
        if self.settings.auto_start_on_focus:
            self.focus_monitor.register_callback(self._on_text_field_focused)
            self.focus_monitor.start_monitoring()
            logger.info("Auto-start on focus enabled")
        
        if self.settings.auto_start_on_left_click:
            self.click_monitor.register_callback(self._on_text_field_clicked)
            self.click_monitor.start_monitoring()
            logger.info("Auto-start on click enabled")

    def _on_text_field_focused(self, field_info: TextFieldInfo):
        """Called when a text field gains focus."""
        if self._should_auto_start(field_info):
            logger.info(f"Auto-starting recording: {field_info.application_name} - {field_info.window_title}")
            self.start_recording()

    def _on_text_field_clicked(self, field_info: TextFieldInfo):
        """Called when a text field is clicked."""
        if self._should_auto_start(field_info):
            logger.info(f"Auto-starting recording on click: {field_info.application_name} - {field_info.window_title}")
            self.start_recording()

    def _should_auto_start(self, field_info: TextFieldInfo) -> bool:
        """
        Determines if recording should auto-start based on field info and settings.
        
        Args:
            field_info: Information about the text field
            
        Returns:
            True if recording should start, False otherwise
        """
        # Don't auto-start if already recording
        if self.engine.is_recording:
            return False
        
        # Don't auto-start if engine not initialized
        if not self.engine.is_initialized:
            return False
        
        # Check application whitelist/blacklist
        if field_info.application_name:
            app_name_lower = field_info.application_name.lower()
            
            # Check blacklist first
            if self.settings.app_blacklist:
                for blocked_app in self.settings.app_blacklist:
                    if blocked_app.lower() in app_name_lower:
                        logger.debug(f"App {field_info.application_name} is blacklisted")
                        return False
            
            # Check whitelist (if not empty)
            if self.settings.app_whitelist:
                allowed = False
                for allowed_app in self.settings.app_whitelist:
                    if allowed_app.lower() in app_name_lower:
                        allowed = True
                        break
                if not allowed:
                    logger.debug(f"App {field_info.application_name} not in whitelist")
                    return False
        
        return True

    def connect_signals(self):
        """Connects signals from UI components and the engine to slots."""
        # Engine to UI
        self.engine.on_volume_change = self.status_tab.update_volume
        self.engine.on_status_change = self.status_bar.showMessage

        # UI to Engine
        self.status_tab.start_recording_clicked.connect(self.start_recording)
        self.status_tab.stop_recording_clicked.connect(self.stop_recording)
        
        # Settings changes
        self.settings_tab.settings_saved.connect(self.on_settings_saved)

    def initialize_engine(self):
        """Initializes the transcription engine in a non-blocking way."""
        self.status_bar.showMessage("Loading transcription model...")
        if self.engine.initialize():
            self.status_bar.showMessage("Model loaded successfully.")
            self.status_tab.update_model_info()
        else:
            self.status_bar.showMessage("Error: Failed to load transcription model.")

    def start_recording(self):
        """Handles the start recording action."""
        if self.engine.start_recording():
            self.status_tab.set_recording_state(True)
        else:
            self.status_bar.showMessage("Error: Could not start recording.")

    def stop_recording(self):
        """Handles the stop recording action and processes the result."""
        self.status_tab.set_recording_state(False)
        self.status_bar.showMessage("Processing...")
        transcription = self.engine.stop_recording()

        if transcription:
            # Insert text into active text field
            if self.text_detector.insert_text(transcription):
                self.status_bar.showMessage(f"Transcribed and inserted: {transcription[:50]}...")
            else:
                self.status_bar.showMessage(f"Transcribed but insertion failed: {transcription[:50]}...")
                logger.warning("Failed to insert transcribed text into active text field")
            
            # Add to history
            self.history_manager.add_record(
                text=transcription,
                duration_seconds=self.engine.get_status().get("recording_time", 0),
                model_used=self.settings.whisper_model,
                language=self.settings.language
            )
            self.history_tab.refresh_history()
            
            # Show notification if enabled
            if self.settings.show_notification_on_transcription:
                self._show_transcription_notification(transcription)
        else:
            self.status_bar.showMessage("No transcription available.")

    def on_settings_saved(self):
        """Reloads settings and re-initializes components as needed."""
        logger.info("Settings have been saved, updating application state.")
        self.settings = self.settings_manager.get_settings()
        self.engine.config = self.settings
        self.history_manager.max_size = self.settings.history_size
        
        # Re-initialize hotkeys if settings changed
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        self.setup_hotkeys()
        
        # Re-initialize auto-start monitors
        self.focus_monitor.stop_monitoring()
        self.click_monitor.stop_monitoring()
        self.focus_monitor.unregister_callback(self._on_text_field_focused)
        self.click_monitor.unregister_callback(self._on_text_field_clicked)
        self.setup_auto_start()
        
        # Re-initialize engine if model or device changed
        # This is a simplified approach; a more robust solution would check specific settings.
        self.initialize_engine()
        self.status_bar.showMessage("Settings updated and applied.")

    def show_and_raise(self):
        """Shows the window and brings it to the front."""
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        """
        Handles the window close event. Hides to tray if enabled, otherwise quits.
        """
        # Save window geometry
        self.settings.window_width = self.width()
        self.settings.window_height = self.height()
        self.settings_manager.save()

        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.close_application()

    def _show_transcription_notification(self, text: str):
        """Shows a system tray notification for completed transcription."""
        if self.tray_icon.isVisible():
            preview = text[:100] + "..." if len(text) > 100 else text
            self.tray_icon.showMessage(
                "VoiceClick - Transcription Complete",
                preview,
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )

    def close_application(self):
        """Ensures a clean shutdown of the application."""
        logger.info("Closing VoiceClick application.")
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        if self.focus_monitor:
            self.focus_monitor.stop_monitoring()
        if self.click_monitor:
            self.click_monitor.stop_monitoring()
        self.tray_icon.hide()
        QApplication.quit()

