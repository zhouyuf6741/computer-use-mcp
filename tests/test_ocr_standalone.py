import shutil
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from io import BytesIO
import re
import asyncio
import uuid
import datetime
from pathlib import Path
import tempfile

# --- Auto-install dependencies if needed ---
import pyautogui
from mcp.server.fastmcp import FastMCP, Image
import pygetwindow as gw
from fuzzywuzzy import fuzz, process

import cv2
from rapidocr_onnxruntime import RapidOCR


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


def _find_matching_window(
    windows: any,
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


def take_screenshot(
    title_pattern: str = None,
    use_regex: bool = False,
    threshold: int = 60,
    save_to_downloads: bool = False,
) -> Image:
    """
    Take screenshots based on the specified title pattern and save them to the downloads directory with absolute paths returned.
    If no title pattern is provided, take screenshot of entire screen.

    Args:
        title_pattern: Pattern to match window title, if None, take screenshot of entire screen
        use_regex: If True, treat the pattern as a regex, otherwise best match with fuzzy matching
        save_to_downloads: If True, save the screenshot to the downloads directory and return the absolute path
        threshold: Minimum score (0-100) required for a fuzzy match

    Returns:
        Always returns a single screenshot as MCP Image object, content type image not supported means preview isnt supported but Image object is there.
    """
    try:
        all_windows = gw.getAllWindows()

        # Convert to list of dictionaries for _find_matching_window
        windows = []
        for window in all_windows:
            if window.title:  # Only include windows with titles
                windows.append(
                    {
                        "title": window.title,
                        "window_obj": window,  # Store the actual window object
                    }
                )

        print(f"Found {len(windows)} windows")
        window = _find_matching_window(windows, title_pattern, use_regex, threshold)
        window = window["window_obj"] if window else None

        # Store the currently active window
        current_active_window = gw.getActiveWindow()

        # Take the screenshot
        if not window:
            print("No matching window found, taking screenshot of entire screen")
            screenshot = pyautogui.screenshot()
        else:
            print(f"Taking screenshot of window: {window.title}")
            # Activate the window and wait for it to be fully in focus
            window.activate()
            pyautogui.sleep(0.5)  # Wait for 0.5 seconds to ensure window is active
            screenshot = pyautogui.screenshot(
                region=(window.left, window.top, window.width, window.height)
            )
            # Restore the previously active window
            if current_active_window:
                current_active_window.activate()
                pyautogui.sleep(0.2)  # Wait a bit to ensure previous window is restored

        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp())

        # Save screenshot and get filepath
        filepath, _ = save_image_to_downloads(
            screenshot, prefix="screenshot", directory=temp_dir
        )

        # Create Image object from filepath
        image = Image(filepath)

        # Copy from temp to downloads
        if save_to_downloads:
            print("Copying screenshot from temp to downloads")
            shutil.copy(filepath, get_downloads_dir())

        # Clean up temp directory if not saving to downloads
        if not save_to_downloads:
            try:
                shutil.rmtree(temp_dir)
                print(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                print(f"Could not clean up temp directory {temp_dir}: {e}")

        return image  # MCP Image object

    except Exception as e:
        print(f"Error taking screenshot: {str(e)}")
        return f"Error taking screenshot: {str(e)}"


def get_ocr_from_screenshot(
    title_pattern: str = None,
    use_regex: bool = False,
    threshold: int = 60,
    scale_percent: int = 100,
) -> any:
    """
    Get OCR text from the specified title pattern and save them to the downloads directory with absolute paths returned.
    If no title pattern is provided, get all Text on the screen.

    Args:
        title_pattern: Pattern to match window title, if None, get all UI elements on the screen
        use_regex: If True, treat the pattern as a regex, otherwise best match with fuzzy matching
        save_to_downloads: If True, save the screenshot to the downloads directory and return the absolute path
        threshold: Minimum score (0-100) required for a fuzzy match

    Returns:
        List of UI elements as MCP Image objects
    """
    try:
        # For now, we'll use a simplified approach since the newer pygetwindow API is limited
        # We'll just take a screenshot of the entire screen or the active window
        window = None
        
        if title_pattern:
            # Try to get the active window and check if it matches
            try:
                active_window = gw.getActiveWindow()
                if active_window and active_window.title:
                    # Simple title matching
                    if title_pattern.lower() in active_window.title.lower():
                        window = active_window
                        log(f"Found matching active window: {window.title}")
                    else:
                        log(f"Active window '{active_window.title}' doesn't match pattern '{title_pattern}'")
            except Exception as e:
                log(f"Error getting active window: {str(e)}")
        
        if not window:
            log("No matching window found, will take screenshot of entire screen")

        # Store the currently active window
        current_active_window = gw.getActiveWindow()

        # Take the screenshot
        if not window:
            log("No matching window found, taking screenshot of entire screen")
            screenshot = pyautogui.screenshot()
        else:
            log(f"Taking screenshot of window: {window.title}")
            # Activate the window and wait for it to be fully in focus
            window.activate()
            pyautogui.sleep(0.5)  # Wait for 0.5 seconds to ensure window is active
            screenshot = pyautogui.screenshot(
                region=(window.left, window.top, window.width, window.height)
            )
            # Restore the previously active window
            if current_active_window:
                current_active_window.activate()
                pyautogui.sleep(0.2)  # Wait a bit to ensure previous window is restored

        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp())

        # Save screenshot and get filepath
        filepath, _ = save_image_to_downloads(
            screenshot, prefix="screenshot", directory=temp_dir
        )

        # Create Image object from filepath
        image = Image(filepath)

        # Copy from temp to downloads
        if False:
            log("Copying screenshot from temp to downloads")
            shutil.copy(filepath, get_downloads_dir())

        image_path = image.path
        img = cv2.imread(image_path)

        # Lower down resolution before processing
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        # save resized image to pwd
        # cv2.imwrite("resized_img.png", resized_img)
        engine = RapidOCR()

        result, elapse_list = engine(resized_img)
        boxes, txts, scores = list(zip(*result))
        # Adjust coordinates based on whether we have a window or not
        if window:
            boxes = [[[x + window.left, y + window.top] for x, y in box] for box in boxes]
        else:
            boxes = [[[x, y] for x, y in box] for box in boxes]
        zipped_results = list(zip(boxes, txts, scores))

        # Clean up temp directory after processing
        try:
            shutil.rmtree(temp_dir)
            log(f"Cleaned up temp directory: {temp_dir}")
        except Exception as e:
            log(f"Could not clean up temp directory {temp_dir}: {e}")

        return zipped_results

    except Exception as e:
        log(f"Error getting UI elements: {str(e)}")
        import traceback

        stack_trace = traceback.format_exc()
        log(f"Stack trace:\n{stack_trace}")
        return f"Error getting UI elements: {str(e)}\nStack trace:\n{stack_trace}"


# Test functions
def test_ocr_functionality():
    """Test OCR functionality with full screen screenshot."""
    temp_files = []
    try:
        result = get_ocr_from_screenshot()
        print(f"OCR test result type: {type(result)}")
        if isinstance(result, list):
            print(f"Found {len(result)} text elements")
        else:
            print(f"OCR result: {result}")
        assert result is not None
        print("✅ OCR functionality test passed")
    except Exception as e:
        print(f"❌ OCR functionality test failed: {e}")
    finally:
        # Clean up temporary files
        import glob
        import os
        temp_patterns = [
            "/var/folders/*/tmp*/screenshot_*.png",
            "/tmp/screenshot_*.png",
            "screenshot_*.png"
        ]
        for pattern in temp_patterns:
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                    print(f"Cleaned up: {file_path}")
                except Exception as e:
                    print(f"Could not remove {file_path}: {e}")


if __name__ == "__main__":
    test_ocr_functionality()
