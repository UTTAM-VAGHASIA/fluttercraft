from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from .base import Command
from .models import CommandMetadata


class CommandRegistry:
    """Central registry for FlutterCraft commands."""

    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}
        self._by_category: Dict[str, List[Command]] = defaultdict(list)

    def register(self, command: Command) -> None:
        key = command.name.lower()
        if key in self._commands:
            raise ValueError(f"Command '{command.name}' already registered")

        self._commands[key] = command
        for alias in command.aliases:
            alias_key = alias.lower()
            if alias_key in self._commands:
                raise ValueError(f"Alias '{alias}' conflicts with existing command")
            self._commands[alias_key] = command

        self._by_category[command.category].append(command)

    def get(self, token: str) -> Optional[Command]:
        return self._commands.get(token.lower())

    def list_commands(self) -> Iterable[Command]:
        seen = set()
        for command in self._commands.values():
            if command in seen:
                continue
            seen.add(command)
            yield command

    def list_by_category(self, category: str) -> Iterable[Command]:
        return tuple(self._by_category.get(category, ()))

    def to_metadata(self) -> Iterable[CommandMetadata]:
        for command in self.list_commands():
            yield command.get_metadata()
