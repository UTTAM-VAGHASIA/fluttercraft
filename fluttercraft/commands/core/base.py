from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .models import CommandContext, CommandResult, CommandMetadata


class Command(ABC):
    """Base class for all FlutterCraft CLI commands."""

    def __init__(self, metadata: CommandMetadata) -> None:
        self.metadata = metadata

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def aliases(self) -> tuple[str, ...]:
        return self.metadata.aliases

    @property
    def keywords(self) -> tuple[str, ...]:
        return self.metadata.keywords

    @property
    def category(self) -> str:
        return self.metadata.category

    def matches(self, token: str) -> bool:
        normalized = token.lower()
        targets: Iterable[str] = (
            self.name.lower(),
            *[alias.lower() for alias in self.aliases],
        )
        return normalized in targets

    @abstractmethod
    def execute(self, context: CommandContext, args: list[str]) -> CommandResult:
        """Execute the command and return a standardized result."""

    def get_metadata(self) -> CommandMetadata:
        return self.metadata
