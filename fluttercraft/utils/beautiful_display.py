"""Beautiful display utilities for FlutterCraft CLI with enhanced formatting."""

import os
import platform
import subprocess
from pathlib import Path

from rich.console import Console

console = Console()


def create_ascii_art():
    """Create the FlutterCraft ASCII art in ANSI Shadow style."""
    art = """   
███████╗██╗     ██╗   ██╗████████╗████████╗███████╗██████╗  
██╔════╝██║     ██║   ██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗ 
█████╗  ██║     ██║   ██║   ██║      ██║   █████╗  ██████╔╝ 
██╔══╝  ██║     ██║   ██║   ██║      ██║   ██╔══╝  ██╔══██╗ 
██║     ███████╗╚██████╔╝   ██║      ██║   ███████╗██║  ██║ 
╚═╝     ╚══════╝ ╚═════╝    ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝ 
 ██████╗██████╗  █████╗ ███████╗████████╗                   
██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝                   
██║     ██████╔╝███████║█████╗     ██║                      
██║     ██╔══██╗██╔══██║██╔══╝     ██║                      
╚██████╗██║  ██║██║  ██║██║        ██║                      
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝                      
"""
    return art.strip()


def get_git_info():
    """Get current git branch and status."""
    try:
        # Get current directory
        cwd = os.getcwd()
        
        # Get git branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=2
        )
        
        if branch_result.returncode == 0:
            branch = branch_result.stdout.strip()
            
            # Check if there are uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=2
            )
            
            has_changes = bool(status_result.stdout.strip())
            status_indicator = "*" if has_changes else ""
            
            return f"{branch}{status_indicator}"
        else:
            return None
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return None


def get_current_path():
    """Get current working directory relative to home."""
    try:
        cwd = Path.cwd()
        home = Path.home()
        
        # Try to make it relative to home
        try:
            rel_path = cwd.relative_to(home)
            return f"~\\{rel_path}"
        except ValueError:
            # Not relative to home, use absolute path
            return str(cwd)
    except Exception:
        return os.getcwd()


def display_welcome_header(platform_info, flutter_info, fvm_info, show_ascii=True):
    """Display the beautiful welcome header with system information.
    
    Args:
        platform_info: Dictionary containing platform information
        flutter_info: Dictionary containing Flutter version information
        fvm_info: Dictionary containing FVM version information
        show_ascii: Whether to show ASCII art and clear screen
    """
    if show_ascii:
        clear_screen()
        art = create_ascii_art()
        console.print(f"[bold cyan]{art}[/]\n")
    
    # Display tips section
    console.print("[bold]Tips for getting started:[/]")
    console.print("[dim]1. Use slash commands like /help, /clear, /quit[/]")
    console.print("[dim]2. Manage Flutter versions with FVM commands[/]")
    console.print("[dim]3. Run 'flutter upgrade' to update Flutter[/]")
    console.print("[dim]4. Type / to see available commands[/]\n")
    
    # Display system info as part of header
    platform_name = platform_info.get('system', 'Unknown')
    python_version = platform_info.get('python_version', 'Unknown')
    fvm_version = fvm_info.get('version') if fvm_info.get('version') else 'Not installed'
    
    # Format Flutter version with update indicator
    flutter_version = flutter_info.get('current_version')
    if flutter_version:
        if flutter_info.get('update_available'):
            latest = flutter_info.get('latest_version', 'unknown')
            flutter_display = f"{flutter_version} [yellow](→ {latest} available)[/yellow]"
        else:
            flutter_display = f"{flutter_version} [green]✓[/green]"
    else:
        flutter_display = 'None'
    
    console.print(f"[dim]Platform: {platform_name} | "
                  f"Python: {python_version} | "
                  f"Flutter: {flutter_display} | "
                  f"FVM: {fvm_version}[/]\n")


