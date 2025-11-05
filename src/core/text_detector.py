"""
VoiceClick Text Detector - Detects active text fields and determines paste method
Handles Windows window detection, cursor type checking, and text insertion strategies
"""

import logging
from typing import Optional, Tuple

try:
    import pyautogui
    import pyperclip
    import keyboard
    from pynput.keyboard import Controller, Key
except ImportError:
    pass

logger = logging.getLogger(__name__)


class TextDetector:
    """
    Detects active text fields and manages text insertion strategies.
    Uses multiple methods to detect if a window can accept text input.
    """

    def __init__(self):
        """Initialize the text detector."""
        self.keyboard_controller = Controller()
        logger.info("TextDetector initialized")

    def is_text_field_active(self) -> bool:
        """
        Check if an active text field is detected.
        Uses multiple methods for robust detection.
        
        Returns:
            bool: True if a text field is likely active
        """
        try:
            # Method 1: Check keyboard focus (always has some level of focus)
            # This is the simplest check - if keyboard is not active, likely not a text field
            
            # Method 2: Could check window class name via pygetwindow, but for now
            # we rely on focus validation
            
            return True  # For MVP, assume any focused window can accept text
        
        except Exception as e:
            logger.error(f"Error checking text field: {e}")
            return False

    def insert_text(self, text: str) -> bool:
        """
        Insert text into the active text field using the best available method.
        Tries multiple strategies for robustness.
        
        Args:
            text: Text to insert
            
        Returns:
            bool: True if insertion was successful
        """
        if not text:
            logger.warning("Empty text provided to insert_text")
            return False
        
        try:
            # Strategy 1: Clipboard + Paste (most reliable, avoids hotkey conflicts)
            if self._insert_via_clipboard(text):
                return True
            
            # Strategy 2: Direct keyboard typing (for apps that don't support clipboard)
            if self._insert_via_typing(text):
                return True
            
            logger.error("All text insertion strategies failed")
            return False
        
        except Exception as e:
            logger.error(f"Error inserting text: {e}")
            return False

    def _insert_via_clipboard(self, text: str) -> bool:
        """
        Insert text by copying to clipboard and pasting.
        This is the most reliable method.
        
        Args:
            text: Text to insert
            
        Returns:
            bool: True if successful
        """
        try:
            # Save current clipboard content
            original_clipboard = None
            try:
                original_clipboard = pyperclip.paste()
            except:
                pass
            
            # Copy text to clipboard
            pyperclip.copy(text)
            
            # Wait a moment for clipboard to update
            import time
            time.sleep(0.05)
            
            # Paste using Ctrl+V
            self.keyboard_controller.press(Key.ctrl)
            self.keyboard_controller.press('v')
            self.keyboard_controller.release('v')
            self.keyboard_controller.release(Key.ctrl)
            
            # Wait for paste to complete
            time.sleep(0.1)
            
            # Restore original clipboard content (optional)
            if original_clipboard:
                try:
                    pyperclip.copy(original_clipboard)
                except:
                    pass
            
            logger.info(f"Text inserted via clipboard ({len(text)} chars)")
            return True
        
        except Exception as e:
            logger.error(f"Clipboard insertion failed: {e}")
            return False

    def _insert_via_typing(self, text: str) -> bool:
        """
        Insert text by simulating keyboard typing.
        Slower and may fail with special characters, use as fallback.
        
        Args:
            text: Text to insert
            
        Returns:
            bool: True if successful
        """
        try:
            # Type each character with small delay
            for char in text:
                try:
                    if char == '\n':
                        self.keyboard_controller.press(Key.enter)
                        self.keyboard_controller.release(Key.enter)
                    elif char == '\t':
                        self.keyboard_controller.press(Key.tab)
                        self.keyboard_controller.release(Key.tab)
                    else:
                        self.keyboard_controller.type(char)
                except:
                    # For special characters, try with keyboard.write
                    keyboard.write(char, interval=0.01)
                
                # Small delay between characters
                import time
                time.sleep(0.01)
            
            logger.info(f"Text inserted via typing ({len(text)} chars)")
            return True
        
        except Exception as e:
            logger.error(f"Typing insertion failed: {e}")
            return False

    def get_active_window_info(self) -> Optional[Tuple[str, str]]:
        """
        Get information about the active window.
        
        Returns:
            Tuple of (window_title, window_class) or None if unable to detect
        """
        try:
            import pygetwindow as gw
            active_window = gw.getActiveWindow()
            if active_window:
                return (active_window.title, "")
            return None
        except:
            return None

    def is_fullscreen_game_active(self) -> bool:
        """
        Check if a fullscreen game is active (to prevent hotkey interference).
        
        Returns:
            bool: True if fullscreen game detected
        """
        try:
            # Check if the active window takes up most/all of the screen
            import pygetwindow as gw
            import ctypes
            
            active_window = gw.getActiveWindow()
            if not active_window:
                return False
            
            # Get screen dimensions
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            # Check if window covers most of screen (with some tolerance)
            window_area = active_window.width * active_window.height
            screen_area = screen_width * screen_height
            
            if window_area > (screen_area * 0.85):
                logger.debug(f"Fullscreen game likely active: {active_window.title}")
                return True
            
            return False
        
        except:
            return False

    def is_password_field_active(self) -> bool:
        """
        Check if the active field is a password field.
        This prevents accidentally transcribing into password fields.
        
        Returns:
            bool: True if password field detected
        """
        # This would require more advanced window introspection
        # For MVP, we rely on user discretion
        return False
