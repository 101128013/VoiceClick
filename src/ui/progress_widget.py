"""
VoiceClick Development Progress Widget
A sleek, minimalist status bar showing project development progress
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import QSize, QRect
from PyQt6.QtGui import QPainter, QPen, QBrush


class ProgressBarWidget(QWidget):
    """Thin, sleek progress bar with custom styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0
        self.max_progress = 100
        self.bar_color = QColor(66, 133, 244)  # Google Blue
        self.background_color = QColor(240, 240, 240)  # Light gray
        self.setFixedHeight(3)
        self.setStyleSheet("border: none;")
    
    def set_progress(self, value: int):
        """Update progress value."""
        self.progress = min(max(value, 0), self.max_progress)
        self.update()
    
    def set_max_progress(self, max_value: int):
        """Set maximum progress value."""
        self.max_progress = max_value
        self.update()
    
    def set_color(self, color: QColor):
        """Set progress bar color."""
        self.bar_color = color
        self.update()
    
    def paintEvent(self, event):
        """Paint the progress bar."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), self.background_color)
        
        # Draw progress
        if self.max_progress > 0:
            progress_width = (self.progress / self.max_progress) * self.width()
            progress_rect = QRect(0, 0, int(progress_width), self.height())
            painter.fillRect(progress_rect, self.bar_color)
        
        painter.end()


class DevelopmentProgressWidget(QWidget):
    """
    Sleek development status widget with progress bar and status text.
    Designed to be compact (taskbar height ~28px).
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_task = 1
        self.total_tasks = 30
        self.task_name = "Initializing..."
        self.task_stage = "Setup Phase"
        self.setup_ui()
        self.setMaximumHeight(32)
    
    def setup_ui(self):
        """Set up the widget UI."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        
        # Progress bar
        self.progress_bar = ProgressBarWidget()
        self.progress_bar.set_max_progress(self.total_tasks)
        main_layout.addWidget(self.progress_bar)
        
        # Status text container
        text_container = QWidget()
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)
        
        # Task name (main status)
        self.task_label = QLabel(self.task_name)
        task_font = QFont()
        task_font.setPointSize(9)
        task_font.setBold(True)
        self.task_label.setFont(task_font)
        self.task_label.setStyleSheet("color: #333333; background: transparent;")
        text_layout.addWidget(self.task_label)
        
        # Task stage and progress
        self.stage_label = QLabel(self.task_stage)
        stage_font = QFont()
        stage_font.setPointSize(7)
        self.stage_label.setFont(stage_font)
        self.stage_label.setStyleSheet("color: #999999; background: transparent;")
        text_layout.addWidget(self.stage_label)
        
        text_container.setLayout(text_layout)
        main_layout.addWidget(text_container)
        
        self.setLayout(main_layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-top: 1px solid #E8E8E8;
            }
        """)
    
    def update_progress(self, task_number: int, task_name: str, stage: str):
        """
        Update progress widget with current task info.
        
        Args:
            task_number: Current task number (1-30)
            task_name: Name of the current task
            stage: Current development stage
        """
        self.current_task = task_number
        self.task_name = task_name
        self.task_stage = stage
        
        # Update progress bar
        self.progress_bar.set_progress(task_number)
        
        # Update labels
        self.task_label.setText(f"Task {task_number}/{self.total_tasks}: {task_name}")
        self.stage_label.setText(f"{stage} • {int((task_number/self.total_tasks)*100)}% complete")
        
        # Animate progress bar color based on progress
        progress_percent = (task_number / self.total_tasks)
        if progress_percent < 0.33:
            color = QColor(66, 133, 244)  # Blue - early phase
        elif progress_percent < 0.66:
            color = QColor(251, 188, 4)   # Amber - middle phase
        else:
            color = QColor(52, 168, 83)   # Green - final phase
        
        self.progress_bar.set_color(color)
    
    def set_error_state(self, error_message: str):
        """Show error state."""
        self.task_label.setText(f"❌ Error: {error_message}")
        self.stage_label.setText("Please check the logs")
        self.progress_bar.set_color(QColor(229, 57, 53))  # Red
    
    def set_success_state(self):
        """Show success state."""
        self.task_label.setText("✓ Development Complete!")
        self.stage_label.setText("All tasks completed successfully")
        self.progress_bar.set_progress(self.total_tasks)
        self.progress_bar.set_color(QColor(52, 168, 83))  # Green
    
    def reset(self):
        """Reset to initial state."""
        self.update_progress(1, "Initializing...", "Setup Phase")


# Alternative: Horizontal Status Bar Widget (wider layout)
class HorizontalProgressWidget(QWidget):
    """
    Horizontal layout version - progress bar on left, text on right.
    More compact for window integration.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_task = 1
        self.total_tasks = 30
        self.setup_ui()
        self.setMaximumHeight(28)
    
    def setup_ui(self):
        """Set up horizontal layout."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(4)
        
        # Top bar: progress bar on left, percentage on right
        top_widget = QWidget()
        top_layout = QVBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        
        self.progress_bar = ProgressBarWidget()
        self.progress_bar.set_max_progress(self.total_tasks)
        top_layout.addWidget(self.progress_bar)
        top_widget.setLayout(top_layout)
        main_layout.addWidget(top_widget)
        
        # Bottom: Task info
        info_label = QLabel()
        info_font = QFont()
        info_font.setPointSize(8)
        info_label.setFont(info_font)
        info_label.setStyleSheet("color: #555555; background: transparent;")
        self.info_label = info_label
        main_layout.addWidget(info_label)
        
        self.setLayout(main_layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #FAFAFA;
                border-top: 1px solid #E0E0E0;
            }
        """)
    
    def update_progress(self, task_number: int, task_name: str, stage: str):
        """Update progress display."""
        self.current_task = task_number
        progress_percent = int((task_number / self.total_tasks) * 100)
        
        self.progress_bar.set_progress(task_number)
        self.info_label.setText(
            f"Task {task_number}/30 • {task_name} ({stage}) • {progress_percent}%"
        )
        
        # Update color
        if progress_percent < 33:
            color = QColor(66, 133, 244)
        elif progress_percent < 66:
            color = QColor(251, 188, 4)
        else:
            color = QColor(52, 168, 83)
        
        self.progress_bar.set_color(color)
