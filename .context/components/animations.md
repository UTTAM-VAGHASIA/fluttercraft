# Animation System

The Animation System provides a unified way to create smooth, professional CLI animations in FlutterCraft.

## Components

### AnimationEngine

`fluttercraft.utils.animations.engine.AnimationEngine`

The core driver for animations. It handles the render loop, timing, and frame updates using `rich.live`.

**Key Methods:**
- `animate(renderable_factory, duration, easing, transient)`: generic animation loop.
- `slide_in(renderable, direction="left", duration=0.3, start_offset=20)`: Slide elements into view from a direction.
- `wipe_in(text, duration=0.5, vertical=True)`: Reveal text line-by-line (vertical) or char-by-char (horizontal).
- `fade_in(text, duration)`: (Planned) Fade in text.

### Effects

`fluttercraft.utils.animations.effects`

Contains standard easing functions and effect definitions.

**Available Easings:**
- `linear`
- `ease_in_quad`, `ease_out_quad`, `ease_in_out_quad`
- `ease_in_cubic`, `ease_out_cubic`, `ease_in_out_cubic`
- `pulse_effect`

## Usage

### Generic Animation
```python
from fluttercraft.utils.animations.engine import AnimationEngine
from fluttercraft.utils.animations import effects
from rich.text import Text

def render_frame(progress):
    return Text("Hello", style=f"rgb({int(255*progress)},0,0)")

engine = AnimationEngine()
engine.animate(render_frame, duration=1.0, easing=effects.ease_out_cubic)
```

### Slide In
```python
# Slide in a panel from the left
engine.slide_in(my_panel, direction="left", duration=0.3)
```

### Wipe In (Text Reveal)
```python
# Reveal text line by line
engine.wipe_in(my_large_text, duration=0.5, vertical=True)
```

## Design Principles

- **Sleek & Subtle**: Animations should be fast (200-300ms) and non-intrusive.
- **Performance**: Maintain 30fps minimum.
- **Respect**: Honor "reduced motion" preferences (future).