"""
Tests for window management functions.
"""

import sys
sys.path.append('src')
from computer_use_mcp.core import list_windows, activate_window, get_screen_size
import pygetwindow as gw

def test_list_windows():
    """Test listing windows functionality."""
    try:
        result = list_windows()
        print(f"List windows result type: {type(result)}")
        print(f"Found {len(result)} windows")
        
        # Check that we get a list
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check that each window has at least a title
        for window in result:
            assert "title" in window
            assert window["title"] is not None
            print(f"Window: {window['title']} (active: {window.get('is_active', False)})")
        
        print("✅ list_windows test passed")
    except Exception as e:
        print(f"❌ list_windows test failed: {e}")
        raise

def test_activate_window():
    """Test window activation functionality."""
    try:
        # Get current active window title (returns string in newer API)
        current_active_title = gw.getActiveWindow()
        if current_active_title:
            print(f"Current active window: {current_active_title}")
            
            # Try to activate the same window (should work)
            result = activate_window(current_active_title)
            print(f"Activate window result: {result}")
            
            # Should return success message
            assert "already active" in result or "matches pattern" in result
        else:
            print("No active window found, testing with generic pattern")
            result = activate_window("test")
            print(f"Activate window result: {result}")
            assert "limited" in result or "Error" in result
        
        print("✅ activate_window test passed")
    except Exception as e:
        print(f"❌ activate_window test failed: {e}")
        raise

def test_window_api_limitations():
    """Test what window API functions are available."""
    try:
        print("Testing available pygetwindow functions:")
        
        # Test getAllTitles
        titles = gw.getAllTitles()
        print(f"getAllTitles: {len(titles)} titles found")
        assert isinstance(titles, list)
        
        # Test getActiveWindow (returns string in newer API)
        active = gw.getActiveWindow()
        if active:
            print(f"getActiveWindow: {active} (type: {type(active)})")
            print(f"  - This is the active window title")
        else:
            print("getActiveWindow: No active window")
        
        print("✅ window API limitations test passed")
    except Exception as e:
        print(f"❌ window API limitations test failed: {e}")
        raise

if __name__ == "__main__":
    print("Running window function tests...")
    test_window_api_limitations()
    test_list_windows()
    test_activate_window()
    print("\n🎉 All window function tests completed!") 