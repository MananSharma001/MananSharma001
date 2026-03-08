"""
main.py
=======
Entry point for the OzZoo Zoo Simulation Game.

Usage
-----
    # Terminal (CLI) mode — default
    python main.py

    # Graphical (GUI) mode
    python main.py --gui
"""

import sys
import os

# Ensure the ozzoo package directory is on the Python path
sys.path.insert(0, os.path.dirname(__file__))


def _run_cli() -> None:
    """Launch the OzZoo interactive CLI."""
    from cli import CLI
    app = CLI()
    app.run()


def _run_gui() -> None:
    """Launch the OzZoo tkinter GUI."""
    try:
        import tkinter  # Check availability before attempting to launch the GUI
    except ImportError:
        print(
            "❌  tkinter is not available in your Python installation.\n"
            "    On Debian/Ubuntu: sudo apt-get install python3-tk\n"
            "    On Windows/macOS: tkinter ships with the standard Python installer."
        )
        sys.exit(1)

    from gui import run_gui
    run_gui()


def main() -> None:
    """Dispatch to GUI or CLI based on command-line arguments."""
    if "--gui" in sys.argv:
        _run_gui()
    else:
        _run_cli()


if __name__ == "__main__":
    main()
