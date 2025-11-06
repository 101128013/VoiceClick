"""
Utility functions shared across core modules.

This module provides common helper functions to reduce code duplication.
"""

import logging
import time
from typing import Callable, TypeVar, Optional

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_operation(operation: Callable[[], T], 
                   max_retries: int = 3, 
                   delay: float = 0.1,
                   operation_name: str = "operation") -> Optional[T]:
    """
    Retries an operation multiple times with a delay between attempts.
    
    Args:
        operation: The function to execute
        max_retries: Maximum number of retry attempts
        delay: Delay in seconds between retries
        operation_name: Name of the operation for logging
        
    Returns:
        Result of the operation, or None if all retries failed
    """
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"{operation_name} failed after {max_retries} attempts: {e}")
                return None
            else:
                time.sleep(delay)
    return None


def normalize_key(key) -> any:
    """
    Normalizes a keyboard key to a consistent format.
    
    Args:
        key: A key object from pynput
        
    Returns:
        Normalized key representation (char or key object)
    """
    if hasattr(key, 'char') and key.char:
        return key.char
    return key

