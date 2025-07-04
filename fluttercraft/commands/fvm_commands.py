"""FVM commands for FlutterCraft CLI - Backward compatibility module.

This module re-exports the functions from the modular structure in the fvm/ package
to maintain backward compatibility with existing code.
"""

# Re-export all functions from the new modular structure
from fluttercraft.commands.fvm.version import check_fvm_version
from fluttercraft.commands.fvm.install import fvm_install_command
from fluttercraft.commands.fvm.uninstall import fvm_uninstall_command
from fluttercraft.commands.fvm.releases import fvm_releases_command
from fluttercraft.commands.fvm.list import fvm_list_command

__all__ = [
    'check_fvm_version',
    'fvm_install_command',
    'fvm_uninstall_command',
    'fvm_releases_command',
    'fvm_list_command',
]
