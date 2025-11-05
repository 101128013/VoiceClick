"""
Example usage of the Development Progress Widget
Demonstrates both vertical and horizontal layouts
"""

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QTimer
from src.ui.progress_widget import DevelopmentProgressWidget, HorizontalProgressWidget


class ProgressDemoWindow(QMainWindow):
    """Demo window showing the progress widget in action."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceClick - Development Progress")
        self.setGeometry(100, 100, 600, 250)
        
        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Add progress widget (vertical version)
        self.progress_widget = DevelopmentProgressWidget()
        main_layout.addWidget(self.progress_widget)
        
        # Add demo button to simulate progress
        demo_button = QPushButton("Simulate Progress")
        demo_button.clicked.connect(self.simulate_progress)
        main_layout.addWidget(demo_button)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Progress simulation
        self.current_task = 1
        self.timer = QTimer()
        self.timer.timeout.connect(self.increment_progress)
        self.timer.setInterval(2000)  # Update every 2 seconds
    
    def simulate_progress(self):
        """Start progress simulation."""
        if self.timer.isActive():
            self.timer.stop()
            self.current_task = 1
            self.progress_widget.reset()
        else:
            self.timer.start()
    
    def increment_progress(self):
        """Increment progress and update widget."""
        self.current_task += 1
        
        # Map task numbers to actual task names
        tasks = {
            1: ("Set up project repository and structure", "Setup Phase"),
            2: ("Define project requirements and dependencies", "Setup Phase"),
            3: ("Refactor existing script into modular architecture", "Architecture"),
            4: ("Create configuration management system", "Architecture"),
            5: ("Design PyQt6 main window layout", "UI Design"),
            6: ("Implement PyQt6 main window structure", "UI Development"),
            7: ("Build Status tab UI", "UI Development"),
            8: ("Build Settings tab UI", "UI Development"),
            9: ("Build History tab UI", "UI Development"),
            10: ("Implement system tray integration", "UI Development"),
            11: ("Connect UI to core engine", "Integration"),
            12: ("Create application icons and resources", "Assets"),
            13: ("Write unit tests for core modules", "Testing"),
            14: ("Create PyInstaller spec file", "Packaging"),
            15: ("Test PyInstaller build locally", "Packaging"),
            16: ("Set up clean Windows 11 VM for testing", "Testing"),
            17: ("Test executable on clean Windows 11 VM", "Testing"),
            18: ("Create NSIS installer script", "Installer"),
            19: ("Install NSIS and build installer", "Installer"),
            20: ("Test installer on clean Windows 11 VM", "Testing"),
            21: ("Write user documentation", "Documentation"),
            22: ("Set up GitHub Actions CI/CD pipeline", "DevOps"),
            23: ("Conduct internal beta testing", "Beta Testing"),
            24: ("Fix critical bugs from beta testing", "Bug Fixes"),
            25: ("Create product website/landing page", "Marketing"),
            26: ("Prepare release notes for v1.0.0", "Release"),
            27: ("Create version tag and trigger release build", "Release"),
            28: ("Publish release on GitHub", "Release"),
            29: ("Set up user support channels", "Post-Release"),
            30: ("Plan post-launch feature roadmap", "Post-Release"),
        }
        
        if self.current_task <= 30:
            task_name, stage = tasks.get(self.current_task, ("Unknown Task", "Unknown"))
            self.progress_widget.update_progress(self.current_task, task_name, stage)
        else:
            self.timer.stop()
            self.progress_widget.set_success_state()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = ProgressDemoWindow()
    window.show()
    sys.exit(app.exec())
