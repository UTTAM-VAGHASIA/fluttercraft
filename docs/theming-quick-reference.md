# FlutterCraft Theming - Quick Reference

## Commands

| Command | Description |
|---------|-------------|
| `fluttercraft theme` | 🎨 **Interactive selector** (recommended) |
| `fluttercraft theme select` | Launch interactive theme selector |
| `fluttercraft theme list` | List all available themes |
| `fluttercraft theme set <name>` | Set active theme directly |
| `fluttercraft theme current` | Show current theme info |
| `fluttercraft theme preview <name>` | Preview a theme |

## Available Themes

| Theme | Type | Best For |
|-------|------|----------|
| **ansi_dark** | Dark | High-contrast dark palettes inspired by ANSI terminals |
| **atom_one_dark** | Dark | Developers who prefer Atom One colorways |
| **ayu_dark** | Dark | Warm dark theme lovers |
| **default_dark** | Dark | Balanced dark mode baseline |
| **dracula** | Dark | Fans of the Dracula palette |
| **github_dark** | Dark | GitHub-style dark mode |
| **shades_of_purple** | Dark | Vibrant purple gradients |
| **ansi_light** | Light | ANSI-inspired light palette |
| **ayu_light** | Light | Soft light mode aesthetics |
| **default_light** | Light | Neutral light mode baseline |
| **github_light** | Light | GitHub-style light theme |
| **google_code_light** | Light | Classic Google Code look |
| **xcode_light** | Light | macOS Xcode-inspired palette |

## Quick Start

### Interactive Selector (Recommended)
```bash
# Launch interactive theme selector
fluttercraft theme

# Navigate with ↑/↓ arrows
# Press Enter to select
# Press Q or Esc to cancel
```

### Direct Theme Setting
```bash
# Set Gemini theme (default)
fluttercraft theme set gemini

# Set Dark theme
fluttercraft theme set dark

# Set Light theme
fluttercraft theme set light

# Set Minimal theme
fluttercraft theme set minimal
```

## Features

- 🌈 **Gradient Text**: Beautiful color gradients on ASCII art
- 🎨 **Semantic Colors**: Consistent success/error/warning/info colors
- 💾 **Persistent**: Theme saved to `~/.fluttercraft/theme.json`
- 📱 **Responsive**: ASCII art adapts to terminal width
- ⚡ **Fast**: Instant theme switching

## Color Reference

### Gemini Theme
- Primary: Purple (`#ac65ff`)
- Secondary: Cyan (`#a1feff`)
- Success: Green (`#A5FF90`)
- Error: Red (`#ff628c`)

### Dark Theme
- Primary: Purple (`#CBA6F7`)
- Secondary: Blue (`#89B4FA`)
- Success: Green (`#A6E3A1`)
- Error: Red (`#F38BA8`)

### Light Theme
- Primary: Purple (`#8B5CF6`)
- Secondary: Blue (`#3B82F6`)
- Success: Green (`#3CA84B`)
- Error: Red (`#DD4C4C`)

### Minimal Theme
- Primary: Magenta
- Secondary: Cyan
- Success: Green
- Error: Red

## Integration

The theme automatically applies to:
- ✅ ASCII art and headers
- ✅ Success/error/warning/info messages
- ✅ Command output
- ✅ Help screens
- ✅ About screen
- ✅ All CLI interactions

## Configuration File

Location: `~/.fluttercraft/theme.json`

```json
{
  "theme": "gemini"
}
```

## Tips

1. **Try all themes**: Use `preview` to see before applying
2. **Match your terminal**: Choose theme based on your terminal background
3. **Accessibility**: Light theme for bright rooms, dark for low light
4. **Performance**: All themes have equal performance

---

For detailed documentation, see [THEMING_GUIDE.md](../THEMING_GUIDE.md)
