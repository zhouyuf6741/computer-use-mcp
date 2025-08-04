"""
Entry point for running the Computer Use MCP as a module.

This module serves as the main entry point for the package.
When executed directly (e.g., with `python -m computer_use_mcp`),
it will run the CLI interface.

For CLI functionality, use:
    computer-use-mcp <command>
    python -m computer_use_mcp <command>
"""

from computer_use_mcp.cli import main as cli_main

def main():
    """Main entry point for the package."""
    # Run the CLI when the module is executed directly
    cli_main()

if __name__ == "__main__":
    main()
