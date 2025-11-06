"""
Quick test runner - Execute all test suites
"""

import subprocess
import sys

print("=" * 70)
print("VOICE CLICK - TEST SUITE RUNNER")
print("=" * 70)
print()

test_files = [
    ("test_comprehensive.py", "Comprehensive Unit Tests"),
    ("test_integration.py", "Integration Tests"),
]

print("Available Test Suites:\n")

for i, (file, desc) in enumerate(test_files, 1):
    print(f"{i}. {desc}")
    print(f"   File: {file}\n")

print("=" * 70)
print()
print("To run all tests, execute:")
print("  pytest test_comprehensive.py test_integration.py -v")
print()
print("To run a specific test suite:")
print("  pytest test_comprehensive.py -v")
print("  pytest test_integration.py -v")
print()
print("=" * 70)
print("\nInstalling pytest if needed...")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pytest"], check=False)

print("\nRunning comprehensive tests...\n")
result1 = subprocess.run([sys.executable, "-m", "pytest", "test_comprehensive.py", "-v", "--tb=short"], cwd=".")

print("\n" + "=" * 70)
print("Running integration tests...\n")
result2 = subprocess.run([sys.executable, "-m", "pytest", "test_integration.py", "-v", "--tb=short"], cwd=".")

print("\n" + "=" * 70)
print("TEST EXECUTION COMPLETE")
print("=" * 70)

if result1.returncode == 0 and result2.returncode == 0:
    print("\n[OK] All tests passed!")
else:
    print("\n[WARNING] Some tests failed - see output above")
