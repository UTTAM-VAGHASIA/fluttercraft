"""Beautiful prompt system using prompt_toolkit for FlutterCraft CLI."""

from typing import Iterable, TYPE_CHECKING

from prompt_toolkit import Application
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.styles import Style
from prompt_toolkit.layout import Layout, HSplit, Window, FormattedTextControl
from rich.console import Console
import os
from pathlib import Path

from fluttercraft.utils.themed_display import get_theme

if TYPE_CHECKING:
    from fluttercraft.commands.core import CommandMetadata

console = Console()

# Define slash commands with descriptions
SLASH_COMMANDS = {
    "/quit": "Exit FlutterCraft CLI",
    "/clear": "Clear screen and conversation history",
    "/help": "Show comprehensive help information",
    "/about": "Show information about FlutterCraft CLI",
    "/theme": "Launch interactive theme selector",
}

# Define FVM commands with descriptions
FVM_COMMANDS = {
    "fvm": "Show FVM help",
    "fvm install": "Install Flutter Version Manager",
    "fvm uninstall": "Uninstall Flutter Version Manager",
    "fvm releases": "List all available Flutter SDK versions",
    "fvm releases stable": "List stable Flutter versions",
    "fvm releases beta": "List beta Flutter versions",
    "fvm releases dev": "List dev Flutter versions",
    "fvm list": "List installed Flutter SDK versions",
    "fvm --help": "Show FVM help",
}

# Define Flutter commands with descriptions
FLUTTER_COMMANDS = {
    "flutter upgrade": "Upgrade Flutter to latest version",
    "flutter --version": "Show Flutter version (Coming Soon)",
    "flutter doctor": "Check Flutter installation (Coming Soon)",
}

# Combine all commands
BASE_COMMANDS = {**SLASH_COMMANDS, **FVM_COMMANDS, **FLUTTER_COMMANDS}
ALL_COMMANDS = dict(BASE_COMMANDS)

# Completion management
def update_command_completions(
    command_metadata: Iterable["CommandMetadata"],
) -> None:
    """Refresh completion map from registered commands."""

    global ALL_COMMANDS

    commands = dict(BASE_COMMANDS)
    for metadata in command_metadata:
        description = metadata.help_text or ""
        commands[metadata.name] = description
        for alias in metadata.aliases:
            commands[alias] = description

    ALL_COMMANDS = commands


def build_prompt_style() -> Style:
    theme = get_theme()

    return Style.from_dict(
        {
            "prompt": f"{theme.semantic.text_accent} bold",
            "bottom-toolbar": f"{theme.semantic.text_primary} bg:{theme.semantic.background_primary}",
            "completion-menu": f"bg:{theme.semantic.background_primary} {theme.semantic.text_primary}",
            "completion-menu.completion": f"bg:{theme.semantic.background_primary} {theme.semantic.text_primary}",
            "completion-menu.completion.current": f"bg:{theme.semantic.border_focused} {theme.semantic.background_primary}",
            "completion-menu.meta": f"{theme.semantic.text_secondary}",
            "scrollbar.background": f"bg:{theme.semantic.background_primary}",
            "scrollbar.button": f"bg:{theme.semantic.border_focused}",
            "ascii-art": f"{theme.semantic.text_accent} bold",
            "tips-header": f"{theme.semantic.text_primary} bold",
            "tips": theme.semantic.text_secondary,
            "system-info": theme.semantic.text_secondary,
            "toolbar": theme.semantic.text_secondary,
            "frame": f"bg:{theme.semantic.background_primary} {theme.semantic.border_default}",
        }
    )


class FlutterCraftCompleter(Completer):
    """Custom completer for FlutterCraft that shows command descriptions."""

    def get_completions(self, document, complete_event):
        """Get completions for the current input."""
        # Get the text on the current line before cursor
        text = document.current_line_before_cursor.lstrip()

        # If text starts with /, show slash commands immediately
        if text.startswith("/"):
            for cmd, desc in SLASH_COMMANDS.items():
                if cmd.startswith(text):
                    yield Completion(
                        cmd[len(text):],  # Only complete the remaining part
                        display=cmd,
                        display_meta=desc,
                    )
        # If text is just "/", show all slash commands
        elif text == "/":
            for cmd, desc in SLASH_COMMANDS.items():
                yield Completion(
                    cmd[1:],  # Skip the / since user already typed it
                    display=cmd,
                    display_meta=desc,
                )
        # If text is empty, don't show anything
        elif text == "":
            pass
        # Otherwise show matching commands from all categories
        else:
            for cmd, desc in ALL_COMMANDS.items():
                if cmd.lower().startswith(text.lower()):
                    yield Completion(
                        cmd[len(text):],  # Only complete the remaining part
                        display=cmd,
                        display_meta=desc,
                    )


