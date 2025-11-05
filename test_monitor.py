#!/usr/bin/env python3
"""Test that monitor.py loads correctly"""
try:
    import monitor
    print("✓ Monitor module loads successfully")
    print("✓ All imports working")
    print("✓ Ready to run!")
except Exception as e:
    print(f"✗ Error loading monitor: {e}")
    import traceback
    traceback.print_exc()
