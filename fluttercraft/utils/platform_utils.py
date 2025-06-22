"""Utility functions for platform detection."""

import platform
import os
import sys


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
