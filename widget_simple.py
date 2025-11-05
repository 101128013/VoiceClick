#!/usr/bin/env python3
"""
VoiceClick Development Progress Monitor
Lightweight standalone widget - no heavy dependencies
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush


class VerticalProgressBar(QWidget):
    """Vertical progress bar widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0  # 0-100
        self.setStyleSheet("background-color: transparent; border: 1px solid #555;")
        
    def set_progress(self, value):
        """Set progress value (0-100)"""
        self.progress = max(0, min(100, value))
        self.update()
    
    def paintEvent(self, event):
        """Paint the vertical progress bar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        bg_color = QColor(60, 60, 60)
        painter.fillRect(self.rect(), bg_color)
        
        # Draw progress from bottom to top
        if self.progress > 0:
            height = self.height()
            fill_height = int((self.progress / 100) * height)
            
            # Green progress fill
            progress_color = QColor(0, 255, 0)
            fill_rect = QRect(0, height - fill_height, self.width(), fill_height)
            painter.fillRect(fill_rect, progress_color)


class SimpleProgressWidget(QWidget):
    """Lightweight progress display widget"""
    
    def __init__(self):
        super().__init__()
        self.current_task = 5
        self.total_tasks = 30
        self.task_name = "Design main window"
        self.dragging = False
        self.drag_position = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("VoiceClick Progress")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                          Qt.WindowType.WindowStaysOnTopHint | 
                          Qt.WindowType.Tool)
        
        # Dark background with green border
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border: 2px solid #00ff00;
                border-radius: 4px;
            }
            QLabel {
                color: white;
                background-color: transparent;
                border: none;
            }
        """)
        
        # Main horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(8)
        
        # Left side: Text labels in vertical layout
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        # Task info label
        self.task_label = QLabel(f"Task {self.current_task}/{self.total_tasks}: {self.task_name}")
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        self.task_label.setFont(font)
        text_layout.addWidget(self.task_label)
        
        # Progress label
        progress_pct = int((self.current_task / self.total_tasks) * 100)
        self.progress_label = QLabel(f"Phase 2 - UI Development • {progress_pct}% complete")
        small_font = QFont("Segoe UI", 8)
        self.progress_label.setFont(small_font)
        self.progress_label.setStyleSheet("color: #aaaaaa;")
        text_layout.addWidget(self.progress_label)
        
        main_layout.addLayout(text_layout, 1)
        
        # Right side: Vertical progress bar (same width as margin)
        self.progress_bar = VerticalProgressBar()
        self.progress_bar.setFixedSize(8, 42)  # 8px wide to match margin
        progress_pct = int((self.current_task / self.total_tasks) * 100)
        self.progress_bar.set_progress(progress_pct)
        main_layout.addWidget(self.progress_bar)
        
        self.setLayout(main_layout)
        
        # Set size to match taskbar height (46px) and reasonable width
        self.setFixedSize(333, 46)
        
        # Load saved position or use default
        self.load_position()
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide() if self.isVisible() else self.show()
        elif event.key() == Qt.Key.Key_Up:
            self.current_task = min(self.current_task + 1, self.total_tasks)
            self.update_display()
        elif event.key() == Qt.Key.Key_Down:
            self.current_task = max(self.current_task - 1, 1)
            self.update_display()
            
    def update_display(self):
        """Update the display"""
        self.task_label.setText(f"Task {self.current_task}/{self.total_tasks}: {self.task_name}")
        progress_pct = int((self.current_task / self.total_tasks) * 100)
        self.progress_label.setText(f"Phase 2 - UI Development • {progress_pct}% complete")
        self.progress_bar.set_progress(progress_pct)
    
    def mousePressEvent(self, event):
        """Start dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle dragging - horizontal only, locked to bottom"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            # Calculate new position
            new_pos = event.globalPosition().toPoint() - self.drag_position
            
            # Only use X coordinate, keep Y locked ON the taskbar
            screen = QApplication.primaryScreen().geometry()
            taskbar_height = 46
            locked_y = screen.height() - taskbar_height  # ON the taskbar
            
            # Constrain X to screen bounds
            new_x = max(0, min(new_pos.x(), screen.width() - 333))
            
            self.move(new_x, locked_y)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Stop dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.save_position()  # Save position when user releases drag
            event.accept()
    
    def load_position(self):
        """Load saved position or use default"""
        config_dir = Path.home() / '.voice_click'
        config_file = config_dir / 'widget_position.json'
        
        screen = QApplication.primaryScreen().geometry()
        taskbar_height = 46  # Windows 11 taskbar height
        
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    x = data.get('x', None)
                    y = data.get('y', None)
                    if x is not None and y is not None:
                        # Sit ON the taskbar (same Y as taskbar top)
                        y_taskbar = screen.height() - taskbar_height
                        self.move(x, y_taskbar)
                        return
        except Exception as e:
            pass
        
        # Default position: right side, ON the taskbar
        default_x = screen.width() - 333 - 10  # 10px margin from right edge
        default_y = screen.height() - taskbar_height  # ON the taskbar
        self.move(default_x, default_y)
    
    def save_position(self):
        """Save current X position only (Y is always snapped to taskbar)"""
        config_dir = Path.home() / '.voice_click'
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / 'widget_position.json'
        
        try:
            pos = self.pos()
            # Only save X position, Y will always be calculated to snap to taskbar
            data = {'x': pos.x(), 'y': pos.y()}
            with open(config_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            pass


def main():
    """Launch the widget"""
    app = QApplication(sys.argv)
    widget = SimpleProgressWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
