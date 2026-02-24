from __future__ import annotations

from dataclasses import dataclass, field


# ── Theme definition ──────────────────────────────────────────────────────────


@dataclass(slots=True)
class ThemeDefinition:
    """All colour tokens for one FlutterCraft theme.

    Colours are hex strings (``#rrggbb``).
    """

    name: str
    description: str
    is_dark: bool

    # Backgrounds (darkest → lightest for dark themes, reversed for light)
    bg: str           # Screen background
    bg_surface: str   # Panel / sidebar surface
    bg_overlay: str   # Output panel / darkest overlay

    # Structural
    border: str       # Border colour
    resize_handle: str  # Resize handle strip

    # Text
    text: str         # Main text
    text_muted: str   # Dimmed / secondary text

    # Accent
    accent: str       # Primary accent (numbers, titles, links)
    accent_alt: str   # Secondary accent (icons, tags)

    # Semantic
    green: str        # Success / ▶
    red: str          # Error / ✖
    yellow: str       # Warning / ⚠

    # Footer (typically inverted)
    footer_bg: str
    footer_fg: str


# ── Pure helper ───────────────────────────────────────────────────────────────


def generate_theme_css(theme: ThemeDefinition) -> str:
    """Return a Textual TCSS snippet that defines CSS variables for *theme*.

    The returned string can be assigned to ``App.CSS`` so that any TCSS rule
    using these ``$variable`` names picks up the theme colours.
    """
    return (
        f"/* FlutterCraft theme: {theme.name} */\n"
        f"$theme-bg: {theme.bg};\n"
        f"$theme-surface: {theme.bg_surface};\n"
        f"$theme-overlay: {theme.bg_overlay};\n"
        f"$theme-border: {theme.border};\n"
        f"$theme-text: {theme.text};\n"
        f"$theme-muted: {theme.text_muted};\n"
        f"$theme-accent: {theme.accent};\n"
        f"$theme-accent-alt: {theme.accent_alt};\n"
        f"$theme-green: {theme.green};\n"
        f"$theme-red: {theme.red};\n"
        f"$theme-yellow: {theme.yellow};\n"
        f"$theme-footer-bg: {theme.footer_bg};\n"
        f"$theme-footer-fg: {theme.footer_fg};\n"
    )


# ── 13 built-in themes ────────────────────────────────────────────────────────

# ─── Dark (7) ────────────────────────────────────────────────────────────────

TOKYO_NIGHT = ThemeDefinition(
    name="Tokyo Night",
    description="Cool dark blue-purple, the FlutterCraft default",
    is_dark=True,
    bg="#1a1b26",      bg_surface="#1f2335",  bg_overlay="#16161e",
    border="#3b4261",  resize_handle="#3b4261",
    text="#a9b1d6",    text_muted="#565f89",
    accent="#7aa2f7",  accent_alt="#bb9af7",
    green="#9ece6a",   red="#f7768e",         yellow="#e0af68",
    footer_bg="#7aa2f7", footer_fg="#1a1b26",
)

DRACULA = ThemeDefinition(
    name="Dracula",
    description="Dark purple and pink tones",
    is_dark=True,
    bg="#282a36",      bg_surface="#21222c",  bg_overlay="#1e1f29",
    border="#44475a",  resize_handle="#44475a",
    text="#f8f8f2",    text_muted="#6272a4",
    accent="#bd93f9",  accent_alt="#ff79c6",
    green="#50fa7b",   red="#ff5555",         yellow="#f1fa8c",
    footer_bg="#bd93f9", footer_fg="#282a36",
)

NORD = ThemeDefinition(
    name="Nord",
    description="Cool arctic blue-grey palette",
    is_dark=True,
    bg="#2e3440",      bg_surface="#3b4252",  bg_overlay="#242933",
    border="#4c566a",  resize_handle="#4c566a",
    text="#d8dee9",    text_muted="#616e88",
    accent="#88c0d0",  accent_alt="#81a1c1",
    green="#a3be8c",   red="#bf616a",         yellow="#ebcb8b",
    footer_bg="#88c0d0", footer_fg="#2e3440",
)

