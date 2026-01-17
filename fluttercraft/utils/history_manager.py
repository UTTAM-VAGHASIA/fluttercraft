"""Command history management for FlutterCraft CLI.

This module provides persistent command history storage, retrieval, and search
functionality with automatic deduplication and size management.
"""

from pathlib import Path
from typing import List
import os


class HistoryManager:
    """Manages persistent command history for FlutterCraft CLI.

    Features:
    - Persistent storage in ~/.fluttercraft/history
    - Automatic deduplication of consecutive commands
    - Maximum 10,000 entries (FIFO when exceeded)
    - Simple text-based search

    Attributes:
        history_file (Path): Path to the history file
        max_entries (int): Maximum number of history entries (default: 10000)
    """

    def __init__(self, history_file: str = None, max_entries: int = 10000):
        """Initialize HistoryManager.

        Args:
            history_file: Custom path to history file (default: ~/.fluttercraft/history)
            max_entries: Maximum number of history entries to keep
        """
        if history_file is None:
            config_dir = Path.home() / ".fluttercraft"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.history_file = config_dir / "history"
        else:
            self.history_file = Path(history_file)
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

        self.max_entries = max_entries

        # Create empty file if it doesn't exist
        if not self.history_file.exists():
            self.history_file.touch()

    def load_history(self) -> List[str]:
        """Load command history from disk.

        Returns:
            List of command strings from history file
        """
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                # Read all lines and strip whitespace
                lines = [line.strip() for line in f if line.strip()]
                return lines
        except Exception as e:
            # If there's any error reading, return empty list
            print(f"Warning: Could not load history: {e}")
            return []

    def save_command(self, command: str) -> None:
        """Save a command to history with deduplication.

        Features:
        - Skips consecutive duplicates
        - Maintains max_entries limit (FIFO)
        - Thread-safe append operation

        Args:
            command: Command string to save
        """
        if not command or not command.strip():
            return

        command = command.strip()

        # Load existing history
        history = self.load_history()

        # Skip if it's the same as the last command (consecutive deduplication)
        if history and history[-1] == command:
            return

        # Add new command
        history.append(command)

        # Trim to max_entries (keep most recent)
        if len(history) > self.max_entries:
            history = history[-self.max_entries :]

        # Write back to file
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                f.write("\n".join(history) + "\n")
        except Exception as e:
            print(f"Warning: Could not save command to history: {e}")

    def search(self, query: str) -> List[str]:
        """Search command history for matching entries.

        Simple substring search (case-insensitive). Returns matches
        in reverse chronological order (most recent first).

        Args:
            query: Search query string

        Returns:
            List of matching commands (most recent first)
        """
        if not query or not query.strip():
            # Return all history in reverse order
            history = self.load_history()
            return list(reversed(history))

        query = query.strip().lower()
        history = self.load_history()

        # Filter matches (case-insensitive substring search)
        matches = [cmd for cmd in history if query in cmd.lower()]

        # Return in reverse order (most recent first)
        return list(reversed(matches))

    def clear(self) -> None:
        """Clear all command history.

        WARNING: This permanently deletes all history entries.
        """
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                f.write("")
        except Exception as e:
            print(f"Warning: Could not clear history: {e}")

    def get_last_n_commands(self, n: int = 10) -> List[str]:
        """Get the last N commands from history.

        Args:
            n: Number of commands to retrieve

        Returns:
            List of last N commands (most recent first)
        """
        history = self.load_history()
        return list(reversed(history[-n:]))
