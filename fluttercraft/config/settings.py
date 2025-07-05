"""
Configuration Management

Cross-platform configuration management for FlutterCraft including
user preferences, theme settings, and application state.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import toml
from rich.console import Console

from fluttercraft.utils.platform import (
    ensure_directory_exists,
    get_config_directory,
    format_path_for_display
)
from fluttercraft.utils.validators import ValidationError, validate_config_value


class ConfigurationError(Exception):
    """Raised when configuration operations fail."""
    
    def __init__(self, message: str, suggestions: list[str] = None):
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(message)


class ConfigManager:
    """
    Cross-platform configuration management.
    
    Handles loading, saving, and validating configuration data with
    platform-appropriate storage locations and caching.
    
    Attributes:
        config_dir: Configuration directory path
        config_file: Main configuration file path
        theme_file: Theme configuration file path
        cache_file: Cache file path
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Custom configuration directory (auto-detected if None)
        """
        self.config_dir = config_dir or get_config_directory()
        self.config_file = self.config_dir / "fluttercraft.toml"
        self.theme_file = self.config_dir / "theme.json"
        self.cache_file = self.config_dir / "cache.json"
        
        # Internal state
        self._config: Dict[str, Any] = {}
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Setup logging
        self.logger = logging.getLogger("fluttercraft.config")
        
        # Initialize configuration
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize configuration system."""
        try:
            # Ensure config directory exists
            ensure_directory_exists(self.config_dir)
            
            # Load configuration
            self._config = self._load_config()
            
            # Load cache
            self._cache = self._load_cache()
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize configuration: {str(e)}",
                [
                    "Check if you have write permissions to the config directory",
                    f"Config directory: {format_path_for_display(self.config_dir)}",
                    "Try running with elevated permissions if needed"
                ]
            )
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        if not self.config_file.exists():
            self.logger.info("Config file not found, creating default configuration")
            return self._create_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = toml.load(f)
            
            self.logger.debug(f"Loaded configuration from {self.config_file}")
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.logger.info("Creating backup and using default configuration")
            
            # Backup corrupted config
            backup_file = self.config_file.with_suffix('.backup')
            try:
                self.config_file.rename(backup_file)
                self.logger.info(f"Backed up corrupted config to {backup_file}")
            except Exception:
                pass
            
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Create default configuration.
        
        Returns:
            Default configuration dictionary
        """
        default_config = {
            "general": {
                "first_run": True,
                "auto_update_check": True,
                "default_theme": "gemini-classic",
                "verbose_mode": False,
                "check_prerequisites": True,
                "show_tips": True,
                "analytics_enabled": False,
            },
            "flutter": {
                "auto_doctor_check": True,
                "preferred_channel": "stable",
                "auto_upgrade": False,
                "default_platforms": ["android", "ios"],
                "web_renderer": "html",
            },
            "fvm": {
                "auto_install": False,
                "default_version": "latest",
                "cache_path": "",
                "skip_setup": False,
                "use_git_cache": True,
            },
            "ui": {
                "show_progress_bars": True,
                "use_animations": True,
                "console_width": 0,  # 0 = auto-detect
                "color_support": "auto",  # auto, always, never
                "emoji_support": True,
            },
            "advanced": {
                "parallel_downloads": 3,
                "network_timeout": 30,
                "retry_attempts": 3,
                "log_level": "INFO",
                "debug_mode": False,
            }
        }
        
        # Save default config
        self.save_config(default_config)
        return default_config
    
    def _load_cache(self) -> Dict[str, Any]:
        """
        Load cache from file.
        
        Returns:
            Cache dictionary
        """
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Validate cache structure
            if not isinstance(cache_data, dict):
                return {}
            
            return cache_data.get("cache", {})
            
        except Exception as e:
            self.logger.warning(f"Error loading cache: {e}")
            return {}
    
    def get(self, key: str, default: Any = None, use_cache: bool = True) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'general.first_run')
            default: Default value if key not found
            use_cache: Whether to use cached value
            
        Returns:
            Configuration value
        """
        # Check cache first if enabled
        if use_cache and key in self._cache:
            current_time = time.time()
            if current_time - self._cache_timestamps.get(key, 0) < self._cache_ttl:
                return self._cache[key]
        
        # Get value from config
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                value = default
                break
        
        # Cache the result
        if use_cache:
            self._cache[key] = value
            self._cache_timestamps[key] = time.time()
        
        return value
    
    def set(self, key: str, value: Any, validate: bool = True) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'general.first_run')
            value: Value to set
            validate: Whether to validate the value
            
        Raises:
            ValidationError: If value validation fails
            ConfigurationError: If setting value fails
        """
        try:
            # Validate value if requested
            if validate:
                self._validate_config_key(key, value)
            
            # Navigate to parent dictionary
            keys = key.split('.')
            config = self._config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                elif not isinstance(config[k], dict):
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            
            # Invalidate cache for this key
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
            
            # Save configuration
            self.save_config(self._config)
            
            self.logger.debug(f"Set config '{key}' = {value}")
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to set config '{key}': {str(e)}",
                ["Check if the key path is valid", "Ensure the value type is correct"]
            )
    
    def _validate_config_key(self, key: str, value: Any) -> None:
        """
        Validate configuration key and value.
        
        Args:
            key: Configuration key
            value: Value to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Define expected types for known config keys
        config_types = {
            "general.first_run": bool,
            "general.auto_update_check": bool,
            "general.default_theme": str,
            "general.verbose_mode": bool,
            "general.analytics_enabled": bool,
            "flutter.auto_doctor_check": bool,
            "flutter.preferred_channel": str,
            "flutter.auto_upgrade": bool,
            "fvm.auto_install": bool,
            "fvm.default_version": str,
            "fvm.skip_setup": bool,
            "ui.show_progress_bars": bool,
            "ui.use_animations": bool,
            "ui.console_width": int,
            "ui.emoji_support": bool,
            "advanced.parallel_downloads": int,
            "advanced.network_timeout": int,
            "advanced.retry_attempts": int,
            "advanced.debug_mode": bool,
        }
        
        if key in config_types:
            expected_type = config_types[key]
            validate_config_value(key, value, expected_type)
        
        # Additional validation for specific keys
        if key == "flutter.preferred_channel":
            valid_channels = ["stable", "beta", "dev", "master"]
            if value not in valid_channels:
                raise ValidationError(
                    f"Invalid Flutter channel: {value}",
                    [f"Valid channels: {', '.join(valid_channels)}"]
                )
        
        elif key == "ui.color_support":
            valid_options = ["auto", "always", "never"]
            if value not in valid_options:
                raise ValidationError(
                    f"Invalid color support option: {value}",
                    [f"Valid options: {', '.join(valid_options)}"]
                )
        
        elif key == "advanced.log_level":
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if value not in valid_levels:
                raise ValidationError(
                    f"Invalid log level: {value}",
                    [f"Valid levels: {', '.join(valid_levels)}"]
                )
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            
        Raises:
            ConfigurationError: If saving fails
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                toml.dump(config, f)
            
            self._config = config
            self.logger.debug(f"Saved configuration to {self.config_file}")
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to save configuration: {str(e)}",
                [
                    "Check if you have write permissions",
                    f"Config file: {format_path_for_display(self.config_file)}",
                    "Ensure disk space is available"
                ]
            )
    
    def get_current_theme(self) -> Optional[str]:
        """
        Get currently selected theme.
        
        Returns:
            Current theme name or None if not set
        """
        if not self.theme_file.exists():
            return self.get("general.default_theme", "gemini-classic")
        
        try:
            with open(self.theme_file, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            return theme_data.get("current_theme")
        except Exception as e:
            self.logger.warning(f"Error loading theme config: {e}")
            return self.get("general.default_theme", "gemini-classic")
    
    def set_current_theme(self, theme_name: str) -> None:
        """
        Set currently selected theme.
        
        Args:
            theme_name: Name of theme to set
            
        Raises:
            ConfigurationError: If setting theme fails
        """
        theme_data = {
            "current_theme": theme_name,
            "last_updated": time.time()
        }
        
        try:
            with open(self.theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2)
            
            self.logger.debug(f"Set current theme to '{theme_name}'")
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to save theme configuration: {str(e)}",
                ["Check write permissions for config directory"]
            )
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first run.
        
        Returns:
            True if first run, False otherwise
        """
        return self.get("general.first_run", True)
    
    def set_first_run_complete(self) -> None:
        """Mark first run as complete."""
        self.set("general.first_run", False)
    
    def reset_to_defaults(self) -> None:
        """
        Reset configuration to default values.
        
        Raises:
            ConfigurationError: If reset fails
        """
        try:
            # Backup current config
            backup_file = self.config_file.with_suffix('.user_backup')
            if self.config_file.exists():
                self.config_file.rename(backup_file)
                self.logger.info(f"Backed up current config to {backup_file}")
            
            # Create new default config
            self._config = self._create_default_config()
            
            # Clear cache
            self._cache.clear()
            self._cache_timestamps.clear()
            
            self.logger.info("Configuration reset to defaults")
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to reset configuration: {str(e)}",
                ["Check write permissions for config directory"]
            )
    
    def export_config(self, export_path: Path) -> None:
        """
        Export current configuration to a file.
        
        Args:
            export_path: Path to export file
            
        Raises:
            ConfigurationError: If export fails
        """
        try:
            export_data = {
                "fluttercraft_version": "0.1.2",
                "export_timestamp": time.time(),
                "config": self._config
            }
            
            if export_path.suffix.lower() == '.json':
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2)
            else:
                with open(export_path, 'w', encoding='utf-8') as f:
                    toml.dump(export_data, f)
            
            self.logger.info(f"Configuration exported to {export_path}")
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to export configuration: {str(e)}",
                ["Check write permissions for export path"]
            )
    
    def import_config(self, import_path: Path) -> None:
        """
        Import configuration from a file.
        
        Args:
            import_path: Path to import file
            
        Raises:
            ConfigurationError: If import fails
        """
        try:
            if import_path.suffix.lower() == '.json':
                with open(import_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
            else:
                with open(import_path, 'r', encoding='utf-8') as f:
                    import_data = toml.load(f)
            
            # Validate import data
            if "config" not in import_data:
                raise ConfigurationError(
                    "Invalid configuration file format",
                    ["File must contain a 'config' section"]
                )
            
            # Import configuration
            imported_config = import_data["config"]
            self.save_config(imported_config)
            
            # Clear cache
            self._cache.clear()
            self._cache_timestamps.clear()
            
            self.logger.info(f"Configuration imported from {import_path}")
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to import configuration: {str(e)}",
                ["Check if the file exists and is readable"]
            )
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Get information about the configuration system.
        
        Returns:
            Dictionary with configuration info
        """
        return {
            "config_dir": str(self.config_dir),
            "config_file": str(self.config_file),
            "theme_file": str(self.theme_file),
            "cache_file": str(self.cache_file),
            "config_exists": self.config_file.exists(),
            "theme_exists": self.theme_file.exists(),
            "cache_exists": self.cache_file.exists(),
            "cache_entries": len(self._cache),
            "current_theme": self.get_current_theme(),
            "first_run": self.is_first_run(),
        }
    
    def invalidate_cache(self, key: str = None) -> None:
        """
        Invalidate cache entries.
        
        Args:
            key: Specific key to invalidate (all if None)
        """
        if key:
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
        
        self.logger.debug("Cache invalidated")
    
    def cleanup(self) -> None:
        """Clean up resources and save any pending changes."""
        try:
            # Save current cache
            if self._cache:
                cache_data = {
                    "cache": self._cache,
                    "timestamps": self._cache_timestamps,
                    "last_updated": time.time()
                }
                
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, indent=2)
            
            self.logger.debug("Configuration cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