CATPPUCCIN_MOCHA = ThemeDefinition(
    name="Catppuccin Mocha",
    description="Warm dark with pastel accents",
    is_dark=True,
    bg="#1e1e2e",      bg_surface="#181825",  bg_overlay="#11111b",
    border="#313244",  resize_handle="#45475a",
    text="#cdd6f4",    text_muted="#585b70",
    accent="#89b4fa",  accent_alt="#cba6f7",
    green="#a6e3a1",   red="#f38ba8",         yellow="#f9e2af",
    footer_bg="#89b4fa", footer_fg="#1e1e2e",
)

GRUVBOX_DARK = ThemeDefinition(
    name="Gruvbox Dark",
    description="Earthy retro warm tones",
    is_dark=True,
    bg="#282828",      bg_surface="#3c3836",  bg_overlay="#1d2021",
    border="#504945",  resize_handle="#665c54",
    text="#ebdbb2",    text_muted="#928374",
    accent="#83a598",  accent_alt="#d3869b",
    green="#b8bb26",   red="#fb4934",         yellow="#fabd2f",
    footer_bg="#83a598", footer_fg="#282828",
)

ONE_DARK = ThemeDefinition(
    name="One Dark",
    description="Atom-inspired dark with cyan-blue accents",
    is_dark=True,
    bg="#282c34",      bg_surface="#21252b",  bg_overlay="#1b1f27",
    border="#3e4452",  resize_handle="#4b5263",
    text="#abb2bf",    text_muted="#5c6370",
    accent="#61afef",  accent_alt="#c678dd",
    green="#98c379",   red="#e06c75",         yellow="#e5c07b",
    footer_bg="#61afef", footer_fg="#282c34",
)

SYNTHWAVE = ThemeDefinition(
    name="Synthwave",
    description="Neon retro-futurism pink and cyan",
    is_dark=True,
    bg="#262335",      bg_surface="#1a1a2e",  bg_overlay="#16213e",
    border="#495495",  resize_handle="#495495",
    text="#e2e2ff",    text_muted="#72729a",
    accent="#ff7edb",  accent_alt="#7ee8fa",
    green="#72f1b8",   red="#fe4450",         yellow="#fede5d",
    footer_bg="#ff7edb", footer_fg="#262335",
)

# ─── Light (6) ───────────────────────────────────────────────────────────────

SOLARIZED_LIGHT = ThemeDefinition(
    name="Solarized Light",
    description="Warm parchment with cool accents",
    is_dark=False,
    bg="#fdf6e3",      bg_surface="#eee8d5",  bg_overlay="#fdf6e3",
    border="#93a1a1",  resize_handle="#839496",
    text="#657b83",    text_muted="#93a1a1",
    accent="#268bd2",  accent_alt="#6c71c4",
    green="#859900",   red="#dc322f",         yellow="#b58900",
    footer_bg="#268bd2", footer_fg="#fdf6e3",
)

CATPPUCCIN_LATTE = ThemeDefinition(
    name="Catppuccin Latte",
    description="Soft light with pastel colours",
    is_dark=False,
    bg="#eff1f5",      bg_surface="#e6e9ef",  bg_overlay="#ccd0da",
    border="#bcc0cc",  resize_handle="#acb0be",
    text="#4c4f69",    text_muted="#8c8fa1",
    accent="#1e66f5",  accent_alt="#8839ef",
    green="#40a02b",   red="#d20f39",         yellow="#df8e1d",
    footer_bg="#1e66f5", footer_fg="#eff1f5",
)

GRUVBOX_LIGHT = ThemeDefinition(
    name="Gruvbox Light",
    description="Earthy warm tones, light variant",
    is_dark=False,
    bg="#fbf1c7",      bg_surface="#f2e5bc",  bg_overlay="#f9f5d7",
    border="#d5c4a1",  resize_handle="#a89984",
    text="#3c3836",    text_muted="#7c6f64",
    accent="#076678",  accent_alt="#8f3f71",
    green="#79740e",   red="#9d0006",         yellow="#b57614",
    footer_bg="#076678", footer_fg="#fbf1c7",
)

ONE_LIGHT = ThemeDefinition(
    name="One Light",
    description="Atom-inspired light with vivid accents",
    is_dark=False,
    bg="#fafafa",      bg_surface="#f0f0f1",  bg_overlay="#ffffff",
    border="#c2c2c3",  resize_handle="#c2c2c3",
    text="#383a42",    text_muted="#a0a1a7",
    accent="#4078f2",  accent_alt="#a626a4",
    green="#50a14f",   red="#e45649",         yellow="#c18401",
    footer_bg="#4078f2", footer_fg="#fafafa",
)

