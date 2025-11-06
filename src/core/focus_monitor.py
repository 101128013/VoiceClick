"""
Focus monitoring system for text fields.

This module provides functionality to monitor focus changes and detect when
text fields gain or lose focus, enabling automatic activation features.
"""

import logging
import threading
import time
from typing import Optional, Callable

from src.core.text_field_monitor import TextFieldMonitor, TextFieldInfo
from src.core.base_monitor import BaseMonitor

logger = logging.getLogger(__name__)


class FocusMonitor(BaseMonitor):
    """
    Monitors focus changes and detects when text fields are focused.
    
    Runs in a background thread and calls registered callbacks when
    text field focus events occur.
    """
    
    def __init__(self, text_field_monitor: Optional[TextFieldMonitor] = None, cooldown_period: float = 2.0, debounce_delay: float = 0.1):
        """
        Initializes the FocusMonitor.
        
        Args:
            text_field_monitor: Optional TextFieldMonitor instance. If None, creates one.
            cooldown_period: Seconds between activations (default: 2.0)
            debounce_delay: Minimum delay between focus checks (default: 0.1)
        """
        super().__init__(cooldown_period=cooldown_period, debounce_delay=debounce_delay)
        self.text_field_monitor = text_field_monitor or TextFieldMonitor()
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # State tracking
        self.last_focused_field: Optional[TextFieldInfo] = None
        self.last_focus_time: float = 0.0
    
    def register_callback(self, callback: Callable[[TextFieldInfo], None]):
        """
        Registers a callback to be called when a text field gains focus.
        
        Args:
            callback: Function that takes a TextFieldInfo parameter.
        """
        super().register_callback(callback, "focus callback")
    
    def unregister_callback(self, callback: Callable[[TextFieldInfo], None]):
        """Unregisters a callback."""
        super().unregister_callback(callback, "focus callback")
    
    def start_monitoring(self):
        """Starts monitoring focus changes in a background thread."""
        if self.monitoring:
            logger.warning("Focus monitoring already started.")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Focus monitoring started.")
    
    def stop_monitoring(self):
        """Stops monitoring focus changes."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)  # Increased timeout
            if self.monitor_thread.is_alive():
                logger.warning("Focus monitor thread did not stop within timeout")
        logger.info("Focus monitoring stopped.")
    
    def cleanup(self):
        """
        Ensures all resources are properly cleaned up.
        Should be called when the monitor is no longer needed.
        """
        self.stop_monitoring()
        super().cleanup()
    
    def _monitor_loop(self):
        """Main monitoring loop running in background thread."""
        logger.info("Focus monitor loop started.")
        
        while self.monitoring:
            try:
                current_info = self.text_field_monitor.get_focused_element_info()
                current_time = time.time()
                
                # Check if focus changed to a text field
                if current_info.is_text_field:
                    # Debounce: only trigger if enough time has passed
                    if (current_time - self.last_focus_time) >= self.debounce_delay:
                        # Check if this is a new focus (different from last)
                        if (self.last_focused_field is None or 
                            self._is_different_field(current_info, self.last_focused_field)):
                            
                            # Check cooldown period
                            if self._check_cooldown(current_time):
                                self._notify_callbacks(current_info, "focus callback")
                                self._update_activation_time(current_time)
                            
                            self.last_focused_field = current_info
                            self.last_focus_time = current_time
                else:
                    # Not a text field, reset tracking
                    if self.last_focused_field is not None:
                        self.last_focused_field = None
                        self.last_focus_time = current_time
                
                # Small sleep to prevent excessive CPU usage
                time.sleep(0.05)  # Check every 50ms
                
            except Exception as e:
                logger.error(f"Error in focus monitor loop: {e}", exc_info=True)
                time.sleep(0.1)  # Longer sleep on error
    
    def _is_different_field(self, info1: TextFieldInfo, info2: TextFieldInfo) -> bool:
        """Checks if two field infos represent different text fields."""
        if info1.bounds and info2.bounds:
            # Compare bounds (with small tolerance)
            tolerance = 5
            return (abs(info1.bounds[0] - info2.bounds[0]) > tolerance or
                    abs(info1.bounds[1] - info2.bounds[1]) > tolerance)
        
        # Compare by window title and control type
        return (info1.window_title != info2.window_title or
                info1.control_type != info2.control_type)
    

