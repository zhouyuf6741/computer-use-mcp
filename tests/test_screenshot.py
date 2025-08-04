import sys
sys.path.append('src')
from computer_use_mcp.core import take_screenshot

def test_screenshot_basic():
    """Test taking a screenshot without saving to downloads."""
    result = take_screenshot(save_to_downloads=False)
    assert result is not None
    print('✅ Basic screenshot test passed')

def test_screenshot_with_save():
    """Test taking a screenshot with saving to downloads."""
    result = take_screenshot(save_to_downloads=True)
    assert result is not None
    print('✅ Screenshot with save_to_downloads test passed')
