"""
Unit tests for VoiceClick Progress Manager
"""
import pytest
from src.ui.progress_manager import (
    DevelopmentProgressManager, 
    DevelopmentTask,
    TaskStatus,
    DevelopmentPhase
)


class TestDevelopmentTask:
    """Test DevelopmentTask class"""
    
    def test_task_creation(self):
        """Test creating a task"""
        task = DevelopmentTask(
            task_id=1,
            name="Test Task",
            phase=DevelopmentPhase.SETUP,
            description="Test description"
        )
        
        assert task.task_id == 1
        assert task.name == "Test Task"
        assert task.phase == DevelopmentPhase.SETUP
        assert task.status == TaskStatus.NOT_STARTED
        assert task.progress_percent == 0
    
    def test_task_start(self):
        """Test starting a task"""
        task = DevelopmentTask(1, "Test", DevelopmentPhase.SETUP)
        task.start()
        
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.progress_percent == 0
    
    def test_task_complete(self):
        """Test completing a task"""
        task = DevelopmentTask(1, "Test", DevelopmentPhase.SETUP)
        task.complete()
        
        assert task.status == TaskStatus.COMPLETED
        assert task.progress_percent == 100


class TestProgressManager:
    """Test DevelopmentProgressManager class"""
    
    def test_manager_initialization(self):
        """Test progress manager initializes with all tasks"""
        manager = DevelopmentProgressManager()
        
        assert len(manager.tasks) == 30
        assert manager.completed_tasks == 13  # Current state
        assert manager.current_task_id == 14
    
    def test_get_task(self):
        """Test retrieving individual tasks"""
        manager = DevelopmentProgressManager()
        
        task = manager.get_task(1)
        assert task is not None
        assert task.task_id == 1
        assert task.name == "Set up project repository and structure"
    
    def test_get_current_task(self):
        """Test getting current task"""
        manager = DevelopmentProgressManager()
        
        current = manager.get_current_task()
        assert current is not None
        assert current.task_id == 14
    
    def test_get_progress_percent(self):
        """Test calculating progress percentage"""
        manager = DevelopmentProgressManager()
        
        progress = manager.get_progress_percent()
        assert abs(progress - 43.33) < 0.01  # 13/30 ≈ 43.33%
    
    def test_get_phase_progress(self):
        """Test getting phase-specific progress"""
        manager = DevelopmentProgressManager()
        
        setup_progress = manager.get_phase_progress(DevelopmentPhase.SETUP)
        
        assert setup_progress['phase'] == DevelopmentPhase.SETUP.value
        assert setup_progress['total'] >= 0
        assert setup_progress['completed'] >= 0
        assert 0 <= setup_progress['percent'] <= 100
    
    def test_get_summary(self):
        """Test getting comprehensive summary"""
        manager = DevelopmentProgressManager()
        
        summary = manager.get_summary()
        
        assert summary['total_tasks'] == 30
        assert summary['completed_tasks'] == 13
        assert summary['current_task_id'] == 14
        assert abs(summary['overall_progress_percent'] - 43.33) < 0.01
        assert 'phases' in summary
    
    def test_export_progress_report(self):
        """Test exporting progress report"""
        manager = DevelopmentProgressManager()
        
        report = manager.export_progress_report()
        
        assert isinstance(report, str)
        assert "VoiceClick" in report
        assert "Progress Report" in report
        assert "30" in report  # Total tasks
    
    def test_all_30_tasks_defined(self):
        """Verify all 30 tasks are properly defined"""
        manager = DevelopmentProgressManager()
        
        # Check all task IDs from 1 to 30 exist
        for task_id in range(1, 31):
            task = manager.get_task(task_id)
            assert task is not None
            assert task.task_id == task_id
            assert task.name != ""
            assert task.phase is not None
    
    def test_completed_tasks_status(self):
        """Test that completed tasks have correct status"""
        manager = DevelopmentProgressManager()
        
        # Tasks 1-13 should be completed
        for task_id in range(1, 14):
            task = manager.get_task(task_id)
            assert task.status == TaskStatus.COMPLETED
            assert task.progress_percent == 100
    
    def test_current_task_in_progress(self):
        """Test that current task is in progress"""
        manager = DevelopmentProgressManager()
        
        task = manager.get_task(14)
        assert task.status == TaskStatus.IN_PROGRESS


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
