#!/usr/bin/env python3
"""
VoiceClick Application Entry Point.

This script launches the VoiceClick application, a voice-to-text tool.
It sets up logging, initializes the Qt application, and displays the main window.
"""

import sys
import logging
from pathlib import Path

# Add project root to the Python path to ensure correct module resolution.
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import torch-related modules BEFORE PyQt6 to avoid DLL loading conflicts
# This ensures torch DLLs are loaded before Qt's DLL loader interferes
try:
    import torch
    from faster_whisper import WhisperModel
except ImportError:
    pass  # Will be imported later when needed

# Now import PyQt6 after torch is loaded
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def setup_logging():
    """
    Configures logging for the application.
    
    Logs are saved to a file in the user's home directory and also streamed to the console.
    """
    log_dir = Path.home() / '.voice_click'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'voiceclick.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    # Suppress noisy logs from third-party libraries if necessary
    # logging.getLogger("some_library").setLevel(logging.WARNING)

def main():
    """
    Main application entry point.
    
    Initializes and runs the VoiceClick application.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting VoiceClick application...")

    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        
        logger.info("VoiceClick application started successfully.")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        # Optionally, show a user-friendly error dialog here
        sys.exit(1)


if __name__ == "__main__":
    main()