def get_git_info():
    """Get current git branch and status."""
    try:
        import subprocess

        cwd = os.getcwd()

        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=2,
        )

        if branch_result.returncode == 0:
            branch = branch_result.stdout.strip()

            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=2,
            )

            has_changes = bool(status_result.stdout.strip())
            status_indicator = "*" if has_changes else ""

            return f"{branch}{status_indicator}"
        else:
            return None
    except Exception:
        return None


def get_current_path():
    """Get current working directory relative to home."""
    try:
        cwd = Path.cwd()
        home = Path.home()

        try:
            rel_path = cwd.relative_to(home)
            return f"~\\{rel_path}"
        except ValueError:
            return str(cwd)
    except Exception:
        return os.getcwd()


def create_prompt_session():
    """Create and configure a prompt_toolkit session with beautiful styling."""

    # Create custom completer
    completer = FlutterCraftCompleter()

    # Create history
    history = InMemoryHistory()

    # Create key bindings
    kb = KeyBindings()

    @kb.add("c-c")
    def _(event):
        """Handle Ctrl+C - cancel current input."""
        event.app.current_buffer.reset()

    @kb.add("c-d")
    def _(event):
        """Handle Ctrl+D - exit (same as /quit)."""
        raise EOFError

    @kb.add("escape", "enter")  # Alt+Enter for multiline
    def _(event):
        """Handle Alt+Enter - insert newline for multiline input."""
        event.current_buffer.insert_text("\n")

    # Create session
    custom_style = build_prompt_style()

    session = PromptSession(
        history=history,
        auto_suggest=AutoSuggestFromHistory(),
        completer=completer,
        style=custom_style,
        multiline=False,  # Disable multiline - Enter should submit
        complete_while_typing=True,
        key_bindings=kb,
        mouse_support=True,
        enable_history_search=True,
        complete_in_thread=False,  # Disable threading for immediate display
        # Show completions in a column with descriptions
        complete_style="COLUMN",
        # Show completions immediately without needing Tab
        enable_open_in_editor=False,
        reserve_space_for_menu=8,  # Reserve space for completion menu
    )

    return session


def get_bottom_toolbar():
    """Get the bottom toolbar text with path and git info."""
    path = get_current_path()
    git_info = get_git_info()

    if git_info:
        location = f"{path} ({git_info})"
    else:
        location = path

    return HTML(f"<b>{location}</b>")


