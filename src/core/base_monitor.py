"""
Base class for text field monitors.

This module provides a base class that contains common functionality
for monitoring text fields, including callback management and cooldown logic.
"""

import logging
import threading
import time
from typing import Optional, Callable

from src.core.text_field_monitor import TextFieldInfo

logger = logging.getLogger(__name__)


class BaseMonitor:
    """
    Base class for text field monitors.
    
    Provides common functionality for callback management, cooldown logic,
    and resource cleanup.
    """
    
    def __init__(self, cooldown_period: float = 2.0, debounce_delay: float = 0.1):
        """
        Initializes the BaseMonitor.
        
        Args:
            cooldown_period: Seconds between activations (default: 2.0)
            debounce_delay: Minimum delay between events (default: 0.1)
        """
        self.callbacks: list[Callable[[TextFieldInfo], None]] = []
        self.callbacks_lock = threading.Lock()
        self.cooldown_period: float = cooldown_period
        self.debounce_delay: float = debounce_delay
        self.last_activation_time: float = 0.0
    
    def register_callback(self, callback: Callable[[TextFieldInfo], None], callback_name: str = "callback"):
        """
        Registers a callback to be called when a text field event occurs.
        
        Args:
            callback: Function that takes a TextFieldInfo parameter.
            callback_name: Name for logging purposes.
        """
        with self.callbacks_lock:
            if callback not in self.callbacks:
                self.callbacks.append(callback)
                func_name = getattr(callback, '__name__', 'unknown')
                logger.info(f"Registered {callback_name}: {func_name}")
    
    def unregister_callback(self, callback: Callable[[TextFieldInfo], None], callback_name: str = "callback"):
        """
        Unregisters a callback.
        
        Args:
            callback: Function to unregister.
            callback_name: Name for logging purposes.
        """
        with self.callbacks_lock:
            if callback in self.callbacks:
                self.callbacks.remove(callback)
                func_name = getattr(callback, '__name__', 'unknown')
                logger.info(f"Unregistered {callback_name}: {func_name}")
    
    def _notify_callbacks(self, field_info: TextFieldInfo, callback_name: str = "callback"):
        """
        Notifies all registered callbacks of an event.
        
        Args:
            field_info: Information about the text field event.
            callback_name: Name for logging purposes.
        """
        # Create a copy of callbacks list to avoid lock contention during iteration
        with self.callbacks_lock:
            callbacks_copy = self.callbacks.copy()
        
        for callback in callbacks_copy:
            try:
                callback(field_info)
            except Exception as e:
                func_name = getattr(callback, '__name__', 'unknown')
                logger.error(f"Error in {callback_name} {func_name}: {e}", exc_info=True)
    
    def _check_cooldown(self, current_time: Optional[float] = None) -> bool:
        """
        Checks if enough time has passed since last activation.
        
        Args:
            current_time: Current time (defaults to time.time() if None)
            
        Returns:
            True if cooldown period has passed, False otherwise.
        """
        if current_time is None:
            current_time = time.time()
        return (current_time - self.last_activation_time) >= self.cooldown_period
    
    def set_cooldown_period(self, seconds: float):
        """
        Sets the cooldown period between activations.
        
        Args:
            seconds: Cooldown period in seconds (will be clamped to >= 0).
        """
        self.cooldown_period = max(0.0, seconds)
        logger.info(f"Cooldown period set to {self.cooldown_period}s")
    
    def reset_cooldown(self):
        """Resets the cooldown timer (allows immediate activation)."""
        self.last_activation_time = 0.0
    
    def _update_activation_time(self, current_time: Optional[float] = None):
        """
        Updates the last activation time.
        
        Args:
            current_time: Current time (defaults to time.time() if None).
        """
        self.last_activation_time = current_time if current_time is not None else time.time()
    
    def cleanup(self):
        """
        Ensures all resources are properly cleaned up.
        Should be called when the monitor is no longer needed.
        """
        with self.callbacks_lock:
            self.callbacks.clear()
        logger.info(f"{self.__class__.__name__} cleanup complete.")

