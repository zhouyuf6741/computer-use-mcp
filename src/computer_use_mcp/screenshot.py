#!/usr/bin/env python3
"""
Screenshot and OCR functionality for Computer Control MCP
"""

import shutil
import tempfile
import atexit
import os
from pathlib import Path
from typing import Any, List, Tuple

import pyautogui
import pygetwindow as gw
import cv2
from rapidocr_onnxruntime import RapidOCR

from mcp.server.fastmcp import Image
from .utils import log, save_image_to_downloads, compress_image

# Keep track of temporary files for cleanup
_temp_files_to_cleanup = []

def _cleanup_temp_files():
    """Clean up temporary files on exit."""
    for filepath in _temp_files_to_cleanup:
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
                log(f"Cleaned up temp file: {filepath}")
        except Exception as e:
            log(f"Could not clean up temp file {filepath}: {e}")

# Register cleanup function
atexit.register(_cleanup_temp_files)


class ScreenshotManager:
    """Manages screenshot capture and OCR processing."""
    
    def __init__(self):
        self.ocr_engine = RapidOCR()
    
    def capture_screenshot(self, title_pattern: str = None) -> Tuple[Any, Any]:
        """
        Capture a screenshot of the specified window or entire screen.
        
        Args:
            title_pattern: Pattern to match window title, if None, capture entire screen
            
        Returns:
            Tuple of (screenshot_pil_image, window_object_or_None)
        """
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

        # Take the screenshot
        if not window:
            log("Taking screenshot of entire screen")
            screenshot = pyautogui.screenshot()
        else:
            current_active_window = gw.getActiveWindow()
            log(f"Taking screenshot of window: {window.title}")
            # Activate the window and wait for it to be fully in focus
            window.activate()
            pyautogui.sleep(0.5)  # Wait for 0.5 seconds to ensure window is active
            screenshot = pyautogui.screenshot(
                region=(window.left, window.top, window.width, window.height)
            )
            # Restore the previously active window
            if current_active_window:
                try:
                    current_active_window.activate()
                    pyautogui.sleep(0.2)  # Wait a bit to ensure previous window is restored
                except Exception as e:
                    log(f"Error restoring previous window: {str(e)}")

        return screenshot, window
    
    def process_screenshot(
        self,
        title_pattern: str = None,
        with_ocr_text_and_coords: bool = False,
        scale_percent_for_ocr: int = 100,
        save_to_downloads: bool = False,
    ) -> Any:
        """
        Process screenshot with optional OCR.
        
        Args:
            title_pattern: Pattern to match window title
            with_ocr_text_and_coords: If True, get OCR text with coordinates
            scale_percent_for_ocr: Percentage to scale image before OCR processing
            save_to_downloads: If True, save screenshot to downloads directory
            
        Returns:
            MCP Image object or list with image and OCR results
        """
        try:
            # Capture screenshot
            screenshot, window = self.capture_screenshot(title_pattern)
            
            # Create temp directory
            temp_dir = Path(tempfile.mkdtemp())
            
            try:
                # Save screenshot and get filepath
                filepath, _ = save_image_to_downloads(
                    screenshot, prefix="screenshot", directory=temp_dir
                )

                # Compress the image to reduce size
                compressed_path = compress_image(filepath)
                
                # Copy compressed image to downloads before creating Image object
                if save_to_downloads:
                    downloads_dir = self.get_downloads_dir()
                    final_path = downloads_dir / Path(compressed_path).name
                    shutil.copy(compressed_path, final_path)
                    image = Image(str(final_path))
                    log(f"Saved compressed screenshot to downloads: {final_path}")
                else:
                    # Copy to a more permanent temp location to avoid cleanup issues
                    import tempfile
                    persistent_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                    persistent_temp.close()
                    shutil.copy(compressed_path, persistent_temp.name)
                    image = Image(persistent_temp.name)
                    # Track for cleanup later
                    _temp_files_to_cleanup.append(persistent_temp.name)

                if not with_ocr_text_and_coords:
                    return image  # MCP Image object

                # Process OCR
                ocr_results = self._process_ocr(
                    image.path, window, scale_percent_for_ocr
                )

                return [image, *ocr_results]
                
            finally:
                # Clean up temp directory
                try:
                    shutil.rmtree(temp_dir)
                    log(f"Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    log(f"Could not clean up temp directory {temp_dir}: {e}")

        except Exception as e:
            log(f"Error in screenshot processing: {str(e)}")
            import traceback
            stack_trace = traceback.format_exc()
            log(f"Stack trace:\n{stack_trace}")
            return f"Error in screenshot processing: {str(e)}\nStack trace:\n{stack_trace}"
    
    def _process_ocr(
        self, image_path: str, window: Any, scale_percent: int
    ) -> List[Tuple]:
        """
        Process OCR on the given image.
        
        Args:
            image_path: Path to the image file
            window: Window object (for coordinate adjustment)
            scale_percent: Percentage to scale image before processing
            
        Returns:
            List of OCR results with coordinates
        """
        img = cv2.imread(image_path)

        # Scale down resolution before processing
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        
        # Run OCR
        result, elapse_list = self.ocr_engine(resized_img)
        boxes, txts, scores = list(zip(*result))
        
        # Adjust coordinates if window was specified
        if window:
            boxes = [
                [[x + window.left, y + window.top] for x, y in box]
                for box in boxes
            ]
        
        return list(zip(boxes, txts, scores))
    
    def get_downloads_dir(self):
        """Get downloads directory - imported from utils."""
        from .utils import get_downloads_dir
        return get_downloads_dir()


# Global instance
screenshot_manager = ScreenshotManager() 