def prompt_user_with_border(completer, history):
    """Prompt user with bordered input box and permanent completion menu area below.

    Args:
        completer: The completer instance
        history: The history instance

    Returns:
        str: The user's input
    """
    from prompt_toolkit.layout.containers import VSplit, Window as LayoutWindow
    from prompt_toolkit.layout.controls import BufferControl
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.document import Document
    from prompt_toolkit.layout.dimension import Dimension

    # Track selected completion index and scroll position
    selected_index = [0]  # Use list to make it mutable in nested functions
    scroll_offset = [0]  # Scroll position for viewing window
    current_completions = []  # Store current completions
    VISIBLE_ITEMS = 5  # Number of items visible at once

    # Create buffer for input
    input_buffer = Buffer(
        completer=completer,
        complete_while_typing=False,  # Don't auto-complete while typing
        history=history,
        auto_suggest=AutoSuggestFromHistory(),
        multiline=False,
    )

    # Create input control
    input_control = BufferControl(
        buffer=input_buffer,
        focusable=True,
    )

    prompt_symbol = " > "

    # Create completion menu text control
    def get_completions_text():
        """Get formatted completions text with highlighting and scrolling."""
        nonlocal current_completions
        document = input_buffer.document
        text = document.text_before_cursor.lstrip()

        if not text:
            current_completions = []
            selected_index[0] = 0
            scroll_offset[0] = 0
            return ""

        # Check if text exactly matches a command (hide menu if exact match)
        all_commands = {**SLASH_COMMANDS, **FVM_COMMANDS, **FLUTTER_COMMANDS}
        if text in all_commands:
            current_completions = []
            selected_index[0] = 0
            scroll_offset[0] = 0
            return ""

        completions = list(completer.get_completions(document, None))
        current_completions = completions  # Store ALL completions

        if not current_completions:
            selected_index[0] = 0
            scroll_offset[0] = 0
            return ""

        # Ensure selected index is valid
        if selected_index[0] >= len(current_completions):
            selected_index[0] = 0
            scroll_offset[0] = 0

        # Calculate scroll window
        # If selected item is below visible window, scroll down
        if selected_index[0] >= scroll_offset[0] + VISIBLE_ITEMS:
            scroll_offset[0] = selected_index[0] - VISIBLE_ITEMS + 1
        # If selected item is above visible window, scroll up
        elif selected_index[0] < scroll_offset[0]:
            scroll_offset[0] = selected_index[0]

        # Get visible slice of completions
        visible_completions = current_completions[
            scroll_offset[0]: scroll_offset[0] + VISIBLE_ITEMS
        ]

        # Format completions as FormattedText with highlighting
        from prompt_toolkit.formatted_text import FormattedText

        lines = []
        for i, comp in enumerate(visible_completions):
            actual_index = scroll_offset[0] + i

            # Get display text - handle both string and FormattedText
            if hasattr(comp.display, "__iter__") and not isinstance(comp.display, str):
                display_str = "".join(text for style, text in comp.display)
            else:
                display_str = str(comp.display) if comp.display else comp.text

            # Get meta text
            if hasattr(comp.display_meta, "__iter__") and not isinstance(
                comp.display_meta, str
            ):
                meta_str = "".join(text for style, text in comp.display_meta)
            else:
                meta_str = str(comp.display_meta) if comp.display_meta else ""

            # Create formatted line with highlighting
            line = f" {display_str:<25} {meta_str}"

            # Highlight selected item
            if actual_index == selected_index[0]:
                lines.append(("class:completion-menu.completion.current", line))
            else:
                lines.append(("", line))

            if i < len(visible_completions) - 1:
                lines.append(("", "\n"))

        # Add scroll indicator if there are more items
        if len(current_completions) > VISIBLE_ITEMS:
            total = len(current_completions)
            showing = f" ({scroll_offset[0] + 1}-{min(scroll_offset[0] + VISIBLE_ITEMS, total)} of {total})"
            if lines:
                lines.append(("", "\n"))
            lines.append(("class:completion-menu.meta", showing))

        return FormattedText(lines)

    completion_control = FormattedTextControl(
        get_completions_text,
        focusable=False,
    )

    # Create toolbar text
    def get_toolbar_text():
        path = get_current_path()
        git_info = get_git_info()
        if git_info:
            return f"{path} ({git_info})"
        return path

    toolbar_control = FormattedTextControl(
        lambda: get_toolbar_text(),
        focusable=False,
    )

    def build_rounded_frame(content: LayoutWindow, *, style: str, with_prompt: bool = False) -> HSplit:
        from prompt_toolkit.layout.containers import ConditionalContainer
        from prompt_toolkit.widgets.base import Border

        border_style = "class:frame.border"

        def border_window(char: str, *, width: int = 1, height: int = 1, stretch: bool = False) -> Window:
            return Window(
                char=char,
                width=width if not stretch else None,
                height=height,
                style=border_style,
            )

        top = VSplit(
            [
                border_window("╭"),
                border_window("─", height=1, stretch=True),
                border_window("╮"),
            ],
            height=1,
        )

        middle_children = [border_window("│")]

        if with_prompt:
            from prompt_toolkit.layout.containers import Window as PlainWindow
            from prompt_toolkit.layout.controls import FormattedTextControl as PlainTextControl

            prompt_window = PlainWindow(
                content=PlainTextControl(lambda: prompt_symbol),
                width=len(prompt_symbol),
                style="class:frame.prompt",
                dont_extend_width=True,
                align="left",
            )
            middle_children.append(prompt_window)

        middle_children.append(content)
        middle_children.append(border_window("│"))

        middle = VSplit(
            middle_children,
            padding=0,
        )

        bottom = VSplit(
            [
                border_window("╰"),
                border_window("─", height=1, stretch=True),
                border_window("╯"),
            ],
            height=1,
        )

        return HSplit([top, middle, bottom], style=style)

    # Create layout (system info now in static header)
    root_container = HSplit(
        [
            # Input box with frame (fixed 1 line height)
            build_rounded_frame(
                LayoutWindow(
                    content=input_control,
                    height=1,  # Fixed 1 line height
                ),
                style="class:frame",
                with_prompt=True,
            ),
            # Completion menu area (permanent, shows completions when available)
            build_rounded_frame(
                LayoutWindow(
                    content=completion_control,
                    height=Dimension(
                        min=6, max=6
                    ),  # Fixed height for menu (5 items + 1 scroll indicator)
                    style="class:completion-menu",
                ),
                style="class:completion-menu",
            ),
            # Toolbar
            build_rounded_frame(
                LayoutWindow(
                    content=toolbar_control,
                    height=1,
                    style="class:toolbar",
                ),
                style="class:toolbar",
            ),
        ]
    )

    layout = Layout(root_container, focused_element=input_control)

    # Create key bindings
    kb = KeyBindings()

    @kb.add("c-c")
    def _(event):
        """Cancel input."""
        event.app.exit(result="")

    @kb.add("c-d")
    def _(event):
        """Exit."""
        event.app.exit(result="/quit")

    @kb.add("down")
    def _(event):
        """Navigate down in completion menu."""
        if current_completions:
            selected_index[0] = (selected_index[0] + 1) % len(current_completions)
            event.app.invalidate()  # Redraw to show highlight

    @kb.add("up")
    def _(event):
        """Navigate up in completion menu."""
        if current_completions:
            selected_index[0] = (selected_index[0] - 1) % len(current_completions)
            event.app.invalidate()  # Redraw to show highlight

    @kb.add("tab")
    def _(event):
        """Select highlighted completion."""
        if current_completions and selected_index[0] < len(current_completions):
            comp = current_completions[selected_index[0]]
            # Get the full command text
            if hasattr(comp.display, "__iter__") and not isinstance(comp.display, str):
                text = "".join(t for s, t in comp.display)
            else:
                text = str(comp.display) if comp.display else comp.text
            # Replace current input with selected completion
            input_buffer.text = text
            input_buffer.cursor_position = len(text)

    @kb.add("enter")
    def _(event):
        """Select completion if menu active, otherwise submit."""
        if current_completions and selected_index[0] < len(current_completions):
            # Select the highlighted completion
            comp = current_completions[selected_index[0]]
            if hasattr(comp.display, "__iter__") and not isinstance(comp.display, str):
                text = "".join(t for s, t in comp.display)
            else:
                text = str(comp.display) if comp.display else comp.text
            input_buffer.text = text
            input_buffer.cursor_position = len(text)
            # Clear completions after selection
            selected_index[0] = 0
            event.app.invalidate()
        else:
            # No completions, submit the input
            event.app.exit(result=input_buffer.text)

    @kb.add("escape", "enter")
    def _(event):
        """New line."""
        input_buffer.insert_text("\n")

    # Create application (NOT full-screen - we want to preserve command output!)
    custom_style = build_prompt_style()

    app = Application(
        layout=layout,
        key_bindings=kb,
        style=custom_style,
        full_screen=False,  # NOT full-screen - preserve command output
        mouse_support=False,  # Disable to allow terminal scrolling
    )

    # Run and return result
    try:
        result = app.run()
        return result.strip() if result else ""
    except KeyboardInterrupt:
        return ""
    except EOFError:
        return "/quit"


def prompt_user(session, show_toolbar=True):
    """Prompt the user for input with beautiful Gemini-style styling.

    Args:
        session: The prompt_toolkit session
        show_toolbar: Whether to show the bottom toolbar

    Returns:
        str: The user's input
    """
    try:
        # Get input with toolbar (Gemini-style: simple prompt with toolbar at bottom)
        toolbar = get_bottom_toolbar() if show_toolbar else None

        user_input = session.prompt(
            "> ",  # Simple prompt like Gemini
            bottom_toolbar=toolbar,
            rprompt="",
        )

        return user_input.strip()

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        return ""
    except EOFError:
        # Handle Ctrl+D as quit command
        return "/quit"


def is_slash_command(command):
    """Check if a command is a slash command.

    Args:
        command: The command string

    Returns:
        bool: True if it's a slash command
    """
    return command.startswith("/")


def parse_slash_command(command):
    """Parse a slash command and return the command name and arguments.

    Args:
        command: The slash command string (e.g., '/clear', '/help')

    Returns:
        tuple: (command_name, args_list)
    """
    parts = command.split()
    if not parts:
        return None, []

    command_name = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []

    return command_name, args
