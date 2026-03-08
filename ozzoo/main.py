"""
main.py
=======
Entry point for the OzZoo Zoo Simulation Game.

Usage
-----
    python main.py
"""

import sys
import os

# Ensure the ozzoo package directory is on the Python path
sys.path.insert(0, os.path.dirname(__file__))

from cli import CLI


def main() -> None:
    """Launch the OzZoo interactive CLI."""
    app = CLI()
    app.run()


if __name__ == "__main__":
    main()
