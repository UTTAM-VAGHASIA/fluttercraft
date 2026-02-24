from __future__ import annotations

import pytest

from fluttercraft.themes.theme_manager import (
    ALL_THEMES,
    TOKYO_NIGHT,
    DRACULA,
    NORD,
    ThemeDefinition,
    ThemeManager,
    generate_theme_css,
)


# ── ThemeDefinition tests ─────────────────────────────────────────────────────


def test_tokyo_night_is_dark():
    assert TOKYO_NIGHT.is_dark is True


def test_dracula_is_dark():
    assert DRACULA.is_dark is True


def test_all_themes_count():
    assert len(ALL_THEMES) == 13


def test_dark_themes_count():
    dark = [t for t in ALL_THEMES if t.is_dark]
    assert len(dark) == 7


def test_light_themes_count():
    light = [t for t in ALL_THEMES if not t.is_dark]
    assert len(light) == 6


def test_all_themes_have_names():
    for theme in ALL_THEMES:
        assert theme.name != ""


def test_all_themes_have_valid_bg_color():
    for theme in ALL_THEMES:
        assert theme.bg.startswith("#")
        assert len(theme.bg) == 7


def test_all_themes_have_valid_accent_color():
    for theme in ALL_THEMES:
        assert theme.accent.startswith("#")


def test_all_themes_have_valid_footer_colors():
    for theme in ALL_THEMES:
        assert theme.footer_bg.startswith("#")
        assert theme.footer_fg.startswith("#")


def test_all_theme_names_are_unique():
    names = [t.name for t in ALL_THEMES]
    assert len(names) == len(set(names))


def test_theme_definition_dataclass_fields():
    assert TOKYO_NIGHT.bg == "#1a1b26"
    assert TOKYO_NIGHT.accent == "#7aa2f7"
    assert TOKYO_NIGHT.footer_bg == "#7aa2f7"
    assert TOKYO_NIGHT.footer_fg == "#1a1b26"


# ── generate_theme_css tests ──────────────────────────────────────────────────


def test_generate_theme_css_contains_name():
    css = generate_theme_css(TOKYO_NIGHT)
    assert "Tokyo Night" in css


def test_generate_theme_css_contains_bg():
    css = generate_theme_css(TOKYO_NIGHT)
    assert TOKYO_NIGHT.bg in css


def test_generate_theme_css_contains_accent():
    css = generate_theme_css(TOKYO_NIGHT)
    assert TOKYO_NIGHT.accent in css


def test_generate_theme_css_has_variable_prefix():
    css = generate_theme_css(TOKYO_NIGHT)
    assert "$theme-bg:" in css
    assert "$theme-accent:" in css


def test_generate_theme_css_returns_string():
    assert isinstance(generate_theme_css(DRACULA), str)


def test_generate_theme_css_different_themes_differ():
    css1 = generate_theme_css(TOKYO_NIGHT)
    css2 = generate_theme_css(DRACULA)
    assert css1 != css2


# ── ThemeManager tests ────────────────────────────────────────────────────────


def test_theme_manager_default_is_tokyo_night():
    mgr = ThemeManager()
    assert mgr.active.name == "Tokyo Night"


def test_theme_manager_len():
    mgr = ThemeManager()
    assert len(mgr) == 13


def test_theme_manager_all_names_length():
    mgr = ThemeManager()
    assert len(mgr.all_names) == 13


def test_theme_manager_next_advances():
    mgr = ThemeManager()
    first = mgr.active.name
    mgr.next()
    assert mgr.active.name != first


def test_theme_manager_next_wraps_around():
    mgr = ThemeManager()
    for _ in range(13):
        mgr.next()
    assert mgr.active.name == "Tokyo Night"


def test_theme_manager_prev_goes_back():
    mgr = ThemeManager()
    mgr.next()
    second = mgr.active.name
    mgr.prev()
    assert mgr.active.name == "Tokyo Night"


def test_theme_manager_prev_wraps_around():
    mgr = ThemeManager()
    mgr.prev()
    assert mgr.active.name == ALL_THEMES[-1].name


def test_theme_manager_set_by_name_found():
    mgr = ThemeManager()
    result = mgr.set_by_name("Dracula")
    assert result is not None
    assert mgr.active.name == "Dracula"


def test_theme_manager_set_by_name_not_found():
    mgr = ThemeManager()
    result = mgr.set_by_name("Nonexistent Theme")
    assert result is None
    assert mgr.active.name == "Tokyo Night"  # unchanged


def test_theme_manager_set_by_index():
    mgr = ThemeManager()
    mgr.set_by_index(2)
    assert mgr.active_index == 2
    assert mgr.active.name == ALL_THEMES[2].name


def test_theme_manager_set_by_index_clamps_high():
    mgr = ThemeManager()
    mgr.set_by_index(999)
    assert mgr.active_index == len(ALL_THEMES) - 1


def test_theme_manager_set_by_index_clamps_low():
    mgr = ThemeManager()
    mgr.set_by_index(-5)
    assert mgr.active_index == 0


def test_theme_manager_dark_themes():
    mgr = ThemeManager()
    assert len(mgr.dark_themes) == 7
    assert all(t.is_dark for t in mgr.dark_themes)


def test_theme_manager_light_themes():
    mgr = ThemeManager()
    assert len(mgr.light_themes) == 6
    assert all(not t.is_dark for t in mgr.light_themes)


def test_theme_manager_custom_themes():
    custom = [TOKYO_NIGHT, DRACULA]
    mgr = ThemeManager(themes=custom)
    assert len(mgr) == 2
    mgr.next()
    assert mgr.active.name == "Dracula"
    mgr.next()
    assert mgr.active.name == "Tokyo Night"


def test_theme_manager_save_and_load():
    """save() and load() round-trip via a simple dict-backed config mock."""

    class _MockConfig:
        def __init__(self):
            self._store: dict = {}

        def set(self, key: str, value) -> None:
            self._store[key] = value

        def get(self, key: str, default=None):
            return self._store.get(key, default)

        def save(self) -> None:
            pass

    config = _MockConfig()
    mgr = ThemeManager()
    mgr.set_by_name("Nord")
    mgr.save(config)

    mgr2 = ThemeManager()
    mgr2.load(config)
    assert mgr2.active.name == "Nord"


def test_theme_manager_load_unknown_name_stays_default():
    class _MockConfig:
        def get(self, key, default=None):
            return "Unknown Theme XYZ"
        def set(self, *a, **k): pass
        def save(self): pass

    mgr = ThemeManager()
    mgr.load(_MockConfig())
    # set_by_name returns None for unknown → index stays 0
    assert mgr.active.name == "Tokyo Night"
