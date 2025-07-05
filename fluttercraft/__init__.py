"""
FlutterCraft - Automate your Flutter app setup like a pro 🛠️🚀

A powerful CLI tool that helps developers set up Flutter projects with ease,
manage Flutter Version Manager (FVM), and provides an interactive development experience.

Copyright (c) 2025 FlutterCraft
Licensed under AGPL v3
"""

__version__ = "0.1.2"
__author__ = "UTTAM-VAGHASIA"
__description__ = "Automate your Flutter app setup like a pro"
__license__ = "AGPL v3"

# Public API
from fluttercraft.cli.core import FlutterCraftApp
from fluttercraft.cli.themes.manager import ThemeManager
from fluttercraft.config.settings import ConfigManager

__all__ = [
    "FlutterCraftApp",
    "ThemeManager", 
    "ConfigManager",
    "__version__",
    "__author__",
    "__description__",
    "__license__",
]
