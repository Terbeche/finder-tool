"""Utility functions used across the application"""


def format_size(size_bytes):
    """
    Format file size in bytes to human-readable string.
    
    Args:
        size_bytes: Size in bytes (int or float)
        
    Returns:
        str: Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