TOKYO_NIGHT_LIGHT = ThemeDefinition(
    name="Tokyo Night Light",
    description="Tokyo Night palette in light mode",
    is_dark=False,
    bg="#d5d6db",      bg_surface="#e9e9ec",  bg_overlay="#f0f0f4",
    border="#9699a3",  resize_handle="#b0b0bd",
    text="#343b58",    text_muted="#9699a3",
    accent="#2959aa",  accent_alt="#5a4a78",
    green="#485e30",   red="#8c4351",         yellow="#8f5e15",
    footer_bg="#2959aa", footer_fg="#d5d6db",
)

NORD_LIGHT = ThemeDefinition(
    name="Nord Light",
    description="Arctic palette in light mode",
    is_dark=False,
    bg="#eceff4",      bg_surface="#e5e9f0",  bg_overlay="#f0f0f4",
    border="#adb7c8",  resize_handle="#9099a8",
    text="#2e3440",    text_muted="#677592",
    accent="#5e81ac",  accent_alt="#81a1c1",
    green="#4c6e3b",   red="#bf616a",         yellow="#c9924c",
    footer_bg="#5e81ac", footer_fg="#eceff4",
)

ALL_THEMES: list[ThemeDefinition] = [
    TOKYO_NIGHT,
    DRACULA,
    NORD,
    CATPPUCCIN_MOCHA,
    GRUVBOX_DARK,
    ONE_DARK,
    SYNTHWAVE,
    SOLARIZED_LIGHT,
    CATPPUCCIN_LATTE,
    GRUVBOX_LIGHT,
    ONE_LIGHT,
    TOKYO_NIGHT_LIGHT,
    NORD_LIGHT,
]


# ── ThemeManager ──────────────────────────────────────────────────────────────


class ThemeManager:
    """Manages the active theme and cycles through the built-in library.

    Usage::

        mgr = ThemeManager()
        theme = mgr.next()        # advance and return new active theme
        mgr.save(config_manager)  # persist selection
        mgr.load(config_manager)  # restore on startup
    """

    def __init__(self, themes: list[ThemeDefinition] | None = None) -> None:
        self._themes: list[ThemeDefinition] = list(themes or ALL_THEMES)
        self._index: int = 0

    # ── Active theme ──────────────────────────────────────────────────────────

    @property
    def active(self) -> ThemeDefinition:
        """The currently selected theme."""
        return self._themes[self._index]

    @property
    def active_index(self) -> int:
        return self._index

    # ── Navigation ────────────────────────────────────────────────────────────

    def next(self) -> ThemeDefinition:
        """Advance to the next theme (wraps around) and return it."""
        self._index = (self._index + 1) % len(self._themes)
        return self.active

    def prev(self) -> ThemeDefinition:
        """Go back to the previous theme (wraps around) and return it."""
        self._index = (self._index - 1) % len(self._themes)
        return self.active

    def set_by_name(self, name: str) -> ThemeDefinition | None:
        """Select a theme by name.  Returns it, or ``None`` if not found."""
        for i, t in enumerate(self._themes):
            if t.name == name:
                self._index = i
                return t
        return None

    def set_by_index(self, index: int) -> ThemeDefinition:
        """Select theme by index (clamped).  Returns the new active theme."""
        self._index = max(0, min(len(self._themes) - 1, index))
        return self.active

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self, config: object) -> None:
        """Persist the active theme name via *config* (a ConfigManager)."""
        config.set("theme.active", self.active.name)  # type: ignore[union-attr]
        config.save()  # type: ignore[union-attr]

    def load(self, config: object) -> None:
        """Restore the saved theme from *config* (a ConfigManager)."""
        name = config.get("theme.active", TOKYO_NIGHT.name)  # type: ignore[union-attr]
        self.set_by_name(name)  # silently falls back to index 0 if unknown

    # ── Inspection ────────────────────────────────────────────────────────────

    @property
    def all_names(self) -> list[str]:
        """Return all theme names in order."""
        return [t.name for t in self._themes]

    @property
    def dark_themes(self) -> list[ThemeDefinition]:
        return [t for t in self._themes if t.is_dark]

    @property
    def light_themes(self) -> list[ThemeDefinition]:
        return [t for t in self._themes if not t.is_dark]

    def __len__(self) -> int:
        return len(self._themes)
