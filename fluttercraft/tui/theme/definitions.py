"""
Standard themes implementing the Theme interface.
"""
from dataclasses import dataclass
from .interface import Theme

@dataclass
class BaseTheme(Theme):
    _name: str
    
    # Base
    _primary: str
    _secondary: str
    _accent: str
    
    # Status
    _error: str
    _warning: str
    _success: str
    _info: str
    
    # Text
    _text: str
    _text_muted: str
    _text_emphasized: str
    
    # Background
    _background: str
    _background_secondary: str
    _background_darker: str
    
    # Border
    _border_normal: str
    _border_focused: str
    _border_dim: str

    @property
    def name(self) -> str: return self._name
    
    @property
    def primary(self) -> str: return self._primary
    @property
    def secondary(self) -> str: return self._secondary
    @property
    def accent(self) -> str: return self._accent
    
    @property
    def error(self) -> str: return self._error
    @property
    def warning(self) -> str: return self._warning
    @property
    def success(self) -> str: return self._success
    @property
    def info(self) -> str: return self._info
    
    @property
    def text(self) -> str: return self._text
    @property
    def text_muted(self) -> str: return self._text_muted
    @property
    def text_emphasized(self) -> str: return self._text_emphasized
    
    @property
    def background(self) -> str: return self._background
    @property
    def background_secondary(self) -> str: return self._background_secondary
    @property
    def background_darker(self) -> str: return self._background_darker
    
    @property
    def border_normal(self) -> str: return self._border_normal
    @property
    def border_focused(self) -> str: return self._border_focused
    @property
    def border_dim(self) -> str: return self._border_dim

# OpenCode Dark Theme
OPENCODE_DARK = BaseTheme(
    _name="opencode_dark",
    
    # Base
    _primary="#5FAFFF",      # Blue
    _secondary="#AF87FF",    # Purple
    _accent="#5FDFDF",       # Cyan
    
    # Status
    _error="#FF5F5F",
    _warning="#DFAF5F",
    _success="#5FD75F",
    _info="#5FAFFF",
    
    # Text
    _text="#E0E0E0",
    _text_muted="#6A6A7A",
    _text_emphasized="#FFFFFF",
    
    # Background
    _background="#0A0A0F",   # Deep dark
    _background_secondary="#141419",
    _background_darker="#000000",
    
    # Border
    _border_normal="#4A4A5A",
    _border_focused="#5FDFDF",
    _border_dim="#2A2A3A",
)

# Dracula Theme
DRACULA = BaseTheme(
    _name="dracula",
    
    # Base
    _primary="#BD93F9",      # Purple
    _secondary="#6272A4",    # Blue Gray
    _accent="#8BE9FD",       # Cyan
    
    # Status
    _error="#FF5555",
    _warning="#F1FA8C",
    _success="#50FA7B",
    _info="#8BE9FD",
    
    # Text
    _text="#F8F8F2",
    _text_muted="#6272A4",
    _text_emphasized="#FFFFFF",
    
    # Background
    _background="#282A36",
    _background_secondary="#44475A",
    _background_darker="#21222C",
    
    # Border
    _border_normal="#6272A4",
    _border_focused="#BD93F9",
    _border_dim="#44475A",
)
