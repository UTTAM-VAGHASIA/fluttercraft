"""ASCII art definitions for FlutterCraft CLI.

Multiple sizes of ASCII art for different terminal widths.
"""

# Full ASCII art (for wide terminals, 70+ columns)
FULL_ASCII_LOGO = """
███████╗██╗     ██╗   ██╗████████╗████████╗███████╗██████╗      ██████╗██████╗  █████╗ ███████╗████████╗   
██╔════╝██║     ██║   ██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗    ██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝   
█████╗  ██║     ██║   ██║   ██║      ██║   █████╗  ██████╔╝    ██║     ██████╔╝███████║█████╗     ██║      
██╔══╝  ██║     ██║   ██║   ██║      ██║   ██╔══╝  ██╔══██╗    ██║     ██╔══██╗██╔══██║██╔══╝     ██║      
██║     ███████╗╚██████╔╝   ██║      ██║   ███████╗██║  ██║    ╚██████╗██║  ██║██║  ██║██║        ██║      
╚═╝     ╚══════╝ ╚═════╝    ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝      
"""

# Compact ASCII art (for medium terminals, 50-70 columns)
COMPACT_ASCII_LOGO = """
███████╗██╗     ██╗   ██╗████████╗████████╗███████╗██████╗ 
██╔════╝██║     ██║   ██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗
█████╗  ██║     ██║   ██║   ██║      ██║   █████╗  ██████╔╝
██╔══╝  ██║     ██║   ██║   ██║      ██║   ██╔══╝  ██╔══██╗
██║     ███████╗╚██████╔╝   ██║      ██║   ███████╗██║  ██║
╚═╝     ╚══════╝ ╚═════╝    ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝
 ██████╗██████╗  █████╗ ███████╗████████╗
██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝
██║     ██████╔╝███████║█████╗     ██║   
██║     ██╔══██╗██╔══██║██╔══╝     ██║   
╚██████╗██║  ██║██║  ██║██║        ██║   
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝   
"""

# Tiny ASCII art (for very small terminals, <30 columns)
TINY_ASCII_LOGO = """
███████╗ ██████╗
██╔════╝██╔════╝
█████╗  ██║     
██╔══╝  ██║     
██║     ╚██████╗
╚═╝      ╚═════╝
"""


def get_ascii_width(ascii_art: str) -> int:
    """Calculate the width of ASCII art.

    Args:
        ascii_art: ASCII art string

    Returns:
        Width in characters
    """
    lines = ascii_art.strip().split("\n")
    return max(len(line) for line in lines) if lines else 0


def select_ascii_art(terminal_width: int, prefer_block: bool = False) -> str:
    """Select appropriate ASCII art based on terminal width.

    Args:
        terminal_width: Width of terminal in columns
        prefer_block: Whether to prefer block style logo

    Returns:
        ASCII art string
    """
    if terminal_width >= 120:
        return FULL_ASCII_LOGO.strip()
    elif terminal_width >= 70:
        return COMPACT_ASCII_LOGO.strip()
    else:
        return TINY_ASCII_LOGO.strip()


# Export all logos
__all__ = [
    "FULL_ASCII_LOGO",
    "COMPACT_ASCII_LOGO",
    "TINY_ASCII_LOGO",
    "get_ascii_width",
    "select_ascii_art",
]
