# FlutterCraft v0.1.2 - Technical Reference

## GEMINI CLI Analysis & Insights

Based on the analysis of the official Google GEMINI CLI repository, here are the key insights for FlutterCraft v0.1.2:

### GEMINI CLI Key Features
- **Interactive AI workflow tool** that connects to tools and understands code
- **Node.js/TypeScript based** but we'll adapt concepts to Python
- **Theme selection** during initial setup ("Pick a color theme")
- **Authentication flow** (we won't have AI, but will have interactive setup)
- **Status messages** with spinners and progress indicators
- **Graceful error handling** with suggestions
- **Cross-platform support** (Windows, Linux, macOS)

### User Experience Patterns from GEMINI CLI
1. **Onboarding Flow**: Welcome → Theme Selection → Authentication → Ready to use
2. **Interactive Prompts**: Natural language style questions
3. **Visual Feedback**: Rich status indicators, spinners, progress bars
4. **Context Awareness**: Commands understand current state and provide relevant help
5. **Graceful Degradation**: Fallbacks when features aren't available

## Framework Implementation Details

### Typer + Rich Integration
```python
# Core integration pattern for FlutterCraft
import typer
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from rich.status import Status

class FlutterCraftApp:
    """Main application class integrating Typer and Rich."""
    
    def __init__(self):
        self.app = typer.Typer(
            name="fluttercraft",
            help="Automate your Flutter app setup like a pro 🛠️🚀",
            rich_markup_mode="rich",  # Enable Rich markup in help
            no_args_is_help=True,     # Show help when no args provided
        )
        self.console = Console()
        self.theme_manager = ThemeManager(self.console)
        
    def setup_commands(self):
        """Register all commands with the Typer app."""
        # Theme commands
        self.app.command("theme")(self.theme_command)
        self.app.command("start")(self.start_interactive)
        
        # FVM commands
        fvm_app = typer.Typer(name="fvm", help="Flutter Version Manager commands")
        fvm_app.command("setup")(self.fvm_setup)
        fvm_app.command("list")(self.fvm_list)
        self.app.add_typer(fvm_app, name="fvm")
        
        # Flutter commands
        flutter_app = typer.Typer(name="flutter", help="Flutter SDK commands")
        flutter_app.command("setup")(self.flutter_setup)
        flutter_app.command("doctor")(self.flutter_doctor)
        self.app.add_typer(flutter_app, name="flutter")
```

### Rich Theme System Implementation
```python
# Theme system based on Rich's theming capabilities
from rich.theme import Theme
from rich.style import Style
from typing import Dict, Any
import json
from pathlib import Path

class FlutterCraftTheme:
    """Custom theme class extending Rich's Theme functionality."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        
        # Create Rich theme from config
        self.rich_theme = Theme({
            "primary": config.get("primary", "blue"),
            "secondary": config.get("secondary", "cyan"),
            "accent": config.get("accent", "magenta"),
            "success": config.get("success", "green"),
            "warning": config.get("warning", "yellow"),
            "error": config.get("error", "red"),
            "info": config.get("info", "blue"),
            "muted": config.get("muted", "dim white"),
            
            # Component styles
            "panel.border": config.get("panel_border", "blue"),
            "panel.title": config.get("panel_title", "bold blue"),
            "table.header": config.get("table_header", "bold magenta"),
            "button": config.get("button", "bold white on blue"),
            "input": config.get("input", "cyan"),
            
            # Status styles
            "status.working": config.get("status_working", "yellow"),
            "status.success": config.get("status_success", "green"),
            "status.error": config.get("status_error", "red"),
        })
    
    @property
    def spinner(self) -> str:
        """Get spinner style for this theme."""
        return self.config.get("spinner", "dots")
    
    @classmethod
    def from_file(cls, theme_file: Path) -> "FlutterCraftTheme":
        """Load theme from JSON file."""
        with open(theme_file, 'r') as f:
            config = json.load(f)
        return cls(theme_file.stem, config)

# GEMINI-inspired theme definitions
GEMINI_THEMES = {
    "gemini-classic": {
        "name": "Gemini Classic",
        "description": "Professional blue theme inspired by Google's design",
        "primary": "#1a73e8",
        "secondary": "#34a853",
        "accent": "#fbbc04",
        "success": "#34a853",
        "warning": "#ff9800",
        "error": "#ea4335",
        "info": "#1a73e8",
        "background": "#ffffff",
        "surface": "#f8f9fa",
        "panel_border": "blue",
        "panel_title": "bold blue",
        "table_header": "bold blue",
        "spinner": "dots"
    },
    
    "gemini-dark": {
        "name": "Gemini Dark",
        "description": "Dark theme with bright accents",
        "primary": "#4285f4",
        "secondary": "#0f9d58",
        "accent": "#f4b400",
        "success": "#0f9d58",
        "warning": "#ff6d01",
        "error": "#d93025",
        "info": "#4285f4",
        "background": "#121212",
        "surface": "#1e1e1e",
        "panel_border": "bright_blue",
        "panel_title": "bold bright_blue",
        "table_header": "bold bright_blue",
        "spinner": "arc"
    },
    
    "gemini-neon": {
        "name": "Gemini Neon",
        "description": "Cyberpunk-inspired vibrant theme",
        "primary": "#00ffff",
        "secondary": "#ff00ff",
        "accent": "#ffff00",
        "success": "#00ff00",
        "warning": "#ff8c00",
        "error": "#ff0040",
        "info": "#00bfff",
        "background": "#0a0a0a",
        "surface": "#1a1a2e",
        "panel_border": "bright_cyan",
        "panel_title": "bold bright_cyan",
        "table_header": "bold bright_magenta",
        "spinner": "monkey"
    }
}
```

### Interactive Shell Implementation
```python
# Chat-like interactive shell inspired by GEMINI CLI
import asyncio
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

class InteractiveShell:
    """GEMINI CLI-inspired interactive shell."""
    
    def __init__(self, console: Console, theme_manager: ThemeManager):
        self.console = console
        self.theme_manager = theme_manager
        self.commands = CommandRegistry()
        self.history = []
        self.context = {}
        
    async def start(self):
        """Start the interactive shell session."""
        self.show_welcome()
        
        # Initial setup if first time
        if self.is_first_run():
            await self.onboarding_flow()
        
        # Main interaction loop
        while True:
            try:
                user_input = self.get_user_input()
                
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    self.show_goodbye()
                    break
                
                response = await self.process_input(user_input)
                self.display_response(response)
                
            except KeyboardInterrupt:
                if Confirm.ask("\n[yellow]Do you want to exit FlutterCraft?[/yellow]"):
                    break
                else:
                    self.console.print("[green]Continuing...[/green]")
            except Exception as e:
                self.handle_error(e)
    
    def show_welcome(self):
        """Display themed welcome message."""
        logo = """
╭─────────────────────────────────────────╮
│  ███████╗██╗     ██╗   ██╗████████╗    │
│  ██╔════╝██║     ██║   ██║╚══██╔══╝    │
│  █████╗  ██║     ██║   ██║   ██║       │
│  ██╔══╝  ██║     ██║   ██║   ██║       │
│  ██║     ███████╗╚██████╔╝   ██║       │
│  ╚═╝     ╚══════╝ ╚═════╝    ╚═╝       │
│                                         │
│         FlutterCraft v0.1.2             │
│    🛠️ Your Flutter Development         │
│         Companion 🚀                   │
╰─────────────────────────────────────────╯
        """
        
        welcome_panel = Panel(
            logo,
            title="Welcome",
            border_style=self.theme_manager.current_theme.rich_theme.styles["primary"],
            padding=(1, 2)
        )
        
        self.console.print(welcome_panel)
        self.console.print()
        self.console.print(
            "[dim]Type [bold]help[/bold] for available commands, "
            "[bold]theme[/bold] to customize appearance, or just start chatting![/dim]"
        )
        self.console.print()
    
    async def onboarding_flow(self):
        """First-time setup flow inspired by GEMINI CLI."""
        self.console.print(
            Panel(
                "[bold]Welcome to FlutterCraft! 🎉[/bold]\n\n"
                "Let's get you set up with a personalized experience.",
                title="First Time Setup",
                border_style="green"
            )
        )
        
        # Theme selection
        await self.theme_selection()
        
        # Environment check
        await self.environment_check()
        
        # Ready to go
        self.console.print(
            Panel(
                "[bold green]✅ Setup complete![/bold green]\n\n"
                "You're all set to start using FlutterCraft. "
                "Type [bold]help[/bold] to see what you can do!",
                title="Ready to Go",
                border_style="green"
            )
        )
    
    async def theme_selection(self):
        """Interactive theme selection."""
        self.console.print("\n[bold]🎨 Let's choose your theme![/bold]\n")
        
        # Show available themes
        theme_table = Table(title="Available Themes")
        theme_table.add_column("Name", style="cyan")
        theme_table.add_column("Description", style="white")
        theme_table.add_column("Style", style="magenta")
        
        for theme_name, theme_config in GEMINI_THEMES.items():
            theme_table.add_row(
                theme_config["name"],
                theme_config["description"],
                f"[{theme_config['primary']}]●[/] [{theme_config['secondary']}]●[/] [{theme_config['accent']}]●[/]"
            )
        
        self.console.print(theme_table)
        
        # Get user choice
        theme_choices = list(GEMINI_THEMES.keys())
        theme_choice = Prompt.ask(
            "\n[bold]Which theme would you like to use?[/bold]",
            choices=theme_choices,
            default="gemini-classic"
        )
        
        # Apply theme
        self.theme_manager.set_theme(theme_choice)
        self.console.print(f"\n[green]✅ Theme '{GEMINI_THEMES[theme_choice]['name']}' applied![/green]")
    
    def get_user_input(self) -> str:
        """Get user input with themed prompt."""
        theme = self.theme_manager.current_theme
        prompt_style = theme.rich_theme.styles.get("primary", "blue")
        
        return Prompt.ask(
            f"[{prompt_style}]fluttercraft[/] [dim]›[/dim]",
            console=self.console
        )
    
    async def process_input(self, user_input: str) -> str:
        """Process user input and return response."""
        # Add to history
        self.history.append(user_input)
        
        # Parse input
        if user_input.startswith('/'):
            # Command mode
            return await self.execute_command(user_input[1:])
        else:
            # Natural language mode (for now, just echo)
            return await self.handle_natural_input(user_input)
    
    async def execute_command(self, command_str: str) -> str:
        """Execute a specific command."""
        parts = command_str.split()
        if not parts:
            return "No command specified."
        
        command_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        command = self.commands.get_command(command_name)
        if not command:
            return f"Unknown command: {command_name}. Type 'help' for available commands."
        
        try:
            with self.console.status(f"[yellow]Executing {command_name}...[/yellow]"):
                result = await command.execute({"args": args})
            return f"Command '{command_name}' completed successfully." if result else f"Command '{command_name}' failed."
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    async def handle_natural_input(self, text: str) -> str:
        """Handle natural language input (simplified for v0.1.2)."""
        # Simple keyword matching for common requests
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['help', 'what can', 'what do']):
            return self.get_help_text()
        elif any(word in text_lower for word in ['theme', 'color', 'appearance']):
            return "You can change themes using the 'theme' command. Type '/theme list' to see available themes."
        elif any(word in text_lower for word in ['flutter', 'setup', 'install']):
            return "I can help you set up Flutter! Try '/flutter setup' to get started."
        elif any(word in text_lower for word in ['fvm', 'version']):
            return "I can help with Flutter Version Manager! Try '/fvm list' to see installed versions."
        else:
            return (
                f"I heard you say: '{text}'\n\n"
                "I'm still learning to understand natural language. "
                "For now, try using commands like:\n"
                "• /help - Show available commands\n"
                "• /theme list - Show available themes\n"
                "• /flutter setup - Set up Flutter\n"
                "• /fvm list - List Flutter versions"
            )
```

### Command System Architecture
```python
# Modular command system
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import asyncio

class BaseCommand(ABC):
    """Base class for all FlutterCraft commands."""
    
    def __init__(self, console: Console, theme_manager: ThemeManager):
        self.console = console
        self.theme_manager = theme_manager
    
    @abstractmethod
    async def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the command with given arguments."""
        pass
    
    @abstractmethod
    def get_help(self) -> str:
        """Return help text for the command."""
        pass
    
    @abstractmethod
    def get_short_description(self) -> str:
        """Return short description for command listing."""
        pass
    
    def validate_prerequisites(self) -> bool:
        """Validate command prerequisites."""
        return True
    
    def show_progress(self, message: str, spinner: str = None):
        """Show progress with themed spinner."""
        if spinner is None:
            spinner = self.theme_manager.current_theme.spinner
        
        return self.console.status(
            f"[{self.theme_manager.current_theme.rich_theme.styles['primary']}]{message}[/]",
            spinner=spinner
        )
    
    def show_success(self, message: str):
        """Show success message."""
        self.console.print(
            f"[{self.theme_manager.current_theme.rich_theme.styles['success']}]✅ {message}[/]"
        )
    
    def show_error(self, message: str, suggestions: List[str] = None):
        """Show error message with suggestions."""
        error_content = f"[bold]{message}[/bold]"
        
        if suggestions:
            error_content += "\n\n💡 Suggestions:\n"
            error_content += "\n".join(f"• {suggestion}" for suggestion in suggestions)
        
        error_panel = Panel(
            error_content,
            title="❌ Error",
            border_style=self.theme_manager.current_theme.rich_theme.styles["error"]
        )
        self.console.print(error_panel)

class ThemeCommand(BaseCommand):
    """Theme management commands."""
    
    async def execute(self, args: Dict[str, Any]) -> bool:
        """Execute theme command."""
        command_args = args.get("args", [])
        
        if not command_args or command_args[0] == "list":
            return await self.list_themes()
        elif command_args[0] == "set" and len(command_args) > 1:
            return await self.set_theme(command_args[1])
        elif command_args[0] == "preview" and len(command_args) > 1:
            return await self.preview_theme(command_args[1])
        else:
            self.show_error("Invalid theme command. Use: list, set <name>, or preview <name>")
            return False
    
    async def list_themes(self) -> bool:
        """List available themes."""
        theme_table = Table(title="Available Themes")
        theme_table.add_column("Name", style="cyan")
        theme_table.add_column("Description", style="white")
        theme_table.add_column("Preview", style="magenta")
        theme_table.add_column("Current", style="green")
        
        current_theme_name = self.theme_manager.current_theme.name
        
        for theme_name, theme_config in GEMINI_THEMES.items():
            is_current = "✅" if theme_name == current_theme_name else ""
            preview = f"[{theme_config['primary']}]●[/] [{theme_config['secondary']}]●[/] [{theme_config['accent']}]●[/]"
            
            theme_table.add_row(
                theme_config["name"],
                theme_config["description"],
                preview,
                is_current
            )
        
        self.console.print(theme_table)
        return True
    
    async def set_theme(self, theme_name: str) -> bool:
        """Set the active theme."""
        if theme_name not in GEMINI_THEMES:
            self.show_error(
                f"Theme '{theme_name}' not found.",
                ["Use 'theme list' to see available themes"]
            )
            return False
        
        with self.show_progress(f"Applying theme '{theme_name}'..."):
            await asyncio.sleep(0.5)  # Simulate theme loading
            self.theme_manager.set_theme(theme_name)
        
        self.show_success(f"Theme '{GEMINI_THEMES[theme_name]['name']}' applied!")
        return True
    
    def get_help(self) -> str:
        return """
Theme Commands:
  list              List all available themes
  set <name>        Set the active theme
  preview <name>    Preview a theme without applying

Examples:
  theme list
  theme set gemini-dark
  theme preview gemini-neon
        """.strip()
    
    def get_short_description(self) -> str:
        return "Manage and customize themes"
```

### Configuration Management
```python
# Cross-platform configuration system
import platform
import json
import toml
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigManager:
    """Cross-platform configuration management."""
    
    def __init__(self):
        self.config_dir = self._get_config_directory()
        self.config_file = self.config_dir / "fluttercraft.toml"
        self.theme_file = self.config_dir / "current_theme.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create default config
        self._config = self._load_config()
    
    def _get_config_directory(self) -> Path:
        """Get platform-appropriate configuration directory."""
        system = platform.system()
        
        if system == "Windows":
            # Use AppData/Local on Windows
            return Path.home() / "AppData" / "Local" / "FlutterCraft"
        elif system == "Darwin":  # macOS
            # Use Application Support on macOS
            return Path.home() / "Library" / "Application Support" / "FlutterCraft"
        else:  # Linux and others
            # Use XDG config directory on Linux
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            if xdg_config:
                return Path(xdg_config) / "fluttercraft"
            else:
                return Path.home() / ".config" / "fluttercraft"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                return toml.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        default_config = {
            "general": {
                "first_run": True,
                "auto_update_check": True,
                "default_theme": "gemini-classic"
            },
            "flutter": {
                "auto_doctor_check": True,
                "preferred_channel": "stable"
            },
            "fvm": {
                "auto_install": False,
                "default_version": "latest"
            }
        }
        
        # Save default config
        self.save_config(default_config)
        return default_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save configuration
        self.save_config(self._config)
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                toml.dump(config, f)
            self._config = config
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_current_theme(self) -> Optional[str]:
        """Get currently selected theme."""
        if not self.theme_file.exists():
            return None
        
        try:
            with open(self.theme_file, 'r') as f:
                theme_data = json.load(f)
            return theme_data.get("current_theme")
        except Exception:
            return None
    
    def set_current_theme(self, theme_name: str):
        """Set currently selected theme."""
        theme_data = {"current_theme": theme_name}
        
        try:
            with open(self.theme_file, 'w') as f:
                json.dump(theme_data, f, indent=2)
        except Exception as e:
            print(f"Error saving theme config: {e}")
    
    def is_first_run(self) -> bool:
        """Check if this is the first run."""
        return self.get("general.first_run", True)
    
    def set_first_run_complete(self):
        """Mark first run as complete."""
        self.set("general.first_run", False)
```

### Error Handling System
```python
# Comprehensive error handling with recovery suggestions
from typing import List, Optional
import traceback
import logging

class FlutterCraftError(Exception):
    """Base exception class for FlutterCraft."""
    
    def __init__(self, message: str, suggestions: List[str] = None, recoverable: bool = True):
        self.message = message
        self.suggestions = suggestions or []
        self.recoverable = recoverable
        super().__init__(message)

class CommandExecutionError(FlutterCraftError):
    """Raised when command execution fails."""
    pass

class ThemeError(FlutterCraftError):
    """Raised when theme operations fail."""
    pass

class ConfigurationError(FlutterCraftError):
    """Raised when configuration is invalid."""
    pass

class ValidationError(FlutterCraftError):
    """Raised when input validation fails."""
    pass

class ErrorHandler:
    """Centralized error handling with themed output."""
    
    def __init__(self, console: Console, theme_manager: ThemeManager):
        self.console = console
        self.theme_manager = theme_manager
        self.logger = logging.getLogger("fluttercraft")
    
    def handle_error(self, error: Exception, context: str = None):
        """Handle any error with appropriate user feedback."""
        if isinstance(error, FlutterCraftError):
            self._handle_fluttercraft_error(error, context)
        else:
            self._handle_unexpected_error(error, context)
    
    def _handle_fluttercraft_error(self, error: FlutterCraftError, context: str = None):
        """Handle known FlutterCraft errors."""
        error_content = f"[bold]{error.message}[/bold]"
        
        if context:
            error_content = f"[dim]Context: {context}[/dim]\n\n{error_content}"
        
        if error.suggestions:
            error_content += "\n\n💡 Suggestions:\n"
            error_content += "\n".join(f"• {suggestion}" for suggestion in error.suggestions)
        
        if error.recoverable:
            error_content += "\n\n[dim]You can try again or use 'help' for more information.[/dim]"
        
        error_panel = Panel(
            error_content,
            title="❌ Error",
            border_style=self.theme_manager.current_theme.rich_theme.styles["error"]
        )
        
        self.console.print(error_panel)
        
        # Log error for debugging
        self.logger.error(f"{type(error).__name__}: {error.message}", exc_info=error)
    
    def _handle_unexpected_error(self, error: Exception, context: str = None):
        """Handle unexpected errors."""
        error_content = f"[bold]An unexpected error occurred[/bold]"
        
        if context:
            error_content += f"\n[dim]Context: {context}[/dim]"
        
        error_content += f"\n\nError: {str(error)}"
        error_content += "\n\n💡 This might be a bug. Please consider reporting it."
        error_content += "\n\n[dim]You can continue using FlutterCraft. Type 'help' if you need assistance.[/dim]"
        
        error_panel = Panel(
            error_content,
            title="❌ Unexpected Error",
            border_style=self.theme_manager.current_theme.rich_theme.styles["error"]
        )
        
        self.console.print(error_panel)
        
        # Log full error details
        self.logger.error(f"Unexpected error in {context}: {str(error)}", exc_info=error)
```

## Performance Optimization Strategies

### 1. Lazy Loading Implementation
```python
# Lazy loading for commands and themes
from typing import TYPE_CHECKING
import importlib

if TYPE_CHECKING:
    from fluttercraft.commands.base import BaseCommand

class CommandRegistry:
    """Registry with lazy loading for commands."""
    
    def __init__(self):
        self._command_modules = {
            "theme": "fluttercraft.commands.theme",
            "fvm": "fluttercraft.commands.fvm",
            "flutter": "fluttercraft.commands.flutter",
        }
        self._loaded_commands = {}
    
    def get_command(self, name: str) -> Optional["BaseCommand"]:
        """Get command with lazy loading."""
        if name in self._loaded_commands:
            return self._loaded_commands[name]
        
        if name in self._command_modules:
            module = importlib.import_module(self._command_modules[name])
            command_class = getattr(module, f"{name.title()}Command")
            command = command_class()
            self._loaded_commands[name] = command
            return command
        
        return None
```

### 2. Configuration Caching
```python
# Efficient configuration caching
import time
from typing import Dict, Any

class CachedConfigManager(ConfigManager):
    """Configuration manager with caching."""
    
    def __init__(self):
        super().__init__()
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 300  # 5 minutes
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with caching."""
        current_time = time.time()
        
        # Check cache first
        if (key in self._cache and 
            current_time - self._cache_timestamps.get(key, 0) < self._cache_ttl):
            return self._cache[key]
        
        # Load from file
        value = super().get(key, default)
        
        # Cache the result
        self._cache[key] = value
        self._cache_timestamps[key] = current_time
        
        return value
    
    def invalidate_cache(self, key: str = None):
        """Invalidate cache for specific key or all keys."""
        if key:
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
```

## Testing Framework

### Test Implementation Example
```python
# Comprehensive testing example
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from rich.console import Console
from io import StringIO

class TestThemeCommand:
    """Test suite for theme commands."""
    
    @pytest.fixture
    def console(self):
        """Mock console for testing."""
        return Console(file=StringIO(), width=80)
    
    @pytest.fixture
    def theme_manager(self):
        """Mock theme manager."""
        mock_manager = Mock()
        mock_manager.current_theme.name = "gemini-classic"
        mock_manager.current_theme.rich_theme.styles = {
            "primary": "blue",
            "success": "green",
            "error": "red"
        }
        return mock_manager
    
    @pytest.fixture
    def theme_command(self, console, theme_manager):
        """Theme command instance for testing."""
        return ThemeCommand(console, theme_manager)
    
    @pytest.mark.asyncio
    async def test_list_themes_success(self, theme_command):
        """Test successful theme listing."""
        result = await theme_command.execute({"args": ["list"]})
        assert result is True
    
    @pytest.mark.asyncio
    async def test_set_theme_success(self, theme_command, theme_manager):
        """Test successful theme setting."""
        result = await theme_command.execute({"args": ["set", "gemini-dark"]})
        assert result is True
        theme_manager.set_theme.assert_called_once_with("gemini-dark")
    
    @pytest.mark.asyncio
    async def test_set_theme_invalid(self, theme_command):
        """Test setting invalid theme."""
        result = await theme_command.execute({"args": ["set", "nonexistent-theme"]})
        assert result is False
    
    def test_get_help(self, theme_command):
        """Test help text generation."""
        help_text = theme_command.get_help()
        assert "list" in help_text
        assert "set" in help_text
        assert "preview" in help_text
```

This technical reference provides the detailed implementation guidance needed for FlutterCraft v0.1.2, ensuring consistency with the GEMINI CLI experience while leveraging the power of Typer and Rich for Python-based development.
