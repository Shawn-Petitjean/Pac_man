"""Launcher for the packaged Pac-Man build.

Kept at the repository root so PyInstaller has a single, stable entry
point. Running ``python pacman.py [config.json]`` behaves exactly like
``python -m src``.
"""
from src.__main__ import main

if __name__ == "__main__":
    main()
