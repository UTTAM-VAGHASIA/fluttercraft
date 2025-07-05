"""
ASCII Art Definitions

This module contains ASCII art logo definitions for FlutterCraft CLI.
These logos are inspired by the GEMINI CLI design and provide a visually
distinctive branding for the command-line interface.
"""

from typing import Dict, Union

# FlutterCraft ASCII art collection
ASCII_ART: Dict[str, str] = {
    # Main FlutterCraft logo
    "main": """
 ██╗      ███████╗██╗     ██╗   ██╗████████╗████████╗███████╗██████╗  ██████╗██████╗  █████╗ ███████╗████████╗
 ╚██╗     ██╔════╝██║     ██║   ██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝
  ╚██╗    █████╗  ██║     ██║   ██║   ██║      ██║   █████╗  ██████╔╝██║     ██████╔╝███████║█████╗     ██║   
  ██╔╝    ██╔══╝  ██║     ██║   ██║   ██║      ██║   ██╔══╝  ██╔══██╗██║     ██╔══██╗██╔══██║██╔══╝     ██║   
 ██╔╝     ██║     ███████╗╚██████╔╝   ██║      ██║   ███████╗██║  ██║╚██████╗██║  ██║██║  ██║██║        ██║   
 ╚═╝      ╚═╝     ╚══════╝ ╚═════╝    ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝   
""",
    
    # Compact logo for smaller terminals
    "compact": """
 ██╗      ███████╗██╗     ██╗   ██╗████████╗████████╗███████╗██████╗    
 ╚██╗     ██╔════╝██║     ██║   ██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗    
  ╚██╗    █████╗  ██║     ██║   ██║   ██║      ██║   █████╗  ██████╔╝   
   ╚██╗   ██╔══╝  ██║     ██║   ██║   ██║      ██║   ██╔══╝  ██╔══██╗   
    ╚██╗  ██║     ███████╗╚██████╔╝   ██║      ██║   ███████╗██║  ██║   
     ╚██╗ ╚═╝     ╚══════╝ ╚═════╝    ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝   
     ██╔╝  ██████╗██████╗  █████╗ ███████╗████████╗                     
    ██╔╝  ██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝                     
   ██╔╝   ██║     ██████╔╝███████║█████╗     ██║                        
  ██╔╝    ██║     ██╔══██╗██╔══██║██╔══╝     ██║                        
 ██╔╝     ╚██████╗██║  ██║██║  ██║██║        ██║                        
 ╚═╝       ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝                        
""",
    
    # Minimal logo for very small terminals
    "minimal": """
 ███████╗██╗  ██╗   ██╗████████╗████████╗███████╗██████╗ 
 ██╔════╝██║  ██║   ██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗
 █████╗  ██║  ██║   ██║   ██║      ██║   █████╗  ██████╔╝
 ██╔══╝  ██║  ██║   ██║   ██║      ██║   ██╔══╝  ██╔══██╗
 ██║     ███████║   ██║   ██║      ██║   ███████╗██║  ██║
 ╚═╝     ╚══════╝   ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝
""",

    # Small logo for extremely constrained spaces
    "small": """
 ███████╗ ██╗     ██╗   ██╗████████╗████████╗███████╗██████╗ 
 ██╔════╝ ██║     ██║   ██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗
 █████╗   ██║     ██║   ██║   ██║      ██║   █████╗  ██████╔╝
 ██╔══╝   ██║     ██║   ██║   ██║      ██║   ██╔══╝  ██╔══██╗
 ██║      ███████╗╚██████╔╝   ██║      ██║   ███████╗██║  ██║
 ╚═╝      ╚══════╝ ╚═════╝    ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝
"""
}

def get_ascii_art(name: str = "main") -> str:
    """
    Get ASCII art by name.
    
    Args:
        name: Name of the ASCII art to retrieve
        
    Returns:
        ASCII art string
    """
    return ASCII_ART.get(name, ASCII_ART["main"])

def get_appropriate_logo(width_or_name: Union[int, str]) -> str:
    """
    Get the appropriate logo for the given terminal width or name.
    
    Args:
        width_or_name: Terminal width in characters or specific logo name
        
    Returns:
        ASCII art string
    """
    # If a string is provided, treat it as a logo name
    if isinstance(width_or_name, str):
        return get_ascii_art(width_or_name)
    
    # Otherwise, use width to determine appropriate logo
    width = width_or_name
    if width >= 100:
        return get_ascii_art("main")
    elif width >= 80:
        return get_ascii_art("compact")
    elif width >= 60:
        return get_ascii_art("minimal")
    else:
        return get_ascii_art("small")