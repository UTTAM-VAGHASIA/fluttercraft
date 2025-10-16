"""Help command handler functionality."""

from fluttercraft.commands.help.global_help import show_global_help
from fluttercraft.commands.help.fvm_help import (
    show_fvm_help,
    show_fvm_install_help,
    show_fvm_uninstall_help,
    show_fvm_releases_help,
    show_fvm_list_help,
)
from fluttercraft.commands.help.common import show_clear_help


def handle_help_command(command_parts):
    """
    Handle help requests for various commands.

    Args:
        command_parts (list): The command split into parts

    Returns:
        str: Message indicating which help was displayed
    """
    # Handle empty command parts (just 'help')
    if not command_parts or len(command_parts) == 0:
        return show_global_help()

    # First part is always 'help' in this function
    if len(command_parts) == 1:
        return show_global_help()

    # Check for command-specific help
    if command_parts[0] == "fvm":
        if len(command_parts) == 1:
            # Just "fvm", show global help
            return show_global_help()
        elif len(command_parts) == 2 and command_parts[1] in ["help", "--help", "-h"]:
            # "fvm help"
            return show_fvm_help()
        elif len(command_parts) >= 3 and command_parts[2] in ["help", "--help", "-h"]:
            # "fvm <command> help"
            if command_parts[1] == "install":
                return show_fvm_install_help()
            elif command_parts[1] == "uninstall":
                return show_fvm_uninstall_help()
            elif command_parts[1] == "releases":
                return show_fvm_releases_help()
            elif command_parts[1] == "list":
                return show_fvm_list_help()
    elif (
        command_parts[0] == "clear"
        and len(command_parts) >= 2
        and command_parts[1] in ["help", "--help", "-h"]
    ):
        return show_clear_help()

    # If we reach here, it's not a recognized help command
    return show_global_help()
