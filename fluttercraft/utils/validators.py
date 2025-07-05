"""
Input Validation Utilities

Validation functions for user inputs, command arguments, and configuration values.
Ensures data integrity and provides helpful error messages.
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from fluttercraft.utils.platform import is_windows


class ValidationError(Exception):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, suggestions: List[str] = None):
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(message)


def validate_flutter_version(version: str) -> bool:
    """
    Validate Flutter version format.
    
    Args:
        version: Version string to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If version format is invalid
    """
    if not version:
        raise ValidationError(
            "Version cannot be empty",
            ["Use format: X.Y.Z (e.g., 3.16.0)", "Use 'latest' for latest version"]
        )
    
    if version.lower() == "latest":
        return True
    
    # Flutter version pattern: major.minor.patch with optional pre-release
    pattern = r'^\d+\.\d+\.\d+(?:-[\w\.-]+)?(?:\+[\w\.-]+)?$'
    
    if not re.match(pattern, version):
        raise ValidationError(
            f"Invalid version format: {version}",
            [
                "Use format: X.Y.Z (e.g., 3.16.0)",
                "Pre-release format: X.Y.Z-beta.1",
                "Build format: X.Y.Z+hotfix.1",
                "Use 'latest' for latest version"
            ]
        )
    
    return True


def validate_project_name(name: str) -> bool:
    """
    Validate Flutter project name.
    
    Args:
        name: Project name to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If project name is invalid
    """
    if not name:
        raise ValidationError(
            "Project name cannot be empty",
            ["Use lowercase letters, numbers, and underscores only"]
        )
    
    if len(name) < 2:
        raise ValidationError(
            "Project name must be at least 2 characters long",
            ["Use a descriptive name like 'my_app' or 'hello_world'"]
        )
    
    if len(name) > 50:
        raise ValidationError(
            "Project name cannot exceed 50 characters",
            ["Use a shorter, more concise name"]
        )
    
    # Flutter project name pattern
    pattern = r'^[a-z]([a-z0-9_]*[a-z0-9])?$'
    
    if not re.match(pattern, name):
        raise ValidationError(
            f"Invalid project name: {name}",
            [
                "Must start with a lowercase letter",
                "Can only contain lowercase letters, numbers, and underscores",
                "Cannot end with an underscore",
                "Examples: my_app, hello_world, test123"
            ]
        )
    
    # Check for reserved keywords
    reserved_keywords = {
        'test', 'flutter', 'dart', 'android', 'ios', 'web', 'linux', 'macos', 'windows',
        'main', 'lib', 'pubspec', 'readme', 'license', 'changelog', 'analysis_options',
        'build', 'doc', 'example', 'tool', 'assets', 'fonts', 'images'
    }
    
    if name.lower() in reserved_keywords:
        raise ValidationError(
            f"'{name}' is a reserved keyword and cannot be used as a project name",
            ["Try adding a prefix like 'my_' or suffix like '_app'"]
        )
    
    return True


def validate_package_name(name: str) -> bool:
    """
    Validate Dart package name.
    
    Args:
        name: Package name to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If package name is invalid
    """
    if not name:
        raise ValidationError(
            "Package name cannot be empty",
            ["Use lowercase letters, numbers, and underscores only"]
        )
    
    # Package name pattern (similar to project name but more restrictive)
    pattern = r'^[a-z]([a-z0-9_]*[a-z0-9])?$'
    
    if not re.match(pattern, name):
        raise ValidationError(
            f"Invalid package name: {name}",
            [
                "Must start with a lowercase letter",
                "Can only contain lowercase letters, numbers, and underscores",
                "Cannot start or end with an underscore",
                "Examples: http, shared_preferences, path_provider"
            ]
        )
    
    return True


def validate_path(path: Union[str, Path], must_exist: bool = False, must_be_directory: bool = False) -> bool:
    """
    Validate file or directory path.
    
    Args:
        path: Path to validate
        must_exist: Whether path must exist
        must_be_directory: Whether path must be a directory
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If path is invalid
    """
    if not path:
        raise ValidationError(
            "Path cannot be empty",
            ["Provide a valid file or directory path"]
        )
    
    path_obj = Path(path) if isinstance(path, str) else path
    
    try:
        # Try to resolve the path to check for invalid characters
        resolved_path = path_obj.resolve()
    except (OSError, ValueError) as e:
        raise ValidationError(
            f"Invalid path: {path}",
            [
                "Check for invalid characters in the path",
                "Ensure the path format is correct for your operating system"
            ]
        )
    
    if must_exist and not path_obj.exists():
        raise ValidationError(
            f"Path does not exist: {path}",
            [
                "Check if the path is spelled correctly",
                "Ensure you have permission to access the path"
            ]
        )
    
    if must_be_directory and path_obj.exists() and not path_obj.is_dir():
        raise ValidationError(
            f"Path is not a directory: {path}",
            ["Specify a directory path, not a file"]
        )
    
    return True


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not url:
        raise ValidationError(
            "URL cannot be empty",
            ["Provide a valid HTTP or HTTPS URL"]
        )
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError(
                f"Invalid URL format: {url}",
                [
                    "URL must include protocol (http:// or https://)",
                    "URL must include domain name",
                    "Example: https://github.com/flutter/flutter"
                ]
            )
        
        if parsed.scheme not in ['http', 'https']:
            raise ValidationError(
                f"Unsupported URL scheme: {parsed.scheme}",
                ["Only HTTP and HTTPS URLs are supported"]
            )
    
    except Exception:
        raise ValidationError(
            f"Invalid URL: {url}",
            ["Check the URL format and try again"]
        )
    
    return True


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        raise ValidationError(
            "Email address cannot be empty",
            ["Provide a valid email address"]
        )
    
    # Basic email pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError(
            f"Invalid email format: {email}",
            [
                "Use format: name@example.com",
                "Check for typos in the email address"
            ]
        )
    
    return True


def validate_theme_name(name: str) -> bool:
    """
    Validate theme name.
    
    Args:
        name: Theme name to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If theme name is invalid
    """
    if not name:
        raise ValidationError(
            "Theme name cannot be empty",
            ["Use lowercase letters, numbers, and hyphens only"]
        )
    
    # Theme name pattern
    pattern = r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
    
    if not re.match(pattern, name):
        raise ValidationError(
            f"Invalid theme name: {name}",
            [
                "Must start and end with lowercase letter or number",
                "Can only contain lowercase letters, numbers, and hyphens",
                "Examples: gemini-classic, dark-theme, blue-ocean"
            ]
        )
    
    return True


def validate_command_args(args: List[str], min_args: int = 0, max_args: Optional[int] = None) -> bool:
    """
    Validate command arguments count.
    
    Args:
        args: List of command arguments
        min_args: Minimum number of arguments required
        max_args: Maximum number of arguments allowed (None for unlimited)
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If argument count is invalid
    """
    arg_count = len(args)
    
    if arg_count < min_args:
        raise ValidationError(
            f"Too few arguments. Expected at least {min_args}, got {arg_count}",
            ["Check the command help for required arguments"]
        )
    
    if max_args is not None and arg_count > max_args:
        raise ValidationError(
            f"Too many arguments. Expected at most {max_args}, got {arg_count}",
            ["Check the command help for argument limits"]
        )
    
    return True


def validate_config_value(key: str, value: Any, expected_type: type) -> bool:
    """
    Validate configuration value type.
    
    Args:
        key: Configuration key name
        value: Value to validate
        expected_type: Expected value type
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If value type is invalid
    """
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"Invalid type for config '{key}'. Expected {expected_type.__name__}, got {type(value).__name__}",
            [f"Set '{key}' to a {expected_type.__name__} value"]
        )
    
    return True


def sanitize_input(text: str, allow_special_chars: bool = False) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Text to sanitize
        allow_special_chars: Whether to allow special characters
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    if not allow_special_chars:
        # Only allow alphanumeric, spaces, and basic punctuation
        sanitized = re.sub(r'[^a-zA-Z0-9\s\.\-_]', '', sanitized)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def is_safe_command(command: List[str]) -> bool:
    """
    Check if a command is safe to execute.
    
    Args:
        command: Command arguments list
        
    Returns:
        True if command is considered safe
        
    Raises:
        ValidationError: If command is potentially dangerous
    """
    if not command:
        raise ValidationError(
            "Command cannot be empty",
            ["Provide a valid command to execute"]
        )
    
    # List of potentially dangerous commands/patterns
    dangerous_patterns = [
        r'rm\s+-rf',  # rm -rf
        r'del\s+/[qsf]',  # Windows del with force flags
        r'format\s+',  # format command
        r'fdisk\s+',  # disk partitioning
        r'dd\s+',  # disk duplication
        r'sudo\s+',  # sudo prefix
        r'su\s+',  # switch user
        r'shutdown\s+',  # system shutdown
        r'reboot\s+',  # system reboot
        r'halt\s+',  # system halt
        r'poweroff\s+',  # power off
        r':\(\)\{\s*:\|:\&\s*\};:',  # fork bomb
        r'>\s*/dev/',  # writing to device files
        r'curl.*\|\s*sh',  # curl pipe to shell
        r'wget.*\|\s*sh',  # wget pipe to shell
    ]
    
    command_str = ' '.join(command)
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command_str, re.IGNORECASE):
            raise ValidationError(
                f"Potentially dangerous command detected: {command[0]}",
                [
                    "This command could harm your system",
                    "Please review the command and try again",
                    "Use built-in FlutterCraft commands instead"
                ]
            )
    
    return True
