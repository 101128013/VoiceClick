#!/usr/bin/env python3
"""
Quick check of progress manager status
"""
import sys
sys.path.insert(0, 'src/ui')

from progress_manager import DevelopmentProgressManager

manager = DevelopmentProgressManager()

print("=" * 60)
print("VOICECLICK PROGRESS STATUS")
print("=" * 60)
print(f"Total Tasks: {len(manager.tasks)}")
print(f"Completed Tasks: {manager.completed_tasks}")
print(f"Current Task ID: {manager.current_task_id}")
print(f"Overall Progress: {manager.get_progress_percent():.2f}%")
print("=" * 60)

current_task = manager.get_current_task()
if current_task:
    print(f"\nCurrent Task: #{current_task.task_id}")
    print(f"Name: {current_task.name}")
    print(f"Phase: {current_task.phase.value}")
    print(f"Status: {current_task.status.value}")

print("\n" + "=" * 60)
print("COMPLETED TASKS:")
print("=" * 60)
for i in range(1, manager.completed_tasks + 1):
    task = manager.get_task(i)
    print(f"✅ Task {i}: {task.name}")

print("\n" + "=" * 60)
