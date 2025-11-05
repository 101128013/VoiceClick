"""
VoiceClick Test Runner
Run all unit tests with coverage
"""
import pytest
import sys

if __name__ == '__main__':
    # Run tests with verbose output
    args = [
        'tests/',
        '-v',
        '--tb=short',
        '--color=yes'
    ]
    
    exit_code = pytest.main(args)
    sys.exit(exit_code)
