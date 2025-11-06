"""
Build script for VoiceClick.

Automates the process of building the executable and creating the installer.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
BUILD_DIR = PROJECT_ROOT / 'build'
DIST_DIR = PROJECT_ROOT / 'dist'
SPEC_FILE = PROJECT_ROOT / 'voiceclick.spec'

def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous builds...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    print("[OK] Cleaned build directories")

def build_executable():
    """Build the executable using PyInstaller."""
    print("\nBuilding executable with PyInstaller...")
    
    if not SPEC_FILE.exists():
        print(f"ERROR: Spec file not found: {SPEC_FILE}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', str(SPEC_FILE)],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True
        )
        print("[OK] Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: PyInstaller failed:\n{e.stderr}")
        return False

def get_version():
    """Get version from constants."""
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from src.config import constants
        return constants.APP_VERSION
    except Exception:
        return "1.0.0"

def create_portable():
    """Create portable ZIP version."""
    print("\nCreating portable version...")
    
    exe_path = DIST_DIR / 'VoiceClick.exe'
    if not exe_path.exists():
        print("ERROR: Executable not found")
        return False
    
    portable_dir = DIST_DIR / 'VoiceClick-Portable'
    portable_dir.mkdir(exist_ok=True)
    
    # Copy executable
    shutil.copy2(exe_path, portable_dir / 'VoiceClick.exe')
    
    # Create README for portable version
    readme_content = """VoiceClick Portable Version
=======================

This is a portable version of VoiceClick that doesn't require installation.

Usage:
1. Extract this folder anywhere
2. Run VoiceClick.exe
3. Settings and history will be stored in your user directory

Note: First run may take longer as it downloads the Whisper model.
"""
    (portable_dir / 'readme.txt').write_text(readme_content)
    
    # Create ZIP
    version = get_version()
    zip_name = DIST_DIR / f'VoiceClick-Portable-v{version}.zip'
    
    shutil.make_archive(
        str(zip_name).replace('.zip', ''),
        'zip',
        portable_dir.parent,
        portable_dir.name
    )
    
    print(f"[OK] Portable version created: {zip_name.name}")
    return True

def main():
    """Main build process."""
    print("=" * 60)
    print("VoiceClick Build Script")
    print("=" * 60)
    
    # Check PyInstaller is installed
    try:
        import PyInstaller
        print(f"[OK] PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("ERROR: PyInstaller not installed. Install with: pip install pyinstaller")
        return 1
    
    # Clean
    clean_build()
    
    # Build executable
    if not build_executable():
        return 1
    
    # Create portable version
    create_portable()
    
    print("\n" + "=" * 60)
    print("Build completed successfully!")
    print("=" * 60)
    print(f"\nOutput:")
    print(f"  Executable: {DIST_DIR / 'VoiceClick.exe'}")
    print(f"  Portable: {DIST_DIR / 'VoiceClick-Portable-v{get_version()}.zip'}")
    print("\nNext steps:")
    print("  1. Test the executable")
    print("  2. Create installer using Inno Setup (installer.iss)")
    print("  3. (Optional) Code sign the executable")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