def display_flutter_version(flutter_info):
    """Display Flutter version information with proper formatting."""
    if flutter_info["installed"]:
        if flutter_info["current_version"]:
            version_str = f"[bold green]Flutter version:[/] {flutter_info['current_version']}"
            
            if flutter_info["latest_version"]:
                if flutter_info["current_version"] != flutter_info["latest_version"]:
                    version_str += f" [yellow](Latest version available: {flutter_info['latest_version']})[/]"
                else:
                    version_str += " [green](Your Flutter version is already up to date)[/]"
            else:
                version_str += " [green](up to date)[/]"
            
            console.print(version_str)
        else:
            console.print("[yellow]Flutter is installed, but version could not be determined[/]")
    else:
        console.print("[bold red]Flutter is not installed[/]")


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if platform.system().lower() == "windows" else "clear")


def show_platform_not_supported(platform_name):
    """Show animated coming soon message for unsupported platforms.
    
    Args:
        platform_name: Name of the platform (Darwin for macOS, Linux)
    """
    import time
    from rich.live import Live
    from rich.align import Align
    from rich.panel import Panel
    from rich.text import Text
    
    clear_screen()
    
    # Display platform name
    platform_display = "macOS" if platform_name == "Darwin" else "Linux"
    
    # Animated emoji frames (rotating effect)
    frames = [
        "🚀",
        "🛸",
        "✨",
        "⭐",
        "💫",
        "🌟",
        "✨",
        "🛸",
    ]
    
    # Show ASCII art
    art = create_ascii_art()
    console.print(f"[bold cyan]{art}[/]\n")
    
    # Create the message
    message = Text()
    message.append(f"\n{platform_display} Support Coming Soon!\n\n", style="bold yellow")
    message.append("FlutterCraft is currently optimized for Windows.\n", style="dim")
    message.append(f"Support for {platform_display} is under development and will be available soon.\n\n", style="dim")
    message.append("Stay tuned for updates! ", style="cyan")
    
    # Animate for a few seconds
    try:
        with Live(console=console, refresh_per_second=4) as live:
            for _ in range(12):  # 3 seconds of animation
                for frame in frames:
                    # Create panel with current frame
                    emoji_text = Text(frame, style="bold", justify="center")
                    emoji_text.append("\n")
                    
                    content = Text()
                    content.append(emoji_text)
                    content.append(message)
                    
                    panel = Panel(
                        Align.center(content),
                        border_style="cyan",
                        padding=(1, 2),
                    )
                    
                    live.update(panel)
                    time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    
    console.print("\n[dim]Press Ctrl+C to exit[/]\n")
    
    # Wait for user to exit
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Thank you for your interest in FlutterCraft! 👋[/]\n")


def update_system_info(platform_info, flutter_info, fvm_info):
    """Update just the system info line without clearing screen.
    
    Args:
        platform_info: Dictionary containing platform information
        flutter_info: Dictionary containing Flutter version information
        fvm_info: Dictionary containing FVM version information
    """
    platform_name = platform_info.get('system', 'Unknown')
    python_version = platform_info.get('python_version', 'Unknown')
    fvm_version = fvm_info.get('version') if fvm_info.get('version') else 'Not installed'
    
    # Format Flutter version with update indicator
    flutter_version = flutter_info.get('current_version')
    if flutter_version:
        if flutter_info.get('update_available'):
            latest = flutter_info.get('latest_version', 'unknown')
            flutter_display = f"{flutter_version} [yellow](→ {latest} available)[/yellow]"
        else:
            flutter_display = f"{flutter_version} [green]✓[/green]"
    else:
        flutter_display = 'None'
    
    console.print(f"\n[dim]Updated: Platform: {platform_name} | "
                  f"Python: {python_version} | "
                  f"Flutter: {flutter_display} | "
                  f"FVM: {fvm_version}[/]\n")


