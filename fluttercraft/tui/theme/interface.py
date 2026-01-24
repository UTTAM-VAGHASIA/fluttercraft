"""
Theme interface for FlutterCraft TUI.
Mirrors OpenCode's theme interface structure but for Textual/Python.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class Theme(ABC):
    """
    Abstract base class for TUI themes.
    Defines semantic color slots that all themes must implement.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    # Base Colors
    @property
    @abstractmethod
    def primary(self) -> str: pass
    
    @property
    @abstractmethod
    def secondary(self) -> str: pass
    
    @property
    @abstractmethod
    def accent(self) -> str: pass

    # Status Colors
    @property
    @abstractmethod
    def error(self) -> str: pass
    
    @property
    @abstractmethod
    def warning(self) -> str: pass
    
    @property
    @abstractmethod
    def success(self) -> str: pass
    
    @property
    @abstractmethod
    def info(self) -> str: pass

    # Text Colors
    @property
    @abstractmethod
    def text(self) -> str: pass
    
    @property
    @abstractmethod
    def text_muted(self) -> str: pass
    
    @property
    @abstractmethod
    def text_emphasized(self) -> str: pass

    # Background Colors
    @property
    @abstractmethod
    def background(self) -> str: pass
    
    @property
    @abstractmethod
    def background_secondary(self) -> str: pass
    
    @property
    @abstractmethod
    def background_darker(self) -> str: pass

    # Border Colors
    @property
    @abstractmethod
    def border_normal(self) -> str: pass
    
    @property
    @abstractmethod
    def border_focused(self) -> str: pass
    
    @property
    @abstractmethod
    def border_dim(self) -> str: pass

    def to_css_vars(self) -> Dict[str, str]:
        """Convert theme colors to Textual CSS variables."""
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "error": self.error,
            "warning": self.warning,
            "success": self.success,
            "info": self.info,
            "text": self.text,
            "text-muted": self.text_muted,
            "text-emphasized": self.text_emphasized,
            "background": self.background,
            "background-secondary": self.background_secondary,
            "background-darker": self.background_darker,
            "border-normal": self.border_normal,
            "border-focused": self.border_focused,
            "border-dim": self.border_dim,
        }
