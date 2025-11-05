"""
VoiceClick Monitor Control Script
Commands to control the progress monitor widget
"""

import sys
from pathlib import Path

def print_help():
    print("""
VoiceClick Monitor Control
==========================

Usage:
    python monitor_control.py <command> [args]

Commands:
    start           Start the monitor widget immediately
    stop            Stop all monitor instances
    autostart-on    Enable auto-start on Windows login
    autostart-off   Disable auto-start
    set-task N      Set current task to N (1-30)
    next            Move to next task
    prev            Move to previous task
    reset           Reset to task 1
    
Examples:
    python monitor_control.py start
    python monitor_control.py set-task 5
    python monitor_control.py autostart-on
    python monitor_control.py next
    """)

def run_command(cmd, *args):
    import subprocess
    
    monitor_path = Path(__file__).parent / "monitor.py"
    
    if cmd == "start":
        subprocess.Popen([sys.executable, str(monitor_path)])
        print("Monitor widget started")
    
    elif cmd == "stop":
        subprocess.run([
            "taskkill", "/IM", "python.exe", "/F"
        ], capture_output=True)
        print("Monitor stopped")
    
    elif cmd == "autostart-on":
        subprocess.run([sys.executable, str(monitor_path), "--autostart"])
        print("Auto-start ENABLED - widget will start on next login")
    
    elif cmd == "autostart-off":
        subprocess.run([sys.executable, str(monitor_path), "--disable-autostart"])
        print("Auto-start DISABLED")
    
    elif cmd == "set-task":
        if args:
            try:
                task_num = int(args[0])
                if 1 <= task_num <= 30:
                    subprocess.run([sys.executable, str(monitor_path), 
                                  "--set-task", str(task_num)])
                    print(f"Task set to {task_num}")
                else:
                    print("Task must be between 1 and 30")
            except ValueError:
                print("Invalid task number")
    
    elif cmd == "next":
        from monitor import TaskbarProgressMonitor
        try:
            widget = TaskbarProgressMonitor()
            widget.increment_task()
            print(f"Advanced to task {widget.current_task}")
        except Exception as e:
            print(f"Error: {e}")
    
    elif cmd == "prev":
        from monitor import TaskbarProgressMonitor
        try:
            widget = TaskbarProgressMonitor()
            if widget.current_task > 1:
                widget.set_task(widget.current_task - 1)
                print(f"Moved to task {widget.current_task}")
        except Exception as e:
            print(f"Error: {e}")
    
    elif cmd == "reset":
        from monitor import TaskbarProgressMonitor
        try:
            widget = TaskbarProgressMonitor()
            widget.set_task(1)
            print("Reset to task 1")
        except Exception as e:
            print(f"Error: {e}")
    
    else:
        print(f"Unknown command: {cmd}")
        print_help()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
    else:
        run_command(sys.argv[1], *sys.argv[2:])
