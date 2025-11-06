"""
Windows UI Automation wrapper for text field detection.

This module provides functionality to detect text fields and monitor focus changes
using the Windows UI Automation API.
"""

import logging
from typing import Optional
from dataclasses import dataclass

try:
    import win32gui
    import win32con
    import win32process
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    logging.warning("Windows API not available. Text field detection will use fallback methods.")

logger = logging.getLogger(__name__)


@dataclass
class TextFieldInfo:
    """Information about a detected text field."""
    is_text_field: bool
    control_type: Optional[str] = None
    application_name: Optional[str] = None
    window_title: Optional[str] = None
    is_password_field: bool = False
    is_readonly: bool = False
    bounds: Optional[tuple] = None  # (x, y, width, height)


class TextFieldMonitor:
    """
    Monitors and detects text fields using Windows UI Automation API.
    
    Provides methods to check if the currently focused element is a text field
    and to get information about it.
    """
    
    def __init__(self):
        """Initializes the TextFieldMonitor."""
        self.ui_automation = None
        self.root_element = None
        self._initialize_ui_automation()
    
    def _initialize_ui_automation(self):
        """Initializes the UI Automation COM interface."""
        if not WINDOWS_AVAILABLE:
            logger.warning("Windows API not available. Using fallback detection.")
            return
        
        # Note: Full UI Automation COM interface initialization is complex
        # For now, we use Windows API calls (win32gui) which are more reliable
        # This can be enhanced later with full UI Automation if needed
        logger.info("Using Windows API for text field detection.")
    
    def get_focused_element_info(self) -> TextFieldInfo:
        """
        Gets information about the currently focused UI element.
        
        Returns:
            TextFieldInfo object with details about the focused element.
        """
        if not WINDOWS_AVAILABLE:
            return TextFieldInfo(is_text_field=True)  # Fallback: assume text field
        
        try:
            # Get foreground window
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return TextFieldInfo(is_text_field=False)
            
            # Get window info
            window_title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            
            # Get process name
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                import psutil
                process = psutil.Process(pid)
                app_name = process.name()
            except (ImportError, Exception):
                # Fallback: use class name if psutil not available
                app_name = class_name
            
            # Check if focused control is likely a text field
            # This is a heuristic approach since full UI Automation can be complex
            focused_hwnd = win32gui.GetFocus()
            if focused_hwnd:
                focused_class = win32gui.GetClassName(focused_hwnd)
                focused_text = win32gui.GetWindowText(focused_hwnd)
                
                # Common text field class names in Windows
                text_field_classes = [
                    'Edit', 'RichEdit', 'RichEdit20W', 'RichEdit50W',
                    'RICHEDIT', 'RICHEDIT50W', 'RICHEDIT20W'
                ]
                
                is_text = focused_class in text_field_classes
                
                # Check for password field (heuristic: class name or style)
                is_password = False
                if is_text:
                    style = win32gui.GetWindowLong(focused_hwnd, win32con.GWL_STYLE)
                    # ES_PASSWORD = 0x0020
                    is_password = bool(style & 0x0020)
                
                # Get bounds
                try:
                    rect = win32gui.GetWindowRect(focused_hwnd)
                    bounds = (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
                except Exception:
                    bounds = None
                
                return TextFieldInfo(
                    is_text_field=is_text,
                    control_type=focused_class,
                    application_name=app_name,
                    window_title=window_title,
                    is_password_field=is_password,
                    bounds=bounds
                )
            
            # Fallback: check if window class suggests text editing
            text_window_classes = ['Notepad', 'WordPadClass', 'OpusApp', 'Chrome_WidgetWin_1']
            is_text_window = any(cls in class_name for cls in text_window_classes)
            
            return TextFieldInfo(
                is_text_field=is_text_window,
                control_type=class_name,
                application_name=app_name,
                window_title=window_title
            )
            
        except Exception as e:
            logger.error(f"Error detecting text field: {e}", exc_info=True)
            return TextFieldInfo(is_text_field=False)
    
    def is_text_field_active(self) -> bool:
        """
        Checks if a text field is currently active/focused.
        
        Returns:
            True if a text field is active, False otherwise.
        """
        info = self.get_focused_element_info()
        return info.is_text_field and not info.is_password_field
    
    def get_active_text_field_info(self) -> TextFieldInfo:
        """
        Gets detailed information about the active text field.
        
        Returns:
            TextFieldInfo object with details.
        """
        return self.get_focused_element_info()

