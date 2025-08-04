# Computer Control MCP

### MCP server that provides computer control capabilities using PyAutoGUI.

# Expecting Issues
1. Most Models are too slow with MCP server + PyAutoGUI 
2. Screenshot consumes a lot of tokens
3. It is diffcult for the model to click at the right position

# Potential
1. By using this generic mcp server, model can take all the actions locally
2. The actuation layer is extremely thin

---

## Quick Usage (MCP Setup)

### Option 1: Using Local Development Version

```json
{
  "mcpServers": {
    "computer-control-mcp": {
      "command": "python3",
      "args": ["-m", "computer_use_mcp"],
      "cwd": "/path/to/your/computer-control-mcp"
    }
  }
}
```

### Option 2: Using Global Installation

First install globally:
```bash
pip3 install -e . --break-system-packages
```

Then use this configuration:
```json
{
  "mcpServers": {
    "computer-control-mcp": {
      "command": "python3",
      "args": ["-m", "computer_use_mcp"]
    }
  }
}
```

### Option 3: Using uvx (Remote Version)

```json
{
  "mcpServers": {
    "computer-control-mcp": {
      "command": "uvx",
      "args": ["computer-control-mcp@latest"]
    }
  }
}
```

## Features

- Control mouse movements and clicks (left and right click)
- Type text at the current cursor position
- Take screenshots of the entire screen or specific windows with optional saving to downloads directory
- Extract text from screenshots using OCR (Optical Character Recognition)
- List and activate windows (adapted to newer pygetwindow API)
- Press keyboard keys
- Drag and drop operations
- Image compression to handle large screenshots
- Automatic cleanup of temporary files

## Available Tools

### Mouse Control
- `click_screen(x: int, y: int)`: Left click at specified screen coordinates
- `right_click(x: int, y: int)`: Right click at specified screen coordinates
- `move_mouse(x: int, y: int)`: Move mouse cursor to specified coordinates
- `drag_mouse(from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5)`: Drag mouse from one position to another

### Keyboard Control
- `type_text(text: str)`: Type the specified text at current cursor position
- `press_key(key: str)`: Press a specified keyboard key

### Screen and Window Management
- `take_screenshot(title_pattern: str = None, use_regex: bool = False, threshold: int = 60, with_ocr_text_and_coords: bool = False, scale_percent_for_ocr: int = 100, save_to_downloads: bool = False)`: Capture screen or window with optional OCR
- `get_screen_size()`: Get current screen resolution
- `list_windows()`: List all open windows with active window detection
- `activate_window(title_pattern: str, use_regex: bool = False, threshold: int = 60)`: Find and report matching windows

## Recent Improvements

### ✅ **API Compatibility**
- **Fixed pygetwindow API issues** - Updated to work with newer version that returns strings instead of window objects
- **Removed deprecated functions** - Eliminated `getAllWindows()` and `VisRes` usage
- **Improved error handling** - Better exception handling for API limitations

### ✅ **New Features**
- **Right-click functionality** - Added `right_click()` function for right mouse button clicks
- **Image compression** - Automatic resizing and compression to stay within Claude Desktop's 1MB limit
- **Temporary file cleanup** - Automatic cleanup of test files and temporary screenshots

### ✅ **Testing & Quality**
- **Comprehensive test suite** - 10/10 tests passing with full coverage
- **Proper test organization** - Moved development files to tests directory
- **Performance optimization** - Removed screenshots from window listing to reduce response size

## Current Limitations

Due to changes in the `pygetwindow` API:
- **Window activation** is limited (can detect but not fully control windows)
- **Window properties** (position, size) are not available in newer API
- **Window manipulation** is restricted to detection and reporting

## Development

### Setting up the Development Environment

```bash
# Clone the repository
git clone https://github.com/zhouyuf6741/computer-use-mcp.git
cd computer-control-mcp

# Install dependencies with dev tools
uv sync --extra dev

# Start server
python3 -m computer_use_mcp.core
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test categories
uv run pytest tests/test_basic.py -v
uv run pytest tests/test_screenshot.py -v
uv run pytest tests/test_window_functions.py -v
uv run pytest tests/test_ocr_standalone.py -v
```

### Test Coverage

✅ **Basic Functionality** (4 tests)
- Screen size detection
- Tool version information
- Mouse control functions
- Keyboard control functions

✅ **Screenshot & OCR** (3 tests)
- Basic screenshot functionality
- Screenshot with download saving
- OCR text extraction (89+ text elements detected)

✅ **Window Management** (3 tests)
- Window listing (52+ windows detected)
- Window activation detection
- API compatibility verification

## Troubleshooting

### Common Issues

1. **"No module named 'pyautogui'"**: Install the package globally with `pip3 install -e . --break-system-packages`

2. **"module 'pygetwindow' has no attribute 'getAllWindows'"**: This is expected with newer versions. The code has been updated to handle this limitation.

3. **"result exceeds maximum length"**: Screenshots are automatically compressed. If you still get this error, try using `scale_percent_for_ocr=50` when taking screenshots.

4. **Permission issues on macOS**: You may need to grant accessibility permissions to your terminal/IDE in System Preferences > Security & Privacy > Privacy > Accessibility.

### Performance Tips

- Use `scale_percent_for_ocr=50` for faster OCR processing
- Avoid taking screenshots with OCR unless necessary
- The `list_windows()` function no longer includes screenshots to reduce response size
- Temporary files are automatically cleaned up after processing

## API Reference

See the [API Reference](docs/api.md) for detailed information about the available functions and classes.

## License

MIT

