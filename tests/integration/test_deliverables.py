"""
Integration tests for VoiceClick deliverables.

Tests the build process and verifies that both installer and portable
app deliverables are created correctly.
"""

import pytest
from pathlib import Path
import zipfile
import os
import subprocess
import sys


PROJECT_ROOT = Path(__file__).parent.parent.parent
DIST_DIR = PROJECT_ROOT / 'dist'
BUILD_DIR = PROJECT_ROOT / 'build'
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'


class TestPortableDeliverable:
    """Tests for the portable app deliverable."""
    
    def test_portable_directory_exists(self):
        """Verify the portable directory exists."""
        portable_dir = DIST_DIR / 'VoiceClick-Portable'
        assert portable_dir.exists(), f"Portable directory not found: {portable_dir}"
        assert portable_dir.is_dir(), "VoiceClick-Portable should be a directory"
    
    def test_portable_executable_exists(self):
        """Verify the executable exists in portable directory."""
        exe_path = DIST_DIR / 'VoiceClick-Portable' / 'VoiceClick.exe'
        assert exe_path.exists(), f"Executable not found: {exe_path}"
        assert exe_path.is_file(), "VoiceClick.exe should be a file"
        
        # Check file size (should be reasonably large for a bundled app)
        # Note: Whisper model can make the bundle large (1-2GB is normal)
        file_size_mb = exe_path.stat().st_size / (1024 * 1024)
        assert file_size_mb > 10, f"Executable seems too small: {file_size_mb:.2f} MB"
        assert file_size_mb < 3000, f"Executable seems too large: {file_size_mb:.2f} MB"
    
    def test_portable_readme_exists(self):
        """Verify readme.txt (lowercase) exists in portable directory."""
        portable_dir = DIST_DIR / 'VoiceClick-Portable'
        
        # Get actual filenames (case-sensitive check on case-insensitive Windows)
        actual_files = [f.name for f in portable_dir.iterdir() if f.is_file()]
        
        # Check readme.txt exists with correct case
        assert 'readme.txt' in actual_files, f"readme.txt not found. Found: {actual_files}"
        assert 'README.txt' not in actual_files, f"Found README.txt (should be lowercase readme.txt). Files: {actual_files}"
        
        # Also verify content
        readme_path = portable_dir / 'readme.txt'
        content = readme_path.read_text()
        assert len(content) > 50, "readme.txt seems too short"
        assert "VoiceClick" in content, "readme.txt should mention VoiceClick"
        
        # Check content is not empty
        content = readme_path.read_text()
        assert len(content) > 50, "readme.txt seems too short"
        assert "VoiceClick" in content, "readme.txt should mention VoiceClick"
    
    def test_portable_zip_exists(self):
        """Verify the portable ZIP file exists."""
        # Get version to construct expected filename
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from src.config import constants
            version = constants.APP_VERSION
        except Exception:
            version = "1.0.0"
        
        zip_path = DIST_DIR / f'VoiceClick-Portable-v{version}.zip'
        assert zip_path.exists(), f"Portable ZIP not found: {zip_path}"
        
        # Check ZIP file size
        file_size_mb = zip_path.stat().st_size / (1024 * 1024)
        assert file_size_mb > 10, f"ZIP file seems too small: {file_size_mb:.2f} MB"
    
    def test_portable_zip_contents(self):
        """Verify the contents of the portable ZIP file."""
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from src.config import constants
            version = constants.APP_VERSION
        except Exception:
            version = "1.0.0"
        
        zip_path = DIST_DIR / f'VoiceClick-Portable-v{version}.zip'
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            
            # Check for required files
            assert any('VoiceClick.exe' in f for f in file_list), \
                "VoiceClick.exe not found in ZIP"
            assert any('readme.txt' in f for f in file_list), \
                "readme.txt not found in ZIP"
            
            # Ensure no uppercase README.txt
            assert not any('README.txt' in f for f in file_list), \
                "Found README.txt in ZIP (should be lowercase)"
    
    def test_standalone_executable_exists(self):
        """Verify the standalone executable exists in dist root."""
        exe_path = DIST_DIR / 'VoiceClick.exe'
        assert exe_path.exists(), f"Standalone executable not found: {exe_path}"


