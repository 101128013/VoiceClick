#!/usr/bin/env python3
"""
VoiceClick Application Entry Point
Main launcher for the VoiceClick voice-to-text application
"""

import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - VoiceClick - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / '.voice_click' / 'voiceclick.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are installed"""
    required = {
        'PyQt6': 'PyQt6',
        'faster_whisper': 'faster-whisper',
        'sounddevice': 'sounddevice',
        'numpy': 'numpy',
        'pynput': 'pynput',
        'pyperclip': 'pyperclip'
    }
    
    missing = []
    for import_name, package_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        print("\n❌ Missing dependencies!")
        print("Install with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True


def main():
    """Main application entry point"""
    logger.info("Starting VoiceClick application...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        from src.ui.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        
        logger.info("VoiceClick application started successfully")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
