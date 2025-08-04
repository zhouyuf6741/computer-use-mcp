"""
Server module for Computer Use MCP.

This module provides a simple way to run the MCP server.
"""

from computer_use_mcp.core import main as run_server

def main():
    """Run the MCP server."""
    print("Starting Computer Use MCP server...")
    run_server()

if __name__ == "__main__":
    main()
