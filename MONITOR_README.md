# VoiceClick Development Monitor

**Standalone taskbar widget for real-time project progress monitoring**

## What It Does

The VoiceClick Monitor is a **non-interactive, always-on-top widget** that displays on top of your Windows taskbar and shows:

```
┌─────────────────────────────────────┐
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  ← GREEN progress bar (4px)
│ Task 5/30: Design main window (17%) │  ← Line 1: Task info
│ UI Design • 17% complete            │  ← Line 2: Stage info
└─────────────────────────────────────┘
  ▲ Positioned above taskbar          
  └─ Only 70px tall, 500px wide
```

## Features

✅ **Minimal & Non-Intrusive**
- Only 70px height, fits perfectly above taskbar
- Green progress bar only (no background clutter)
- Read-only, can't be interacted with
- Double-click to hide/show

✅ **Accurate Progress Tracking**
- 30 tasks mapped to 16 development phases
- Real-time percentage updates
- Task descriptions + current stage
- Updates every second

✅ **Auto-Start on Login**
- Runs automatically when Windows starts
- Starts minimized, just monitors in background
- No need to manually launch

✅ **Simple Control**
- Keyboard shortcuts: ↑/↓ to navigate tasks
- Command line control: `python monitor_control.py`
- Can be manually updated via progress.json

## Quick Start

### 1. Enable Auto-Start (Run Once)

**Option A:** Click the batch file
```
Double-click: enable_autostart.bat
```

**Option B:** Command line
```powershell
python monitor.py --autostart
```

The monitor will now start automatically when you log in!

### 2. Start Monitor Immediately

```powershell
# Simple start
python monitor.py

# Or via control script
python monitor_control.py start
```

### 3. Control the Monitor

```powershell
# Set to specific task (1-30)
python monitor_control.py set-task 5

# Move to next task
python monitor_control.py next

# Move to previous task
python monitor_control.py prev

# Reset to task 1
python monitor_control.py reset

# Disable auto-start
python monitor_control.py autostart-off
```

## Manual Task Updates

Edit the progress file directly:

```json
~/.voice_click/progress.json

{
  "current_task": 5,
  "total_tasks": 30,
  "timestamp": "2025-11-05T14:30:00"
}
```

The monitor reads this every second and updates the display automatically.

## Keyboard Shortcuts

When widget is focused:
- **↑** - Previous task
- **↓** - Next task  
- **ESC** - Hide widget
- **Double-click** - Toggle visibility

## Files

```
monitor.py              Main widget application
monitor_control.py      Command-line control script
enable_autostart.bat    Enable auto-start on login
disable_autostart.bat   Disable auto-start
```

## Task Definitions (All 30)

```
Task 1-4:   Setup & Architecture
Task 5-12:  UI Development  
Task 13-20: Testing & Packaging
Task 21-30: Documentation & Release
```

## Technical Details

**Technology Stack:**
- PyQt6 for GUI
- Frameless window (no titlebar/borders)
- Always-on-top positioning
- Windows Registry auto-start integration
- JSON config persistence
- Logging to `~/.voice_click/monitor.log`

**Performance:**
- Minimal CPU/memory footprint
- 1-second update interval (customizable)
- No network/external dependencies
- Pure local file monitoring

**Auto-Start Mechanism:**
- Batch file in Windows Startup registry
- Launches with Python interpreter
- Runs as background process
- Respects Windows login permissions

## Troubleshooting

**Widget not appearing on top of taskbar?**
- Check if "Always on Top" is enabled (it is by default)
- Try moving the window with arrow keys

**Auto-start not working?**
- Run `enable_autostart.bat` again
- Check `~/.voice_click/monitor.log` for errors
- Make sure Python is in system PATH

**Can't update task manually?**
- Edit `~/.voice_click/progress.json` directly
- Monitor will pick up changes within 1 second

## Customization

Edit `monitor.py` to customize:
- `taskbar_height`: Adjust vertical position
- `width`: Change widget width (default 500px)
- Update font sizes, colors, or refresh rate
- Add new task names/stages

## Logs

All activity logged to:
```
~/.voice_click/monitor.log
```

Check this file for debugging issues.

---

**This is an independent tool for internal team use only.**
It will remain running in the background, silently monitoring project progress.
