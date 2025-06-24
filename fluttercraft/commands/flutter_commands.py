"""Flutter commands for FlutterCraft CLI - Backward compatibility module.

This module re-exports the functions from the modular structure in the flutter/ package
to maintain backward compatibility with existing code.
"""

# Re-export functions from the new modular structure
from fluttercraft.commands.flutter.version import check_flutter_version

__all__ = [
    'check_flutter_version',
]
