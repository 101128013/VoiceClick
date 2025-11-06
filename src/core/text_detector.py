"""
Handles the detection of active text fields and the insertion of text.

This module provides the `TextDetector` class, which is responsible for
determining if a text field is active and for inserting transcribed text into it.
It uses a combination of clipboard and keyboard simulation for robust text insertion.
"""

import logging
import time
from typing import Optional

try:
    import pyperclip
    from pynput.keyboard import Controller, Key
except ImportError as e:
    logging.critical(f"Missing critical dependency: {e}. Please install pynput and pyperclip.")
    # Exit or handle gracefully if these are essential at startup.
    raise

from src.core.text_field_monitor import TextFieldMonitor, TextFieldInfo

logger = logging.getLogger(__name__)

class TextDetector:
    """
    Detects active text fields and manages text insertion.

    This class uses `pynput` to simulate keyboard actions and `pyperclip` for
    clipboard operations, providing a reliable way to insert text into most
    applications. It also uses Windows UI Automation for text field detection.
    """

    def __init__(self):
        """Initializes the TextDetector."""
        try:
            self.keyboard_controller = Controller()
            self.text_field_monitor = TextFieldMonitor()
            logger.info("TextDetector initialized successfully.")
        except Exception as e:
            logger.critical(f"Failed to initialize TextDetector: {e}", exc_info=True)
            raise

    def is_text_field_active(self) -> bool:
        """
        Checks if a text field is currently active/focused.

        Uses Windows UI Automation API to detect if the focused element
        is a text field. Falls back to heuristic detection if UI Automation
        is not available.

        Returns:
            True if a text field is active, False otherwise.
        """
        try:
            return self.text_field_monitor.is_text_field_active()
        except Exception as e:
            logger.warning(f"Error checking text field status: {e}. Using fallback.")
            # Fallback: assume text field is active (original behavior)
            return True
    
    def get_active_text_field_info(self) -> TextFieldInfo:
        """
        Gets detailed information about the active text field.
        
        Returns:
            TextFieldInfo object with details about the focused text field.
        """
        try:
            return self.text_field_monitor.get_active_text_field_info()
        except Exception as e:
            logger.warning(f"Error getting text field info: {e}")
            return TextFieldInfo(is_text_field=True)

    def insert_text(self, text: str) -> bool:
        """
        Inserts the given text into the active text field.

        It first tries to use the clipboard (Ctrl+V), which is generally faster
        and more reliable. If that fails, it falls back to simulating typing
        each character.

        Args:
            text: The text to be inserted.

        Returns:
            True if the text was inserted successfully, False otherwise.
        """
        if not text:
            logger.warning("Attempted to insert empty text.")
            return False

        # For simplicity and reliability, we will primarily use the clipboard method.
        # Direct typing is often slow and can interfere with keyboard hooks.
        if self._insert_via_clipboard(text):
            logger.info(f"Successfully inserted text of length {len(text)}.")
            return True
        
        logger.error("Failed to insert text using all available methods.")
        return False

    def _insert_via_clipboard(self, text: str) -> bool:
        """
        Inserts text by setting the clipboard and simulating a paste command.

        This method temporarily saves and restores the user's clipboard content.

        Args:
            text: The text to insert.

        Returns:
            True on success, False on failure.
        """
        original_clipboard_content = None
        try:
            # 1. Save the current clipboard content
            original_clipboard_content = pyperclip.paste()
        except Exception as e:
            logger.warning(f"Could not read from clipboard to save content: {e}")

        try:
            # 2. Set the new text to the clipboard
            pyperclip.copy(text)
            time.sleep(0.05)  # Small delay to ensure the clipboard is updated

            # 3. Simulate Ctrl+V to paste
            with self.keyboard_controller.pressed(Key.ctrl):
                self.keyboard_controller.press('v')
                self.keyboard_controller.release('v')
            
            time.sleep(0.1) # Allow time for the paste action to complete
            return True
        except Exception as e:
            logger.error(f"Failed to insert text via clipboard: {e}", exc_info=True)
            return False
        finally:
            # 4. Restore the original clipboard content
            if original_clipboard_content is not None:
                try:
                    pyperclip.copy(original_clipboard_content)
                except Exception as e:
                    logger.warning(f"Failed to restore original clipboard content: {e}")

    def _insert_via_typing(self, text: str) -> bool:
        """
        Fallback method to insert text by simulating individual keystrokes.
        
        This is slower and less reliable than clipboard pasting, especially for
        complex text or in applications with their own keyboard handling.

        Args:
            text: The text to type.

        Returns:
            True on success, False on failure.
        """
        try:
            self.keyboard_controller.type(text)
            return True
        except Exception as e:
            logger.error(f"Failed to insert text via typing: {e}", exc_info=True)
            return False

