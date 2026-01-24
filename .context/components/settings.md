---
component: Settings
layer: Presentation
last_updated: 2026-01-24
maintainer: Core Team
---

# Settings Component

## Purpose

Provides a persistent configuration system and an interactive TUI for user preferences.

## Public API

### Config Manager
```python
from fluttercraft.infrastructure.storage.config_manager import get_config_manager

config = get_config_manager()

# Get values
fuzzy_enabled = config.get("completion.fuzzy_enabled", True)
max_history = config.get("history.max_entries")

# Set values
config.set("ui.compact_mode", True)
# Auto-saves to ~/.fluttercraft/config.json
```

### Settings UI
```python
from fluttercraft.commands.settings.settings_ui import SettingsUI

ui = SettingsUI(console)
ui.show() # enters interactive loop
```

## Configuration Schema

Stored in `~/.fluttercraft/config.json`:

```json
{
  "version": "1.0.0",
  "theme": "gradient",
  "animations": {
    "enabled": true,
    "reduced_motion": false,
    "duration_multiplier": 1.0
  },
  "completion": {
    "fuzzy_enabled": true,
    "auto_show_slash": true
  },
  "history": {
    "max_entries": 10000,
    "save_duplicates": false
  },
  "ui": {
    "compact_mode": false,
    "show_tips": true,
    "show_timing": true
  }
}
```

## Architecture

```
fluttercraft/
├── infrastructure/
│   └── storage/
│       └── config_manager.py  # Persistence layer
└── commands/
    └── settings/
        ├── settings_ui.py     # TUI implementation
        ├── settings_command.py # Core command logic
        └── slash_settings.py  # /settings wrapper
```

## Usage

User can access settings via:
- `/settings`
- `/config`

## Dependencies

- `rich` for TUI rendering
- `pathlib` for file storage
- `json` for serialization