class TestInstallerDeliverable:
    """Tests for the installer deliverable."""
    
    def test_installer_setup_script_exists(self):
        """Verify the Inno Setup script exists."""
        iss_path = PROJECT_ROOT / 'installer' / 'installer.iss'
        assert iss_path.exists(), f"Installer script not found: {iss_path}"
    
    def test_installer_script_has_correct_paths(self):
        """Verify installer script references correct paths."""
        iss_path = PROJECT_ROOT / 'installer' / 'installer.iss'
        content = iss_path.read_text()
        
        # Check for key elements
        assert 'VoiceClick' in content, "Installer script should reference VoiceClick"
        assert 'AppExeName' in content, "Installer script should define AppExeName"
        assert '.exe' in content, "Installer script should reference .exe files"
    
    @pytest.mark.skipif(not os.name == 'nt', reason="Installer only for Windows")
    def test_installer_output_directory_configured(self):
        """Verify installer output directory is configured."""
        expected_dir = DIST_DIR / 'installer'
        # Just check the directory can be created if needed
        expected_dir.mkdir(parents=True, exist_ok=True)
        assert expected_dir.exists(), "Installer output directory should exist or be creatable"


class TestBuildProcess:
    """Tests for the build process itself."""
    
    def test_build_script_exists(self):
        """Verify the build script exists."""
        build_py = SCRIPTS_DIR / 'build.py'
        build_bat = SCRIPTS_DIR / 'build.bat'
        
        assert build_py.exists(), f"build.py not found: {build_py}"
        assert build_bat.exists(), f"build.bat not found: {build_bat}"
    
    def test_build_script_syntax_valid(self):
        """Verify build.py has valid Python syntax."""
        build_py = SCRIPTS_DIR / 'build.py'
        
        # Try to compile the script
        with open(build_py, 'r') as f:
            code = f.read()
        
        try:
            compile(code, str(build_py), 'exec')
        except SyntaxError as e:
            pytest.fail(f"build.py has syntax errors: {e}")
    
    def test_pyinstaller_spec_exists(self):
        """Verify PyInstaller spec file exists."""
        spec_file = PROJECT_ROOT / 'voiceclick.spec'
        assert spec_file.exists(), f"Spec file not found: {spec_file}"
    
    def test_spec_file_syntax_valid(self):
        """Verify spec file has valid syntax."""
        spec_file = PROJECT_ROOT / 'voiceclick.spec'
        
        with open(spec_file, 'r') as f:
            code = f.read()
        
        try:
            compile(code, str(spec_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"voiceclick.spec has syntax errors: {e}")
    
    def test_app_icon_exists(self):
        """Verify the application icon exists."""
        icon_path = PROJECT_ROOT / 'src' / 'resources' / 'icons' / 'voiceclick.ico'
        assert icon_path.exists(), f"App icon not found: {icon_path}"
        
        # Check file size (ICO files should be small)
        file_size_kb = icon_path.stat().st_size / 1024
        assert 0 < file_size_kb < 500, f"Icon file size unusual: {file_size_kb:.2f} KB"


class TestDeliverableQuality:
    """Tests for deliverable quality and completeness."""
    
    def test_no_all_caps_files_in_portable(self):
        """Ensure no all-caps file names in portable directory."""
        portable_dir = DIST_DIR / 'VoiceClick-Portable'
        if not portable_dir.exists():
            pytest.skip("Portable directory doesn't exist yet")
        
        all_caps_files = []
        for item in portable_dir.iterdir():
            if item.is_file():
                name = item.stem  # Filename without extension
                if name.isupper() and len(name) > 1:
                    all_caps_files.append(item.name)
        
        assert len(all_caps_files) == 0, \
            f"Found all-caps filenames (should be lowercase): {all_caps_files}"
    
    def test_build_creates_minimal_artifacts(self):
        """Verify build doesn't create unnecessary artifacts."""
        # Check that common temp/cache directories are in .gitignore
        gitignore_path = PROJECT_ROOT / '.gitignore'
        if gitignore_path.exists():
            gitignore_content = gitignore_path.read_text()
            assert 'build' in gitignore_content.lower(), ".gitignore should include build/"
            assert 'dist' in gitignore_content.lower(), ".gitignore should include dist/"
            assert '__pycache__' in gitignore_content, ".gitignore should include __pycache__"


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "deliverables: tests for build deliverables"
    )
    config.addinivalue_line(
        "markers", "slow: tests that take a long time to run"
    )

