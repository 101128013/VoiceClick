# VoiceClick Deployment Guide

This guide covers deploying and distributing VoiceClick to end users.

## Distribution Options

### Option 1: Installer (Recommended)
- **File**: `VoiceClick-Setup-v1.0.0.exe`
- **Size**: ~60-120MB
- **Type**: Windows Installer
- **Usage**: Double-click → Install → Use

### Option 2: Portable Version
- **File**: `VoiceClick-Portable-v1.0.0.zip`
- **Size**: ~50-100MB (compressed)
- **Type**: ZIP Archive
- **Usage**: Extract → Run VoiceClick.exe

## For End Users

### Installation Steps (Installer)

1. Download `VoiceClick-Setup-v1.0.0.exe` from GitHub Releases
2. Double-click the file
3. Click "Next" through the wizard
4. Choose installation location (default is fine)
5. Optionally create desktop shortcut
6. Click "Install"
7. Wait for installation (~30 seconds)
8. Click "Finish"
9. Launch from Start Menu

**Total time**: ~2 minutes

### Usage Steps (Portable)

1. Download `VoiceClick-Portable-v1.0.0.zip`
2. Right-click → Extract All
3. Open extracted folder
4. Double-click `VoiceClick.exe`
5. Done!

**Total time**: ~30 seconds

### First Launch

1. Application opens
2. Shows "Loading transcription model..."
3. Downloads Whisper model (2-5 minutes, one-time only)
4. Shows "Model loaded successfully"
5. Ready to use!

**Note**: Model download only happens once. Subsequent launches are instant.

## For Developers

### Building for Distribution

See `docs/build.md` for detailed build instructions.

### Automated Releases

When you push a version tag, GitHub Actions automatically:
- Builds the executable
- Creates a GitHub Release
- Uploads artifacts

```bash
git tag v1.0.0
git push origin v1.0.0
```

### Manual Distribution

1. Build the executable and installer (see `docs/build.md`)
2. Upload to your hosting service
3. Share download links with users

## Distribution Checklist

- [ ] Build executable successfully
- [ ] Test on clean Windows 11 VM
- [ ] Create installer
- [ ] Test installer on clean system
- [ ] Update version numbers
- [ ] Create GitHub Release
- [ ] Update README with download links
- [ ] (Optional) Code sign executable

## Key Features

### Standalone Executable
- All dependencies bundled
- Python runtime included
- No installation required (portable version)
- Works on any Windows 11 PC

### Professional Installer
- Modern wizard interface
- Customizable options
- Start menu integration
- Uninstaller
- Registry entries

### Auto-Updates
- Checks on startup (configurable)
- GitHub Releases integration
- User-friendly notifications
- One-click download

## Notes

- **File Size**: Executable is large (~60-120MB) - this is normal for PyInstaller
- **Models**: Whisper models are NOT bundled (downloaded on first run)
- **Dependencies**: All Python dependencies are included in executable
- **Windows Only**: Currently Windows-specific (uses pywin32)

