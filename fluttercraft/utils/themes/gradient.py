"""Gradient text utilities for FlutterCraft CLI.

Provides functions to create gradient text effects using Rich library.
"""

from typing import List, Optional
from rich.text import Text
from rich.color import Color
from rich.style import Style


def hex_to_rgb(hex_color: str) -> tuple[int, ...]:
    """Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., '#FF0000' or 'FF0000')

    Returns:
        RGB tuple (r, g, b)
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i: i + 2], 16) for i in (0, 2, 4))


def interpolate_color(
    color1: tuple[int, int, int], color2: tuple[int, int, int], factor: float
) -> tuple[int, ...]:
    """Interpolate between two RGB colors.

    Args:
        color1: First RGB color
        color2: Second RGB color
        factor: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated RGB color
    """
    return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))


def create_gradient_text(
    text: str,
    colors: List[str],
    bold: bool = False,
    italic: bool = False,
) -> Text:
    """Create gradient text using Rich library.

    Args:
        text: Text to apply gradient to
        colors: List of hex colors for gradient (minimum 2)
        bold: Whether to make text bold
        italic: Whether to make text italic

    Returns:
        Rich Text object with gradient applied
    """
    if len(colors) < 2:
        colors = colors * 2  # Duplicate if only one color

    # Convert hex colors to RGB
    rgb_colors = []
    for color in colors:
        try:
            if color.startswith("#"):
                rgb_colors.append(hex_to_rgb(color))
            else:
                # Try to parse as named color
                c = Color.parse(color)
                rgb_colors.append((c.triplet.red, c.triplet.green, c.triplet.blue))
        except Exception:
            # Fallback to white if color parsing fails
            rgb_colors.append((255, 255, 255))

    if len(rgb_colors) < 2:
        rgb_colors.append(rgb_colors[0])

    result = Text()
    text_length = len(text)

    if text_length == 0:
        return result

    # Calculate color for each character
    for i, char in enumerate(text):
        # Calculate position in gradient (0.0 to 1.0)
        position = i / max(text_length - 1, 1)

        # Find which color segment we're in
        segment_count = len(rgb_colors) - 1
        segment_position = position * segment_count
        segment_index = min(int(segment_position), segment_count - 1)
        local_position = segment_position - segment_index

        # Interpolate between colors
        color1 = rgb_colors[segment_index]
        color2 = rgb_colors[min(segment_index + 1, len(rgb_colors) - 1)]
        interpolated = interpolate_color(color1, color2, local_position)

        # Create style with interpolated color
        style_attrs = []
        if bold:
            style_attrs.append("bold")
        if italic:
            style_attrs.append("italic")

        style = Style(
            color=Color.from_rgb(*interpolated),
            bold=bold,
            italic=italic,
        )

        result.append(char, style=style)

    return result


def create_gradient_multiline(
    text: str,
    colors: List[str],
    bold: bool = False,
    italic: bool = False,
) -> Text:
    """Create gradient text that works across multiple lines.

    Args:
        text: Multi-line text to apply gradient to
        colors: List of hex colors for gradient
        bold: Whether to make text bold
        italic: Whether to make text italic

    Returns:
        Rich Text object with gradient applied
    """
    lines = text.split("\n")
    result = Text()

    for i, line in enumerate(lines):
        if i > 0:
            result.append("\n")
        result.append(create_gradient_text(line, colors, bold, italic))

    return result


def apply_gradient_to_ascii(ascii_art: str, colors: List[str]) -> Text:
    """Apply gradient to ASCII art.

    Args:
        ascii_art: ASCII art string
        colors: List of hex colors for gradient

    Returns:
        Rich Text object with gradient applied to ASCII art
    """
    return create_gradient_multiline(ascii_art, colors, bold=True)
