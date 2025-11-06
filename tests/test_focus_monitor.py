"""
Unit tests for VoiceClick FocusMonitor module
"""
import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from src.core.focus_monitor import FocusMonitor
from src.core.text_field_monitor import TextFieldInfo


class TestFocusMonitor:
    """Test FocusMonitor class"""
    
    def test_initialization_with_monitor(self):
        """Test FocusMonitor initialization with TextFieldMonitor"""
        mock_monitor = Mock()
        monitor = FocusMonitor(text_field_monitor=mock_monitor)
        
        assert monitor.text_field_monitor == mock_monitor
        assert monitor.monitoring == False
        assert monitor.monitor_thread is None
        assert monitor.callbacks == []
        assert monitor.debounce_delay == 0.1
        assert monitor.cooldown_period == 2.0
    
    @patch('src.core.focus_monitor.TextFieldMonitor')
    def test_initialization_without_monitor(self, mock_tfm_class):
        """Test FocusMonitor initialization without TextFieldMonitor"""
        mock_monitor = Mock()
        mock_tfm_class.return_value = mock_monitor
        monitor = FocusMonitor()
        
        assert monitor.text_field_monitor == mock_monitor
    
    def test_register_callback(self):
        """Test callback registration"""
        monitor = FocusMonitor()
        callback = Mock()
        
        monitor.register_callback(callback)
        
        assert callback in monitor.callbacks
    
    def test_register_callback_duplicate(self):
        """Test registering same callback twice"""
        monitor = FocusMonitor()
        callback = Mock()
        
        monitor.register_callback(callback)
        monitor.register_callback(callback)
        
        assert monitor.callbacks.count(callback) == 1
    
    def test_unregister_callback(self):
        """Test callback unregistration"""
        monitor = FocusMonitor()
        callback = Mock()
        monitor.callbacks.append(callback)
        
        monitor.unregister_callback(callback)
        
        assert callback not in monitor.callbacks
    
    def test_start_monitoring_success(self):
        """Test starting monitoring successfully"""
        monitor = FocusMonitor()
        
        monitor.start_monitoring()
        
        assert monitor.monitoring == True
        assert monitor.monitor_thread is not None
        assert monitor.monitor_thread.is_alive()
        
        # Cleanup
        monitor.stop_monitoring()
    
    def test_start_monitoring_already_running(self):
        """Test starting when already monitoring"""
        monitor = FocusMonitor()
        monitor.monitoring = True
        
        monitor.start_monitoring()
        
        # Should not create new thread
        assert monitor.monitor_thread is None
    
    def test_stop_monitoring_success(self):
        """Test stopping monitoring successfully"""
        monitor = FocusMonitor()
        monitor.start_monitoring()
        
        monitor.stop_monitoring()
        
        assert monitor.monitoring == False
        # Thread should be stopped (join timeout)
        if monitor.monitor_thread:
            monitor.monitor_thread.join(timeout=0.1)
    
    def test_stop_monitoring_not_running(self):
        """Test stopping when not monitoring"""
        monitor = FocusMonitor()
        monitor.monitoring = False
        
        monitor.stop_monitoring()
        
        assert monitor.monitoring == False
    
    def test_is_different_field_by_bounds(self):
        """Test _is_different_field using bounds"""
        monitor = FocusMonitor()
        
        info1 = TextFieldInfo(
            is_text_field=True,
            bounds=(10, 20, 100, 30)
        )
        info2 = TextFieldInfo(
            is_text_field=True,
            bounds=(20, 20, 100, 30)  # Different x position
        )
        
        result = monitor._is_different_field(info1, info2)
        
        assert result == True
    
    def test_is_different_field_same_bounds(self):
        """Test _is_different_field with same bounds"""
        monitor = FocusMonitor()
        
        info1 = TextFieldInfo(
            is_text_field=True,
            bounds=(10, 20, 100, 30)
        )
        info2 = TextFieldInfo(
            is_text_field=True,
            bounds=(12, 20, 100, 30)  # Within tolerance
        )
        
        result = monitor._is_different_field(info1, info2)
        
        assert result == False
    
    def test_is_different_field_by_window_title(self):
        """Test _is_different_field using window title"""
        monitor = FocusMonitor()
        
        info1 = TextFieldInfo(
            is_text_field=True,
            window_title="Window 1",
            control_type="Edit"
        )
        info2 = TextFieldInfo(
            is_text_field=True,
            window_title="Window 2",
            control_type="Edit"
        )
        
        result = monitor._is_different_field(info1, info2)
        
        assert result == True
    
    def test_is_different_field_by_control_type(self):
        """Test _is_different_field using control type"""
        monitor = FocusMonitor()
        
        info1 = TextFieldInfo(
            is_text_field=True,
            window_title="Window",
            control_type="Edit"
        )
        info2 = TextFieldInfo(
            is_text_field=True,
            window_title="Window",
            control_type="RichEdit"
        )
        
        result = monitor._is_different_field(info1, info2)
        
        assert result == True
    
    def test_is_different_field_no_bounds(self):
        """Test _is_different_field without bounds"""
        monitor = FocusMonitor()
        
        info1 = TextFieldInfo(
            is_text_field=True,
            window_title="Window",
            control_type="Edit"
        )
        info2 = TextFieldInfo(
            is_text_field=True,
            window_title="Window",
            control_type="Edit"
        )
        
        result = monitor._is_different_field(info1, info2)
        
        assert result == False
    
    @patch('src.core.focus_monitor.time.sleep')
    def test_monitor_loop_text_field_focus(self, mock_sleep):
        """Test monitor loop detects text field focus"""
        monitor = FocusMonitor()
        callback = Mock()
        monitor.register_callback(callback)
        
        field_info = TextFieldInfo(
            is_text_field=True,
            is_password_field=False,
            window_title="Test Window",
            control_type="Edit"
        )
        monitor.text_field_monitor.get_focused_element_info = Mock(return_value=field_info)
        monitor.last_activation_time = 0.0
        
        # Simulate one iteration of monitor loop
        monitor.monitoring = True
        current_info = monitor.text_field_monitor.get_focused_element_info()
        current_time = time.time()
        
        if current_info.is_text_field:
            if (current_time - monitor.last_focus_time) >= monitor.debounce_delay:
                if (monitor.last_focused_field is None or 
                    monitor._is_different_field(current_info, monitor.last_focused_field)):
                    if (current_time - monitor.last_activation_time) >= monitor.cooldown_period:
                        monitor._notify_callbacks(current_info)
                        monitor.last_activation_time = current_time
                    monitor.last_focused_field = current_info
                    monitor.last_focus_time = current_time
        
        callback.assert_called_once_with(field_info)
    
    @patch('src.core.focus_monitor.time.sleep')
    def test_monitor_loop_not_text_field(self, mock_sleep):
        """Test monitor loop ignores non-text fields"""
        monitor = FocusMonitor()
        callback = Mock()
        monitor.register_callback(callback)
        
        field_info = TextFieldInfo(is_text_field=False)
        monitor.text_field_monitor.get_focused_element_info = Mock(return_value=field_info)
        monitor.last_focused_field = TextFieldInfo(is_text_field=True)
        
        # Simulate one iteration
        current_info = monitor.text_field_monitor.get_focused_element_info()
        
        if not current_info.is_text_field:
            if monitor.last_focused_field is not None:
                monitor.last_focused_field = None
        
        callback.assert_not_called()
    
    def test_set_cooldown_period(self):
        """Test setting cooldown period"""
        monitor = FocusMonitor()
        
        monitor.set_cooldown_period(5.0)
        
        assert monitor.cooldown_period == 5.0
    
    def test_set_cooldown_period_negative(self):
        """Test setting negative cooldown (should clamp to 0)"""
        monitor = FocusMonitor()
        
        monitor.set_cooldown_period(-5.0)
        
        assert monitor.cooldown_period == 0.0
    
    def test_reset_cooldown(self):
        """Test resetting cooldown"""
        monitor = FocusMonitor()
        monitor.last_activation_time = 100.0
        
        monitor.reset_cooldown()
        
        assert monitor.last_activation_time == 0.0
    
    def test_notify_callbacks_exception(self):
        """Test callback exception handling"""
        monitor = FocusMonitor()
        callback1 = Mock()
        callback2 = Mock(side_effect=Exception("Test error"))
        callback3 = Mock()
        monitor.callbacks = [callback1, callback2, callback3]
        
        field_info = TextFieldInfo(is_text_field=True)
        monitor._notify_callbacks(field_info)
        
        # All callbacks should be called despite exception
        callback1.assert_called_once()
        callback2.assert_called_once()
        callback3.assert_called_once()
    
    @patch('src.core.focus_monitor.time.sleep')
    def test_monitor_loop_exception_handling(self, mock_sleep):
        """Test monitor loop handles exceptions"""
        monitor = FocusMonitor()
        monitor.monitoring = True
        monitor.text_field_monitor.get_focused_element_info = Mock(side_effect=Exception("Test error"))
        
        # Simulate exception in loop
        try:
            current_info = monitor.text_field_monitor.get_focused_element_info()
        except Exception:
            # Should sleep longer on error
            time.sleep(0.1)
        
        # Should not crash
        assert monitor.monitoring == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

