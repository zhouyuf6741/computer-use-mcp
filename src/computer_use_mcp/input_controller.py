#!/usr/bin/env python3
"""
Input control functionality for Computer Control MCP
"""

import asyncio
import pyautogui
from .utils import log


class InputController:
    """Manages mouse and keyboard input operations."""
    
    def __init__(self):
        # Enable failsafe for safety
        pyautogui.FAILSAFE = True
    
    def click_screen(self, x: int, y: int) -> str:
        """Click at the specified screen coordinates."""
        try:
            pyautogui.click(x=x, y=y)
            return f"Successfully clicked at coordinates ({x}, {y})"
        except Exception as e:
            return f"Error clicking at coordinates ({x}, {y}): {str(e)}"
    
    def right_click(self, x: int, y: int) -> str:
        """Right-click at the specified screen coordinates."""
        try:
            pyautogui.rightClick(x=x, y=y)
            return f"Successfully right-clicked at coordinates ({x}, {y})"
        except Exception as e:
            return f"Error right-clicking at coordinates ({x}, {y}): {str(e)}"
    
    def move_mouse(self, x: int, y: int) -> str:
        """Move the mouse to the specified screen coordinates."""
        try:
            pyautogui.moveTo(x=x, y=y)
            return f"Successfully moved mouse to coordinates ({x}, {y})"
        except Exception as e:
            return f"Error moving mouse to coordinates ({x}, {y}): {str(e)}"
    
    async def drag_mouse(
        self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5
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
        try:
            # First move to the starting position
            pyautogui.moveTo(x=from_x, y=from_y)
            # Then drag to the destination
            log("Starting drag")
            await asyncio.to_thread(pyautogui.dragTo, x=to_x, y=to_y, duration=duration)
            log("Drag completed")
            return f"Successfully dragged from ({from_x}, {from_y}) to ({to_x}, {to_y})"
        except Exception as e:
            return f"Error dragging from ({from_x}, {from_y}) to ({to_x}, {to_y}): {str(e)}"
    
    def type_text(self, text: str) -> str:
        """Type the specified text at the current cursor position."""
        try:
            pyautogui.typewrite(text)
            return f"Successfully typed text: {text}"
        except Exception as e:
            return f"Error typing text: {str(e)}"
    
    def press_key(self, key: str) -> str:
        """Press the specified keyboard key."""
        try:
            pyautogui.press(key)
            return f"Successfully pressed key: {key}"
        except Exception as e:
            return f"Error pressing key {key}: {str(e)}"
    
    def get_screen_size(self) -> dict:
        """Get the current screen resolution."""
        try:
            width, height = pyautogui.size()
            return {
                "width": width,
                "height": height,
                "message": f"Screen size: {width}x{height}",
            }
        except Exception as e:
            return {"error": str(e), "message": f"Error getting screen size: {str(e)}"}
    
    def get_mouse_position(self) -> dict:
        """Get the current mouse position."""
        try:
            x, y = pyautogui.position()
            return {
                "x": x,
                "y": y,
                "message": f"Mouse position: ({x}, {y})",
            }
        except Exception as e:
            return {"error": str(e), "message": f"Error getting mouse position: {str(e)}"}


# Global instance
input_controller = InputController() 