"""
Focus monitoring system for text fields.

This module provides functionality to monitor focus changes and detect when
text fields gain or lose focus, enabling automatic activation features.
"""

import logging
import threading
import time
from typing import Optional, Callable
from queue import Queue

from src.core.text_field_monitor import TextFieldMonitor, TextFieldInfo

logger = logging.getLogger(__name__)


class FocusMonitor:
    """
    Monitors focus changes and detects when text fields are focused.
    
    Runs in a background thread and calls registered callbacks when
    text field focus events occur.
    """
    
    def __init__(self, text_field_monitor: Optional[TextFieldMonitor] = None):
        """
        Initializes the FocusMonitor.
        
        Args:
            text_field_monitor: Optional TextFieldMonitor instance. If None, creates one.
        """
        self.text_field_monitor = text_field_monitor or TextFieldMonitor()
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.callbacks: list[Callable[[TextFieldInfo], None]] = []
        
        # State tracking
        self.last_focused_field: Optional[TextFieldInfo] = None
        self.last_focus_time: float = 0.0
        self.debounce_delay: float = 0.1  # 100ms debounce
        
        # Cooldown to prevent rapid re-activation
        self.cooldown_period: float = 2.0  # 2 seconds
        self.last_activation_time: float = 0.0
        
    def register_callback(self, callback: Callable[[TextFieldInfo], None]):
        """
        Registers a callback to be called when a text field gains focus.
        
        Args:
            callback: Function that takes a TextFieldInfo parameter.
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)
            logger.info(f"Registered focus callback: {callback.__name__}")
    
    def unregister_callback(self, callback: Callable[[TextFieldInfo], None]):
        """Unregisters a callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            logger.info(f"Unregistered focus callback: {callback.__name__}")
    
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
            self.monitor_thread.join(timeout=2.0)
        logger.info("Focus monitoring stopped.")
    
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
                            if (current_time - self.last_activation_time) >= self.cooldown_period:
                                self._notify_callbacks(current_info)
                                self.last_activation_time = current_time
                            
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
    
    def _notify_callbacks(self, field_info: TextFieldInfo):
        """Notifies all registered callbacks of a focus event."""
        for callback in self.callbacks:
            try:
                callback(field_info)
            except Exception as e:
                logger.error(f"Error in focus callback {callback.__name__}: {e}", exc_info=True)
    
    def set_cooldown_period(self, seconds: float):
        """Sets the cooldown period between activations."""
        self.cooldown_period = max(0.0, seconds)
        logger.info(f"Cooldown period set to {self.cooldown_period}s")
    
    def reset_cooldown(self):
        """Resets the cooldown timer (allows immediate activation)."""
        self.last_activation_time = 0.0

