# FlutterCraft CLI - Gemini-Style Interface Documentation

## Overview

FlutterCraft CLI features a beautiful, modern interface inspired by Gemini CLI with ANSI Shadow ASCII art, bordered input boxes, and an interactive completion menu.

## Features

### 🎨 Visual Design

#### ANSI Shadow ASCII Art
```
███████╗██╗     ██╗   ██╗████████╗████████╗███████╗██████╗  ██████╗██████╗  █████╗ ███████╗████████╗
██╔════╝██║     ██║   ██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝
█████╗  ██║     ██║   ██║   ██║      ██║   █████╗  ██████╔╝██║     ██████╔╝███████║█████╗     ██║   
██╔══╝  ██║     ██║   ██║   ██║      ██║   ██╔══╝  ██╔══██╗██║     ██╔══██╗██╔══██║██╔══╝     ██║   
██║     ███████╗╚██████╔╝   ██║      ██║   ███████╗██║  ██║╚██████╗██║  ██║██║  ██║██║        ██║   
╚═╝     ╚══════╝ ╚═════╝    ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝
```

#### Bordered Input Box
```
┌─────────────────────────────────────────────────────────────┐
│ > your command here█                                        │
└─────────────────────────────────────────────────────────────┘
```

#### Permanent Completion Menu
```
┌─────────────────────────────────────────────────────────────┐
│ > /█                                                        │
└─────────────────────────────────────────────────────────────┘
 /quit                     Exit FlutterCraft CLI  ← Highlighted
 /exit                     Exit FlutterCraft CLI
 /clear                    Clear screen and conversation history
 /help                     Show comprehensive help information
 /q                        Exit FlutterCraft CLI
~\fluttercraft (main*)
```

### ⌨️ Interactive Navigation

#### Arrow Key Navigation
- **↑ (Up Arrow)** - Navigate up in completion menu
- **↓ (Down Arrow)** - Navigate down in completion menu
- Visual highlighting shows current selection
- Navigation wraps around (top ↔ bottom)

