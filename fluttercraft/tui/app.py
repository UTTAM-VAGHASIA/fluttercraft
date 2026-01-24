"""Main Textual App for FlutterCraft TUI."""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Input, Log, Static
from textual.binding import Binding
from fluttercraft.utils.theme.theme_config import get_current_theme

class FlutterCraftTUI(App):
    """A Textual app that mimics the OpenAI Codex CLI look and feel."""

    CSS = """
    Screen {
        background: $background;
        color: $foreground;
    }

    #header {
        dock: top;
        height: 3;
        background: $surface;
        border-bottom: solid $border;
        padding: 0 1;
        content-align: center middle;
    }

    #main-container {
        height: 1fr;
        border: solid $border;
        background: $panel_bg;
        margin: 1;
        padding: 1;
    }

    #input-container {
        dock: bottom;
        height: 3;
        border-top: solid $border;
        background: $surface;
        padding: 0 1;
    }

    Input {
        width: 100%;
        background: $surface;
        border: none;
        color: $foreground;
    }
    
    Input:focus {
        border: none;
    }

    Log {
        background: $panel_bg;
        color: $foreground;
        border: none;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+d", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        theme = get_current_theme()
        self.design.theme = "dark" # Use base dark theme
        
        # Apply theme colors variables
        self.styles.set_variable("background", theme.background)
        self.styles.set_variable("foreground", theme.foreground)
        self.styles.set_variable("surface", theme.surface)
        self.styles.set_variable("border", theme.border)
        self.styles.set_variable("panel_bg", theme.panel_bg)
        
        self.query_one(Log).write("Welcome to FlutterCraft CLI (Codex Style)")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="header"):
            yield Static("FlutterCraft", classes="title")

        with Container(id="main-container"):
            yield Log(id="output-log")

        with Container(id="input-container"):
            yield Input(placeholder="Type a command...", id="command-input")

        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        command = event.value
        log = self.query_one(Log)
        log.write(f"> {command}")
        
        # Placeholder for command execution logic
        if command.strip() == "exit":
            self.exit()
        else:
            log.write(f"Executing: {command}")
            
        event.input.value = ""

if __name__ == "__main__":
    app = FlutterCraftTUI()
    app.run()
