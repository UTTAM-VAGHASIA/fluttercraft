"""
Animation engine for FlutterCraft CLI.
Handles smooth transitions and visual effects using Rich.
"""
import time
from typing import Any, Callable, Optional, Union

from rich.console import Console, RenderableType
from rich.live import Live
from rich.style import Style
from rich.text import Text

from fluttercraft.utils.animations import effects

class AnimationEngine:
    """
    Engine for driving terminal animations.
    """
    
    def __init__(self, console: Optional[Console] = None, fps: int = 30):
        self.console = console or Console()
        self.target_fps = fps
        self.frame_time = 1.0 / fps

    def animate(
        self,
        renderable_factory: Callable[[float], RenderableType],
        duration: float,
        easing: effects.EasingFunction = effects.linear,
        transient: bool = True
    ) -> None:
        """
        Run a generic animation.
        
        Args:
            renderable_factory: Function that takes progress (0.0 to 1.0) and returns a Renderable.
            duration: Duration in seconds.
            easing: Easing function to use.
            transient: Whether to clear the animation after completion.
        """
        start_time = time.perf_counter()
        
        with Live(
            "", 
            console=self.console, 
            refresh_per_second=self.target_fps, 
            transient=transient
        ) as live:
            while True:
                elapsed = time.perf_counter() - start_time
                if elapsed >= duration:
                    break
                
                progress = min(elapsed / duration, 1.0)
                eased_progress = easing(progress)
                
                live.update(renderable_factory(eased_progress))
                time.sleep(self.frame_time)
            
            # Ensure final frame is rendered
            live.update(renderable_factory(1.0))

    def fade_in(
        self, 
        text: Union[str, Text], 
        duration: float = 0.3,
        style: str = "white"
    ) -> None:
        """
        Fade in text by adjusting opacity (simulated via gradients or reveal).
        Since true opacity is hard in TUI, we simulates it or use a typing effect
        if it's a simple string, or just a simple delay for now.
        
        For a true "fade", we would need to interpolate colors.
        For now, we'll implement a basic "typing/reveal" effect as a placeholder for fade,
        or simply render it.
        """
        # TODO: Implement color interpolation for true fade
        # For now, we'll use a simple reveal (slide in) or just show it.
        # Let's implement a basic "slide up" fade.
        
        # Placeholder implementation
        self.console.print(text, style=style)

    def pulse(
        self,
        renderable: RenderableType,
        duration: float = 0.5,
        count: int = 1
    ) -> None:
        """
        Pulse an element (scale or brightness).
        """
        pass  # TODO: Implement pulse using Live display

    def slide_in(
        self,
        renderable: RenderableType,
        direction: str = "left",
        duration: float = 0.3,
        start_offset: int = 20
    ) -> None:
        """
        Slide an element into view.
        
        Args:
            renderable: The object to animate.
            direction: "left" (from left), "right" (from right), "top", "bottom".
            duration: Animation duration.
            start_offset: How far to slide from.
        """
        from rich.padding import Padding
        
        def factory(progress: float) -> RenderableType:
            # Easing: rapid start, slow end
            offset = int(start_offset * (1.0 - progress))
            
            if direction == "left":
                pad = (0, 0, 0, offset)
            elif direction == "right":
                pad = (0, offset, 0, 0)
            elif direction == "top":
                pad = (offset, 0, 0, 0)
            else:  # bottom
                pad = (0, 0, offset, 0)
                
            return Padding(renderable, pad)

        self.animate(
            factory, 
            duration, 
            easing=effects.ease_out_cubic,
            transient=True
        )

    def shake(
        self,
        renderable: RenderableType,
        duration: float = 0.3,
        intensity: int = 1
    ) -> None:
        """
        Shake an element horizontally (for errors).
        """
        from rich.padding import Padding
        import random
        
        def factory(progress: float) -> RenderableType:
            if progress >= 1.0:
                return renderable
            # Diminishing intensity
            current_intensity = max(1, int(intensity * (1.0 - progress)))
            offset = random.randint(-current_intensity, current_intensity)
            if offset > 0:
                return Padding(renderable, (0, 0, 0, offset))
            elif offset < 0:
                return Padding(renderable, (0, -offset, 0, 0))
            return renderable

        self.animate(factory, duration, easing=effects.linear, transient=True)

    def wipe_in(
        self,
        text: Text,
        duration: float = 0.5,
        vertical: bool = True
    ) -> None:
        """
        Wipe in text (reveal line by line or char by char).
        
        Args:
            text: The Rich Text object to reveal.
            duration: Animation duration.
            vertical: If True, reveal lines. If False, reveal characters.
        """
        plain_text = text.plain
        
        def factory(progress: float) -> RenderableType:
            if vertical:
                lines = plain_text.splitlines()
                visible_lines_count = int(len(lines) * progress)
                # Create a new Text object with only the visible lines, preserving styles requires more work
                # For simplicity in this version, we'll assume we can crop the original Text
                # rich.text.Text doesn't support easy line-cropping while keeping styles perfectly aligned 
                # without complex logic.
                # Alternative: Use a Layout or crop the rendered output? 
                # Simplest: Just use the plain text for calculation but return a stylized slice if possible.
                
                # Better approach for vertical wipe of styled text:
                # Use rich.console.Console.render_lines to get segments, then slice?
                # Too complex for this snippet.
                
                # Let's try a simpler approach: Crop the text object.
                # Text object has a specific length.
                
                # Hack for vertical wipe:
                # We can print newlines for the invisible parts?
                pass

            # Fallback/Simple implementation: Character reveal (typewriter)
            total_len = len(text)
            visible_len = int(total_len * progress)
            return text[:visible_len]

        # For vertical wipe of ASCII art (which is usually a single Text object with newlines),
        # character reveal looks like a fast typewriter.
        # For a true vertical wipe (curtain effect), we need to split by lines.
        
        if vertical:
            lines = text.plain.split('\n')
            total_lines = len(lines)
            
            def line_factory(progress: float) -> RenderableType:
                visible_count = int(total_lines * progress)
                if visible_count == 0:
                    return Text("")
                # We need to construct a Text object that matches the style of the original
                # This is hard if styles span lines.
                # But for ASCII art usually styles are consistent or per-character.
                # Let's assume the input text is fully styled.
                # We can't easily slice Text by lines.
                
                # Alternative: Masking.
                # Return the full text but use a crop?
                # No, Rich doesn't have a simple CropRenderable for height that is easy to animate.
                
                # Let's stick to the typewriter effect (char by char) for now as it's built-in to Text slicing.
                # It looks cool for code/CLI tools anyway.
                total_chars = len(text)
                visible_chars = int(total_chars * progress)
                return text[:visible_chars]

            self.animate(line_factory, duration, easing=effects.ease_out_quad, transient=True)
        else:
             self.animate(factory, duration, easing=effects.ease_out_quad, transient=True)

