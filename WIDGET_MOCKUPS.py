"""
PROGRESS WIDGET VISUAL MOCKUPS
═══════════════════════════════════════════════════════════════════════════════
"""

# MOCKUP 1: Early Phase (0-33% - Blue)
# ─────────────────────────────────────────────────────────────────────────────

EARLY_PHASE = """
┌─────────────────────────────────────────────────────────────────────┐
│ ▌▌▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← 3px Bar
├─────────────────────────────────────────────────────────────────────┤
│ Task 5/30: Design PyQt6 main window layout (17%) █ │ ← Line 1 (Bold)
│ UI Design • 17% complete                           │ ← Line 2 (Gray)
└─────────────────────────────────────────────────────────────────────┘

Colors Used:
  Progress Bar: #4285F4 (Google Blue)
  Background: #FFFFFF (White)
  Top Border: #E8E8E8 (Light Gray)
  Task Text: #333333 (Dark Gray)
  Stage Text: #999999 (Medium Gray)
  Height: 32px minimum
"""


# MOCKUP 2: Middle Phase (33-66% - Amber)
# ─────────────────────────────────────────────────────────────────────────────

MIDDLE_PHASE = """
┌─────────────────────────────────────────────────────────────────────┐
│ ▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← 3px Bar
├─────────────────────────────────────────────────────────────────────┤
│ Task 17/30: Test executable on clean Windows 11 VM (57%)            │ ← Line 1
│ Testing • 57% complete                             │ ← Line 2
└─────────────────────────────────────────────────────────────────────┘

Colors Used:
  Progress Bar: #FBB804 (Amber/Gold)
  All other colors remain the same
"""


# MOCKUP 3: Final Phase (66-100% - Green)
# ─────────────────────────────────────────────────────────────────────────────

FINAL_PHASE = """
┌─────────────────────────────────────────────────────────────────────┐
│ ▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← 3px Bar
├─────────────────────────────────────────────────────────────────────┤
│ Task 25/30: Create product website/landing page (83%)               │ ← Line 1
│ Marketing • 83% complete                           │ ← Line 2
└─────────────────────────────────────────────────────────────────────┘

Colors Used:
  Progress Bar: #34A853 (Google Green)
  All other colors remain the same
"""


# MOCKUP 4: Success State (100% - Green)
# ─────────────────────────────────────────────────────────────────────────────

SUCCESS_STATE = """
┌─────────────────────────────────────────────────────────────────────┐
│ ▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌ │ ← Full
├─────────────────────────────────────────────────────────────────────┤
│ ✓ Development Complete!                                              │ ← Line 1
│ All tasks completed successfully                   │ ← Line 2
└─────────────────────────────────────────────────────────────────────┘

Colors Used:
  Progress Bar: #34A853 (Green)
  Task Text: #34A853 (Green with checkmark)
"""


# MOCKUP 5: Error State
# ─────────────────────────────────────────────────────────────────────────────

ERROR_STATE = """
┌─────────────────────────────────────────────────────────────────────┐
│ ▌▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← 3px Bar
├─────────────────────────────────────────────────────────────────────┤
│ ❌ Error: Failed to load Whisper model                               │ ← Line 1
│ Please check the logs                              │ ← Line 2
└─────────────────────────────────────────────────────────────────────┘

Colors Used:
  Progress Bar: #E53935 (Red)
  Task Text: #E53935 (Red with X mark)
"""


# MOCKUP 6: Horizontal Layout (Alternative)
# ─────────────────────────────────────────────────────────────────────────────

HORIZONTAL_LAYOUT = """
┌─────────────────────────────────────────────────────────────────────┐
│ ▌▌▌▌▌▌▌▌▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← 3px Bar
├─────────────────────────────────────────────────────────────────────┤
│ Task 12/30 • Create application icons and resources (Assets) • 40%   │
└─────────────────────────────────────────────────────────────────────┘

Single line of info: Task# • Name • Phase • Percentage
Height: 28px minimum
"""


# MOCKUP 7: Responsive Sizing
# ─────────────────────────────────────────────────────────────────────────────

