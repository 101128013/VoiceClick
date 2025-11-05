# VoiceClick User Documentation

## Installation Guide

### System Requirements
- **OS**: Windows 11 22H2 or later
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 2GB free space
- **GPU**: NVIDIA GPU with CUDA support (optional, for faster transcription)

### Installation Methods

#### Method 1: Installer (Recommended)
1. Download `VoiceClick-1.0.0-installer.exe`
2. Run the installer and follow prompts
3. Choose installation directory (default: `C:\Program Files\VoiceClick`)
4. Click "Install"
5. Launch from Start Menu or Desktop shortcut

#### Method 2: Portable
1. Download `VoiceClick-1.0.0-portable.zip`
2. Extract to desired location
3. Run `VoiceClick.exe`
4. No installation required

### Dependencies
VoiceClick includes all required dependencies. You may need:
- **.NET Framework 4.8** - Usually pre-installed on Windows 11
- **Visual C++ Redistributable** - Download from Microsoft if needed
- **NVIDIA CUDA 11.8+** - Only if using GPU acceleration

## User Guide

### Starting VoiceClick

1. Launch `VoiceClick` from Start Menu or run `VoiceClick.exe`
2. Wait for initialization (~5 seconds first run)
3. Check the Status tab to verify:
   - Audio input device is detected
   - Whisper model is loaded
   - GPU acceleration status (if available)

### Recording Transcription

1. Click the **"Start Recording"** button or press `Ctrl+Shift+R`
2. Speak clearly into your microphone
3. The Status tab shows:
   - Recording duration
   - Audio levels
   - Model processing status
4. Click **"Stop Recording"** when done
5. Transcription appears in History tab

### Using Settings

1. Open **Settings** tab
2. **Model Selection**:
   - `tiny.en` - Fastest (English only)
   - `base.en` - Good balance
   - `small` - High accuracy (multilingual)
   - `medium` - Best accuracy (multilingual)
   - `large` - Highest accuracy (requires 10GB RAM)

3. **Device Selection**:
   - `Auto` - Automatic detection
   - `CUDA` - NVIDIA GPU (if available)
   - `CPU` - Processor only

4. **Output Format**:
   - Plain text
   - SRT (subtitle format)
   - JSON (detailed metadata)

5. Click **Save Settings** to apply changes

### Searching History

1. Open **History** tab
2. Use **Search** box to find transcriptions by keyword
3. View matched results in list
4. Click result to view full text

### Exporting Transcriptions

1. Select transcription in History tab
2. Click **Export** button
3. Choose format (TXT, PDF, Word)
4. Select save location
5. File is saved with timestamp

### System Tray

- Minimize to system tray (click X button)
- Right-click tray icon for options:
  - Show/Hide window
  - Quick record (with custom duration)
  - Exit application

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+R` | Start/Stop recording |
| `Ctrl+F` | Focus search box |
| `Ctrl+Q` | Quit application |
| `Ctrl+,` | Open Settings |

## Troubleshooting

### Application Won't Start
- Ensure Windows 11 22H2 is installed
- Install Visual C++ Redistributable from Microsoft
- Check event viewer for error details
- Try running as Administrator

### Audio Issues
- Check microphone is properly connected
- Verify microphone is not muted in Windows
- Test microphone in Windows Settings > Sound
- In VoiceClick Settings, verify correct device is selected

### No Transcription Output
- Check audio volume wasn't too low
- Verify selected language model is loaded
- Check disk space (models require 1-3GB)
- Try restarting application

### Slow Transcription
- Smaller models are faster (use `tiny` or `base`)
- Enable GPU acceleration if available
- Reduce background processes
- Increase available RAM

### GPU Not Detected
- Install NVIDIA CUDA 11.8 or later
- Install cuDNN 8.5 or later
- Ensure NVIDIA drivers are updated
- Verify NVIDIA GPU is supported (Compute Capability 3.5+)

### High Memory Usage
- Switch to smaller model (`tiny` or `base`)
- Close other applications
- Enable virtual memory/pagefile

## Advanced Configuration

### Model Download Locations
Models are automatically downloaded to:
```
C:\Users\[Username]\AppData\Local\VoiceClick\models
```

To use custom model location, edit `config.json`:
```json
{
  "model_dir": "C:\\custom\\path\\to\\models"
}
```

### Command Line Arguments
```bash
VoiceClick.exe --model tiny --device cuda --no-gui
```

### Configuration File
Located at: `%APPDATA%\VoiceClick\settings.json`

## Performance Tips

1. **Faster Transcription**:
   - Use smaller models (tiny, base)
   - Enable GPU acceleration
   - Reduce audio quality if acceptable

2. **Better Accuracy**:
   - Use larger models (medium, large)
   - Ensure good audio quality
   - Speak clearly at normal pace

3. **Lower Memory Usage**:
   - Use smaller models
   - Enable GPU if available
   - Close background applications

4. **Optimized for Batch Processing**:
   - Record multiple clips
   - Process all at end of session
   - Export results in bulk

## Support and Feedback

- **GitHub**: https://github.com/101128013/VoiceClick
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join community discussions
- **Email**: support@voiceclick.dev

## License

VoiceClick is released under the MIT License. See LICENSE.txt for details.

## Version History

### v1.0.0 (2025-11-05)
- Initial release
- Whisper large-v3 model support
- CUDA GPU acceleration
- Multi-language support
- History search and export
- System tray integration
- Keyboard shortcuts
- Settings persistence

## FAQ

**Q: Can I use VoiceClick offline?**
A: Yes, once models are downloaded, the application works completely offline.

**Q: Does VoiceClick send data to the cloud?**
A: No, all processing happens locally on your computer.

**Q: Can I use a different speech recognition model?**
A: Yes, edit config.json to specify a custom model path.

**Q: Is there a Mac or Linux version?**
A: Not currently, but the codebase is cross-platform compatible.

**Q: How do I update to a new version?**
A: Download the latest installer or portable version and run/extract it.

**Q: Can I use VoiceClick with other microphones?**
A: Yes, any Windows-compatible audio input device works.

---

**Last Updated**: November 5, 2025
**VoiceClick Version**: 1.0.0
