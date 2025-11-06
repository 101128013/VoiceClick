"""
Mouse click monitoring for text field detection.

This module monitors mouse clicks and detects when users click on text fields,
enabling auto-start recording on click functionality.
"""

import logging
import time
from typing import Optional, Callable

try:
    from pynput.mouse import Listener, Button
    MOUSE_AVAILABLE = True
except ImportError:
    MOUSE_AVAILABLE = False
    logging.warning("pynput mouse not available. Click detection disabled.")

from src.core.text_field_monitor import TextFieldMonitor, TextFieldInfo
from src.core.base_monitor import BaseMonitor

logger = logging.getLogger(__name__)


class ClickMonitor(BaseMonitor):
    """
    Monitors mouse clicks and detects clicks on text fields.
    
    Uses mouse event monitoring combined with text field detection
    to determine when a user clicks on a text input field.
    """
    
    def __init__(self, text_field_monitor: Optional[TextFieldMonitor] = None, cooldown_period: float = 2.0, debounce_delay: float = 0.2):
        """
        Initializes the ClickMonitor.
        
        Args:
            text_field_monitor: Optional TextFieldMonitor instance. If None, creates one.
            cooldown_period: Seconds between activations (default: 2.0)
            debounce_delay: Minimum delay between clicks (default: 0.2)
        """
        super().__init__(cooldown_period=cooldown_period, debounce_delay=debounce_delay)
        
        if not MOUSE_AVAILABLE:
            logger.warning("Mouse monitoring not available. Click detection disabled.")
            self.available = False
            self.monitoring = False
            self.listener = None
            self.text_field_monitor = None
            self.last_click_time = 0.0
            return
        
        self.available = True
        self.text_field_monitor = text_field_monitor or TextFieldMonitor()
        self.monitoring = False
        self.listener: Optional[Listener] = None
        
        # State tracking
        self.last_click_time: float = 0.0
    
    def register_callback(self, callback: Callable[[TextFieldInfo], None]):
        """
        Registers a callback to be called when a text field is clicked.
        
        Args:
            callback: Function that takes a TextFieldInfo parameter.
        """
        if not self.available:
            logger.warning("Click monitoring not available. Callback not registered.")
            return
        
        super().register_callback(callback, "click callback")
    
    def unregister_callback(self, callback: Callable[[TextFieldInfo], None]):
        """Unregisters a callback."""
        super().unregister_callback(callback, "click callback")
    
    def start_monitoring(self):
        """Starts monitoring mouse clicks."""
        if not self.available:
            logger.warning("Mouse monitoring not available. Cannot start.")
            return
        
        if self.monitoring:
            logger.warning("Click monitoring already started.")
            return
        
        try:
            self.monitoring = True
            self.listener = Listener(on_click=self._on_click)
            self.listener.start()
            logger.info("Click monitoring started.")
        except Exception as e:
            logger.error(f"Failed to start click monitoring: {e}", exc_info=True)
            self.monitoring = False
    
    def stop_monitoring(self):
        """Stops monitoring mouse clicks."""
        if not self.available or not self.monitoring:
            return
        
        self.monitoring = False
        if self.listener:
            try:
                self.listener.stop()
            except Exception as e:
                logger.warning(f"Error stopping click listener: {e}")
            finally:
                self.listener = None
        logger.info("Click monitoring stopped.")
    
    def cleanup(self):
        """
        Ensures all resources are properly cleaned up.
        Should be called when the monitor is no longer needed.
        """
        self.stop_monitoring()
        super().cleanup()
    
    def _on_click(self, x: int, y: int, button: Button, pressed: bool):
        """
        Handles mouse click events.
        
        Args:
            x: X coordinate of the click
            y: Y coordinate of the click
            button: Mouse button that was clicked
            pressed: True if button was pressed, False if released
        """
        if not pressed or button != Button.left:
            return  # Only handle left button press
        
        current_time = time.time()
        
        # Debounce: ignore rapid clicks
        if (current_time - self.last_click_time) < self.debounce_delay:
            return
        
        self.last_click_time = current_time
        
        # Small delay to allow field to receive focus
        time.sleep(0.1)
        
        # Check if a text field is now focused
        try:
            field_info = self.text_field_monitor.get_focused_element_info()
            
            if field_info.is_text_field and not field_info.is_password_field:
                # Check cooldown period
                if self._check_cooldown(current_time):
                    self._notify_callbacks(field_info, "click callback")
                    self._update_activation_time(current_time)
                    logger.info(f"Text field clicked: {field_info.application_name} - {field_info.window_title}")
        except Exception as e:
            logger.error(f"Error processing click: {e}", exc_info=True)
    

