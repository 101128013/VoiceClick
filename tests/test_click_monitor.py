"""
Unit tests for VoiceClick ClickMonitor module
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from src.core.click_monitor import ClickMonitor
from src.core.text_field_monitor import TextFieldInfo


class TestClickMonitor:
    """Test ClickMonitor class"""
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_initialization_with_monitor(self, mock_listener_class):
        """Test ClickMonitor initialization with TextFieldMonitor"""
        mock_monitor = Mock()
        monitor = ClickMonitor(text_field_monitor=mock_monitor)
        
        assert monitor.available == True
        assert monitor.text_field_monitor == mock_monitor
        assert monitor.monitoring == False
        assert monitor.listener is None
        assert monitor.callbacks == []
        assert monitor.debounce_delay == 0.2
        assert monitor.cooldown_period == 2.0
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_initialization_without_monitor(self, mock_listener_class):
        """Test ClickMonitor initialization without TextFieldMonitor"""
        with patch('src.core.click_monitor.TextFieldMonitor') as mock_tfm_class:
            mock_monitor = Mock()
            mock_tfm_class.return_value = mock_monitor
            monitor = ClickMonitor()
            
            assert monitor.available == True
            assert monitor.text_field_monitor == mock_monitor
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', False)
    def test_initialization_no_mouse(self):
        """Test ClickMonitor initialization when mouse unavailable"""
        monitor = ClickMonitor()
        
        assert monitor.available == False
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_register_callback(self, mock_listener_class):
        """Test callback registration"""
        monitor = ClickMonitor()
        callback = Mock()
        
        monitor.register_callback(callback)
        
        assert callback in monitor.callbacks
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_register_callback_duplicate(self, mock_listener_class):
        """Test registering same callback twice"""
        monitor = ClickMonitor()
        callback = Mock()
        
        monitor.register_callback(callback)
        monitor.register_callback(callback)
        
        assert monitor.callbacks.count(callback) == 1
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', False)
    def test_register_callback_unavailable(self):
        """Test callback registration when unavailable"""
        monitor = ClickMonitor()
        callback = Mock()
        
        monitor.register_callback(callback)
        
        assert len(monitor.callbacks) == 0
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_unregister_callback(self, mock_listener_class):
        """Test callback unregistration"""
        monitor = ClickMonitor()
        callback = Mock()
        monitor.callbacks.append(callback)
        
        monitor.unregister_callback(callback)
        
        assert callback not in monitor.callbacks
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_start_monitoring_success(self, mock_listener_class):
        """Test starting monitoring successfully"""
        monitor = ClickMonitor()
        mock_listener = MagicMock()
        mock_listener_class.return_value = mock_listener
        
        monitor.start_monitoring()
        
        assert monitor.monitoring == True
        assert monitor.listener == mock_listener
        mock_listener.start.assert_called_once()
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_start_monitoring_already_running(self, mock_listener_class):
        """Test starting when already monitoring"""
        monitor = ClickMonitor()
        monitor.monitoring = True
        
        monitor.start_monitoring()
        
        # Should not create new listener
        assert monitor.listener is None
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', False)
    def test_start_monitoring_unavailable(self):
        """Test starting when unavailable"""
        monitor = ClickMonitor()
        
        monitor.start_monitoring()
        
        assert monitor.monitoring == False
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_start_monitoring_exception(self, mock_listener_class):
        """Test starting with exception"""
        monitor = ClickMonitor()
        mock_listener_class.side_effect = Exception("Test error")
        
        monitor.start_monitoring()
        
        assert monitor.monitoring == False
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_stop_monitoring_success(self, mock_listener_class):
        """Test stopping monitoring successfully"""
        monitor = ClickMonitor()
        mock_listener = MagicMock()
        monitor.listener = mock_listener
        monitor.monitoring = True
        
        monitor.stop_monitoring()
        
        assert monitor.monitoring == False
        mock_listener.stop.assert_called_once()
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_stop_monitoring_not_running(self, mock_listener_class):
        """Test stopping when not monitoring"""
        monitor = ClickMonitor()
        monitor.monitoring = False
        
        monitor.stop_monitoring()
        
        assert monitor.monitoring == False
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    @patch('src.core.click_monitor.time.sleep')
    def test_on_click_left_button(self, mock_sleep, mock_listener_class):
        """Test _on_click with left button press"""
        monitor = ClickMonitor()
        callback = Mock()
        monitor.register_callback(callback)
        
        field_info = TextFieldInfo(
            is_text_field=True,
            is_password_field=False,
            application_name="TestApp",
            window_title="Test Window"
        )
        monitor.text_field_monitor.get_focused_element_info = Mock(return_value=field_info)
        monitor.last_activation_time = 0.0
        
        from pynput.mouse import Button
        monitor._on_click(100, 200, Button.left, True)
        
        callback.assert_called_once_with(field_info)
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_on_click_right_button(self, mock_listener_class):
        """Test _on_click with right button (should be ignored)"""
        monitor = ClickMonitor()
        callback = Mock()
        monitor.register_callback(callback)
        
        from pynput.mouse import Button
        monitor._on_click(100, 200, Button.right, True)
        
        callback.assert_not_called()
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_on_click_button_release(self, mock_listener_class):
        """Test _on_click with button release (should be ignored)"""
        monitor = ClickMonitor()
        callback = Mock()
        monitor.register_callback(callback)
        
        from pynput.mouse import Button
        monitor._on_click(100, 200, Button.left, False)
        
        callback.assert_not_called()
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    @patch('src.core.click_monitor.time.sleep')
    def test_on_click_debounce(self, mock_sleep, mock_listener_class):
        """Test debounce logic prevents rapid clicks"""
        monitor = ClickMonitor()
        callback = Mock()
        monitor.register_callback(callback)
        monitor.debounce_delay = 0.5
        
        field_info = TextFieldInfo(is_text_field=True, is_password_field=False)
        monitor.text_field_monitor.get_focused_element_info = Mock(return_value=field_info)
        monitor.last_click_time = time.time() - 0.1  # Recent click
        
        from pynput.mouse import Button
        monitor._on_click(100, 200, Button.left, True)
        
        callback.assert_not_called()
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    @patch('src.core.click_monitor.time.sleep')
    def test_on_click_cooldown(self, mock_sleep, mock_listener_class):
        """Test cooldown prevents rapid activations"""
        monitor = ClickMonitor()
        callback = Mock()
        monitor.register_callback(callback)
        monitor.cooldown_period = 2.0
        monitor.last_activation_time = time.time() - 0.5  # Recent activation
        
        field_info = TextFieldInfo(is_text_field=True, is_password_field=False)
        monitor.text_field_monitor.get_focused_element_info = Mock(return_value=field_info)
        
        from pynput.mouse import Button
        monitor._on_click(100, 200, Button.left, True)
        
        callback.assert_not_called()
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    @patch('src.core.click_monitor.time.sleep')
    def test_on_click_password_field(self, mock_sleep, mock_listener_class):
        """Test password fields are ignored"""
        monitor = ClickMonitor()
        callback = Mock()
        monitor.register_callback(callback)
        
        field_info = TextFieldInfo(
            is_text_field=True,
            is_password_field=True  # Password field
        )
        monitor.text_field_monitor.get_focused_element_info = Mock(return_value=field_info)
        
        from pynput.mouse import Button
        monitor._on_click(100, 200, Button.left, True)
        
        callback.assert_not_called()
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_set_cooldown_period(self, mock_listener_class):
        """Test setting cooldown period"""
        monitor = ClickMonitor()
        
        monitor.set_cooldown_period(5.0)
        
        assert monitor.cooldown_period == 5.0
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_set_cooldown_period_negative(self, mock_listener_class):
        """Test setting negative cooldown (should clamp to 0)"""
        monitor = ClickMonitor()
        
        monitor.set_cooldown_period(-5.0)
        
        assert monitor.cooldown_period == 0.0
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_reset_cooldown(self, mock_listener_class):
        """Test resetting cooldown"""
        monitor = ClickMonitor()
        monitor.last_activation_time = 100.0
        
        monitor.reset_cooldown()
        
        assert monitor.last_activation_time == 0.0
    
    @patch('src.core.click_monitor.MOUSE_AVAILABLE', True)
    @patch('src.core.click_monitor.Listener')
    def test_notify_callbacks_exception(self, mock_listener_class):
        """Test callback exception handling"""
        monitor = ClickMonitor()
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