SMALL_WINDOW = """
Minimum width (400px):
┌────────────────────────────┐
│ ▌▌▌░░░░░░░░░░░░░░░░░░░░░░ │
├────────────────────────────┤
│ Task 5/30: Design UI (17%)  │
│ UI Design • 17%             │
└────────────────────────────┘

Medium width (600px):
┌──────────────────────────────────────────┐
│ ▌▌▌▌▌▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
├──────────────────────────────────────────┤
│ Task 8/30: Build Settings tab UI (27%)    │
│ UI Development • 27% complete             │
└──────────────────────────────────────────┘

Large width (1000px):
┌────────────────────────────────────────────────────────────────────────┐
│ ▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
├────────────────────────────────────────────────────────────────────────┤
│ Task 15/30: Test PyInstaller build locally (50%)                       │
│ Packaging • 50% complete                                               │
└────────────────────────────────────────────────────────────────────────┘
"""


# MOCKUP 8: Integration in Main Window
# ─────────────────────────────────────────────────────────────────────────────

MAIN_WINDOW_INTEGRATION = """
┌──────────────────────────────────────────────────────┐
│ VoiceClick Pro                              _ □ ×    │ ← Title Bar
├──────────────────────────────────────────────────────┤
│                                                      │
│  [Status]  [Settings]  [History]                    │ ← Tab Controls
│                                                      │
│  Main Content Area                                   │
│  (Fills available space)                            │
│                                                      │
│  ......                                              │
│  ......                                              │
│                                                      │
├──────────────────────────────────────────────────────┤ ← At Bottom
│ ▌▌▌▌▌▌▌▌▌▌▌▌▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │ ← 3px Bar
│ Task 11/30: Connect UI to core engine (37%)         │
│ Integration • 37% complete                          │
└──────────────────────────────────────────────────────┘

The progress widget acts as a status bar at the bottom of the window.
Users can see development progress without leaving the application.
"""


# MOCKUP 9: Taskbar-Height Compact
# ─────────────────────────────────────────────────────────────────────────────

TASKBAR_HEIGHT = """
Perfect for taskbar (28px):

┌────────────────────────────────────────┐
│ ▌▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← 3px bar
│ Task 2/30 • Requirements (7%) • Setup  │ ← Single line
└────────────────────────────────────────┘ ← Total height: 28px

Fits perfectly next to system tray or as persistent status indicator.
Can be docked to any window edge.
"""


# MOCKUP 10: Color Transition Timeline
# ─────────────────────────────────────────────────────────────────────────────

COLOR_PROGRESSION = """
Project Progress Timeline with Color Changes:

Task 1 ──> Task 10 ────> Task 15 ─────> Task 20 ──> Task 30
 |           |              |             |           |
 ▌▌       ▌▌▌▌▌▌▌        ▌▌▌▌▌        ▌▌▌▌▌▌▌▌▌    ▌▌▌▌▌▌▌▌▌▌▌▌▌
 │        │              │             │           │
 ↓        ↓              ↓             ↓           ↓
BLUE   BLUE→AMBER    AMBER         AMBER→GREEN   GREEN
(3%)   (33%)         (50%)         (67%)         (100%)


Phase Distribution:

Setup          Architecture    UI Dev       Integration    Testing
│ ▌▌▌         │ ▌▌            │ ▌▌▌▌▌       │ ▌             │ ▌▌▌▌▌▌
1-2            3-4             6-10         11              13,16-17,20

Packaging      Documentation  Beta         Release         Post-Release
│ ▌▌▌          │ ▌              │ ▌▌         │ ▌▌▌           │ ▌▌
14-15          21              23           26-28           29-30
"""


if __name__ == "__main__":
    print("PROGRESS WIDGET VISUAL MOCKUPS")
    print("=" * 77)
    print("\n1. Early Phase (0-33%, Blue):\n")
    print(EARLY_PHASE)
    
    print("\n2. Middle Phase (33-66%, Amber):\n")
    print(MIDDLE_PHASE)
    
    print("\n3. Final Phase (66-100%, Green):\n")
    print(FINAL_PHASE)
    
    print("\n4. Success State (100%, Green):\n")
    print(SUCCESS_STATE)
    
    print("\n5. Error State:\n")
    print(ERROR_STATE)
    
    print("\n6. Horizontal Layout Alternative:\n")
    print(HORIZONTAL_LAYOUT)
    
    print("\n7. Responsive Sizing:\n")
    print(SMALL_WINDOW)
    
    print("\n8. Main Window Integration:\n")
    print(MAIN_WINDOW_INTEGRATION)
    
    print("\n9. Taskbar-Height Compact:\n")
    print(TASKBAR_HEIGHT)
    
    print("\n10. Color Transition Timeline:\n")
    print(COLOR_PROGRESSION)
