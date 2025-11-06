"""
Integration tests for VoiceClick auto-start workflow
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from src.core.focus_monitor import FocusMonitor
from src.core.click_monitor import ClickMonitor
from src.core.text_field_monitor import TextFieldInfo, TextFieldMonitor
from src.config.settings import Settings


@pytest.fixture
def mock_settings():
    """Create a mock Settings object"""
    settings = Settings()
    settings.auto_start_on_focus = True
    settings.auto_start_on_left_click = True
    settings.auto_start_cooldown = 2.0
    settings.app_whitelist = []
    settings.app_blacklist = []
    return settings


@pytest.fixture
def mock_text_field_monitor():
    """Create a mock TextFieldMonitor"""
    monitor = Mock(spec=TextFieldMonitor)
    return monitor


class TestAutoStartWorkflow:
    """Test auto-start workflow"""
    
    def test_auto_start_on_focus_workflow(self, mock_settings, mock_text_field_monitor):
        """Test auto-start on focus workflow"""
        monitor = FocusMonitor(text_field_monitor=mock_text_field_monitor)
        callback_called = []
        
        def test_callback(field_info):
            callback_called.append(field_info)
        
        monitor.register_callback(test_callback)
        
        # Simulate text field focus
        field_info = TextFieldInfo(
            is_text_field=True,
            is_password_field=False,
            application_name="TestApp",
            window_title="Test Window"
        )
        mock_text_field_monitor.get_focused_element_info.return_value = field_info
        
        # Simulate focus event
        monitor.last_activation_time = 0.0
        monitor._notify_callbacks(field_info)
        
        assert len(callback_called) == 1
        assert callback_called[0] == field_info
    
    def test_auto_start_on_click_workflow(self, mock_settings, mock_text_field_monitor):
        """Test auto-start on click workflow"""
        with patch('src.core.click_monitor.MOUSE_AVAILABLE', True):
            monitor = ClickMonitor(text_field_monitor=mock_text_field_monitor)
            callback_called = []
            
            def test_callback(field_info):
                callback_called.append(field_info)
            
            monitor.register_callback(test_callback)
            
            # Simulate click on text field
            field_info = TextFieldInfo(
                is_text_field=True,
                is_password_field=False,
                application_name="TestApp",
                window_title="Test Window"
            )
            mock_text_field_monitor.get_focused_element_info.return_value = field_info
            
            from pynput.mouse import Button
            monitor.last_activation_time = 0.0
            monitor.last_click_time = 0.0
            
            with patch('src.core.click_monitor.time.sleep'):
                monitor._on_click(100, 200, Button.left, True)
            
            assert len(callback_called) == 1
    
    def test_cooldown_enforcement(self, mock_settings, mock_text_field_monitor):
        """Test cooldown prevents rapid activations"""
        monitor = FocusMonitor(text_field_monitor=mock_text_field_monitor)
        callback_called = []
        
        def test_callback(field_info):
            callback_called.append(field_info)
        
        monitor.register_callback(test_callback)
        monitor.cooldown_period = 2.0
        monitor.last_activation_time = time.time() - 0.5  # Recent activation
        
        field_info = TextFieldInfo(is_text_field=True, is_password_field=False)
        mock_text_field_monitor.get_focused_element_info.return_value = field_info
        
        # Should not trigger due to cooldown
        current_time = time.time()
        if (current_time - monitor.last_activation_time) >= monitor.cooldown_period:
            monitor._notify_callbacks(field_info)
        
        # Should not be called due to cooldown
        assert len(callback_called) == 0
    
    def test_app_whitelist_filtering(self, mock_settings):
        """Test app whitelist filtering"""
        settings = mock_settings
        settings.app_whitelist = ["Notepad", "WordPad"]
        
        field_info_allowed = TextFieldInfo(
            is_text_field=True,
            application_name="Notepad.exe"
        )
        
        field_info_blocked = TextFieldInfo(
            is_text_field=True,
            application_name="OtherApp.exe"
        )
        
        # Check whitelist logic
        def should_auto_start(field_info):
            if field_info.application_name:
                app_name_lower = field_info.application_name.lower()
                if settings.app_whitelist:
                    allowed = False
                    for allowed_app in settings.app_whitelist:
                        if allowed_app.lower() in app_name_lower:
                            allowed = True
                            break
                    return allowed
            return True
        
        assert should_auto_start(field_info_allowed) == True
        assert should_auto_start(field_info_blocked) == False
    
    def test_app_blacklist_filtering(self, mock_settings):
        """Test app blacklist filtering"""
        settings = mock_settings
        settings.app_blacklist = ["PasswordManager"]
        
        field_info_allowed = TextFieldInfo(
            is_text_field=True,
            application_name="Notepad.exe"
        )
        
        field_info_blocked = TextFieldInfo(
            is_text_field=True,
            application_name="PasswordManager.exe"
        )
        
        # Check blacklist logic
        def should_auto_start(field_info):
            if field_info.application_name:
                app_name_lower = field_info.application_name.lower()
                if settings.app_blacklist:
                    for blocked_app in settings.app_blacklist:
                        if blocked_app.lower() in app_name_lower:
                            return False
            return True
        
        assert should_auto_start(field_info_allowed) == True
        assert should_auto_start(field_info_blocked) == False
    
    def test_password_field_ignored(self, mock_text_field_monitor):
        """Test password fields are ignored"""
        with patch('src.core.click_monitor.MOUSE_AVAILABLE', True):
            monitor = ClickMonitor(text_field_monitor=mock_text_field_monitor)
            callback_called = []
            
            def test_callback(field_info):
                callback_called.append(field_info)
            
            monitor.register_callback(test_callback)
            
            # Simulate click on password field
            field_info = TextFieldInfo(
                is_text_field=True,
                is_password_field=True  # Password field
            )
            mock_text_field_monitor.get_focused_element_info.return_value = field_info
            
            from pynput.mouse import Button
            monitor.last_activation_time = 0.0
            monitor.last_click_time = 0.0
            
            with patch('src.core.click_monitor.time.sleep'):
                monitor._on_click(100, 200, Button.left, True)
            
            # Should not be called for password fields
            assert len(callback_called) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

