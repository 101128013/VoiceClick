# VoiceClick Build Guide

This guide explains how to build VoiceClick from source into a distributable executable.

## Prerequisites

- Python 3.9+ installed
- Windows 10/11
- All dependencies from `requirements.txt`

## Quick Start

### Step 1: Install Build Tools
```bash
pip install pyinstaller
```

### Step 2: Build Executable
```bash
python scripts/build.py
```

Or on Windows:
```bash
scripts\build.bat
```

### Step 3: Test
Run `dist/VoiceClick.exe` to test the build.

### Step 4: Create Installer (Optional)
1. Download [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Install it
3. Open `installer/installer.iss` in Inno Setup Compiler
4. Click Build → Compile
5. Installer will be in `dist/installer/`

## Output Files

- `dist/VoiceClick.exe` - Standalone executable (~60-120MB)
- `dist/VoiceClick-Portable-v1.0.0.zip` - Portable version

## File Structure

- `voiceclick.spec` - PyInstaller configuration
- `scripts/build.py` - Python build script
- `scripts/build.bat` - Windows batch build script
- `installer/installer.iss` - Inno Setup installer script

## Customization

### Changing Version

Update version in:
- `src/config/constants.py` - `APP_VERSION`
- `installer/installer.iss` - `#define AppVersion`

### Adding Files to Installer

Edit `installer/installer.iss` and add files to the `[Files]` section.

### Customizing Installer Appearance

Edit `installer/installer.iss`:
- Change `SetupIconFile` for custom installer icon
- Modify `WizardStyle` for different wizard appearance
- Customize welcome/finish pages in `[Code]` section

## Troubleshooting

### PyInstaller Issues

- **Missing modules**: Add to `hiddenimports` in `voiceclick.spec`
- **Missing data files**: Add to `datas` in `voiceclick.spec`
- **Large file size**: Try `one-folder` mode instead of `one-file`

### Installer Issues

- **Inno Setup not found**: Install Inno Setup and ensure it's in PATH
- **Missing files**: Check that executable exists in `dist/` before building installer

### Build Size

The executable is large (~60-120MB) because it includes:
- Python runtime
- PyQt6 libraries
- All dependencies

This is normal for PyInstaller one-file builds. The portable ZIP is compressed.

## Automated Builds (GitHub Actions)

The `.github/workflows/build.yml` file automatically builds and creates releases when you push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This will trigger a build and create a GitHub Release with the executable and portable version.

## Code Signing (Optional)

To sign the executable and installer (prevents Windows Defender warnings):

1. Obtain a code signing certificate
2. Use `signtool.exe` to sign:
   ```bash
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com VoiceClick.exe
   ```

## Before Publishing

1. Update GitHub repo URL in `src/core/updater.py` (line 54)
2. Update version in `src/config/constants.py`
3. Test build on clean system
4. Create GitHub Release tag: `git tag v1.0.0 && git push origin v1.0.0`

