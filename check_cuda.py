"""
CUDA and GPU Verification Script
Checks CUDA availability and GPU setup for Whisper
"""

import sys

print("=" * 70)
print("CUDA & GPU VERIFICATION")
print("=" * 70)

# Check PyTorch CUDA
print("\n[1] PyTorch CUDA Check:")
try:
    import torch
    print(f"  PyTorch version: {torch.__version__}")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  CUDA version: {torch.version.cuda}")
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        mem_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"  GPU memory: {mem_total:.1f} GB")
    else:
        print("  ⚠ CUDA not available in PyTorch")
        print("  Note: This might be because PyTorch was installed without CUDA support")
except ImportError:
    print("  ⚠ PyTorch not installed")

# Check faster-whisper CUDA
print("\n[2] Faster-Whisper Device Check:")
try:
    from faster_whisper import WhisperModel
    import ctranslate2
    print(f"  ctranslate2 version: {ctranslate2.__version__}")
    
    # Try to load a tiny model on CUDA
    try:
        print("  Testing CUDA with tiny model...")
        test_model = WhisperModel("tiny", device="cuda", compute_type="float16")
        print("  ✓ CUDA works with faster-whisper!")
        del test_model
    except Exception as e:
        print(f"  ✗ CUDA test failed: {e}")
        print("  Trying CPU...")
        try:
            test_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            print("  ✓ CPU works with faster-whisper")
            del test_model
        except Exception as e2:
            print(f"  ✗ CPU also failed: {e2}")
            
except ImportError as e:
    print(f"  ✗ faster-whisper import error: {e}")

# Check NVIDIA GPU
print("\n[3] NVIDIA GPU Check:")
import subprocess
try:
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        lines = result.stdout.split('\n')
        for line in lines:
            if 'RTX' in line or 'GeForce' in line or 'NVIDIA' in line:
                print(f"  {line.strip()}")
        print("  ✓ NVIDIA GPU detected via nvidia-smi")
    else:
        print("  ✗ nvidia-smi command failed")
except FileNotFoundError:
    print("  ✗ nvidia-smi not found (NVIDIA drivers not installed?)")
except Exception as e:
    print(f"  ⚠ Error running nvidia-smi: {e}")

# Recommendations
print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)

print("\nFor optimal performance with RTX 5060Ti:")
print("  1. Install CUDA Toolkit 11.8 or 12.x from NVIDIA")
print("  2. Install PyTorch with CUDA support:")
print("     pip install torch --index-url https://download.pytorch.org/whl/cu118")
print("  3. Install faster-whisper with CUDA:")
print("     pip install faster-whisper")
print("\nIf CUDA doesn't work:")
print("  - Edit voice_click_minimal.py")
print("  - Change WHISPER_DEVICE = 'cpu'")
print("  - Change WHISPER_COMPUTE_TYPE = 'int8'")
print("  - Model will run on CPU (slower but works)")

print("\n" + "=" * 70)
