"""
Development Progress Manager
Centralized management of project progress tracking and UI updates
"""

import logging
from enum import Enum
from typing import Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class DevelopmentPhase(Enum):
    """Development phases for categorization."""
    SETUP = "Setup Phase"
    ARCHITECTURE = "Architecture"
    UI_DESIGN = "UI Design"
    UI_DEVELOPMENT = "UI Development"
    INTEGRATION = "Integration"
    ASSETS = "Assets"
    TESTING = "Testing"
    PACKAGING = "Packaging"
    INSTALLER = "Installer"
    DOCUMENTATION = "Documentation"
    DEVOPS = "DevOps"
    BETA_TESTING = "Beta Testing"
    BUG_FIXES = "Bug Fixes"
    MARKETING = "Marketing"
    RELEASE = "Release"
    POST_RELEASE = "Post-Release"


class TaskStatus(Enum):
    """Task status indicators."""
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ON_HOLD = "on-hold"


class DevelopmentTask:
    """Single development task with metadata."""
    
    def __init__(
        self,
        task_id: int,
        name: str,
        phase: DevelopmentPhase,
        status: TaskStatus = TaskStatus.NOT_STARTED,
        description: str = ""
    ):
        self.task_id = task_id
        self.name = name
        self.phase = phase
        self.status = status
        self.description = description
        self.progress_percent = 0
    
    def start(self):
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.progress_percent = 0
    
    def complete(self):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.progress_percent = 100
    
    def __str__(self):
        return f"[{self.task_id}] {self.name} - {self.status.value}"


class ProgressSignals(QObject):
    """Qt signals for progress updates (for thread-safe UI updates)."""
    
    progress_updated = pyqtSignal(int, str, str)  # task_number, task_name, phase
    task_completed = pyqtSignal(str)  # task_name
    project_completed = pyqtSignal()
    error_occurred = pyqtSignal(str)  # error_message


