#!/usr/bin/env python3
"""
VoiceClick Development Progress Monitor (Standalone)
Simple taskbar widget showing project progress - no heavy dependencies
"""

import sys
from pathlib import Path

# Add src/ui to path to import progress_manager directly without going through __init__
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'ui'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QProgressBar
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint
from PyQt6.QtGui import QFont, QColor

from progress_manager import DevelopmentProgressManager
from progress_widget import ProgressBarWidget, DevelopmentProgressWidget


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
        
        # Create progress manager and widget
        self.progress_manager = DevelopmentProgressManager()
        self.progress_widget = DevelopmentProgressWidget()
        
        # Update widget with current progress
        current_task = self.progress_manager.get_current_task()
        if current_task:
            self.progress_widget.update_progress(
                current_task.task_id,
                current_task.name,
                current_task.phase.value
            )
        
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
        
        print(f"✓ Widget positioned at ({x}, {y})")
        print(f"✓ Showing progress: {self.progress_manager.get_progress_percent():.1f}%")
        print(f"✓ Current task: {self.progress_manager.current_task_id}/30")


def main():
    """Run progress monitor."""
    app = QApplication(sys.argv)
    
    monitor = ProgressMonitor()
    monitor.show()
    
    print("\n" + "="*60)
    print("VOICECLICK PROGRESS MONITOR RUNNING")
    print("="*60)
    print("✓ Widget visible above Windows taskbar (bottom-right)")
    print("✓ Press Ctrl+C in terminal to close")
    print("✓ Use ESC key to toggle widget visibility")
    print("✓ Use Arrow keys to navigate tasks")
    print("="*60 + "\n")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
