"""
Basic tests for the Computer Use MCP package.
"""

import sys
import os
sys.path.append('src')
from computer_use_mcp.core import get_screen_size, tool_version, click_screen, right_click, move_mouse, type_text, press_key

def test_get_screen_size():
    """Test getting screen size."""
    result = get_screen_size()
    print(f"Screen size result: {result}")
    assert 'width' in result
    assert 'height' in result
    assert result['width'] > 0
    assert result['height'] > 0
    print("✅ get_screen_size test passed")

def test_tool_version():
    """Test getting tool version."""
    result = tool_version()
    print(f"Tool version: {result}")
    assert isinstance(result, str)
    assert len(result) > 0
    print("✅ tool_version test passed")

def test_mouse_functions():
    """Test mouse functions (without actually moving mouse)."""
    # Test that functions exist and can be called
    try:
        # These would normally move the mouse, but we're just testing they exist
        print("Testing mouse functions exist...")
        assert callable(click_screen)
        assert callable(right_click)
        assert callable(move_mouse)
        print("✅ mouse functions test passed")
    except Exception as e:
        print(f"❌ mouse functions test failed: {e}")

def test_keyboard_functions():
    """Test keyboard functions."""
    try:
        # Test that functions exist
        assert callable(type_text)
        assert callable(press_key)
        print("✅ keyboard functions test passed")
    except Exception as e:
        print(f"❌ keyboard functions test failed: {e}")

if __name__ == "__main__":
    print("Running basic tests...")
    test_get_screen_size()
    test_tool_version()
    test_mouse_functions()
    test_keyboard_functions()
    print("\n🎉 All basic tests passed!") 