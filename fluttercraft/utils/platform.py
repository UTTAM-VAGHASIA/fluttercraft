"""
Platform Utilities

Cross-platform functionality for FlutterCraft including path handling,
system detection, and platform-specific operations.
"""

import os
import platform
import sys
from pathlib import Path
from typing import Dict, Optional

from rich.console import Console


def get_platform_info() -> Dict[str, str]:
    """
    Get comprehensive platform information.
    
    Returns:
        Dictionary containing platform details
    """
    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0],
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "node": platform.node(),
    }


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == "Darwin"


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system() == "Linux"


def get_config_directory() -> Path:
    """
    Get platform-appropriate configuration directory.
    
    Returns:
        Path to configuration directory
    """
    if is_windows():
        # Use AppData/Local on Windows
        config_dir = Path.home() / "AppData" / "Local" / "FlutterCraft"
    elif is_macos():
        # Use Application Support on macOS
        config_dir = Path.home() / "Library" / "Application Support" / "FlutterCraft"
    else:  # Linux and others
        # Use XDG config directory on Linux
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            config_dir = Path(xdg_config) / "fluttercraft"
        else:
            config_dir = Path.home() / ".config" / "fluttercraft"
    
    return config_dir


def get_cache_directory() -> Path:
    """
    Get platform-appropriate cache directory.
    
    Returns:
        Path to cache directory
    """
    if is_windows():
        # Use AppData/Local on Windows
        cache_dir = Path.home() / "AppData" / "Local" / "FlutterCraft" / "cache"
    elif is_macos():
        # Use Caches on macOS
        cache_dir = Path.home() / "Library" / "Caches" / "FlutterCraft"
    else:  # Linux and others
        # Use XDG cache directory on Linux
        xdg_cache = os.environ.get("XDG_CACHE_HOME")
        if xdg_cache:
            cache_dir = Path(xdg_cache) / "fluttercraft"
        else:
            cache_dir = Path.home() / ".cache" / "fluttercraft"
    
    return cache_dir


def get_data_directory() -> Path:
    """
    Get platform-appropriate data directory.
    
    Returns:
        Path to data directory
    """
    if is_windows():
        # Use AppData/Local on Windows
        data_dir = Path.home() / "AppData" / "Local" / "FlutterCraft" / "data"
    elif is_macos():
        # Use Application Support on macOS
        data_dir = Path.home() / "Library" / "Application Support" / "FlutterCraft" / "data"
    else:  # Linux and others
        # Use XDG data directory on Linux
        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            data_dir = Path(xdg_data) / "fluttercraft"
        else:
            data_dir = Path.home() / ".local" / "share" / "fluttercraft"
    
    return data_dir


def ensure_directory_exists(directory: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to directory to create
        
    Raises:
        PermissionError: If unable to create directory due to permissions
        OSError: If unable to create directory for other reasons
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise PermissionError(f"Permission denied creating directory: {directory}")
    except OSError as e:
        raise OSError(f"Failed to create directory {directory}: {str(e)}")


def get_executable_extension() -> str:
    """
    Get the executable file extension for the current platform.
    
    Returns:
        File extension for executables ('.exe' on Windows, '' on Unix)
    """
    return ".exe" if is_windows() else ""


def get_shell_name() -> str:
    """
    Get the name of the current shell.
    
    Returns:
        Shell name (e.g., 'powershell', 'bash', 'zsh')
    """
    shell = os.environ.get("SHELL", "")
    if not shell and is_windows():
        # Try to detect PowerShell on Windows
        if "powershell" in os.environ.get("PSModulePath", "").lower():
            return "powershell"
        else:
            return "cmd"
    
    if shell:
        return Path(shell).name
    
    return "unknown"


def get_terminal_size() -> tuple[int, int]:
    """
    Get terminal size.
    
    Returns:
        Tuple of (width, height) in characters
    """
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        # Fallback to default size
        return 80, 24


def is_admin() -> bool:
    """
    Check if running with administrator/root privileges.
    
    Returns:
        True if running as admin/root, False otherwise
    """
    try:
        if is_windows():
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:
            return os.geteuid() == 0
    except (ImportError, AttributeError):
        return False


def get_environment_variables() -> Dict[str, str]:
    """
    Get relevant environment variables for Flutter development.
    
    Returns:
        Dictionary of environment variables
    """
    relevant_vars = [
        "PATH",
        "FLUTTER_ROOT",
        "FLUTTER_GIT_URL", 
        "FVM_HOME",
        "ANDROID_HOME",
        "ANDROID_SDK_ROOT",
        "JAVA_HOME",
        "CHROME_EXECUTABLE",
        "PUB_CACHE",
    ]
    
    env_vars = {}
    for var in relevant_vars:
        value = os.environ.get(var)
        if value:
            env_vars[var] = value
    
    return env_vars


def ensure_platform_compatibility() -> None:
    """
    Ensure the platform is compatible with FlutterCraft.
    
    Raises:
        SystemError: If platform is not supported
        RuntimeError: If Python version is incompatible
    """
    # Check Python version
    if sys.version_info < (3, 10):
        raise RuntimeError(
            f"FlutterCraft requires Python 3.10 or higher. "
            f"Current version: {platform.python_version()}"
        )
    
    # Check platform support
    supported_platforms = ["Windows", "Darwin", "Linux"]
    current_platform = platform.system()
    
    if current_platform not in supported_platforms:
        raise SystemError(
            f"Platform '{current_platform}' is not supported. "
            f"Supported platforms: {', '.join(supported_platforms)}"
        )


def format_path_for_display(path: Path) -> str:
    """
    Format a path for display in the terminal.
    
    Args:
        path: Path to format
        
    Returns:
        Formatted path string
    """
    try:
        # Try to get relative path from home directory
        home = Path.home()
        if path.is_relative_to(home):
            relative_path = path.relative_to(home)
            if is_windows():
                return f"~\\{relative_path}"
            else:
                return f"~/{relative_path}"
    except (ValueError, OSError):
        pass
    
    # Fall back to absolute path
    return str(path)
