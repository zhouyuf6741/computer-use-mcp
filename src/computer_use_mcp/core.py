#!/usr/bin/env python3
"""
Computer Control MCP - Core Implementation
A compact ModelContextProtocol server that provides computer control capabilities
using PyAutoGUI for mouse/keyboard control.
"""

from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP

from .input_controller import input_controller
from .screenshot import screenshot_manager
from .window_manager import window_manager
from .utils import log

# Create FastMCP server instance
mcp = FastMCP("ComputerControlMCP")


# --- MCP Tool Handlers ---

@mcp.tool()
def tool_version() -> str:
    """Get the version of the tool."""
    return "0.2.7"


# --- Input Control Tools ---

@mcp.tool()
def click_screen(x: int, y: int) -> str:
    """Click at the specified screen coordinates."""
    return input_controller.click_screen(x, y)


@mcp.tool()
def right_click(x: int, y: int) -> str:
    """Right-click at the specified screen coordinates."""
    return input_controller.right_click(x, y)


@mcp.tool()
def move_mouse(x: int, y: int) -> str:
    """Move the mouse to the specified screen coordinates."""
    return input_controller.move_mouse(x, y)


@mcp.tool()
async def drag_mouse(
    from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5
) -> str:
    """
    Drag the mouse from one position to another.

    Args:
        from_x: Starting X coordinate
        from_y: Starting Y coordinate
        to_x: Ending X coordinate
        to_y: Ending Y coordinate
        duration: Duration of the drag in seconds (default: 0.5)

    Returns:
        Success or error message
    """
    return await input_controller.drag_mouse(from_x, from_y, to_x, to_y, duration)


@mcp.tool()
def type_text(text: str) -> str:
    """Type the specified text at the current cursor position."""
    return input_controller.type_text(text)


@mcp.tool()
def press_key(key: str) -> str:
    """Press the specified keyboard key."""
    return input_controller.press_key(key)


@mcp.tool()
def get_screen_size() -> Dict[str, Any]:
    """Get the current screen resolution."""
    return input_controller.get_screen_size()


@mcp.tool()
def get_mouse_position() -> Dict[str, Any]:
    """Get the current mouse position."""
    return input_controller.get_mouse_position()


# --- Screenshot and OCR Tools ---

@mcp.tool()
def take_screenshot(
    title_pattern: str = None,
    use_regex: bool = False,
    threshold: int = 60,
    with_ocr_text_and_coords: bool = False,
    scale_percent_for_ocr: int = 100,
    save_to_downloads: bool = False,
) -> Any:
    """
    Get screenshot and OCR text with absolute coordinates from window with the specified title pattern.
    If no title pattern is provided, get screenshot of entire screen and all text on the screen.

    Args:
        title_pattern: Pattern to match window title, if None, take screenshot of entire screen
        use_regex: If True, treat the pattern as a regex, otherwise best match with fuzzy matching
        threshold: Minimum score (0-100) required for a fuzzy match
        with_ocr_text_and_coords: If True, get OCR text with absolute coordinates from the screenshot
        scale_percent_for_ocr: Percentage to scale the image down before processing
        save_to_downloads: If True, save the screenshot to the downloads directory

    Returns:
        Returns a single screenshot as MCP Image object, if with_ocr_text_and_coords is True, 
        returns a MCP Image object followed by list of UI elements as [[4 corners of box], text, confidence]
    """
    return screenshot_manager.process_screenshot(
        title_pattern=title_pattern,
        with_ocr_text_and_coords=with_ocr_text_and_coords,
        scale_percent_for_ocr=scale_percent_for_ocr,
        save_to_downloads=save_to_downloads,
    )


# --- Window Management Tools ---

@mcp.tool()
def list_windows() -> List[Dict[str, Any]]:
    """List all open windows on the system."""
    return window_manager.list_windows()


@mcp.tool()
def activate_window(
    title_pattern: str, use_regex: bool = False, threshold: int = 60
) -> str:
    """
    Activate a window (bring it to the foreground) by matching its title.

    Args:
        title_pattern: Pattern to match window title
        use_regex: If True, treat the pattern as a regex, otherwise use fuzzy matching
        threshold: Minimum score (0-100) required for a fuzzy match

    Returns:
        Success or error message
    """
    return window_manager.activate_window(title_pattern, use_regex, threshold)


@mcp.tool()
def get_active_window() -> str:
    """Get the title of the currently active window."""
    return window_manager.get_active_window()


def main():
    """Main entry point for the MCP server."""
    try:
        # Run the server
        mcp.run()
    except KeyboardInterrupt:
        log("Server shutting down...")
    except Exception as e:
        log(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
