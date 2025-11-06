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
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QStatusBar, QSystemTrayIcon, QMenu, QApplication, QMessageBox, QStackedWidget,
    QPushButton
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, QSize

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
from src.core.updater import Updater

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
        # Track drag offset for a frameless window
        self._drag_position = None

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
        
        # Initialize updater
        self.updater = Updater(check_on_startup=self.settings.check_for_updates)

        self.setup_ui()
        # Compute minimal height (half of full height) for compact UI
        try:
            self.minimal_height = int(self.settings.window_height * 0.5)
        except Exception:
            self.minimal_height = 400
        self.setup_system_tray()
        self.setup_hotkeys()
        self.setup_auto_start()
        self.connect_signals()

        # Defer engine initialization to prevent blocking the UI
        QTimer.singleShot(100, self.initialize_engine)
        
        # Check for updates after a delay (non-blocking)
        if self.settings.check_for_updates:
            QTimer.singleShot(5000, self.check_for_updates)
        
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

        # Set window to always be on top and frameless
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

        # Apply dark theme styling to the main window and its components
        self.setStyleSheet("""
            QMainWindow {
                background-color: #282c34;
                color: #abb2bf;
                border-radius: 10px; /* Rounded corners for frameless window */
                border: 1px solid #61afef;
            }
            QStackedWidget {
                background-color: #282c34;
            }
            /* Styles for tabs within the QStackedWidget (if any, will be refined) */
            QTabBar::tab {
                background-color: #3e4451;
                color: #abb2bf;
                padding: 10px 20px;
                margin-right: 3px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 10pt;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #61afef;
                color: #282c34;
            }
            QTabBar::tab:hover:!selected {
                background-color: #4b5263;
            }
            QStatusBar {
                background-color: #21252b;
                border-top: 1px solid #3e4451;
                color: #abb2bf;
                padding: 6px;
                font-size: 9pt;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QMenuBar {
                background-color: #21252b;
                border-bottom: 1px solid #3e4451;
                padding: 4px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            QMenuBar::item {
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #3e4451;
            }
            QMenu {
                background-color: #21252b;
                border: 1px solid #3e4451;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 32px 8px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3e4451;
                color: #61afef;
            }
            /* General styling for labels, buttons, inputs in dark theme */
            QLabel {
                color: #abb2bf;
            }
            QPushButton {
                background-color: #61afef;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #52a0da;
            }
            QPushButton:pressed {
                background-color: #468cbb;
            }
            QPushButton:disabled {
                background-color: #3e4451;
                color: #7f848e;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #21252b;
                border: 1px solid #3e4451;
                color: #abb2bf;
                border-radius: 4px;
                padding: 5px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #61afef;
            }
            QHeaderView::section {
                background-color: #3e4451;
                color: #abb2bf;
                padding: 5px;
                border: 1px solid #282c34;
            }
            QTableWidget {
                background-color: #282c34;
                color: #abb2bf;
                border: 1px solid #3e4451;
                selection-background-color: #4b5263;
                selection-color: #61afef;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Initialize tabs and pass core components
        self.status_tab = StatusTab(self.engine, self.icon_dir)
        self.settings_tab = SettingsTab(self.settings_manager)
        self.history_tab = HistoryTab(self.history_manager, self.icon_dir)
        
        # Create a widget for the full UI (settings and history)
        self.full_ui_widget = QWidget()
        full_ui_layout = QVBoxLayout(self.full_ui_widget)
        
        # Add a minimize button at the top of the full UI
        minimize_button = QPushButton("")
        minimize_button.setIcon(QIcon(str(self.icon_dir / 'collapse_icon.png')))
        minimize_button.setIconSize(QSize(20, 20))
        minimize_button.setFixedSize(30, 30)
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #3e4451;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #4b5263;
            }
            QPushButton:pressed {
                background-color: #5c6370;
            }
        """)
        minimize_button.clicked.connect(self.toggle_full_ui)
        
        # Layout for the minimize button (top right)
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        header_layout.addWidget(minimize_button)
        full_ui_layout.addLayout(header_layout)
        
        self.full_ui_tabs = QTabWidget()
        self.full_ui_tabs.addTab(self.settings_tab, "Settings")
        self.full_ui_tabs.addTab(self.history_tab, "History")
        full_ui_layout.addWidget(self.full_ui_tabs)

        # Use a stacked widget to manage different views (minimal/full)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.status_tab)       # Index 0: Minimal Status View
        self.stacked_widget.addWidget(self.full_ui_widget)  # Index 1: Full UI View

        main_layout.addWidget(self.stacked_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready.")

        self.create_menu_bar()

    def create_menu_bar(self):
        # For a minimal, always-on-top window, the traditional menu bar is removed.
        # Menu actions will be integrated into the status panel or system tray if needed.
        pass

    def setup_system_tray(self):
        """Initializes the system tray icon and its context menu."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(str(self.icon_dir / 'tray_icon.png')))
        self.tray_icon.setToolTip("VoiceClick - Voice to Text")

        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show Full UI")
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
        self.engine.on_transcription_complete = self.on_transcription_complete
        self.engine.on_transcription_failed = self.on_transcription_failed
        self.engine.on_transcription_progress = self.on_transcription_progress

        # UI to Engine
        self.status_tab.start_recording_clicked.connect(self.start_recording)
        self.status_tab.stop_recording_clicked.connect(self.stop_recording)
        self.status_tab.toggle_full_ui_clicked.connect(self.toggle_full_ui)
        
        # Settings changes
        self.settings_tab.settings_saved.connect(self.on_settings_saved)

    def initialize_engine(self):
        """Initializes the transcription engine in a non-blocking way."""
        self.status_bar.showMessage("Loading transcription model...")
        if self.engine.initialize():
            self.status_bar.showMessage("Model loaded successfully.")
            self.status_tab.update_model_info()
            # Update front-face info with current model details
            front_text = f"Model: {getattr(self.settings, 'whisper_model', 'unknown')} | Language: {getattr(self.settings, 'language', 'auto')}"
            try:
                self.status_tab.update_front_face_info(front_text)
            except Exception:
                pass
        else:
            self.status_bar.showMessage("Error: Failed to load transcription model.")

    def start_recording(self):
        """Handles the start recording action."""
        if self.engine.start_recording():
            self.status_tab.set_recording_state(True)
        else:
            self.status_bar.showMessage("Error: Could not start recording.")

    def stop_recording(self):
        """Handles the stop recording action and starts async transcription."""
        self.status_tab.set_recording_state(False)
        self.status_bar.showMessage("Processing...")
        self.status_tab.set_processing_state(True)
        
        # Start async transcription - result will come via callback
        if not self.engine.stop_recording():
            self.status_bar.showMessage("Error: Could not stop recording.")
            self.status_tab.set_processing_state(False)
    
    def on_transcription_progress(self, message: str):
        """Handles transcription progress updates."""
        self.status_bar.showMessage(message)
    
    def on_transcription_complete(self, transcription: str):
        """Handles successful transcription completion."""
        self.status_tab.set_processing_state(False)
        
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
    
    def on_transcription_failed(self, error: str):
        """Handles transcription failure."""
        self.status_tab.set_processing_state(False)
        self.status_bar.showMessage(f"Transcription failed: {error}")
        logger.error(f"Transcription failed: {error}")

    def toggle_full_ui(self):
        """
        Toggles between the minimal status UI and the full settings/history UI.
        """
        if self.stacked_widget.currentIndex() == 0:
            self.stacked_widget.setCurrentIndex(1) # Show full UI
            self.setFixedSize(self.settings.window_width, self.settings.window_height)
        else:
            self.stacked_widget.setCurrentIndex(0) # Show minimal UI
            # Half the full height for compact UI
            self.setFixedSize(self.settings.window_width, getattr(self, 'minimal_height', 400))

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
        # Update front-face info after settings saved
        try:
            front_text = f"Model: {getattr(self.settings, 'whisper_model', 'unknown')} | Language: {getattr(self.settings, 'language', 'auto')}"
            self.status_tab.update_front_face_info(front_text)
        except Exception:
            pass
        self.status_bar.showMessage("Settings updated and applied.")

    def show_and_raise(self):
        """Shows the window and brings it to the front."""
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def mousePressEvent(self, event):
        # Enable dragging the frameless window with the left mouse button
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_position is not None:
            delta = event.globalPosition().toPoint() - self._drag_position
            self.move(self.pos() + delta)
            self._drag_position = event.globalPosition().toPoint()
            event.accept()

    def closeEvent(self, event):
        """
        Handles the window close event. Hides to tray if enabled, otherwise quits.
        """
        # Save window geometry if showing full UI
        if self.stacked_widget.currentIndex() == 1:
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

    def check_for_updates(self):
        """Checks for available updates (non-blocking)."""
        try:
            update_info = self.updater.check_for_updates()
            if update_info and update_info.is_available:
                self._show_update_notification(update_info)
        except Exception as e:
            logger.error(f"Error checking for updates: {e}", exc_info=True)
    
    def _show_update_notification(self, update_info):
        """Shows a notification about available update."""
        reply = QMessageBox.question(
            self,
            "Update Available",
            f"A new version ({update_info.version}) is available!\n\n"
            f"Would you like to download it now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._download_update(update_info)
    
    def _download_update(self, update_info):
        """Downloads the update installer."""
        try:
            download_path = self.updater.download_update()
            if download_path:
                QMessageBox.information(
                    self,
                    "Update Downloaded",
                    f"Update downloaded to:\n{download_path}\n\n"
                    "Please run the installer to update VoiceClick."
                )
        except Exception as e:
            logger.error(f"Error downloading update: {e}", exc_info=True)
            QMessageBox.warning(
                self,
                "Download Failed",
                f"Failed to download update:\n{e}"
            )

    def close_application(self):
        """Ensures a clean shutdown of the application."""
        logger.info("Closing VoiceClick application.")
        
        try:
            # Stop hotkeys
            if self.hotkey_manager:
                try:
                    self.hotkey_manager.stop()
                except Exception as e:
                    logger.error(f"Error stopping hotkey manager: {e}", exc_info=True)
            
            # Stop monitoring systems
            if self.focus_monitor:
                try:
                    self.focus_monitor.stop_monitoring()
                except Exception as e:
                    logger.error(f"Error stopping focus monitor: {e}", exc_info=True)
            
            if self.click_monitor:
                try:
                    self.click_monitor.stop_monitoring()
                except Exception as e:
                    logger.error(f"Error stopping click monitor: {e}", exc_info=True)
            
            # Cleanup engine
            if self.engine:
                try:
                    self.engine.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up engine: {e}", exc_info=True)
            
            # Hide tray icon
            if self.tray_icon:
                try:
                    self.tray_icon.hide()
                except Exception as e:
                    logger.warning(f"Error hiding tray icon: {e}")
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}", exc_info=True)
        finally:
            QApplication.quit()
    
    def cleanup(self):
        """
        Ensures all resources are properly cleaned up.
        Should be called when the window is closing.
        """
        logger.info("Cleaning up MainWindow resources...")
        self.close_application()

