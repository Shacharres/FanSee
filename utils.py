"""
Utility functions for various tasks.
"""

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))
