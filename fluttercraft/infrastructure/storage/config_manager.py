"""
Configuration manager for FlutterCraft.
Handles loading, saving, and accessing user configuration.
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

DEFAULT_CONFIG = {
    "version": "1.0.0",
    "theme": "gradient",
    "animations": {
        "enabled": True,
        "reduced_motion": False,
        "duration_multiplier": 1.0
    },
    "completion": {
        "fuzzy_enabled": True,
        "auto_show_slash": True
    },
    "history": {
        "max_entries": 10000,
        "save_duplicates": False
    },
    "ui": {
        "compact_mode": False,
        "show_tips": True,
        "show_timing": True
    }
}

class ConfigManager:
    """Manages persistent configuration for the CLI."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".fluttercraft"
        self.config_file = self.config_dir / "config.json"
        self._config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> None:
        """Load configuration from disk."""
        if not self.config_file.exists():
            self.save()
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                # Deep merge with defaults (simplified for now)
                self._update_dict_recursive(self._config, user_config)
        except Exception:
            # If load fails, stick to defaults/current state
            pass

    def save(self) -> None:
        """Save configuration to disk."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
        except Exception:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a config value using dot notation (e.g. 'ui.compact_mode').
        """
        keys = key.split(".")
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set a config value using dot notation and save.
        """
        keys = key.split(".")
        target = self._config
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value
        self.save()

    def _update_dict_recursive(self, target: Dict, source: Dict) -> None:
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._update_dict_recursive(target[key], value)
            else:
                target[key] = value

# Global instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
