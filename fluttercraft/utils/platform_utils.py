"""Utility functions for platform detection and system information."""

import platform
import os
import sys
import subprocess
from pathlib import Path


def get_platform_info():
    """
    Get information about the current platform and environment.

    Returns:
        dict: A dictionary containing platform information.
    """
    info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }

    # Get shell information
    if info["system"] == "Windows":
        info["shell"] = os.environ.get("COMSPEC", "")
    else:
        info["shell"] = os.environ.get("SHELL", "")

    # Get additional environment information
    info["path"] = os.environ.get("PATH", "")

    return info


def get_git_info():
    """
    Get current git branch and status information.

    Returns:
        dict: {"branch": str, "has_changes": bool} or {"branch": "", "has_changes": False}
    """
    try:
        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=2,
            shell=(platform.system() == "Windows"),
        )
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else ""

        # Check for uncommitted changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=2,
            shell=(platform.system() == "Windows"),
        )
        has_changes = (
            bool(status_result.stdout.strip())
            if status_result.returncode == 0
            else False
        )

        return {"branch": branch, "has_changes": has_changes}
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return {"branch": "", "has_changes": False}


def get_current_path():
    """
    Get current working directory path.

    Returns:
        str: Current working directory path, truncated if too long
    """
    try:
        cwd = Path.cwd()
        cwd_str = str(cwd)

        # Truncate if path is too long (for display purposes)
        max_length = 50
        if len(cwd_str) > max_length:
            # Show start and end of path
            parts = cwd_str.split(os.sep)
            if len(parts) > 3:
                return os.sep.join([parts[0], "...", parts[-2], parts[-1]])

        return cwd_str
    except Exception:
        return "Unknown"


def is_windows():
    """Check if running on Windows."""
    return platform.system() == "Windows"


def is_macos():
    """Check if running on macOS."""
    return platform.system() == "Darwin"


def is_linux():
    """Check if running on Linux."""
    return platform.system() == "Linux"
