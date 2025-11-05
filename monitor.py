#!/usr/bin/env python3
"""
VoiceClick Development Progress Monitor
Simple taskbar widget showing project progress
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint
from PyQt6.QtGui import QFont, QColor

from src.ui.progress_widget import ProgressBarWidget, DevelopmentProgressWidget
from src.ui.progress_manager import DevelopmentProgressManager


class ProgressMonitor(QMainWindow):
    """Minimal monitor widget showing development progress."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceClick Progress")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        
        # Set background and border to make it visible
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
                border: 2px solid #00aa00;
                border-radius: 4px;
            }
        """)
        
        # Create widget
        self.progress_widget = DevelopmentProgressWidget()
        self.setCentralWidget(self.progress_widget)
        
        # Set size - make it taskbar height
        self.setFixedSize(500, 40)
        
        # Position RIGHT above taskbar (taskbar is typically 40-48px tall)
        screen = QApplication.primaryScreen().geometry()
        taskbar_height = 48  # Standard Windows 11 taskbar height
        widget_height = 40
        
        # Position at bottom-right, just above taskbar
        x = screen.right() - 510  # 10px margin from right edge
        y = screen.bottom() - taskbar_height - widget_height
        self.move(x, y)
        
        # Timer to update progress
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(1000)
        
        # Load progress manager
        self.manager = DevelopmentProgressManager()
    
    def update_progress(self):
        """Update the displayed progress."""
        try:
            current_task = self.manager.current_task_index
            task = self.manager.tasks[current_task]
            progress = (current_task + 1) / 30 * 100
            
            self.progress_widget.set_progress(
                task_number=current_task + 1,
                task_name=task.name,
                stage=task.phase,
                progress_percent=progress
            )
        except Exception as e:
            print(f"Update error: {e}")
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide() if self.isVisible() else self.show()
        elif event.key() == Qt.Key.Key_Up:
            self.manager.next_task()
            self.update_progress()
        elif event.key() == Qt.Key.Key_Down:
            self.manager.previous_task()
            self.update_progress()


def main():
    """Launch the progress monitor."""
    app = QApplication(sys.argv)
    monitor = ProgressMonitor()
    monitor.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