#### Selection Behavior
- **Tab** - Fill input with highlighted item (doesn't submit)
- **Enter** - Select from menu and fill input, or submit if no menu active
- Input field **doesn't change** while navigating with arrows
- Only fills when Tab or Enter is pressed

### 📋 Live Completion Menu

#### Features
- **Permanent 5-line area** below input box
- Updates **instantly** as you type
- Shows up to 5 matching commands
- Each command displays with description
- Empty when no input or no matches
- No pop-up behavior - always visible

#### Command Categories
1. **Slash Commands** - `/quit`, `/exit`, `/clear`, `/help`, `/q`
2. **FVM Commands** - `fvm install`, `fvm uninstall`, `fvm releases`, `fvm list`
3. **Flutter Commands** - `flutter upgrade`, `flutter --version`, `flutter doctor`

### 📍 Smart Footer

Shows current location and git status:
- **Path**: Current directory relative to home (e.g., `~\fluttercraft`)
- **Git Branch**: Current branch name (e.g., `main`)
- **Git Status**: `*` indicates uncommitted changes
- **Combined**: `~\fluttercraft (main*)`

## Usage

### Starting the CLI

```bash
fluttercraft start
```

### Basic Workflow

1. **Type a command** - Start typing `/`, `fvm`, or `flutter`
2. **See completions** - Menu updates instantly with matching commands
3. **Navigate** - Use ↑/↓ arrows to highlight desired command
4. **Select** - Press Tab to fill input or Enter to select and submit
5. **Execute** - Press Enter again to run the command

### Example Session

```
# Type slash command
> /█
 /quit                     Exit FlutterCraft CLI  ← Highlighted
 /exit                     Exit FlutterCraft CLI
 /clear                    Clear screen

# Press ↓ to navigate
> /█
 /quit                     Exit FlutterCraft CLI
 /exit                     Exit FlutterCraft CLI  ← Highlighted
 /clear                    Clear screen

# Press Tab to fill
> /exit█
 (menu still visible)

# Press Enter to submit
> /exit
[Command executes]
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑` | Navigate up in menu |
| `↓` | Navigate down in menu |
| `Tab` | Fill input with selection (don't submit) |
| `Enter` | Select from menu OR submit command |
| `Ctrl+C` | Cancel current input |
| `Ctrl+D` | Exit FlutterCraft CLI |
| `Alt+Enter` | Insert newline (multiline input) |

## Technical Implementation

### Architecture

```
HSplit Layout:
├── Frame (Bordered Input Box)
│   └── BufferControl (Text Input)
├── Window (Completion Menu - 5 lines)
│   └── FormattedTextControl (Live Updates)
└── Window (Footer Toolbar - 1 line)
    └── FormattedTextControl (Path & Git Info)
```

### Key Components

1. **Buffer** - Stores input text, manages completion state
2. **BufferControl** - Renders input with cursor
3. **FormattedTextControl** - Renders completion menu with highlighting
4. **Frame** - Provides automatic borders around input
5. **HSplit** - Stacks components vertically
6. **Application** - Manages the entire interface

### Live Updates

The completion menu updates on every keystroke:
```python
def get_completions_text():
    """Called on every keystroke."""
    document = input_buffer.document
    text = document.text_before_cursor.lstrip()
    
    # Get matching completions
    completions = list(completer.get_completions(document, None))
    
    # Format with highlighting
    for i, comp in enumerate(completions[:5]):
        if i == selected_index[0]:
            # Highlight selected item
            lines.append(('class:completion-menu.completion.current', line))
        else:
            lines.append(('', line))
```

## Styling

### Custom Style Classes

```python
'completion-menu': 'bg:#333333 #ffffff',
'completion-menu.completion.current': 'bg:#00aaaa #000000',  # Highlighted
'frame': 'bg:#000000 #ffffff',
'toolbar': 'bg:#000000 #888888',
```

### Color Scheme

- **Input Box**: White text on black background with white borders
- **Completion Menu**: White text on dark gray background
- **Highlighted Item**: Black text on cyan background
- **Footer**: Gray text on black background

## Files

### Core Implementation
- `fluttercraft/utils/beautiful_prompt.py` - Prompt and completion system
- `fluttercraft/utils/beautiful_display.py` - ASCII art and header display
- `fluttercraft/commands/start.py` - CLI entry point
- `fluttercraft/commands/command_handler.py` - Command execution

### Completers
- `FlutterCraftCompleter` - Custom completer class
- Yields completions with display text and descriptions
- Handles slash commands, FVM commands, and Flutter commands

## Benefits

✅ **Professional Appearance** - Modern, clean interface
✅ **Instant Feedback** - Live updates as you type
✅ **Easy Navigation** - Arrow keys with visual highlighting
✅ **Smart Behavior** - Input doesn't change while browsing
✅ **Context Aware** - Shows relevant commands based on input
✅ **Discoverable** - All commands visible with descriptions
✅ **Efficient** - Quick selection with Tab/Enter
✅ **Git Integrated** - Always know your location and branch

## Troubleshooting

### Completion menu not showing
- Ensure you're typing valid command prefixes (`/`, `fvm`, `flutter`)
- Check that `complete_while_typing=False` in Buffer (we use manual updates)

### Highlighting not visible
- Check terminal color support
- Verify `class:completion-menu.completion.current` style is defined

### Navigation not working
- Ensure arrow key bindings are registered
- Check that `current_completions` list is populated

## Future Enhancements

- [ ] Fuzzy matching for completions
- [ ] Command history in completion menu
- [ ] Syntax highlighting in input
- [ ] Multi-column completion display
- [ ] Completion preview in footer
- [ ] Custom themes support

---

**Enjoy the beautiful Gemini-style interface! 🎨✨**