def display_about():
    """Display information about FlutterCraft CLI."""
    import platform
    import sys
    from importlib.metadata import version as get_version, PackageNotFoundError
    
    console.print("\n[bold cyan]╔════════════════════════════════════════════════════════════════╗[/]")
    console.print("[bold cyan]║[/]                        [bold white]FlutterCraft CLI[/]                        [bold cyan]║[/]")
    console.print("[bold cyan]╚════════════════════════════════════════════════════════════════╝[/]\n")
    
    console.print("[bold yellow]Description:[/]")
    console.print("  A powerful command-line interface for managing Flutter and FVM")
    console.print("  (Flutter Version Manager) with an intuitive and beautiful interface.\n")
    
    console.print("[bold yellow]Version Information:[/]")
    
    # Try to get version from package metadata
    try:
        version = get_version("fluttercraft")
    except PackageNotFoundError:
        version = "0.1.2"
    
    console.print(f"  [cyan]FlutterCraft:[/] {version}")
    console.print(f"  [cyan]Python:[/] {sys.version.split()[0]}")
    console.print(f"  [cyan]Platform:[/] {platform.system()} {platform.release()}\n")
    
    console.print("[bold yellow]Features:[/]")
    console.print("  [green]✓[/] Flutter Version Manager (FVM) integration")
    console.print("  [green]✓[/] Install and manage FVM")
    console.print("  [green]✓[/] List available Flutter SDK versions")
    console.print("  [green]✓[/] Flutter upgrade with progress tracking")
    console.print("  [green]✓[/] Real-time command output with loading indicators")
    console.print("  [green]✓[/] Beautiful command-line interface")
    console.print("  [green]✓[/] Auto-completion and command history\n")
    
    console.print("[bold yellow]Working Commands:[/]")
    console.print("  [cyan]Slash Commands:[/] /quit, /clear, /help, /about")
    console.print("  [cyan]FVM Commands:[/] fvm install, fvm uninstall, fvm releases, fvm list")
    console.print("  [cyan]Flutter Commands:[/] flutter upgrade (with --force, --verify-only)\n")
    
    console.print("[bold yellow]Author:[/]")
    console.print("  Created with 💝 by UTTAM VAGHASIA for Flutter developers\n")
    
    console.print("[bold yellow]Repository:[/]")
    console.print("  [cyan]https://github.com/UTTAM-VAGHASIA/fluttercraft[/]")
    console.print("  [dim]⭐ Star the repo if you find it useful![/]\n")
    
    console.print("[bold yellow]Quick Start:[/]")
    console.print("  1. Type [cyan]/help[/] to see all available commands")
    console.print("  2. Use [cyan]fvm install[/] to install Flutter Version Manager")
    console.print("  3. Run [cyan]fvm releases[/] to see available Flutter versions")
    console.print("  4. Use [cyan]flutter upgrade[/] to update Flutter\n")
    
    console.print("[dim]Type '/help' for detailed command information[/]\n")


def display_command_help():
    """Display help information for available commands."""
    from fluttercraft.utils.beautiful_prompt import SLASH_COMMANDS, FVM_COMMANDS, FLUTTER_COMMANDS
    
    console.print("\n[bold cyan]Available Commands:[/]\n")
    
    # Display slash commands
    console.print("[bold yellow]Slash Commands:[/]")
    for cmd, desc in SLASH_COMMANDS.items():
        # Pad command name to align descriptions
        cmd_padded = f"{cmd:<25}"
        console.print(f" [cyan]{cmd_padded}[/] {desc}")
    
    console.print()
    
    # Display FVM commands (Working)
    console.print("[bold yellow]FVM Commands:[/] [green]✓ Working[/]")
    for cmd, desc in FVM_COMMANDS.items():
        cmd_padded = f"{cmd:<25}"
        console.print(f" [cyan]{cmd_padded}[/] {desc}")
    
    console.print()
    
    # Display Flutter commands (Partial Support)
    console.print("[bold yellow]Flutter Commands:[/] [yellow]⚠ Partial Support[/]")
    console.print(f" [cyan]{'flutter upgrade':<25}[/] Upgrade Flutter to latest version [green]✓[/]")
    console.print(f" [dim cyan]{'  --force':<25} Force upgrade even if already up to date[/]")
    console.print(f" [dim cyan]{'  --verify-only':<25} Check for updates without upgrading[/]")
    console.print(f" [dim cyan]{'  --help':<25} Show flutter upgrade help[/]")
    console.print(f" [dim]{'flutter --version':<25} Show Flutter version (Coming Soon)[/]")
    console.print(f" [dim]{'flutter doctor':<25} Check Flutter installation (Coming Soon)[/]")
    console.print(f" [dim yellow]Note: Only 'flutter upgrade' is currently implemented[/]")
    
    console.print()
    console.print("[dim]Tip: Type / to see slash commands | Use arrow keys for history[/]\n")
