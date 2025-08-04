#!/usr/bin/env python3
"""
Window management functionality for Computer Control MCP
"""

from typing import Dict, Any, List

import pygetwindow as gw
from .utils import log


class WindowManager:
    """Manages window operations and information."""
    
    def list_windows(self) -> List[Dict[str, Any]]:
        """List all open windows on the system."""
        try:
            # Get all window titles
            all_titles = gw.getAllTitles()
            result = []
            
            # Get the active window title (returns string in newer API)
            active_window_title = gw.getActiveWindow()
            
            for title in all_titles:
                if title:  # Only include windows with titles
                    window_info = {
                        "title": title,
                        "is_active": title == active_window_title,
                    }
                    
                    # For now, we can't get detailed window properties due to API limitations
                    # The newer pygetwindow API only provides titles, not window objects
                    
                    result.append(window_info)
            
            log(f"Listed {len(result)} windows, active: {active_window_title}")
            return result
        except Exception as e:
            log(f"Error listing windows: {str(e)}")
            return [{"error": str(e)}]
    
    def activate_window(
        self, title_pattern: str, use_regex: bool = False, threshold: int = 60
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
        try:
            # Get the current active window title (returns string in newer API)
            current_active_title = gw.getActiveWindow()
            
            if current_active_title:
                # Simple title matching
                if title_pattern.lower() in current_active_title.lower():
                    # Window is already active or matches pattern
                    return f"Window '{current_active_title}' is already active or matches pattern"
                else:
                    log(f"Active window '{current_active_title}' doesn't match pattern '{title_pattern}'")
            
            # Get all window titles to find matching windows
            all_titles = gw.getAllTitles()
            matching_windows = []
            
            for title in all_titles:
                if title and title_pattern.lower() in title.lower():
                    matching_windows.append(title)
            
            if matching_windows:
                log(f"Found {len(matching_windows)} matching windows: {matching_windows}")
                return f"Found {len(matching_windows)} matching windows, but window activation is limited with current pygetwindow API"
            else:
                return f"No windows found matching pattern '{title_pattern}'"
                
        except Exception as e:
            log(f"Error activating window: {str(e)}")
            return f"Error activating window: {str(e)}"
    
    def get_active_window(self) -> str:
        """Get the title of the currently active window."""
        try:
            return gw.getActiveWindow() or "No active window"
        except Exception as e:
            log(f"Error getting active window: {str(e)}")
            return f"Error: {str(e)}"
    
    def get_all_window_titles(self) -> List[str]:
        """Get all window titles."""
        try:
            return [title for title in gw.getAllTitles() if title]
        except Exception as e:
            log(f"Error getting window titles: {str(e)}")
            return []


# Global instance
window_manager = WindowManager() 