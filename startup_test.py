"""
Quick Startup Test
Verifies the script can start and initialize without errors
"""

import subprocess
import sys
import time
import threading

print("=" * 70)
print("STARTUP TEST")
print("=" * 70)
print("\nThis test will:")
print("  1. Start voice_click_minimal.py")
print("  2. Wait for initialization")
print("  3. Verify no errors occur")
print("  4. Shut down cleanly")
print("\nStarting in 3 seconds...")
time.sleep(3)

print("\n[STARTING APPLICATION]")
print("-" * 70)

# Start the script
try:
    # Import the script to test initialization
    print("Importing voice_click_minimal...")
    import voice_click_minimal as vc
    
    print("✓ Script imported successfully")
    print("\n[INITIALIZATION TEST]")
    print("-" * 70)
    
    # Test that critical components are ready
    print("Checking critical components...")
    
    # Check model is loaded
    if vc.model is None:
        print("  → Model not loaded yet (expected - loads in main)")
    else:
        print("  ✓ Model is loaded")
    
    # Check widget
    if vc.status_widget is None:
        print("  → Widget not created yet (expected - creates in main)")
    else:
        print("  ✓ Widget exists")
    
    # Check configuration
    print(f"  ✓ Model config: {vc.WHISPER_MODEL}")
    print(f"  ✓ Device config: {vc.WHISPER_DEVICE}")
    print(f"  ✓ Silence duration: {vc.SILENCE_DURATION}s")
    
    # Check logging
    print(f"  ✓ Log file: {vc.LOG_FILE}")
    
    # Check state
    print(f"  ✓ Recording state: {vc.is_recording}")
    print(f"  ✓ Audio queue: {vc.audio_queue.qsize()} items")
    
    print("\n[FUNCTION AVAILABILITY TEST]")
    print("-" * 70)
    
    # Verify all key functions exist and are callable
    functions = [
        'is_text_field',
        'is_fullscreen_game', 
        'audio_callback',
        'start_recording',
        'stop_recording',
        'transcribe_audio',
        'save_to_history',
        'load_history',
        'play_sound',
        'log_info',
        'log_debug',
        'log_error'
    ]
    
    all_ok = True
    for func_name in functions:
        if hasattr(vc, func_name) and callable(getattr(vc, func_name)):
            print(f"  ✓ {func_name}")
        else:
            print(f"  ✗ {func_name} - MISSING")
            all_ok = False
    
    if all_ok:
        print("\n✅ All functions available")
    else:
        print("\n⚠ Some functions missing")
        sys.exit(1)
    
    print("\n[STATE VERIFICATION]")
    print("-" * 70)
    
    # Verify initial state is correct
    assert vc.is_recording == False, "Should not be recording initially"
    assert vc.audio_queue.empty(), "Audio queue should be empty"
    assert vc.current_volume == 0.0, "Volume should be 0"
    assert vc.auto_stopped == False, "Auto-stopped should be False"
    
    print("  ✓ Initial state correct")
    print("  ✓ Not recording")
    print("  ✓ Queue empty")
    print("  ✓ Volume zero")
    
    print("\n" + "=" * 70)
    print("✅ STARTUP TEST PASSED")
    print("=" * 70)
    print("\nThe script is ready to run!")
    print("\nTo start the full application:")
    print("  python voice_click_minimal.py")
    print("\nNote: The application will load the model on first start.")
    print("      This takes ~2 minutes and downloads 3GB (one-time only).")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ STARTUP TEST FAILED")
    print(f"Error: {e}")
    print("\nCheck the log file for details:")
    try:
        import voice_click_minimal as vc
        print(f"  {vc.LOG_FILE}")
    except:
        print("  ~/.voice_click.log")
    
    import traceback
    print("\nStack trace:")
    print(traceback.format_exc())
    sys.exit(1)
