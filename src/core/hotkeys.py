"""
Global keyboard shortcuts/hotkeys manager for VoiceClick.

This module provides functionality to register and handle global keyboard shortcuts
that work system-wide, even when the application is not in focus.
"""

import logging
import threading
from typing import Optional, Callable

try:
    from pynput import keyboard
    from pynput.keyboard import Key, Listener
except ImportError:
    logging.error("pynput not available for global hotkeys")
    keyboard = None
    Key = None
    Listener = None

logger = logging.getLogger(__name__)


class HotkeyManager:
    """
    Manages global keyboard shortcuts for the application.
    
    Uses pynput to register system-wide hotkeys that work even when
    the application window is not focused.
    """
    
    def __init__(self):
        """Initializes the HotkeyManager."""
        self.listener: Optional[Listener] = None
        self.hotkeys: dict[str, Callable] = {}
        self.pressed_keys: set = set()
        self.running = False
        self.lock = threading.Lock()
        
    def register_hotkey(self, combination: str, callback: Callable) -> bool:
        """
        Registers a global hotkey combination.
        
        Args:
            combination: Hotkey combination string (e.g., "ctrl+shift+v")
            callback: Function to call when hotkey is pressed
            
        Returns:
            True if registration was successful, False otherwise
        """
        if keyboard is None:
            logger.error("Cannot register hotkeys: pynput not available")
            return False
            
        try:
            self.hotkeys[combination] = callback
            logger.info(f"Registered hotkey: {combination}")
            return True
        except Exception as e:
            logger.error(f"Failed to register hotkey {combination}: {e}", exc_info=True)
            return False
    
    def _parse_combination(self, combination: str) -> set:
        """
        Parses a hotkey combination string into a set of key identifiers.
        
        Args:
            combination: String like "ctrl+shift+v"
            
        Returns:
            Set of key identifiers
        """
        if Key is None:
            return set()
            
        parts = combination.lower().split('+')
        keys = set()
        
        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                keys.add(Key.ctrl)
            elif part == 'alt':
                keys.add(Key.alt)
            elif part == 'shift':
                keys.add(Key.shift)
            elif part == 'cmd' or part == 'win':
                keys.add(Key.cmd)
            elif len(part) == 1:
                keys.add(part)
            else:
                # Try to match as a Key enum value
                try:
                    key_attr = getattr(Key, part)
                    keys.add(key_attr)
                except AttributeError:
                    logger.warning(f"Unknown key: {part}")
                    
        return keys
    
    def _on_press(self, key):
        """Handles key press events."""
        try:
            with self.lock:
                # Normalize the key
                if hasattr(key, 'char') and key.char:
                    normalized_key = key.char
                else:
                    normalized_key = key
                    
                self.pressed_keys.add(normalized_key)
                
                # Check each registered hotkey
                for combination, callback in self.hotkeys.items():
                    required_keys = self._parse_combination(combination)
                    if required_keys.issubset(self.pressed_keys):
                        # Hotkey matched, execute callback
                        try:
                            callback()
                        except Exception as e:
                            logger.error(f"Error executing hotkey callback for {combination}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error in key press handler: {e}", exc_info=True)
    
    def _on_release(self, key):
        """Handles key release events."""
        try:
            with self.lock:
                # Normalize the key
                if hasattr(key, 'char') and key.char:
                    normalized_key = key.char
                else:
                    normalized_key = key
                    
                self.pressed_keys.discard(normalized_key)
        except Exception as e:
            logger.error(f"Error in key release handler: {e}", exc_info=True)
    
    def start(self):
        """Starts listening for hotkey presses."""
        if keyboard is None:
            logger.error("Cannot start hotkey listener: pynput not available")
            return False
            
        if self.running:
            logger.warning("Hotkey listener already running")
            return False
            
        try:
            self.listener = Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            self.running = True
            logger.info("Hotkey listener started")
            return True
        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}", exc_info=True)
            return False
    
    def stop(self):
        """Stops listening for hotkey presses."""
        if self.listener:
            try:
                self.listener.stop()
                self.listener = None
                self.running = False
                logger.info("Hotkey listener stopped")
            except Exception as e:
                logger.error(f"Error stopping hotkey listener: {e}", exc_info=True)


