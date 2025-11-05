# VoiceClick Monitor - Setup & Usage Guide

## What You Got

A **professional taskbar monitoring widget** that sits on top of your Windows taskbar and shows:
- Green progress bar (just like in your screenshot)
- 2 lines of streaming text showing current task and stage
- Updates every second in real-time
- Completely non-interactive (read-only)
- Auto-starts on Windows login

## Visual Layout

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ████████░░░░░░░░░░░░░░░░░░░░░░░░░░ ┃  ← 4px GREEN progress bar
┃ Task 5/30: Design main window (17%) ┃  ← Line 1: Task number + name
┃ UI Design • 17% complete            ┃  ← Line 2: Current stage + percent
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  Sits above your taskbar (70px height)
```

## 🚀 Quick Start (3 Steps)

### Step 1: Install PyQt6 (one-time only)

```powershell
cd c:\Users\SUPER\Desktop\VoiceClick
pip install PyQt6
```

### Step 2: Enable Auto-Start on Login

Double-click this batch file:
```
enable_autostart.bat
```

Or run:
```powershell
python monitor.py --autostart
```

**Done!** The widget will now start automatically when you turn on your computer.

### Step 3: Start It Now

```powershell
python monitor.py
```

The green progress widget appears above your taskbar and starts monitoring.

---

## 📊 How to Update Progress

### Method 1: Command Line (Easiest)

```powershell
# Jump to task 5
python monitor_control.py set-task 5

# Move to next task
python monitor_control.py next

# Move to previous task
python monitor_control.py prev

# Reset to task 1
python monitor_control.py reset
```

### Method 2: Edit Progress File

Edit this file in any text editor:
```
C:\Users\SUPER\.voice_click\progress.json
```

Change the `current_task` number (1-30):
```json
{
  "current_task": 5,
  "total_tasks": 30,
  "timestamp": "2025-11-05T14:30:00"
}
```

Save it, and the widget updates within 1 second. ✓

### Method 3: Keyboard Shortcuts

When the widget window is active:
- **↑ Arrow Up** = Previous task
- **↓ Arrow Down** = Next task
- **ESC** = Hide widget
- **Double-click** = Toggle visibility

---

## 📝 All 30 Tasks

The monitor tracks all 30 tasks through 4 phases:

### Phase 1: Setup & Architecture (Tasks 1-4)
1. Set up project repository
2. Define requirements
3. Refactor into modules  
4. Create config system

### Phase 2: UI Development (Tasks 5-12)
5. Design main window
6. Implement main window
7. Build Status tab
8. Build Settings tab
9. Build History tab
10. System tray integration
11. Connect UI to engine
12. Create icons

### Phase 3: Testing & Packaging (Tasks 13-20)
13. Write unit tests
14. Create PyInstaller spec
15. Test PyInstaller build
16. Setup Windows 11 VM
17. Test on Windows 11 VM
18. Create NSIS installer
19. Build installer
20. Test installer on VM

### Phase 4: Documentation & Release (Tasks 21-30)
21. Write documentation
22. Setup CI/CD pipeline
23. Beta testing
24. Fix critical bugs
25. Create website
26. Prepare release notes
27. Create version tag
28. Publish on GitHub
29. Setup support channels
30. Plan feature roadmap

---

## 🎛️ Control Commands

### Start/Stop
```powershell
# Start the monitor
python monitor_control.py start

# Stop all monitor instances
python monitor_control.py stop
```

### Auto-Start Management
```powershell
# Enable auto-start on login
python monitor_control.py autostart-on

# Disable auto-start
python monitor_control.py autostart-off
```

### Task Navigation
```powershell
# Set to specific task (1-30)
python monitor_control.py set-task 8

# Go to next task
python monitor_control.py next

# Go to previous task
python monitor_control.py prev

# Reset to task 1
python monitor_control.py reset
```

---

## 🔍 Monitoring & Logs

The monitor keeps detailed logs of everything it does:

```
C:\Users\SUPER\.voice_click\monitor.log
```

View the log to debug any issues:
```powershell
type $env:USERPROFILE\.voice_click\monitor.log
```

---

## ❓ Troubleshooting

### Widget not visible?
- Make sure it's not hidden. Try keyboard shortcut: **ESC** to toggle
- Check it's not behind other windows (it should be on top)
- Restart: `python monitor_control.py stop` then `python monitor.py`

### PyQt6 not found?
```powershell
pip install PyQt6
```

### Progress not updating?
1. Check the progress file exists: `C:\Users\SUPER\.voice_click\progress.json`
2. Edit it manually with a new task number
3. Check logs: `type $env:USERPROFILE\.voice_click\monitor.log`

### Auto-start not working?
- Run `enable_autostart.bat` again
- Check that batch file is in `C:\Users\SUPER\Desktop\VoiceClick\`
- Make sure Python is in your system PATH

### Want to disable auto-start?
Double-click:
```
disable_autostart.bat
```

Or run:
```powershell
python monitor_control.py autostart-off
```

---

## 📁 File Structure

```
VoiceClick/
├── monitor.py                    ← Main widget (run this!)
├── monitor_control.py            ← Control script
├── test_monitor.py              ← Test script
├── enable_autostart.bat          ← Enable auto-start
├── disable_autostart.bat         ← Disable auto-start
└── MONITOR_SETUP_GUIDE.md       ← This file

~/.voice_click/
├── progress.json                ← Current task (edit this to update)
└── monitor.log                  ← Debug log
```

---

## 🎯 Usage Scenarios

### Scenario 1: Update Progress Every Day

Each morning, update the task:
```powershell
python monitor_control.py set-task 7
```

The widget shows the new task. Everyone on your team sees it on their screens.

### Scenario 2: Automate Progress Updates

Create a scheduled task in Windows Task Scheduler:
- Run: `python c:\Users\SUPER\Desktop\VoiceClick\monitor_control.py set-task {task_number}`
- Daily at a specific time
- Updates all team members' monitors automatically

### Scenario 3: Quick Status Check

When someone asks "what stage are we at?":
- They look at the widget on their taskbar
- Sees exactly what task and phase
- No need to ask or check messages

---

## 🔐 Security & Privacy

- ✓ Runs locally, no internet required
- ✓ No data sent anywhere
- ✓ Only reads/writes local JSON file
- ✓ Logs stored locally in `~/.voice_click/`
- ✓ Completely private to your computer

---

## ⚙️ Customization

To customize the widget, edit `monitor.py`:

```python
# Change widget size
width = 500          # Change this
height = 70          # Or this

# Change refresh rate
self.update_timer.start(1000)  # milliseconds (1000 = 1 second)

# Change position
taskbar_height = 48  # Adjust vertical position

# Change colors
QColor(76, 175, 80)  # RGB green color
QColor(44, 62, 80)   # RGB dark text
```

---

## 📞 Support

If something doesn't work:

1. **Check the log file**
   ```powershell
   type $env:USERPROFILE\.voice_click\monitor.log
   ```

2. **Restart the widget**
   ```powershell
   python monitor_control.py stop
   python monitor.py
   ```

3. **Reset progress file**
   ```powershell
   del $env:USERPROFILE\.voice_click\progress.json
   ```
   Then start fresh.

---

**Questions?** Check `MONITOR_README.md` for detailed technical info.

**Ready to go!** 🚀

Next: Run `python monitor.py` to start monitoring your project progress.
