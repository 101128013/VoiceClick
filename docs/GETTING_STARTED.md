# Getting Started with VoiceClick

Welcome to VoiceClick! This guide will help you understand the project structure and get started.

## Quick Overview

VoiceClick is a professional Windows 11 voice-to-text application. The project is organized into 4 phases with 30 total tasks.

**Current Status:** Phase 1 Complete, Phase 2 Ready to Start

## File Structure

The root directory contains only essential files:

```
app.py              - Main application launcher
monitor.py          - Development progress widget (optional)
PROJECT_ROADMAP.md  - 30-task development plan (READ THIS FIRST)
README.md           - Project overview
requirements.txt    - Python dependencies
.gitignore          - Git configuration
```

Everything else is organized by category:

- `src/` - Application source code
- `docs/` - Documentation and guides
- `tests/` - Unit tests
- `examples/` - Example code
- `.github/` - CI/CD workflows
- `installer/` - Build scripts

## First Steps

### 1. Read the Roadmap
Start with `PROJECT_ROADMAP.md` - it explains all 30 tasks and current progress.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Progress Widget (Optional)
```bash
python monitor.py
```

This shows development progress in a small widget on your taskbar. Keyboard shortcuts:
- **Up/Down arrows** - Navigate tasks
- **ESC** - Toggle visibility

### 4. Review the Code
Check out `src/core/` for the main modules:
- `engine.py` - Speech recognition engine
- `text_detector.py` - Text field detection
- `history.py` - Transcription history

### 5. Start Development
Ready to build? See Phase 2 - UI Development in `PROJECT_ROADMAP.md`

## Documentation Guide

All documentation is in the `docs/` folder:

- `QUICK_REFERENCE.md` - Quick facts and commands
- `ORGANIZATION_COMPLETE.md` - How we organized the project
- `CLEANUP_IMPLEMENTATION_GUIDE.md` - Technical details
- `PROJECT_STATUS.md` - Current status summary
- `ARCHIVED_PHASE1/` - Historical reference (Phase 1 work)

## Project Phases

### Phase 1: Setup & Architecture (Complete)
- Project repository setup
- Requirements defined
- Modular architecture created
- Configuration system implemented

**Status:** 4/4 tasks done

### Phase 2: UI Development (In Progress)
- Main window design
- UI components (Status, Settings, History tabs)
- System tray integration
- Engine connection

**Status:** Ready to start, next task: Design Main Window

### Phase 3: Testing & Packaging (Pending)
- Unit tests
- PyInstaller executable
- NSIS installer
- Windows 11 VM testing

**Status:** Not started

### Phase 4: Documentation & Release (Pending)
- Professional documentation
- CI/CD pipeline
- Beta testing
- GitHub release

**Status:** Not started

## Running the Application

### Main App
```bash
python app.py
```

### Progress Widget
```bash
python monitor.py
```

The widget appears above your taskbar showing real-time project progress.

## Development Workflow

1. **Pick a task** from `PROJECT_ROADMAP.md`
2. **Create** or **modify** files in `src/`
3. **Test** your changes
4. **Commit** to git
5. **Update** progress in roadmap

## Core Modules

### src/core/engine.py
The main transcription engine using Whisper. Features:
- Audio recording with sounddevice
- Real-time volume monitoring
- Silence detection
- Transcription processing

### src/core/text_detector.py
Detects text fields and inserts transcribed text. Features:
- Multi-strategy text insertion
- Clipboard and keyboard fallback
- Window analysis
- Password field detection

### src/core/history.py
Manages transcription history. Features:
- JSON persistence
- Search functionality
- Export to CSV/TXT
- Statistics calculation

### src/config/settings.py
Configuration management with 20+ parameters and JSON persistence.

## UI Components

### src/ui/progress_widget.py
Progress bar and status display widgets for Phase 2 UI.

### src/ui/progress_manager.py
Tracks all 30 development tasks and provides progress signals.

### src/ui/main_window.py
To be created in Phase 2 Task 5 - main application window.

## Next Steps

### This Session
1. Read `PROJECT_ROADMAP.md`
2. Review `src/core/` modules
3. Understand the 30-task plan
4. Check progress widget functionality

### Next Session
Start Phase 2 Task 5: Design Main Window

**What you'll do:**
1. Create `src/ui/main_window.py`
2. Design PyQt6 application window
3. Add menu bar and status bar
4. Create tab container
5. Implement window logic

**Estimated time:** 2-3 hours

### Following Sessions
Complete remaining Phase 2 tasks (6-12) over 3-4 more sessions.

## Helpful Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run main app
python app.py

# Run progress widget
python monitor.py

# Check imports
python -c "from src.core import engine; print('OK')"

# List project structure
tree /F /L 2

# Git status
git status

# Git commit
git commit -am "Your message"
```

## File Locations

| What | Where |
|------|-------|
| Core engine | src/core/engine.py |
| Text detection | src/core/text_detector.py |
| History | src/core/history.py |
| Settings | src/config/settings.py |
| UI components | src/ui/ |
| Tests | tests/ |
| Examples | examples/ |
| Docs | docs/ |
| Roadmap | PROJECT_ROADMAP.md |

## Support

- **Questions about tasks?** See `PROJECT_ROADMAP.md`
- **Questions about code?** Check `src/core/` docstrings
- **Questions about structure?** See `docs/ORGANIZATION_COMPLETE.md`
- **Historical info?** Check `docs/ARCHIVED_PHASE1/`

## Key Points

- Project has clear 30-task roadmap
- Phase 1 complete, Phase 2 ready
- Clean, organized folder structure
- All core code preserved and functional
- Progress widget working
- Well-documented and ready for development

---

Ready to start? Pick up with Phase 2 Task 5 when you're ready.

Enjoy building VoiceClick!
