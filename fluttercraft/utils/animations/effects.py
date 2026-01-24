"""
Animation effects and easing functions for FlutterCraft.
"""
import math
from typing import Callable

# Type alias for easing functions
EasingFunction = Callable[[float], float]

def linear(t: float) -> float:
    """Linear easing: t"""
    return t

def ease_in_quad(t: float) -> float:
    """Quadratic ease-in: t^2"""
    return t * t

def ease_out_quad(t: float) -> float:
    """Quadratic ease-out: 2t - t^2"""
    return t * (2 - t)

def ease_in_out_quad(t: float) -> float:
    """Quadratic ease-in-out"""
    return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t

def ease_in_cubic(t: float) -> float:
    """Cubic ease-in: t^3"""
    return t * t * t

def ease_out_cubic(t: float) -> float:
    """Cubic ease-out: --t^3 + 1"""
    t -= 1
    return t * t * t + 1

def ease_in_out_cubic(t: float) -> float:
    """Cubic ease-in-out"""
    t *= 2
    if t < 1:
        return 0.5 * t * t * t
    t -= 2
    return 0.5 * (t * t * t + 2)

def pulse_effect(t: float) -> float:
    """Pulse effect: 0 -> 1 -> 0"""
    return 0.5 * (1 - math.cos(2 * math.pi * t))
