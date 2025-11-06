"""
Unit tests for VoiceClick TextDetector module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.text_detector import TextDetector
from src.core.text_field_monitor import TextFieldInfo


class TestTextDetector:
    """Test TextDetector class"""
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    def test_initialization(self, mock_tfm_class, mock_controller_class):
        """Test TextDetector initialization"""
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        mock_monitor = Mock()
        mock_tfm_class.return_value = mock_monitor
        
        detector = TextDetector()
        
        assert detector.keyboard_controller == mock_controller
        assert detector.text_field_monitor == mock_monitor
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    def test_initialization_exception(self, mock_tfm_class, mock_controller_class):
        """Test initialization with exception"""
        mock_controller_class.side_effect = Exception("Test error")
        
        with pytest.raises(Exception):
            TextDetector()
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    def test_is_text_field_active_true(self, mock_tfm_class, mock_controller_class):
        """Test is_text_field_active returns True"""
        mock_monitor = Mock()
        mock_monitor.is_text_field_active.return_value = True
        mock_tfm_class.return_value = mock_monitor
        
        detector = TextDetector()
        result = detector.is_text_field_active()
        
        assert result == True
        mock_monitor.is_text_field_active.assert_called_once()
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    def test_is_text_field_active_false(self, mock_tfm_class, mock_controller_class):
        """Test is_text_field_active returns False"""
        mock_monitor = Mock()
        mock_monitor.is_text_field_active.return_value = False
        mock_tfm_class.return_value = mock_monitor
        
        detector = TextDetector()
        result = detector.is_text_field_active()
        
        assert result == False
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    def test_is_text_field_active_exception(self, mock_tfm_class, mock_controller_class):
        """Test is_text_field_active with exception (fallback)"""
        mock_monitor = Mock()
        mock_monitor.is_text_field_active.side_effect = Exception("Test error")
        mock_tfm_class.return_value = mock_monitor
        
        detector = TextDetector()
        result = detector.is_text_field_active()
        
        # Should fallback to True
        assert result == True
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    def test_get_active_text_field_info(self, mock_tfm_class, mock_controller_class):
        """Test get_active_text_field_info"""
        mock_monitor = Mock()
        field_info = TextFieldInfo(is_text_field=True)
        mock_monitor.get_active_text_field_info.return_value = field_info
        mock_tfm_class.return_value = mock_monitor
        
        detector = TextDetector()
        result = detector.get_active_text_field_info()
        
        assert result == field_info
        mock_monitor.get_active_text_field_info.assert_called_once()
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    def test_get_active_text_field_info_exception(self, mock_tfm_class, mock_controller_class):
        """Test get_active_text_field_info with exception"""
        mock_monitor = Mock()
        mock_monitor.get_active_text_field_info.side_effect = Exception("Test error")
        mock_tfm_class.return_value = mock_monitor
        
        detector = TextDetector()
        result = detector.get_active_text_field_info()
        
        # Should return fallback TextFieldInfo
        assert result.is_text_field == True
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    def test_insert_text_empty(self, mock_tfm_class, mock_controller_class):
        """Test insert_text with empty string"""
        detector = TextDetector()
        
        result = detector.insert_text("")
        
        assert result == False
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    @patch('src.core.text_detector.pyperclip')
    @patch('src.core.text_detector.time.sleep')
    def test_insert_text_success(self, mock_sleep, mock_pyperclip, mock_tfm_class, mock_controller_class):
        """Test successful text insertion via clipboard"""
        mock_controller = Mock()
        mock_controller.pressed = MagicMock()
        mock_controller.pressed.__enter__ = MagicMock()
        mock_controller.pressed.__exit__ = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_key = MagicMock()
        with patch('src.core.text_detector.Key', mock_key):
            detector = TextDetector()
            mock_pyperclip.paste.return_value = "original"
            mock_pyperclip.copy.return_value = None
            
            result = detector.insert_text("Hello world")
            
            assert result == True
            mock_pyperclip.copy.assert_any_call("Hello world")
            mock_controller.press.assert_called()
            mock_controller.release.assert_called()
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    @patch('src.core.text_detector.pyperclip')
    @patch('src.core.text_detector.time.sleep')
    def test_insert_text_clipboard_restore(self, mock_sleep, mock_pyperclip, mock_tfm_class, mock_controller_class):
        """Test clipboard content is restored"""
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        mock_key = MagicMock()
        with patch('src.core.text_detector.Key', mock_key):
            detector = TextDetector()
            original_content = "original clipboard"
            mock_pyperclip.paste.return_value = original_content
            
            detector.insert_text("New text")
            
            # Should restore original content
            assert mock_pyperclip.copy.call_count >= 2
            # Last call should restore original
            mock_pyperclip.copy.assert_any_call(original_content)
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    @patch('src.core.text_detector.pyperclip')
    @patch('src.core.text_detector.time.sleep')
    def test_insert_text_clipboard_read_failure(self, mock_sleep, mock_pyperclip, mock_tfm_class, mock_controller_class):
        """Test handling clipboard read failure"""
        mock_controller = Mock()
        mock_controller.pressed = MagicMock()
        mock_controller.pressed.__enter__ = MagicMock()
        mock_controller.pressed.__exit__ = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_key = MagicMock()
        with patch('src.core.text_detector.Key', mock_key):
            detector = TextDetector()
            mock_pyperclip.paste.side_effect = Exception("Read error")
            mock_pyperclip.copy.return_value = None
            
            result = detector.insert_text("Test text")
            
            # Should still succeed even if can't read original clipboard
            assert result == True
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    @patch('src.core.text_detector.pyperclip')
    @patch('src.core.text_detector.time.sleep')
    def test_insert_text_clipboard_write_failure(self, mock_sleep, mock_pyperclip, mock_tfm_class, mock_controller_class):
        """Test handling clipboard write failure"""
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        mock_key = MagicMock()
        with patch('src.core.text_detector.Key', mock_key):
            detector = TextDetector()
            mock_pyperclip.paste.return_value = "original"
            mock_pyperclip.copy.side_effect = Exception("Write error")
            
            result = detector.insert_text("Test text")
            
            assert result == False
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    @patch('src.core.text_detector.pyperclip')
    @patch('src.core.text_detector.time.sleep')
    def test_insert_text_clipboard_restore_failure(self, mock_sleep, mock_pyperclip, mock_tfm_class, mock_controller_class):
        """Test handling clipboard restore failure"""
        mock_controller = Mock()
        mock_controller.pressed = MagicMock()
        mock_controller.pressed.__enter__ = MagicMock()
        mock_controller.pressed.__exit__ = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_key = MagicMock()
        with patch('src.core.text_detector.Key', mock_key):
            detector = TextDetector()
            original_content = "original"
            mock_pyperclip.paste.return_value = original_content
            
            # First copy succeeds, restore fails
            call_count = 0
            def copy_side_effect(text):
                nonlocal call_count
                call_count += 1
                if call_count == 2:  # Restore attempt
                    raise Exception("Restore error")
            
            mock_pyperclip.copy.side_effect = copy_side_effect
            
            result = detector.insert_text("Test text")
            
            # Should still return success even if restore fails
            assert result == True
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    def test_insert_via_typing_success(self, mock_tfm_class, mock_controller_class):
        """Test _insert_via_typing method"""
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        
        detector = TextDetector()
        result = detector._insert_via_typing("Test text")
        
        assert result == True
        mock_controller.type.assert_called_once_with("Test text")
    
    @patch('src.core.text_detector.Controller')
    @patch('src.core.text_detector.TextFieldMonitor')
    def test_insert_via_typing_failure(self, mock_tfm_class, mock_controller_class):
        """Test _insert_via_typing with exception"""
        mock_controller = Mock()
        mock_controller.type.side_effect = Exception("Type error")
        mock_controller_class.return_value = mock_controller
        
        detector = TextDetector()
        result = detector._insert_via_typing("Test text")
        
        assert result == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

