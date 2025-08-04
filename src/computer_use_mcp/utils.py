#!/usr/bin/env python3
"""
Utility functions for Computer Control MCP
"""

import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from io import BytesIO
import re
import uuid
import datetime
from pathlib import Path
import tempfile

from fuzzywuzzy import fuzz, process


def log(message: str) -> None:
    """Log a message to stderr."""
    print(f"STDOUT: {message}", file=sys.stderr)


def get_downloads_dir() -> Path:
    """Get the OS downloads directory."""
    if os.name == "nt":  # Windows
        import winreg

        sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        downloads_guid = "{374DE290-123F-4565-9164-39C4925E467B}"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            downloads_dir = winreg.QueryValueEx(key, downloads_guid)[0]
        return Path(downloads_dir)
    else:  # macOS, Linux, etc.
        return Path.home() / "Downloads"


def save_image_to_downloads(
    image, prefix: str = "screenshot", directory: Path = None
) -> Tuple[str, bytes]:
    """Save an image to the downloads directory and return its absolute path.

    Args:
        image: Either a PIL Image object or MCP Image object
        prefix: Prefix for the filename (default: 'screenshot')
        directory: Optional directory to save the image to

    Returns:
        Tuple of (absolute_path, image_data_bytes)
    """
    # Create a unique filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{prefix}_{timestamp}_{unique_id}.png"

    # Get downloads directory
    downloads_dir = directory or get_downloads_dir()
    filepath = downloads_dir / filename

    # Handle different image types
    if hasattr(image, "save"):  # PIL Image
        image.save(filepath)
        # Also get the bytes for returning
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_bytes = img_byte_arr.getvalue()
    elif hasattr(image, "data"):  # MCP Image
        img_bytes = image.data
        with open(filepath, "wb") as f:
            f.write(img_bytes)
    else:
        raise TypeError("Unsupported image type")

    log(f"Saved image to {filepath}")
    return str(filepath.absolute()), img_bytes


def find_matching_window(
    windows: List[Dict[str, Any]],
    title_pattern: str = None,
    use_regex: bool = False,
    threshold: int = 60,
) -> Optional[Dict[str, Any]]:
    """Helper function to find a matching window based on title pattern.

    Args:
        windows: List of window dictionaries
        title_pattern: Pattern to match window title
        use_regex: If True, treat the pattern as a regex, otherwise use fuzzy matching
        threshold: Minimum score (0-100) required for a fuzzy match

    Returns:
        The best matching window or None if no match found
    """
    if not title_pattern:
        log("No title pattern provided, returning None")
        return None

    # For regex matching
    if use_regex:
        for window in windows:
            if re.search(title_pattern, window["title"], re.IGNORECASE):
                log(f"Regex match found: {window['title']}")
                return window
        return None

    # For fuzzy matching using fuzzywuzzy
    # Extract all window titles
    window_titles = [window["title"] for window in windows]

    # Use process.extractOne to find the best match
    best_match_title, score = process.extractOne(
        title_pattern, window_titles, scorer=fuzz.partial_ratio
    )
    log(f"Best fuzzy match: '{best_match_title}' with score {score}")

    # Only return if the score is above the threshold
    if score >= threshold:
        # Find the window with the matching title
        for window in windows:
            if window["title"] == best_match_title:
                return window

    return None


def compress_image(image_path: str, max_size: Tuple[int, int] = (800, 600)) -> str:
    """Compress an image to reduce file size.
    
    Args:
        image_path: Path to the original image
        max_size: Maximum dimensions (width, height)
        
    Returns:
        Path to the compressed image
    """
    from PIL import Image as PILImage
    
    pil_image = PILImage.open(image_path)
    # Resize to reduce file size while maintaining aspect ratio
    pil_image.thumbnail(max_size, PILImage.Resampling.LANCZOS)
    # Save compressed version
    compressed_path = image_path.replace('.png', '_compressed.png')
    pil_image.save(compressed_path, 'PNG', optimize=True, quality=85)
    
    return compressed_path 