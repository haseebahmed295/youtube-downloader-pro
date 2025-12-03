# coding: utf-8
"""
Utility functions for the YouTube Downloader application
"""
import re
import unicodedata
import os


def clean_unicode_text(text):
    """
    Remove or replace problematic Unicode characters that don't render properly
    
    Args:
        text: Input text string
        
    Returns:
        Cleaned text string
    """
    if not text:
        return text
    
    # Remove ANSI escape codes
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    # Replace common problematic Unicode characters
    replacements = {
        '\u001b': '',  # ESC
        '\u0000': '',  # NULL
        '\u200b': '',  # Zero-width space
        '\u200c': '',  # Zero-width non-joiner
        '\u200d': '',  # Zero-width joiner
        '\ufeff': '',  # Zero-width no-break space (BOM)
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove any remaining control characters except newline and tab
    text = ''.join(char for char in text 
                   if unicodedata.category(char)[0] != 'C' 
                   or char in '\n\t')
    
    return text.strip()


def sanitize_filename(filename):
    """
    Sanitize filename for Windows by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for Windows
    """
    # Windows invalid characters: < > : " / \ | ? *
    # Also remove control characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove trailing dots and spaces (Windows doesn't allow these)
    sanitized = sanitized.rstrip('. ')
    
    # Limit length to avoid path too long errors
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
        
    return sanitized if sanitized else 'video'


def format_file_size(bytes_size):
    """
    Format file size in human-readable format
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "4.52 MB")
    """
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"


def format_speed(speed_bytes):
    """
    Format download speed in human-readable format
    
    Args:
        speed_bytes: Speed in bytes per second
        
    Returns:
        Formatted string (e.g., "4.52 MB/s")
    """
    if not speed_bytes or speed_bytes <= 0:
        return "Calculating..."
        
    if speed_bytes > 1024 * 1024:
        return f"{speed_bytes / (1024 * 1024):.2f} MB/s"
    elif speed_bytes > 1024:
        return f"{speed_bytes / 1024:.2f} KB/s"
    else:
        return f"{speed_bytes:.0f} B/s"


def format_eta(eta_seconds):
    """
    Format ETA in human-readable format
    
    Args:
        eta_seconds: ETA in seconds
        
    Returns:
        Formatted string (e.g., "05:30" or "01:05:30")
    """
    if not eta_seconds or eta_seconds <= 0:
        return "Calculating..."
        
    if eta_seconds > 3600:
        hours = int(eta_seconds // 3600)
        minutes = int((eta_seconds % 3600) // 60)
        seconds = int(eta_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        minutes = int(eta_seconds // 60)
        seconds = int(eta_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
