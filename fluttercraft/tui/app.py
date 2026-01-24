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
        background: #1e1e1e;
        color: #d4d4d4;
    }

    #header {
        dock: top;
        height: 3;
        background: #252526;
        border-bottom: solid #3c3c3c;
        padding: 0 1;
        content-align: center middle;
    }

    #main-container {
        height: 1fr;
        border: solid #3c3c3c;
        background: #1e1e1e;
        margin: 1;
        padding: 1;
    }

    #input-container {
        dock: bottom;
        height: 3;
        border-top: solid #3c3c3c;
        background: #252526;
        padding: 0 1;
    }

    Input {
        width: 100%;
        background: #252526;
        border: none;
        color: #d4d4d4;
    }
    
    Input:focus {
        border: none;
    }

    Log {
        background: #1e1e1e;
        color: #d4d4d4;
        border: none;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+d", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        theme = get_current_theme()
        
        # Apply theme colors directly to widgets to avoid CSS variable issues
        try:
            # Screen
            self.screen.styles.background = theme.background
            self.screen.styles.color = theme.foreground
            
            # Header
            header = self.query_one("#header")
            header.styles.background = theme.surface
            header.styles.border_bottom = ("solid", theme.border)
            
            # Main Container
            main = self.query_one("#main-container")
            main.styles.border = ("solid", theme.border)
            main.styles.background = theme.panel_bg
            
            # Input Container
            inp_cont = self.query_one("#input-container")
            inp_cont.styles.border_top = ("solid", theme.border)
            inp_cont.styles.background = theme.surface
            
            # Input Widget
            inp = self.query_one(Input)
            inp.styles.background = theme.surface
            inp.styles.color = theme.foreground
            
            # Log Widget
            log = self.query_one(Log)
            log.styles.background = theme.panel_bg
            log.styles.color = theme.foreground
            
        except Exception as e:
            # Fallback or log error if widgets aren't found yet (shouldn't happen in on_mount)
            pass
        
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
