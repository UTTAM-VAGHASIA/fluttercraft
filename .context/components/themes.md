---
component: Theming System
layer: Presentation
last_updated: 2026-01-17
maintainer: UI Team
---

# Theming Component

## Purpose

The theming component provides a centralized visual identity system for FlutterCraft's CLI interface, including ASCII art, color gradients, panels, and consistent formatting across all output.

## Public API

### Display Service (Facade)
```python
from fluttercraft.utils.themed_display import display

# Show themed header with ASCII art
display.header("FlutterCraft", subtitle="Ready to code!")

# Show success/error messages
display.success("Operation completed!")
display.error("Something went wrong")

# Show panels
display.panel("Content", title="My Panel", border_style="cyan")

# Show system info
display.system_info(flutter_info, fvm_info, platform_info)
```

### Theme Manager
```python
from fluttercraft.utils.themes.theme_manager import ThemeManager

manager = ThemeManager()

# Get current theme
theme = manager.get_current_theme()

# Switch theme
manager.set_theme("gradient")  # or "ocean", "forest", etc.

# List available themes
themes = manager.get_available_themes()
```

### Theme Service (Low-Level)
```python
from fluttercraft.utils.themes.service import ThemeDisplayService

service = ThemeDisplayService()

# Render gradient text
gradient_text = service.render_gradient("Hello World", colors)

# Render ASCII art
art = service.render_ascii_art("FlutterCraft", theme)
```

## Architecture

```
utils/themes/
├── service.py              # ThemeDisplayService (core renderer)
├── theme_manager.py        # Theme persistence & lookup
├── theme.py                # Theme model/dataclass
├── professional_themes.py  # Theme definitions
├── ascii_art.py            # ASCII art selection
└── gradient.py             # Gradient rendering algorithms

utils/
└── themed_display.py       # Facade (simple API for commands)

commands/theme/
├── interactive_selector.py # Interactive theme picker
└── theme_command.py        # Typer command for theme selection
```

## Dependencies

### Depends On:
- `rich` - Terminal formatting and panels
- `pyfiglet` - ASCII art generation
- External: Theme configuration files (JSON)

### Depended By:
- `commands/start.py` - Header/footer display
- `commands/core/executor.py` - Success/error messages
- `commands/slash_commands.py` - Help/about panels
- `utils/beautiful_prompt.py` - Prompt colors

## Available Themes

### 1. Gradient (Default)
- Colors: Cyan → Blue → Purple
- Style: Modern, vibrant
- Best for: General use

### 2. Ocean
- Colors: Blue → Teal → Cyan
- Style: Calm, professional
- Best for: Long coding sessions

### 3. Forest
- Colors: Green → Emerald → Lime
- Style: Natural, easy on eyes
- Best for: Terminal on dark backgrounds

### 4. Sunset
- Colors: Orange → Red → Pink
- Style: Warm, energetic
- Best for: Creative work

### 5. Monochrome
- Colors: White → Gray → Black
- Style: Minimal, distraction-free
- Best for: Presentations, screenshots

## Theme Configuration

Themes are stored in `~/.fluttercraft/config.json`:

```json
{
  "theme": "gradient",
  "custom_themes": {
    "my_theme": {
      "primary": "#FF6B6B",
      "secondary": "#4ECDC4",
      "accent": "#45B7D1"
    }
  }
}
```

## Design Patterns

### Facade Pattern
`themed_display.py` provides a simple API that hides the complexity of the theme service:

```python
# Simple facade
from fluttercraft.utils.themed_display import display
display.success("Done!")

# vs. Low-level service
from fluttercraft.utils.themes.service import ThemeDisplayService
from fluttercraft.utils.themes.theme_manager import ThemeManager
service = ThemeDisplayService()
theme = ThemeManager().get_current_theme()
console = Console()
console.print(Panel("Done!", border_style=theme.colors["success"]))
```

### Service Layer Pattern
`ThemeDisplayService` centralizes all rendering logic, making it testable and reusable.

### Repository Pattern
`ThemeManager` handles theme persistence and retrieval, abstracting storage details.

## Adding a New Theme

### 1. Define Theme

```python
# utils/themes/professional_themes.py
THEMES = {
    # ... existing themes ...
    "custom": {
        "name": "Custom Theme",
        "description": "My custom color scheme",
        "colors": {
            "primary": "#FF6B6B",
            "secondary": "#4ECDC4",
            "accent": "#45B7D1",
            "success": "green",
            "error": "red",
            "warning": "yellow"
        }
    }
}
```

### 2. Test Theme

```python
def test_custom_theme_renders():
    manager = ThemeManager()
    theme = manager.get_theme("custom")
    assert theme.colors["primary"] == "#FF6B6B"
```

### 3. Add to Theme Selector

Theme will automatically appear in interactive selector.

## Display Components

### Header
- ASCII art with theme colors
- Gradient-rendered title
- System information (Flutter, FVM, Platform)

### Footer
- Current directory path
- Git branch and status
- Contextual information

### Panels
- Bordered content areas
- Color-coded by type (info, success, error, warning)
- Consistent padding and styling

### Status Messages
- Success: Green checkmark + message
- Error: Red X + message
- Warning: Yellow exclamation + message
- Info: Blue info icon + message

## Performance

- **Theme Loading**: < 10ms (cached after first load)
- **Gradient Rendering**: < 5ms for typical text
- **ASCII Art**: < 50ms (cached per theme)
- **Panel Rendering**: < 2ms

Optimizations:
- Theme caching in memory
- Lazy ASCII art generation
- Gradient color pre-computation

## Testing

### Unit Tests
```python
def test_gradient_rendering():
    service = ThemeDisplayService()
    result = service.render_gradient("Hello", ["#FF0000", "#00FF00"])
    assert result is not None

def test_theme_persistence():
    manager = ThemeManager()
    manager.set_theme("ocean")
    assert manager.get_current_theme().name == "ocean"
```

### Visual Testing
```bash
# Test all themes
fluttercraft start
/theme  # Interactive selector
# Verify each theme displays correctly
```

## Change History

### 2026-01-17 (v0.1.3)
- Removed duplicate theme selector implementations
- Kept `interactive_selector.py` as canonical implementation
- Updated theme documentation

### 2025-10-16 (v0.1.2)
- Added interactive theme selection
- Implemented gradient rendering
- Multiple theme support

### 2025-06-15 (v0.1.0)
- Initial theming system
- Basic ASCII art display
- Single gradient theme

## Future Plans

See `.context/architecture.yaml` for FINAL architecture migration (v0.2.0+):
- Themes will move to `presentation/themes/`
- Enhanced theme customization
- Theme marketplace/sharing
- Dynamic theme switching without restart
- Light/dark mode support
- Custom ASCII art support
