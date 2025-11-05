"""
Progress Widget Integration Guide
How to use the Development Progress Widget in VoiceClick
"""

# ============================================================================
# QUICK START - 3 Ways to Use the Progress Widget
# ============================================================================

"""
OPTION 1: Vertical Layout (Default) - Compact and minimal
═════════════════════════════════════════════════════════

Best for: Small windows, status bar at top or bottom
Height: 32px minimum
Features: Thin progress bar + 2-line status text

Usage:
    from src.ui.progress_widget import DevelopmentProgressWidget
    
    progress = DevelopmentProgressWidget()
    progress.update_progress(
        task_number=5,
        task_name="Design PyQt6 main window layout",
        stage="UI Design"
    )
    
    # Add to layout
    layout.addWidget(progress)


OPTION 2: Horizontal Layout - More information density
════════════════════════════════════════════════════

Best for: Window bottom, more details visible
Height: 28px minimum
Features: Progress bar + single line status with percentage

Usage:
    from src.ui.progress_widget import HorizontalProgressWidget
    
    progress = HorizontalProgressWidget()
    progress.update_progress(
        task_number=10,
        task_name="Implement system tray integration",
        stage="UI Development"
    )
    
    # Add to window
    self.setCentralWidget(progress)


OPTION 3: With Progress Manager (Recommended)
═══════════════════════════════════════════════

Best for: Full project tracking with signals
Features: Qt signals, thread-safe, comprehensive tracking

Usage:
    from src.ui.progress_widget import DevelopmentProgressWidget
    from src.ui.progress_manager import DevelopmentProgressManager
    
    # Initialize manager
    manager = DevelopmentProgressManager()
    progress_widget = DevelopmentProgressWidget()
    
    # Connect signals
    manager.signals.progress_updated.connect(
        progress_widget.update_progress
    )
    manager.signals.project_completed.connect(
        progress_widget.set_success_state
    )
    
    # Start a task
    manager.start_task(5)  # Starts task 5
    
    # ... do work ...
    
    # Complete task
    manager.complete_task(5)
"""


# ============================================================================
# INTEGRATION EXAMPLES
# ============================================================================

# Example 1: Add to Main Window
# ─────────────────────────────
"""
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from src.ui.progress_widget import DevelopmentProgressWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        # Add progress widget at the top
        progress = DevelopmentProgressWidget()
        layout.addWidget(progress)
        
        # Add other content
        layout.addWidget(self.create_main_content())
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
    
    def create_main_content(self):
        # ... your main content here
        pass
"""


# Example 2: Auto-update with Timer
# ──────────────────────────────────
"""
from PyQt6.QtCore import QTimer
from src.ui.progress_widget import DevelopmentProgressWidget

class AutoProgressWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.progress_widget = DevelopmentProgressWidget()
        self.current_task = 1
        
        # Setup timer for auto-updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress_step)
        self.timer.setInterval(5000)  # Update every 5 seconds
        self.timer.start()
    
    def update_progress_step(self):
        if self.current_task <= 30:
            task_info = self.get_task_info(self.current_task)
            self.progress_widget.update_progress(
                self.current_task,
                task_info['name'],
                task_info['stage']
            )
            self.current_task += 1
        else:
            self.timer.stop()
            self.progress_widget.set_success_state()
    
    def get_task_info(self, task_id):
        # Return task info by ID
        pass
"""


# Example 3: Integration with Progress Manager
# ────────────────────────────────────────────
"""
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from src.ui.progress_widget import DevelopmentProgressWidget
from src.ui.progress_manager import get_progress_manager

class ManagedProgressWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Get singleton manager
        self.manager = get_progress_manager()
        
        # Create progress widget
        self.progress_widget = DevelopmentProgressWidget()
        
        # Connect signals
        self.manager.signals.progress_updated.connect(
            self.on_progress_updated
        )
        self.manager.signals.task_completed.connect(
            self.on_task_completed
        )
        self.manager.signals.project_completed.connect(
            self.on_project_completed
        )
        
        self.setup_ui()
    
    def setup_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.progress_widget)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
    
    def on_progress_updated(self, task_id, task_name, stage):
        # This is called when a task is updated
        print(f"Task {task_id}: {task_name} ({stage})")
    
    def on_task_completed(self, task_name):
        print(f"✓ Completed: {task_name}")
    
    def on_project_completed(self):
        self.progress_widget.set_success_state()
        print("✓ All tasks completed!")
    
    def start_next_task(self, task_id):
        # Start a task through the manager
        self.manager.start_task(task_id)
    
    def finish_current_task(self):
        # Complete current task
        if self.manager.current_task_id:
            self.manager.complete_task(self.manager.current_task_id)
"""