class DevelopmentProgressManager:
    """
    Centralized manager for VoiceClick development progress.
    Tracks tasks, phases, and provides progress signals for UI updates.
    """
    
    # Task definitions for the entire project
    TASK_DEFINITIONS = [
        (1, "Set up project repository and structure", DevelopmentPhase.SETUP),
        (2, "Define project requirements and dependencies", DevelopmentPhase.SETUP),
        (3, "Refactor existing script into modular architecture", DevelopmentPhase.ARCHITECTURE),
        (4, "Create configuration management system", DevelopmentPhase.ARCHITECTURE),
        (5, "Design PyQt6 main window layout", DevelopmentPhase.UI_DESIGN),
        (6, "Implement PyQt6 main window structure", DevelopmentPhase.UI_DEVELOPMENT),
        (7, "Build Status tab UI", DevelopmentPhase.UI_DEVELOPMENT),
        (8, "Build Settings tab UI", DevelopmentPhase.UI_DEVELOPMENT),
        (9, "Build History tab UI", DevelopmentPhase.UI_DEVELOPMENT),
        (10, "Implement system tray integration", DevelopmentPhase.UI_DEVELOPMENT),
        (11, "Connect UI to core engine", DevelopmentPhase.INTEGRATION),
        (12, "Create application icons and resources", DevelopmentPhase.ASSETS),
        (13, "Write unit tests for core modules", DevelopmentPhase.TESTING),
        (14, "Create PyInstaller spec file", DevelopmentPhase.PACKAGING),
        (15, "Test PyInstaller build locally", DevelopmentPhase.PACKAGING),
        (16, "Set up clean Windows 11 VM for testing", DevelopmentPhase.TESTING),
        (17, "Test executable on clean Windows 11 VM", DevelopmentPhase.TESTING),
        (18, "Create NSIS installer script", DevelopmentPhase.INSTALLER),
        (19, "Install NSIS and build installer", DevelopmentPhase.INSTALLER),
        (20, "Test installer on clean Windows 11 VM", DevelopmentPhase.TESTING),
        (21, "Write user documentation", DevelopmentPhase.DOCUMENTATION),
        (22, "Set up GitHub Actions CI/CD pipeline", DevelopmentPhase.DEVOPS),
        (23, "Conduct internal beta testing", DevelopmentPhase.BETA_TESTING),
        (24, "Fix critical bugs from beta testing", DevelopmentPhase.BUG_FIXES),
        (25, "Create product website/landing page", DevelopmentPhase.MARKETING),
        (26, "Prepare release notes for v1.0.0", DevelopmentPhase.RELEASE),
        (27, "Create version tag and trigger release build", DevelopmentPhase.RELEASE),
        (28, "Publish release on GitHub", DevelopmentPhase.RELEASE),
        (29, "Set up user support channels", DevelopmentPhase.POST_RELEASE),
        (30, "Plan post-launch feature roadmap", DevelopmentPhase.POST_RELEASE),
    ]
    
    def __init__(self):
        """Initialize progress manager."""
        self.signals = ProgressSignals()
        self.tasks = {}
        self.current_task_id = 30  # All tasks complete
        self.completed_tasks = 30  # Tasks 1-30 are complete
        
        # Initialize tasks
        self._init_tasks()
        
        # Mark all tasks 1-30 as completed
        for task_id in range(1, 31):
            if task_id in self.tasks:
                self.tasks[task_id].complete()
        
        logger.info("DevelopmentProgressManager initialized with 30 tasks (ALL 30 COMPLETED - PROJECT FINISHED)")
    
    def _init_tasks(self):
        """Initialize task objects from definitions."""
        for task_id, name, phase in self.TASK_DEFINITIONS:
            self.tasks[task_id] = DevelopmentTask(
                task_id=task_id,
                name=name,
                phase=phase
            )
    
    def start_task(self, task_id: int) -> bool:
        """
        Start a task (mark as in-progress).
        
        Args:
            task_id: Task ID to start
            
        Returns:
            bool: True if successful
        """
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        task.start()
        self.current_task_id = task_id
        
        # Emit signal
        self.signals.progress_updated.emit(
            task_id,
            task.name,
            task.phase.value
        )
        
        logger.info(f"Started task {task_id}: {task.name}")
        return True
    
    def complete_task(self, task_id: int) -> bool:
        """
        Complete a task.
        
        Args:
            task_id: Task ID to complete
            
        Returns:
            bool: True if successful
        """
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        task.complete()
        self.completed_tasks += 1
        
        # Emit signal
        self.signals.task_completed.emit(task.name)
        
        logger.info(f"Completed task {task_id}: {task.name}")
        
        # Check if all tasks completed
        if self.completed_tasks == len(self.tasks):
            self.signals.project_completed.emit()
            logger.info("All tasks completed!")
        
        return True
    
    def get_task(self, task_id: int) -> Optional[DevelopmentTask]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def get_current_task(self) -> Optional[DevelopmentTask]:
        """Get currently active task."""
        if self.current_task_id in self.tasks:
            return self.tasks[self.current_task_id]
        return None
    
    def get_progress_percent(self) -> float:
        """Get overall progress percentage."""
        if not self.tasks:
            return 0
        return (self.completed_tasks / len(self.tasks)) * 100
    
    def get_phase_progress(self, phase: DevelopmentPhase) -> dict:
        """
        Get progress stats for a specific phase.
        
        Args:
            phase: Development phase
            
        Returns:
            dict: Stats with total, completed, percent
        """
        phase_tasks = [t for t in self.tasks.values() if t.phase == phase]
        completed = sum(1 for t in phase_tasks if t.status == TaskStatus.COMPLETED)
        
        return {
            "phase": phase.value,
            "total": len(phase_tasks),
            "completed": completed,
            "percent": (completed / len(phase_tasks) * 100) if phase_tasks else 0
        }
    
    def get_all_phases_progress(self) -> list:
        """Get progress for all phases."""
        phases = set(t.phase for t in self.tasks.values())
        # Sort by phase name instead of enum to avoid comparison issues
        return [self.get_phase_progress(phase) for phase in sorted(phases, key=lambda p: p.value)]
    
    def get_summary(self) -> dict:
        """Get comprehensive progress summary."""
        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": self.completed_tasks,
            "current_task_id": self.current_task_id,
            "overall_progress_percent": self.get_progress_percent(),
            "phases": self.get_all_phases_progress()
        }
    
    def export_progress_report(self) -> str:
        """Generate a text report of project progress."""
        summary = self.get_summary()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║        VoiceClick - Development Progress Report             ║
╚══════════════════════════════════════════════════════════════╝

Overall Progress: {summary['overall_progress_percent']:.1f}%
Completed: {summary['completed_tasks']}/{summary['total_tasks']} tasks

═══════════════════════════════════════════════════════════════

Phase Breakdown:
{chr(10).join(f"  • {p['phase']}: {p['completed']}/{p['total']} ({p['percent']:.1f}%)" for p in summary['phases'])}

═══════════════════════════════════════════════════════════════

Task Status:
"""
        
        for task_id in sorted(self.tasks.keys()):
            task = self.tasks[task_id]
            status_icon = "✓" if task.status == TaskStatus.COMPLETED else "◯"
            report += f"\n  {status_icon} [{task_id:2d}] {task.name}"
        
        report += "\n\n╔══════════════════════════════════════════════════════════════╗\n"
        
        return report


# Singleton instance (optional)
_progress_manager = None


def get_progress_manager() -> DevelopmentProgressManager:
    """Get or create singleton progress manager instance."""
    global _progress_manager
    if _progress_manager is None:
        _progress_manager = DevelopmentProgressManager()
    return _progress_manager
