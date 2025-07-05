"""
FlutterCraft Core Application

This module contains the main FlutterCraftApp class that orchestrates the CLI,
manages commands, handles the interactive shell, and integrates all components.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.align import Align
from rich.status import Status
from rich.live import Live
from rich.columns import Columns
from rich.box import ROUNDED, DOUBLE
from rich.text import Text
from rich.markdown import Markdown
from rich.rule import Rule

try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False

from fluttercraft import __version__
from fluttercraft.cli.themes.manager import ThemeManager, ThemeError
from fluttercraft.config.settings import ConfigManager, ConfigurationError
from fluttercraft.utils.console import (
    print_banner, print_success, print_error, print_info, print_warning
)
from fluttercraft.utils.platform import get_platform_info, format_path_for_display
from fluttercraft.utils.validators import ValidationError


class FlutterCraftApp:
    """
    Main FlutterCraft application class.
    
    Orchestrates the CLI interface, manages commands, handles the interactive
    shell, and integrates theming and configuration systems.
    """
    
    def __init__(self, console: Console, config_manager: ConfigManager):
        """
        Initialize FlutterCraft application.
        
        Args:
            console: Rich console instance
            config_manager: Configuration manager
        """
        self.console = console
        self.config_manager = config_manager
        self.logger = logging.getLogger("fluttercraft.core")
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(console, config_manager)
        
        # Create Typer app for command handling
        self.app = typer.Typer(
            name="fluttercraft",
            help="Automate your Flutter app setup like a pro 🛠️🚀",
            rich_markup_mode="rich",
            add_completion=True,
        )
        
        # Interactive shell state
        self.shell_history: List[str] = []
        self.shell_context: Dict[str, Any] = {}
        
        # Setup logging level based on config
        log_level = self.config_manager.get("advanced.log_level", "INFO")
        logging.getLogger("fluttercraft").setLevel(getattr(logging, log_level))
    
    async def start_interactive(self) -> None:
        """Start the interactive shell mode."""
        import os
        import subprocess
        from pathlib import Path
        from fluttercraft.cli.ui import display_full_interface, display_status_bar
        
        try:
            # Clear screen for a fresh start
            self.console.clear()
            
            # Show welcome screen
            self.show_welcome()
            
            # Get current directory for display
            current_dir = Path(os.getcwd())
            
            # Get git branch if available
            git_branch = None
            try:
                result = subprocess.run(
                    ["git", "branch", "--show-current"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                if result.returncode == 0:
                    git_branch = result.stdout.strip()
            except Exception:
                pass
            
            # Show status bar at the bottom with git branch if available
            display_status_bar(self.console, current_dir, branch=git_branch)
            
            # Check if first run
            if self.config_manager.is_first_run():
                await self.onboarding_flow()
            
            # Start main interaction loop
            await self.interaction_loop()
            
        except KeyboardInterrupt:
            self.show_goodbye()
        except Exception as e:
            self.handle_error(e, "interactive shell")
        finally:
            self.cleanup()
    
    def show_welcome(self) -> None:
        """Display themed welcome message with ASCII logo."""
        from fluttercraft.cli.ui import display_welcome_screen
        
        # Use the UI component to display the welcome screen with ASCII logo
        display_welcome_screen(self.console)
    
    async def onboarding_flow(self) -> None:
        """First-time setup flow inspired by GEMINI CLI."""
        self.console.print(
            Panel(
                "[bold]Welcome to FlutterCraft! 🎉[/bold]\n\n"
                "This looks like your first time using FlutterCraft.\n"
                "Let's get you set up with a personalized experience.",
                title="First Time Setup",
                border_style="green",
                padding=(1, 2)
            )
        )
        
        # Theme selection
        await self.theme_selection()
        
        # Environment check
        await self.environment_check()
        
        # Mark first run complete
        self.config_manager.set_first_run_complete()
        
        # Ready to go
        self.console.print(
            Panel(
                "[bold green]✅ Setup complete![/bold green]\n\n"
                "You're all set to start using FlutterCraft.\n"
                "Type [bold]help[/bold] to see what you can do!",
                title="Ready to Go",
                border_style="green",
                padding=(1, 2)
            )
        )
        self.console.print()
    
    async def theme_selection(self) -> None:
        """Interactive theme selection."""
        self.console.print("\n[bold]🎨 Let's choose your theme![/bold]\n")
        
        # Show available themes
        themes = self.theme_manager.list_themes()
        
        theme_table = Table(title="Available Themes")
        theme_table.add_column("Name", style="cyan", no_wrap=True)
        theme_table.add_column("Description", style="white")
        theme_table.add_column("Colors", style="magenta", no_wrap=True)
        theme_table.add_column("Type", style="yellow", no_wrap=True)
        
        for theme in themes:
            colors = theme["colors"]
            color_preview = (
                f"[{colors['primary']}]●[/] "
                f"[{colors['secondary']}]●[/] "
                f"[{colors['accent']}]●[/]"
            )
            
            theme_type = "GEMINI" if theme["is_gemini"] else "Standard"
            
            theme_table.add_row(
                theme["name"],
                theme["description"],
                color_preview,
                theme_type
            )
        
        self.console.print(theme_table)
        
        # Get user choice
        theme_choices = [theme["id"] for theme in themes]
        current_theme = self.theme_manager.current_theme.name
        
        theme_choice = Prompt.ask(
            "\n[bold]Which theme would you like to use?[/bold]",
            choices=theme_choices,
            default=current_theme
        )
        
        # Apply theme
        if theme_choice != current_theme:
            try:
                self.theme_manager.set_theme(theme_choice)
                selected_theme = next(t for t in themes if t["id"] == theme_choice)
                print_success(self.console, f"Applied theme '{selected_theme['name']}'!")
            except ThemeError as e:
                print_error(self.console, f"Failed to apply theme: {e.message}")
    
    async def environment_check(self) -> None:
        """Check development environment."""
        self.console.print("\n[bold]🔍 Checking your development environment...[/bold]\n")
        
        with Status("Scanning environment...", console=self.console) as status:
            await asyncio.sleep(1)  # Simulate environment check
            
            # Get platform info
            platform_info = get_platform_info()
            
            status.update("Checking system compatibility...")
            await asyncio.sleep(0.5)
            
            # Check for Flutter
            status.update("Looking for Flutter installation...")
            await asyncio.sleep(0.5)
            
            # Check for FVM
            status.update("Checking for FVM...")
            await asyncio.sleep(0.5)
        
        # Show environment summary
        env_table = Table(title="Environment Summary")
        env_table.add_column("Component", style="cyan")
        env_table.add_column("Status", style="white")
        env_table.add_column("Details", style="dim")
        
        env_table.add_row(
            "Operating System",
            f"[green]✅[/green] {platform_info['system']}",
            f"{platform_info['architecture']}"
        )
        
        env_table.add_row(
            "Python",
            f"[green]✅[/green] {platform_info['python_version']}",
            "Compatible"
        )
        
        env_table.add_row(
            "FlutterCraft Config",
            "[green]✅[/green] Ready",
            format_path_for_display(self.config_manager.config_dir)
        )
        
        # Placeholder for future Flutter/FVM detection
        env_table.add_row(
            "Flutter SDK",
            "[yellow]❓[/yellow] Not checked",
            "Use 'flutter setup' to install"
        )
        
        env_table.add_row(
            "FVM",
            "[yellow]❓[/yellow] Not checked", 
            "Use 'fvm setup' to install"
        )
        
        self.console.print(env_table)
        self.console.print()
    
    async def interaction_loop(self) -> None:
        """Main interaction loop for the shell."""
        import os
        import subprocess
        from pathlib import Path
        from fluttercraft.cli.ui import display_status_bar
        
        while True:
            try:
                # Get current directory and git branch info
                current_dir = Path(os.getcwd())
                
                # Try to get git branch if available
                branch = None
                try:
                    result = subprocess.run(
                        ["git", "branch", "--show-current"], 
                        capture_output=True, 
                        text=True, 
                        check=False
                    )
                    if result.returncode == 0:
                        branch = result.stdout.strip()
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass
                
                # Get user input with themed prompt
                user_input = self.get_user_input()
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye'] or user_input == "/exit":
                    self.show_goodbye()
                    break
                
                # Add to history
                if user_input.strip():
                    self.shell_history.append(user_input)
                
                # Process input
                response = await self.process_input(user_input)
                
                # Display response
                if response:
                    self.console.print(response)
                    self.console.print()
                
                # Display status bar after processing
                display_status_bar(self.console, current_dir, branch)
                
            except KeyboardInterrupt:
                if Confirm.ask("\n[yellow]Do you want to exit FlutterCraft?[/yellow]"):
                    self.show_goodbye()
                    break
                else:
                    print_info(self.console, "Continuing...")
            except EOFError:
                # Handle EOF gracefully (e.g., when input is piped in)
                self.show_goodbye()
                break
            except Exception as e:
                self.handle_error(e, "processing input")
    
    def get_user_input(self) -> str:
        """Get user input with themed prompt."""
        from fluttercraft.cli.ui import create_prompt_box
        import os
        from pathlib import Path
        
        # Get current directory for display in the status bar
        current_dir = Path(os.getcwd())
        
        # Use the GEMINI-style prompt box
        return create_prompt_box(self.console, prompt_message=">")
    
    async def process_input(self, user_input: str) -> Optional[str]:
        """
        Process user input and return response.
        
        Args:
            user_input: User's input string
            
        Returns:
            Response string or None
        """
        user_input = user_input.strip()
        
        if not user_input:
            return None
        
        # Check for command mode (starts with /)
        if user_input.startswith('/'):
            return await self.execute_command(user_input[1:])
        
        # Handle natural language mode
        return await self.handle_natural_input(user_input)
    
    async def execute_command(self, command_str: str) -> str:
        """Execute a specific command."""
        parts = command_str.split()
        if not parts:
            return "No command specified."
        
        command_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle built-in commands
        if command_name == "help":
            return self.get_help_text()
        elif command_name == "theme":
            return await self.handle_theme_command(args)
        elif command_name == "config":
            return await self.handle_config_command(args)
        elif command_name == "info":
            return self.get_info_text()
        else:
            return f"Unknown command: {command_name}. Type '/help' for available commands."
    
    async def handle_natural_input(self, text: str) -> str:
        """Handle natural language input (simplified for v0.1.2)."""
        text_lower = text.lower()
        
        # Simple keyword matching for common requests
        if any(word in text_lower for word in ['help', 'what can', 'what do', 'commands']):
            return self.get_help_text()
        elif any(word in text_lower for word in ['theme', 'color', 'appearance', 'style']):
            return (
                "🎨 You can customize the appearance using themes!\n\n"
                "Try these commands:\n"
                "• [bold]/theme list[/bold] - Show available themes\n"
                "• [bold]/theme set <name>[/bold] - Apply a theme\n"
                "• [bold]/theme info[/bold] - Show current theme info"
            )
        elif any(word in text_lower for word in ['flutter', 'setup', 'install']):
            return (
                "🛠️ Flutter setup commands will be available soon!\n\n"
                "Coming in the next milestone:\n"
                "• [bold]/flutter setup[/bold] - Install Flutter SDK\n"
                "• [bold]/flutter doctor[/bold] - Check Flutter installation\n"
                "• [bold]/flutter config[/bold] - Configure Flutter settings"
            )
        elif any(word in text_lower for word in ['fvm', 'version', 'manager']):
            return (
                "📦 FVM (Flutter Version Manager) commands will be available soon!\n\n"
                "Coming in the next milestone:\n"
                "• [bold]/fvm setup[/bold] - Install FVM\n"
                "• [bold]/fvm list[/bold] - List installed versions\n"
                "• [bold]/fvm install <version>[/bold] - Install Flutter version"
            )
        elif any(word in text_lower for word in ['config', 'configuration', 'settings']):
            return (
                "⚙️ Configuration management:\n\n"
                "• [bold]/config show[/bold] - Show current configuration\n"
                "• [bold]/config set <key> <value>[/bold] - Set config value\n"
                "• [bold]/config reset[/bold] - Reset to defaults"
            )
        else:
            return (
                f"💬 I heard you say: '{text}'\n\n"
                "I'm still learning to understand natural language! "
                "For now, try using these commands:\n"
                "• [bold]/help[/bold] - Show available commands\n"
                "• [bold]/theme list[/bold] - Show themes\n"
                "• [bold]/info[/bold] - Show system information\n\n"
                "You can also start commands with [bold]/[/bold] for direct execution."
            )
    
    async def handle_theme_command(self, args: List[str]) -> str:
        """Handle theme-related commands."""
        if not args or args[0] == "list":
            return self.format_theme_list()
        elif args[0] == "set" and len(args) > 1:
            return await self.set_theme(args[1])
        elif args[0] == "info":
            return self.get_theme_info()
        elif args[0] == "preview" and len(args) > 1:
            return self.preview_theme(args[1])
        else:
            return (
                "Theme command usage:\n"
                "• [bold]/theme list[/bold] - Show available themes\n"
                "• [bold]/theme set <name>[/bold] - Apply a theme\n"
                "• [bold]/theme preview <name>[/bold] - Preview a theme\n"
                "• [bold]/theme info[/bold] - Show current theme info"
            )
    
    async def handle_config_command(self, args: List[str]) -> str:
        """Handle configuration commands."""
        if not args or args[0] == "show":
            return self.format_config_info()
        elif args[0] == "set" and len(args) >= 3:
            key, value = args[1], args[2]
            try:
                # Simple type conversion
                if value.lower() in ['true', 'false']:
                    typed_value = value.lower() == 'true'
                elif value.isdigit():
                    typed_value = int(value)
                else:
                    typed_value = value
                
                self.config_manager.set(key, typed_value)
                return f"✅ Set config '{key}' = {value}"
            except Exception as e:
                return f"❌ Failed to set config: {str(e)}"
        elif args[0] == "reset":
            try:
                self.config_manager.reset_to_defaults()
                return "✅ Configuration reset to defaults"
            except Exception as e:
                return f"❌ Failed to reset config: {str(e)}"
        else:
            return (
                "Config command usage:\n"
                "• [bold]/config show[/bold] - Show current configuration\n"
                "• [bold]/config set <key> <value>[/bold] - Set config value\n"
                "• [bold]/config reset[/bold] - Reset to defaults"
            )
    
    def format_theme_list(self) -> str:
        """Format the list of available themes."""
        themes = self.theme_manager.list_themes()
        current_theme = self.theme_manager.current_theme.name
        
        output = "[bold]🎨 Available Themes:[/bold]\n\n"
        
        # Group themes
        gemini_themes = [t for t in themes if t["is_gemini"]]
        other_themes = [t for t in themes if not t["is_gemini"]]
        
        if gemini_themes:
            output += "[bold cyan]GEMINI-Inspired Themes:[/bold cyan]\n"
            for theme in gemini_themes:
                colors = theme["colors"]
                preview = f"[{colors['primary']}]●[/] [{colors['secondary']}]●[/] [{colors['accent']}]●[/]"
                current = "⭐ " if theme["id"] == current_theme else "  "
                output += f"{current}[bold]{theme['name']}[/bold] - {theme['description']} {preview}\n"
            output += "\n"
        
        if other_themes:
            output += "[bold magenta]Other Themes:[/bold magenta]\n"
            for theme in other_themes:
                colors = theme["colors"]
                preview = f"[{colors['primary']}]●[/] [{colors['secondary']}]●[/] [{colors['accent']}]●[/]"
                current = "⭐ " if theme["id"] == current_theme else "  "
                output += f"{current}[bold]{theme['name']}[/bold] - {theme['description']} {preview}\n"
        
        output += f"\nUse [bold]/theme set <name>[/bold] to apply a theme."
        return output
    
    async def set_theme(self, theme_name: str) -> str:
        """Set the active theme."""
        try:
            # Validate theme exists
            available_themes = self.theme_manager.available_themes
            
            # Allow partial matching
            matches = [t for t in available_themes if theme_name.lower() in t.lower()]
            
            if not matches:
                return (
                    f"❌ Theme '{theme_name}' not found.\n\n"
                    f"Available themes: {', '.join(available_themes)}"
                )
            elif len(matches) > 1:
                return (
                    f"❓ Multiple themes match '{theme_name}':\n"
                    f"{', '.join(matches)}\n\n"
                    "Please be more specific."
                )
            
            # Apply theme
            exact_name = matches[0]
            self.theme_manager.set_theme(exact_name)
            
            theme_info = self.theme_manager.preview_theme(exact_name)
            return f"✅ Applied theme '[bold]{theme_info['name']}[/bold]'!"
            
        except ThemeError as e:
            return f"❌ Failed to apply theme: {e.message}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    def preview_theme(self, theme_name: str) -> str:
        """Preview a theme without applying it."""
        try:
            theme_info = self.theme_manager.preview_theme(theme_name)
            colors = theme_info["colors"]
            
            preview = (
                f"🎨 [bold]{theme_info['name']}[/bold]\n"
                f"   {theme_info['description']}\n\n"
                f"   Colors: "
                f"[{colors['primary']}]Primary[/] "
                f"[{colors['secondary']}]Secondary[/] "
                f"[{colors['accent']}]Accent[/] "
                f"[{colors['success']}]Success[/] "
                f"[{colors['warning']}]Warning[/] "
                f"[{colors['error']}]Error[/]\n"
                f"   Spinner: {theme_info['spinner']}\n"
                f"   Author: {theme_info.get('author', 'Unknown')}\n\n"
                f"Use [bold]/theme set {theme_name}[/bold] to apply this theme."
            )
            
            return preview
            
        except ThemeError as e:
            return f"❌ Failed to preview theme: {e.message}"
    
    def get_theme_info(self) -> str:
        """Get current theme information."""
        theme = self.theme_manager.current_theme
        colors = theme.preview_colors()
        
        return (
            f"🎨 [bold]Current Theme: {theme.display_name}[/bold]\n"
            f"   {theme.description}\n\n"
            f"   Colors: "
            f"[{colors['primary']}]Primary[/] "
            f"[{colors['secondary']}]Secondary[/] "
            f"[{colors['accent']}]Accent[/] "
            f"[{colors['success']}]Success[/] "
            f"[{colors['warning']}]Warning[/] "
            f"[{colors['error']}]Error[/]\n"
            f"   Author: {theme.author}\n"
            f"   Version: {theme.version}\n"
            f"   Spinner: {theme.spinner}"
        )
    
    def format_config_info(self) -> str:
        """Format configuration information."""
        config_info = self.config_manager.get_config_info()
        theme_info = self.theme_manager.get_theme_info()
        
        return (
            f"⚙️ [bold]FlutterCraft Configuration[/bold]\n\n"
            f"   Config Directory: {format_path_for_display(Path(config_info['config_dir']))}\n"
            f"   Current Theme: {theme_info['current_theme_display']}\n"
            f"   Total Themes: {theme_info['total_themes']}\n"
            f"   First Run: {'Yes' if config_info['first_run'] else 'No'}\n\n"
            f"Use [bold]/config set <key> <value>[/bold] to modify settings."
        )
    
    def get_help_text(self) -> str:
        """Get help text for available commands."""
        return (
            "[bold]📚 FlutterCraft Commands[/bold]\n\n"
            "[bold cyan]Theme Commands:[/bold cyan]\n"
            "  [bold]/theme list[/bold]           - Show available themes\n"
            "  [bold]/theme set <name>[/bold]     - Apply a theme\n"
            "  [bold]/theme preview <name>[/bold] - Preview a theme\n"
            "  [bold]/theme info[/bold]           - Show current theme info\n\n"
            "[bold yellow]Configuration:[/bold yellow]\n"
            "  [bold]/config show[/bold]          - Show current configuration\n"
            "  [bold]/config set <key> <value>[/bold] - Set config value\n"
            "  [bold]/config reset[/bold]         - Reset to defaults\n\n"
            "[bold green]Information:[/bold green]\n"
            "  [bold]/info[/bold]                 - Show system information\n"
            "  [bold]/help[/bold]                 - Show this help message\n\n"
            "[bold red]Exit:[/bold red]\n"
            "  [bold]exit[/bold], [bold]quit[/bold], [bold]bye[/bold] - Exit FlutterCraft\n\n"
            "[dim]💡 Coming soon: Flutter and FVM commands![/dim]"
        )
    
    def get_info_text(self) -> str:
        """Get system information."""
        platform_info = get_platform_info()
        config_info = self.config_manager.get_config_info()
        theme_info = self.theme_manager.get_theme_info()
        
        return (
            f"[bold]ℹ️ FlutterCraft Information[/bold]\n\n"
            f"[bold cyan]Application:[/bold cyan]\n"
            f"  Version: {__version__}\n"
            f"  Platform: {platform_info['system']} {platform_info['machine']}\n"
            f"  Python: {platform_info['python_version']}\n\n"
            f"[bold magenta]Configuration:[/bold magenta]\n"
            f"  Config Directory: {format_path_for_display(Path(config_info['config_dir']))}\n"
            f"  Current Theme: {theme_info['current_theme_display']}\n"
            f"  Available Themes: {theme_info['total_themes']}\n\n"
            f"[bold green]Shell:[/bold green]\n"
            f"  History Entries: {len(self.shell_history)}\n"
            f"  Interactive Mode: Active"
        )
    
    def show_goodbye(self) -> None:
        """Display goodbye message."""
        from fluttercraft.cli.themes.ascii_art import get_appropriate_logo
        from fluttercraft.utils.platform import get_terminal_size
        from rich.panel import Panel
        from rich.text import Text
        from rich.align import Align
        
        # Get terminal width
        width, _ = get_terminal_size()
        
        # Get appropriate logo for the goodbye message based on terminal width
        logo_size = "small" if width < 60 else "minimal"
        logo = get_appropriate_logo(logo_size)
        
        # Style the logo with the theme color
        primary_color = self.theme_manager.current_theme.get_style("success") or "green"
        styled_logo = Text(logo, style=primary_color)
        
        # Create farewell message
        farewell_message = (
            "\n[bold]Thanks for using FlutterCraft! Have a great day! 👋[/bold]\n"
            "[dim]Run [bold]fluttercraft[/bold] anytime to return[/dim]"
        )
        
        # Create a panel with the logo and farewell message
        # Combine the logo and farewell message
        combined_content = styled_logo.copy()
        combined_content.append("\n")
        combined_content.append(farewell_message)
        
        goodbye_panel = Panel(
            Align.center(combined_content),
            border_style=self.theme_manager.current_theme.get_style("success") or "green",
            padding=(1, 2)
        )
        
        # Clear screen and display goodbye panel
        self.console.clear()
        self.console.print(goodbye_panel)
        self.console.print()
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """Handle errors with user-friendly messages."""
        error_msg = f"An error occurred"
        if context:
            error_msg += f" while {context}"
        
        if isinstance(error, (ConfigurationError, ThemeError, ValidationError)):
            error_content = f"[bold]{error.message}[/bold]"
            if hasattr(error, 'suggestions') and error.suggestions:
                error_content += "\n\n💡 Suggestions:\n"
                error_content += "\n".join(f"• {suggestion}" for suggestion in error.suggestions)
        else:
            error_content = f"[bold]{error_msg}[/bold]\n\n{str(error)}"
        
        error_panel = Panel(
            error_content,
            title="❌ Error",
            border_style=self.theme_manager.current_theme.get_style("error") or "red",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(error_panel)
        self.console.print()
        
        # Log error for debugging
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=error)
    
    def setup_commands(self) -> None:
        """Setup Typer commands for non-interactive mode."""
        # This will be extended in future milestones
        pass
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.theme_manager.cleanup()
            self.config_manager.cleanup()
            self.logger.debug("FlutterCraft cleanup completed")
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore cleanup errors during destruction
