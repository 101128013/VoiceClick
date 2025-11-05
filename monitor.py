"""
VoiceClick Development Monitor - Standalone Taskbar Widget
Monitors project progress in real-time, displays on top of taskbar
Auto-starts on system login
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush
from PyQt6.QtCore import QPoint
import os

# Logging setup
log_dir = Path.home() / '.voice_click'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - VoiceClick Monitor - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GreenProgressBar(QWidget):
    """Simple green-only progress bar - no background, just green fill."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0
        self.max_progress = 30
        self.setFixedHeight(4)  # Very thin, minimal
        self.setStyleSheet("border: none; background: transparent;")
    
    def set_progress(self, value: int):
        """Update progress (0-30 tasks)."""
        self.progress = min(max(value, 0), self.max_progress)
        self.update()
    
    def paintEvent(self, event):
        """Paint only green progress fill."""
        painter = QPainter(self)
        
        # Draw green progress only (no background)
        if self.max_progress > 0:
            progress_width = (self.progress / self.max_progress) * self.width()
            painter.fillRect(0, 0, int(progress_width), self.height(), 
                           QColor(76, 175, 80))  # Material Green
        
        painter.end()


class TaskbarProgressMonitor(QWidget):
    """
    Standalone taskbar monitoring widget
    - Sits on top of taskbar
    - Shows green progress bar + 2 lines of text
    - Non-interactive, read-only
    - Auto-hides/shows with taskbar
    """
    
    def __init__(self):
        super().__init__()
        self.current_task = 1
        self.total_tasks = 30
        self.setup_ui()
        self.setup_taskbar_position()
        self.setup_auto_update()
        self.load_progress()
        
        logger.info("TaskbarProgressMonitor initialized")
    
    def setup_ui(self):
        """Create minimal UI."""
        self.setWindowTitle("VoiceClick Monitor")
        
        # Make it float above taskbar
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.ToolTip
        )
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(1)
        
        # Progress bar (green only)
        self.progress_bar = GreenProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Line 1: Task info (bold)
        self.line1 = QLabel("Task 1/30: Initialize")
        font1 = QFont()
        font1.setPointSize(8)
        font1.setBold(True)
        self.line1.setFont(font1)
        self.line1.setStyleSheet("color: #2C3E50; background: white;")
        self.line1.setMargin(2)
        layout.addWidget(self.line1)
        
        # Line 2: Stage info (regular, gray)
        self.line2 = QLabel("Setup • 3% complete")
        font2 = QFont()
        font2.setPointSize(7)
        self.line2.setFont(font2)
        self.line2.setStyleSheet("color: #7F8C8D; background: white;")
        self.line2.setMargin(2)
        layout.addWidget(self.line2)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: none;
            }
        """)
    
    def setup_taskbar_position(self):
        """Position widget on top of taskbar."""
        # Get screen geometry
        screen = self.screen()
        screen_geom = screen.geometry()
        
        # Position at bottom, spanning taskbar width
        # Taskbar is usually 40-50px tall
        taskbar_height = 48
        x = 0
        y = screen_geom.height() - taskbar_height - 70  # Above taskbar
        width = 500  # Compact width
        height = 70   # Task info + progress
        
        self.setGeometry(x, y, width, height)
        logger.info(f"Widget positioned at ({x}, {y}) with size {width}x{height}")
    
    def setup_auto_update(self):
        """Setup auto-update timer."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second
    
    def load_progress(self):
        """Load current progress from file or settings."""
        try:
            config_file = Path.home() / '.voice_click' / 'progress.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    self.current_task = data.get('current_task', 1)
                    logger.info(f"Loaded progress: task {self.current_task}")
            else:
                self.current_task = 1
                logger.info("No progress file found, starting at task 1")
        except Exception as e:
            logger.error(f"Error loading progress: {e}")
            self.current_task = 1
    
    def save_progress(self):
        """Save current progress to file."""
        try:
            config_file = Path.home() / '.voice_click' / 'progress.json'
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'current_task': self.current_task,
                'timestamp': datetime.now().isoformat(),
                'total_tasks': self.total_tasks
            }
            
            with open(config_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
    
    def update_display(self):
        """Update widget display with current task info."""
        # Task definitions
        tasks_info = {
            1: ("Set up project repository", "Setup"),
            2: ("Define requirements", "Setup"),
            3: ("Refactor into modules", "Architecture"),
            4: ("Create config system", "Architecture"),
            5: ("Design main window", "UI Design"),
            6: ("Implement main window", "UI Development"),
            7: ("Build Status tab", "UI Development"),
            8: ("Build Settings tab", "UI Development"),
            9: ("Build History tab", "UI Development"),
            10: ("System tray integration", "UI Development"),
            11: ("Connect UI to engine", "Integration"),
            12: ("Create icons", "Assets"),
            13: ("Write unit tests", "Testing"),
            14: ("Create PyInstaller spec", "Packaging"),
            15: ("Test PyInstaller build", "Packaging"),
            16: ("Setup Windows 11 VM", "Testing"),
            17: ("Test on Windows 11 VM", "Testing"),
            18: ("Create NSIS installer", "Installer"),
            19: ("Build installer", "Installer"),
            20: ("Test installer on VM", "Testing"),
            21: ("Write documentation", "Documentation"),
            22: ("Setup CI/CD pipeline", "DevOps"),
            23: ("Beta testing", "Beta Testing"),
            24: ("Fix critical bugs", "Bug Fixes"),
            25: ("Create website", "Marketing"),
            26: ("Prepare release notes", "Release"),
            27: ("Create version tag", "Release"),
            28: ("Publish on GitHub", "Release"),
            29: ("Setup support channels", "Post-Release"),
            30: ("Plan feature roadmap", "Post-Release"),
        }
        
        # Get current task info
        task_name, stage = tasks_info.get(
            self.current_task, 
            ("Unknown Task", "Unknown")
        )
        
        percent = int((self.current_task / self.total_tasks) * 100)
        
        # Update UI
        self.line1.setText(
            f"Task {self.current_task}/{self.total_tasks}: {task_name} ({percent}%)"
        )
        self.line2.setText(f"{stage} • {percent}% complete")
        
        # Update progress bar
        self.progress_bar.set_progress(self.current_task)
    
    def set_task(self, task_number: int):
        """Manually set current task."""
        if 1 <= task_number <= self.total_tasks:
            self.current_task = task_number
            self.save_progress()
            self.update_display()
            logger.info(f"Task updated to {task_number}")
    
    def increment_task(self):
        """Move to next task."""
        if self.current_task < self.total_tasks:
            self.set_task(self.current_task + 1)
    
    def keyPressEvent(self, event):
        """Keyboard shortcuts for manual control."""
        if event.key() == Qt.Key.Key_Up:
            # Previous task
            if self.current_task > 1:
                self.set_task(self.current_task - 1)
        elif event.key() == Qt.Key.Key_Down:
            # Next task
            if self.current_task < self.total_tasks:
                self.set_task(self.current_task + 1)
        elif event.key() == Qt.Key.Key_Escape:
            # Hide widget (minimize to tray)
            self.hide()
            logger.info("Widget minimized")
    
    def mouseDoubleClickEvent(self, event):
        """Double-click to toggle visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
    
    def closeEvent(self, event):
        """Handle close - just hide instead."""
        self.hide()
        event.ignore()
        logger.info("Widget hidden (not closed)")


class AutoStartManager:
    """Manages auto-start on system login."""
    
    @staticmethod
    def enable_autostart():
        """Enable auto-start on Windows login."""
        try:
            import winreg
            
            # Path to this script
            script_path = Path(__file__).resolve()
            
            # Create batch file for auto-start
            batch_file = Path.home() / '.voice_click' / 'monitor_autostart.bat'
            batch_file.parent.mkdir(parents=True, exist_ok=True)
            
            batch_content = f"""@echo off
cd /d "{script_path.parent}"
python -m monitor
"""
            
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            # Add to Windows Startup registry
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "VoiceClickMonitor", 0, winreg.REG_SZ, 
                            f'"{batch_file}"')
            winreg.CloseKey(key)
            
            logger.info("Auto-start enabled")
            return True
        except Exception as e:
            logger.error(f"Failed to enable auto-start: {e}")
            return False
    
    @staticmethod
    def disable_autostart():
        """Disable auto-start."""
        try:
            import winreg
            
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, "VoiceClickMonitor")
            winreg.CloseKey(key)
            
            logger.info("Auto-start disabled")
            return True
        except Exception as e:
            logger.error(f"Failed to disable auto-start: {e}")
            return False


def main():
    """Run the monitor widget."""
    app = __import__('PyQt6.QtWidgets', fromlist=['QApplication']).QApplication(sys.argv)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--autostart':
            AutoStartManager.enable_autostart()
            return
        elif sys.argv[1] == '--disable-autostart':
            AutoStartManager.disable_autostart()
            return
        elif sys.argv[1] == '--set-task':
            if len(sys.argv) > 2:
                try:
                    task_num = int(sys.argv[2])
                    widget = TaskbarProgressMonitor()
                    widget.set_task(task_num)
                    return
                except ValueError:
                    print("Invalid task number")
                    return
    
    # Create and show widget
    widget = TaskbarProgressMonitor()
    widget.show()
    
    logger.info("VoiceClick Monitor started")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
