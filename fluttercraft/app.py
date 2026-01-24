"""
Full-screen FlutterCraft TUI using Textual.
"""
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Input, Log
from textual.binding import Binding
from textual.widget import Widget
from textual.reactive import reactive

from fluttercraft.utils.themes.theme_manager import get_theme_manager
from fluttercraft.utils.themes.service import ThemeDisplayService
from rich.console import Console

class FlutterCraftApp(App):
    """Full-screen FlutterCraft TUI."""
    
    CSS = """
    Screen {
        background: $background;
        color: $text;
    }
    
    #header {
        dock: top;
        height: auto;
        background: $surface;
        color: $accent;
        padding: 1;
        border-bottom: solid $accent;
    }
    
    #output-container {
        height: 1fr;
        background: $background;
        border: none;
    }
    
    Log {
        background: $background;
        color: $text;
        border: none;
    }
    
    #input-area {
        dock: bottom;
        height: 3;
        background: $surface;
        border-top: solid $accent;
        padding: 0 1;
    }
    
    Input {
        background: $surface;
        color: $text;
        border: none;
        width: 100%;
    }
    
    Input:focus {
        border: none;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("f1", "toggle_theme", "Toggle Theme"),
    ]
    
    # Define reactive theme variables that match our existing theme system
    theme_background = reactive("#1E1E1E")
    theme_surface = reactive("#252526")
    theme_accent = reactive("#4EC9B0")
    theme_text = reactive("#E0E0E0")
    
    def __init__(self):
        super().__init__()
        self.theme_manager = get_theme_manager()
        self.executor = None # Will be set in on_mount
        self.context = None  # Will be set in on_mount
        
    def on_mount(self) -> None:
        """Initialize the app state."""
        self.update_theme_vars()
        
        # Initialize command system
        from fluttercraft.commands.bootstrap import build_command_system
        from fluttercraft.commands.core import CommandContext
        from fluttercraft.utils.platform_utils import get_platform_info
        from fluttercraft.commands.flutter_commands import check_flutter_version
        from fluttercraft.commands.fvm_commands import check_fvm_version
        from prompt_toolkit.history import InMemoryHistory
        
        # Use a dummy console for the executor since we'll redirect output
        self.console = Console()
        self.executor = build_command_system(self.console)
        
        # Gather info (simulate async later)
        platform_info = get_platform_info()
        flutter_info = {"current_version": "Loading...", "update_available": False}
        fvm_info = {"version": "Loading...", "installed": False}
        
        self.context = CommandContext(
            platform_info=platform_info,
            flutter_info=flutter_info,
            fvm_info=fvm_info,
            console=self.console,
            prompt_history=InMemoryHistory()
        )
        
        # Welcome message
        self.query_one(Log).write("[bold cyan]Welcome to FlutterCraft CLI![/]")
        self.query_one(Log).write("[dim]Type /help for available commands.[/]")

    def update_theme_vars(self):
        """Update CSS variables from current theme."""
        theme = self.theme_manager.get_current_theme()
        
        # Map our theme colors to Textual CSS variables
        self.styles.set_variable("background", theme.background)
        self.styles.set_variable("surface", "#252526") # Approximate for now
        self.styles.set_variable("accent", theme.accent_cyan)
        self.styles.set_variable("text", theme.semantic.text_primary)
        self.styles.set_variable("primary", theme.accent_cyan)
        self.styles.set_variable("secondary", theme.semantic.text_secondary)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="header"):
            yield Static("FlutterCraft CLI", id="app-title")
            
        with Container(id="output-container"):
            yield Log(id="output-log", markup=True)
            
        with Container(id="input-area"):
            yield Input(placeholder="> Enter command...", id="input")
            
        yield Footer() 
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        command = event.value
        if not command:
            return
            
        log = self.query_one(Log)
        log.write(f"\n[bold cyan]> {command}[/]")
        
        # Handle slash commands specially if needed
        if command == "/quit":
            self.exit()
            return
            
        # Execute command
        if self.executor:
            # We need to capture output. This is tricky with the current executor design 
            # which writes directly to a console.
            # Ideally, we refactor executor to return output or take a writable sink.
            # For now, we'll try to execute and print the result message.
            try:
                result = self.executor.dispatch(command, self.context)
                if result.message:
                    log.write(result.message)
            except Exception as e:
                log.write(f"[bold red]Error: {e}[/]")
        
        event.input.value = ""

def main():
    app = FlutterCraftApp()
    app.run()

if __name__ == "__main__":
    main()
