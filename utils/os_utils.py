"""
utils/os_utils.py

Provides cross-platform utility functions for interacting with the desktop file system.
Abstracts away Windows-specific functions like os.startfile.
"""
import sys
import subprocess
import os
from pathlib import Path


def open_file_or_explorer(target_path: Path | str) -> None:
    """
    Opens a file or directory using the native OS default application.
    - Windows: os.startfile()
    - macOS: open
    - Linux: xdg-open
    """
    target = str(target_path)
    if sys.platform == "win32":
        try:
            os.startfile(target)
        except Exception:
            pass
    elif sys.platform == "darwin": # macOS
        try:
            subprocess.run(["open", target], check=False)
        except Exception:
            pass
    else: # Linux/Unix
        try:
            subprocess.run(["xdg-open", target], check=False)
        except Exception:
            pass
