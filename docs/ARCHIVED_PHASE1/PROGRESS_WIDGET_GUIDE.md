# Progress Widget Integration Guide
Quick reference for using the Development Progress Widget in VoiceClick

## Quick Start

### Option 1: Vertical Layout (Default)
Best for: Small windows, status bar at top or bottom
```python
from src.ui.progress_widget import DevelopmentProgressWidget

progress = DevelopmentProgressWidget()
progress.update_progress(
    task_number=5,
    task_name="Design PyQt6 main window layout",
    stage="UI Design"
)
layout.addWidget(progress)
```

### Option 2: Horizontal Layout
Best for: Window bottom, more details visible
```python
from src.ui.progress_widget import HorizontalProgressWidget

progress = HorizontalProgressWidget()
progress.update_progress(
    task_number=10,
    task_name="Implement system tray integration",
    stage="UI Development"
)
```

### Option 3: With Progress Manager (Recommended)
Best for: Full project tracking with signals
```python
from src.ui.progress_widget import DevelopmentProgressWidget
from src.ui.progress_manager import DevelopmentProgressManager

manager = DevelopmentProgressManager()
progress_widget = DevelopmentProgressWidget()

# Connect signals
manager.signals.progress_updated.connect(progress_widget.update_progress)
manager.signals.project_completed.connect(progress_widget.set_success_state)

# Use it
manager.start_task(5)
# ... do work ...
manager.complete_task(5)
```

## Color Coding

- **0-33%** → Blue - Early phase (setup, architecture)
- **33-66%** → Amber - Middle phase (development, testing)
- **66-100%** → Green - Final phase (release, polish)
- **Error** → Red - Something went wrong
- **Complete** → Green - All tasks done!

## Progress Manager Features

1. **Task Tracking**: 30 predefined tasks with phases
2. **Progress Calculation**: Overall and per-phase tracking
3. **Qt Signals**: Thread-safe progress updates
4. **Progress Export**: Text reports and JSON summaries

## Usage Example

```python
manager = get_progress_manager()

# Get progress
progress = manager.get_progress_percent()

# Get phase progress
phase_stats = manager.get_phase_progress(DevelopmentPhase.UI_DEVELOPMENT)

# Generate report
report = manager.export_progress_report()

# Get summary
summary = manager.get_summary()
```

## Best Practices

1. Use Progress Manager for complex projects
2. Emit signals from separate threads for thread safety
3. Update at logical boundaries (task completion, file save, test pass)
4. Use meaningful messages with task numbers and phases
5. Handle errors gracefully with set_error_state()
6. Test in isolation using progress_demo.py

## Troubleshooting

- **Progress not updating?** → Call update_progress() or emit signal
- **Text truncated?** → Increase widget width or use shorter names
- **Color not changing?** → Call set_color() before update()
- **Signals not working?** → Connect before emitting
- **Threading issues?** → Use signals from worker threads, not direct UI updates