# ============================================================================
# COLOR CODING
# ============================================================================

"""
The progress bar changes color based on project completion:

  0-33%  → Blue (#4285F4)      - Early phase (setup, architecture)
 33-66%  → Amber (#FBB804)     - Middle phase (development, testing)
 66-100% → Green (#34A853)     - Final phase (release, polish)

Special States:
  Error  → Red (#E53935)       - Something went wrong
  Complete → Green (#34A853)   - All tasks done!
"""


# ============================================================================
# PROGRESS MANAGER FEATURES
# ============================================================================

"""
DevelopmentProgressManager provides:

1. Task Tracking
   - 30 predefined tasks with phases
   - Task status: not-started, in-progress, completed, blocked
   
2. Progress Calculation
   - Overall progress percentage
   - Per-phase progress tracking
   - Statistics and summaries
   
3. Qt Signals (Thread-Safe)
   - progress_updated(task_number, task_name, phase)
   - task_completed(task_name)
   - project_completed()
   - error_occurred(error_message)
   
4. Progress Export
   - export_progress_report() - Text report
   - get_summary() - JSON-compatible dict
   - get_phase_progress() - Phase-specific stats


Usage Examples:
───────────────

# Get progress
manager = get_progress_manager()
progress = manager.get_progress_percent()
print(f"Overall progress: {progress:.1f}%")

# Get phase progress
phase_stats = manager.get_phase_progress(DevelopmentPhase.UI_DEVELOPMENT)
print(f"UI Development: {phase_stats['completed']}/{phase_stats['total']}")

# Generate report
report = manager.export_progress_report()
print(report)

# Get summary
summary = manager.get_summary()
print(f"Completed: {summary['completed_tasks']}/{summary['total_tasks']}")
"""


# ============================================================================
# STYLING & CUSTOMIZATION
# ============================================================================

"""
Override colors:
────────────────

widget = DevelopmentProgressWidget()
widget.progress_bar.set_color(QColor(255, 0, 0))  # Red

Adjust sizing:
───────────────

widget.setMaximumHeight(48)  # Make taller
widget.progress_bar.setFixedHeight(5)  # Thicker bar

Custom styling:
────────────────

widget.setStyleSheet('''
    QWidget {
        background-color: #F5F5F5;
        border-top: 2px solid #E0E0E0;
    }
    QLabel {
        color: #424242;
    }
''')
"""


# ============================================================================
# BEST PRACTICES
# ============================================================================

"""
1. Use Progress Manager for complex projects
   - Centralized task tracking
   - Thread-safe signals
   - Easier debugging

2. Emit signals from separate threads
   - Use progress_updated.emit() for UI thread safety
   - Never update UI from background threads

3. Update progress at logical boundaries
   - Task completion: clear milestone
   - File save/load: natural checkpoint
   - Test pass: defined event

4. Show meaningful messages
   - Include task number for reference
   - Use consistent naming
   - Be specific about current phase

5. Handle errors gracefully
   - Use set_error_state() to show problems
   - Log errors with logger
   - Provide recovery options

6. Test progress widget in isolation
   - Run progress_demo.py to test
   - Verify all color transitions
   - Check text truncation at various sizes
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Q: Progress bar not updating?
A: Make sure to call update_progress() or emit the signal
   Check that widget is visible: widget.isVisible()

Q: Text truncated?
A: Adjust widget width or use shorter task names
   Minimum width should be 400px

Q: Color not changing?
A: Ensure set_color() is called before update()
   Check that progress_bar is set_progress() is called

Q: Signals not working?
A: Connect signals BEFORE emitting them
   Check that object still exists (not deleted)
   Verify signal slot signatures match

Q: Threading issues?
A: Always emit signals from worker threads
   Never update UI directly from background threads
   Use QTimer for periodic updates from main thread
"""
