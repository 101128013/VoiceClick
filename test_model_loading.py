"""
Quick Model Loading Test
Tests that the large-v3 model can load on CUDA
"""

import sys
import time

print("=" * 70)
print("MODEL LOADING TEST")
print("=" * 70)

print("\n[1] Testing model loading...")
print("  Model: large-v3")
print("  Device: cuda")
print("  Compute: float16")
print("\n  This may take a few minutes on first run (downloading model)...")

start_time = time.time()

try:
    from faster_whisper import WhisperModel
    
    print("\n  Loading model...")
    model = WhisperModel(
        "large-v3",
        device="cuda",
        compute_type="float16"
    )
    
    load_time = time.time() - start_time
    print(f"\n  ✓ Model loaded successfully in {load_time:.1f}s")
    
    # Test transcription with dummy audio
    print("\n[2] Testing transcription...")
    import numpy as np
    
    # Create 3 seconds of silence
    sample_rate = 16000
    test_audio = np.zeros(sample_rate * 3, dtype=np.float32)
    
    segments, info = model.transcribe(test_audio, language="en")
    segments_list = list(segments)
    
    print(f"  ✓ Transcription works!")
    print(f"  Detected language: {info.language}")
    print(f"  Segments found: {len(segments_list)}")
    
    print("\n" + "=" * 70)
    print("SUCCESS! Model is ready to use.")
    print("=" * 70)
    
    # Clean up
    del model
    
except Exception as e:
    print(f"\n  ✗ Error: {e}")
    print("\n  Fallback: Try changing to CPU mode in voice_click_minimal.py:")
    print("    WHISPER_DEVICE = 'cpu'")
    print("    WHISPER_COMPUTE_TYPE = 'int8'")
    sys.exit(1)
