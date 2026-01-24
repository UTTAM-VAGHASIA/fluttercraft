"""
Main TUI Application Model.
Mirrors appModel in OpenCode's tui.go
"""
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Log, Input
from textual.binding import Binding
from textual.reactive import reactive

from .theme.interface import Theme
from .theme.definitions import OPENCODE_DARK, DRACULA

class FlutterCraftTUI(App):
    """
    Main application model.
    """
    
    # Define reactive theme
    current_theme: reactive[Theme] = reactive(OPENCODE_DARK)
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("f1", "toggle_theme", "Toggle Theme"),
    ]
    
    CSS = """
    Screen {
        background: $background;
        color: $text;
    }
    
    #header {
        dock: top;
        height: auto;
        background: $background-secondary;
        color: $accent;
        border-bottom: solid $border-focused;
        padding: 1;
    }
    
    Log {
        background: $background;
        color: $text;
        border: none;
    }
    
    #input-area {
        dock: bottom;
        height: 3;
        background: $background-secondary;
        border-top: solid $border-focused;
    }
    
    Input {
        background: $background-secondary;
        color: $text;
        border: none;
    }
    Input:focus {
        border: none;
    }
    """
    
    def on_mount(self) -> None:
        self.update_theme_vars()
        self.query_one(Log).write("Welcome to FlutterCraft (TUI Mode)")

    def watch_current_theme(self, theme: Theme) -> None:
        """Update CSS variables when theme changes."""
        self.update_theme_vars()
        
    def update_theme_vars(self) -> None:
        """Map Python theme object to CSS variables."""
        css_vars = self.current_theme.to_css_vars()
        for name, value in css_vars.items():
            self.styles.set_variable(name, value)

    def action_toggle_theme(self) -> None:
        if self.current_theme.name == "opencode_dark":
            self.current_theme = DRACULA
        else:
            self.current_theme = OPENCODE_DARK
            
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(id="header") # Placeholder for custom header
        yield Log(id="output-log")
        with Container(id="input-area"):
            yield Input(placeholder="> Enter command...", id="input")
        yield Footer()

def main():
    app = FlutterCraftTUI()
    app.run()

if __name__ == "__main__":
    main()
