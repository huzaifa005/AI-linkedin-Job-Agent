"""
Shared utility functions.
"""

import re


def sanitize_folder_name(name: str) -> str:
    """
    Sanitizes a string to be a safe folder name on Windows/Linux.
    Extracted from the original main.py.
    
    Args:
        name: Raw string (e.g., "Monzo_Staff Product Designer").
        
    Returns:
        Safe folder name with only alphanumeric chars, underscores, hyphens.
    """
    # Keep only alphanumeric characters, spaces, and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9\s_-]', '', name)
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized.strip('_')
