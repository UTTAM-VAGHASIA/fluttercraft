"""Command handler for FlutterCraft CLI with slash command support."""

from rich.console import Console

from fluttercraft.utils.beautiful_display import (
    display_command_help,
    display_welcome_header,
    update_system_info,
)
from fluttercraft.commands.flutter_commands import check_flutter_version
from fluttercraft.commands.fvm_commands import (
    check_fvm_version,
    fvm_install_command,
    fvm_uninstall_command,
    fvm_releases_command,
    fvm_list_command,
)
from fluttercraft.commands.help_commands import (
    show_global_help,
    show_fvm_help,
    show_fvm_install_help,
    show_fvm_uninstall_help,
    show_fvm_releases_help,
    show_fvm_list_help,
)

console = Console()


class CommandHandler:
    """Handles command execution for FlutterCraft CLI."""
    
    def __init__(self, platform_info, flutter_info, fvm_info):
        """Initialize the command handler.
        
        Args:
            platform_info: Platform information dictionary
            flutter_info: Flutter version information dictionary
            fvm_info: FVM version information dictionary
        """
        self.platform_info = platform_info
        self.flutter_info = flutter_info
        self.fvm_info = fvm_info
    
    def handle_slash_command(self, command, args):
        """Handle slash commands.
        
        Args:
            command: The slash command (e.g., '/quit', '/clear')
            args: List of arguments
        
        Returns:
            bool: True if should continue, False if should exit
        """
        command = command.lower()
        
        # Quit commands
        if command in ['/quit']:
            console.print("[yellow]Thank you for using FlutterCraft! Goodbye! 👋[/]")
            return False
        
        # Clear command
        elif command == '/clear':
            display_welcome_header(self.platform_info, self.flutter_info, self.fvm_info, show_ascii=True)
            return True
        
        # Help command
        elif command == '/help':
            display_command_help()
            return True
        
        # About command
        elif command == '/about':
            from fluttercraft.utils.beautiful_display import display_about
            display_about()
            return True
        
        else:
            console.print(f"[red]Unknown slash command: {command}[/]")
            console.print("[yellow]Type '/help' to see available commands[/]")
            return True
    
    def handle_fvm_command(self, command_parts):
        """Handle FVM commands.
        
        Args:
            command_parts: List of command parts
        
        Returns:
            bool: True to continue
        """
        full_command = " ".join(command_parts)
        
        # Check for help flags
        if len(command_parts) > 1 and command_parts[-1] in ["help", "--help", "-h"]:
            if len(command_parts) == 2:
                # "fvm help"
                show_fvm_help()
            else:
                # "fvm <command> help"
                if command_parts[1] == "install":
                    show_fvm_install_help()
                elif command_parts[1] == "uninstall":
                    show_fvm_uninstall_help()
                elif command_parts[1] == "releases":
                    show_fvm_releases_help()
                elif command_parts[1] == "list":
                    show_fvm_list_help()
                else:
                    show_fvm_help()
            return True
        
        # FVM install
        if len(command_parts) == 2 and command_parts[1] == "install":
            updated_fvm_info, _ = fvm_install_command(
                self.platform_info, self.flutter_info, self.fvm_info
            )
            
            if updated_fvm_info != self.fvm_info:
                self.fvm_info = updated_fvm_info
                # Update system info display
                update_system_info(self.platform_info, self.flutter_info, self.fvm_info)
            return True
        
        # FVM uninstall
        elif len(command_parts) == 2 and command_parts[1] == "uninstall":
            updated_fvm_info, _ = fvm_uninstall_command(
                self.platform_info, self.flutter_info, self.fvm_info
            )
            
            if updated_fvm_info != self.fvm_info:
                self.fvm_info = updated_fvm_info
                # Update system info display
                update_system_info(self.platform_info, self.flutter_info, self.fvm_info)
            return True
        
        # FVM releases
        elif len(command_parts) >= 2 and command_parts[1] == "releases":
            channel = None
            
            # Parse channel parameter
            if len(command_parts) >= 3:
                # Handle --channel=value format
                if any(part.startswith("--channel=") for part in command_parts):
                    for part in command_parts:
                        if part.startswith("--channel="):
                            channel = part.split("=")[1]
                            break
                # Handle -c value or --channel value format
                elif command_parts[2] in ["-c", "--channel"] and len(command_parts) >= 4:
                    channel = command_parts[3]
                # If just a single parameter is provided without flags
                elif len(command_parts) == 3 and command_parts[2] in ["stable", "beta", "dev", "all"]:
                    channel = command_parts[2]
            
            try:
                fvm_releases_command(channel)
            except Exception as e:
                console.print(f"[bold red]Error fetching Flutter releases: {str(e)}[/]")
                console.print("[yellow]Try using: fvm releases --channel [stable|beta|dev|all][/]")
            
            return True
        
        # FVM list
        elif len(command_parts) == 2 and command_parts[1] == "list":
            try:
                fvm_list_command()
            except Exception as e:
                console.print(f"[bold red]Error fetching installed Flutter versions: {str(e)}[/]")
                console.print("[yellow]Make sure FVM is properly installed. Try running 'fvm install' first.[/]")
            
            return True
        
        # Just "fvm" without args
        elif len(command_parts) == 1:
            show_fvm_help()
            return True
        
        # Unknown FVM command
        else:
            console.print(f"\n[red]✗ Unknown FVM command: [bold]{full_command}[/bold][/]")
            console.print("\n[yellow]Available FVM commands:[/]")
            console.print("[cyan]  • fvm install[/] [dim]- Install Flutter Version Manager[/]")
            console.print("[cyan]  • fvm uninstall[/] [dim]- Uninstall FVM[/]")
            console.print("[cyan]  • fvm releases[/] [dim]- List available Flutter versions[/]")
            console.print("[cyan]  • fvm list[/] [dim]- List installed Flutter versions[/]")
            console.print("\n[dim]Type 'fvm --help' for detailed help[/]\n")
            return True
    
    def handle_flutter_command(self, command_parts):
        """Handle Flutter commands.
        
        Args:
            command_parts: List of command parts
        
        Returns:
            bool: True to continue
        """
        full_command = " ".join(command_parts)
        
        # Check if it's a flutter upgrade command
        if len(command_parts) >= 2 and command_parts[1] == "upgrade":
            from fluttercraft.utils.terminal_utils import run_with_loading
            import platform as plat
            
            # Check for help flag
            if len(command_parts) > 2 and command_parts[-1] in ["--help", "-h", "help"]:
                console.print("\n[bold cyan]Flutter Upgrade Command Help[/]\n")
                console.print("[bold yellow]Usage:[/]")
                console.print("  flutter upgrade [options]\n")
                console.print("[bold yellow]Description:[/]")
                console.print("  Upgrade Flutter to the latest version available on the current channel.\n")
                console.print("[bold yellow]Options:[/]")
                console.print("  [cyan]--force[/]              Force upgrade even if already up to date")
                console.print("  [cyan]--verify-only[/]        Check for updates without upgrading")
                console.print("  [cyan]--continue[/]           Continue a previously interrupted upgrade")
                console.print("  [cyan]--verbose[/]            Show detailed output")
                console.print("  [cyan]-h, --help[/]           Show this help message\n")
                console.print("[bold yellow]Examples:[/]")
                console.print("  [dim]flutter upgrade[/]                    # Upgrade to latest version")
                console.print("  [dim]flutter upgrade --force[/]            # Force upgrade")
                console.print("  [dim]flutter upgrade --verify-only[/]      # Check for updates only\n")
                return True
            
            # Build command with any additional parameters
            cmd = ["flutter", "upgrade"]
            
            # Check for special flags
            is_verify_only = False
            additional_params = []
            
            # Add any additional parameters (like --force, --verify-only, etc.)
            if len(command_parts) > 2:
                additional_params = command_parts[2:]
                cmd.extend(additional_params)
                
                # Check if it's a verify-only command
                is_verify_only = "--verify-only" in additional_params
                
                console.print(f"[bold yellow]Executing Flutter upgrade with parameters: {' '.join(additional_params)}[/]")
            else:
                console.print("[bold yellow]Executing Flutter upgrade...[/]")
            
            # Run flutter upgrade with shell=True on Windows
            result = run_with_loading(
                cmd,
                status_message="[bold yellow]Upgrading Flutter...[/]" if not is_verify_only else "[bold yellow]Checking for Flutter updates...[/]",
                should_display_command=True,
                clear_on_success=False,
                show_output_on_failure=True,
                show_status_message=True,
            )
            
            # Check if command was successful
            if result.returncode == 0:
                if is_verify_only:
                    # For verify-only, just show completion message
                    console.print("[bold green]✓ Flutter update check completed![/]")
                else:
                    # For actual upgrade, show success and update version
                    console.print("[bold green]✓ Flutter upgrade completed successfully![/]")
                    
                    # Re-check Flutter version
                    updated_flutter_info = check_flutter_version(silent=True)
                    
                    # Update the stored flutter_info
                    if updated_flutter_info != self.flutter_info:
                        self.flutter_info = updated_flutter_info
                        console.print("[dim]Flutter version updated.[/]")
                        # Update system info display
                        update_system_info(self.platform_info, self.flutter_info, self.fvm_info)
                    else:
                        console.print("[dim]Flutter version unchanged.[/]")
            else:
                console.print("[bold red]✗ Flutter upgrade command failed![/]")
            
            return True
        
        # Other Flutter commands not yet implemented
        console.print("\n[bold yellow]⚠ Flutter Command Not Yet Implemented[/]")
        console.print(f"[dim]Command: {full_command}[/]")
        console.print("\n[cyan]This Flutter command is coming soon for Windows![/]")
        console.print("[dim]Currently working commands:[/]")
        console.print("[dim]  • flutter upgrade - Upgrade Flutter to latest version[/]")
        console.print("[dim]  • FVM commands (fvm install, fvm releases, etc.)[/]")
        console.print("[dim]  • Slash commands (/help, /clear, /quit)[/]")
        console.print("\n[dim]Tip: Use '/help' to see all available commands[/]\n")
        return True
    
    def handle_help_command(self, command_parts):
        """Handle help commands.
        
        Args:
            command_parts: List of command parts
        
        Returns:
            bool: True to continue
        """
        display_command_help()
        return True
    
    def handle_regular_command(self, command):
        """Handle regular (non-slash) commands.
        
        Args:
            command: The command string
        
        Returns:
            bool: True to continue
        """
        command_parts = command.lower().strip().split()
        
        if not command_parts:
            return True
        
        # FVM commands
        if command_parts[0] == "fvm":
            return self.handle_fvm_command(command_parts)
        
        # Flutter commands
        elif command_parts[0] == "flutter":
            return self.handle_flutter_command(command_parts)
        
        # Help command (only if it's the first word or standalone)
        elif command_parts[0] in ["help", "h"]:
            return self.handle_help_command(command_parts)
        
        # Check for help flags only if not already handled by specific command
        elif command_parts[-1] in ["help", "--help", "-h"]:
            return self.handle_help_command(command_parts)
        
        # Unknown command
        else:
            console.print(f"\n[red]✗ Unknown command: [bold]{command}[/bold][/]")
            console.print("\n[yellow]Available command types:[/]")
            console.print("[cyan]  • Slash commands:[/] [dim]/quit, /clear, /help[/]")
            console.print("[cyan]  • FVM commands:[/] [dim]fvm install, fvm releases, fvm list, etc.[/]")
            console.print("[cyan]  • Flutter commands:[/] [dim yellow](Coming Soon)[/]")
            console.print("\n[dim]Type '/help' to see all available commands[/]\n")
            return True
    
    def execute_command(self, command):
        """Execute a command and return whether to continue.
        
        Args:
            command: The command string
        
        Returns:
            bool: True if should continue, False if should exit
        """
        if not command:
            return True
        
        # Check if it's a slash command
        if command.startswith('/'):
            from fluttercraft.utils.beautiful_prompt import parse_slash_command
            cmd_name, args = parse_slash_command(command)
            return self.handle_slash_command(cmd_name, args)
        
        # Regular command
        return self.handle_regular_command(command)
