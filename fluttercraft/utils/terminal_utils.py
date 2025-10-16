"""Terminal utilities for FlutterCraft CLI."""

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
import subprocess
import threading
import time
import shutil
from queue import Queue, Empty

console = Console()


def _read_stream_output(stream, queue):
    """Read output from stream and put it in queue."""
    for line in iter(stream.readline, b""):
        queue.put(line.decode("utf-8", errors="replace").rstrip())
    stream.close()


def run_with_loading(
    cmd,
    status_message=None,
    shell=True,
    should_display_command=True,
    clear_on_success=True,
    show_output_on_failure=False,  # Don't show output panel on failure by default
    show_status_message=False,  # Don't show status messages by default
):
    """Run a command with a loading indicator and real-time output.

    Args:
        cmd: Command to run (list or string)
        status_message: Custom status message (defaults to "Running command...")
        shell: Whether to run command in shell
        should_display_command: Whether to display the command before running
        clear_on_success: Whether to clear the command output on success
        show_output_on_failure: Whether to keep the output panel visible on failure
        show_status_message: Whether to show status messages after command completes

    Returns:
        CompletedProcess instance with stdout and stderr
    """
    if isinstance(cmd, list):
        cmd_str = " ".join(cmd)
    else:
        cmd_str = cmd

    if should_display_command:
        console.print(f"[bold cyan]Running command:[/] {cmd_str}")

    if not status_message:
        status_message = f"[bold yellow]Running {cmd_str}, please wait...[/]"

    # Create queues for output
    stdout_queue = Queue()
    stderr_queue = Queue()

    # Combined output to preserve
    all_output = []

    # Start the process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell,
        text=False,  # We'll handle encoding manually
    )

    # Start threads to read stdout and stderr
    stdout_thread = threading.Thread(
        target=_read_stream_output, args=(process.stdout, stdout_queue)
    )
    stderr_thread = threading.Thread(
        target=_read_stream_output, args=(process.stderr, stderr_queue)
    )

    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()

    # Get terminal width for the panel
    terminal_width = shutil.get_terminal_size().columns
    panel_width = min(terminal_width - 4, 100)  # Keep some margin

    # Start a Live display
    output_lines = []

    # Track if we've collected any output at all
    has_output = False

    # Loading animation frames
    loading_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    frame_index = [0]  # Use list to make it mutable

    # Use Live display with transient=True to allow removing the panel completely
    # We'll manually manage when to show/hide it
    live = Live(
        Panel(
            f"{loading_frames[0]} {status_message}\n",
            title="Command Output",
            width=panel_width,
        ),
        console=console,
        refresh_per_second=10,
        transient=True,  # This allows the panel to be removed completely when stopped
    )
    live.start()

    try:
        # Keep track of whether we've seen any error output
        has_errors = False

        # Collect stdout and stderr as they arrive
        stdout_content = []
        stderr_content = []

        # Process still running
        while process.poll() is None:
            # Update loading animation frame
            frame_index[0] = (frame_index[0] + 1) % len(loading_frames)
            current_frame = loading_frames[frame_index[0]]

            # Check for output from stdout
            try:
                while not stdout_queue.empty():
                    line = stdout_queue.get_nowait()
                    has_output = True
                    stdout_content.append(line)
                    output_lines.append(f"[dim]{line}[/dim]")
                    all_output.append(line)
                    # Keep only the last 15 lines in the display to avoid overwhelming the terminal
                    if len(output_lines) > 15:
                        output_lines.pop(0)
            except Empty:
                pass

            # Check for output from stderr
            try:
                while not stderr_queue.empty():
                    line = stderr_queue.get_nowait()
                    has_output = True
                    stderr_content.append(line)
                    output_lines.append(f"[red]{line}[/red]")
                    all_output.append(line)
                    has_errors = True
                    # Keep only the last 15 lines in the display
                    if len(output_lines) > 15:
                        output_lines.pop(0)
            except Empty:
                pass

            # Update the panel with loading indicator
            if output_lines:
                # Show output with loading indicator at top
                content = (
                    f"[cyan]{current_frame}[/cyan] {status_message}\n\n"
                    + "\n".join(output_lines)
                )
            else:
                # Show just loading indicator
                content = f"[cyan]{current_frame}[/cyan] {status_message}"

            live.update(
                Panel(
                    content,
                    title="Command Output",
                    width=panel_width,
                )
            )

            # Small sleep to prevent CPU spinning
            time.sleep(0.1)

        # Final check for any remaining output
        for queue, content, color in [
            (stdout_queue, stdout_content, "dim"),
            (stderr_queue, stderr_content, "red"),
        ]:
            try:
                while not queue.empty():
                    line = queue.get_nowait()
                    has_output = True
                    content.append(line)
                    output_lines.append(f"[{color}]{line}[/{color}]")
                    all_output.append(line)
                    if queue == stderr_queue:
                        has_errors = True
                    # Keep only the last 15 lines
                    if len(output_lines) > 15:
                        output_lines.pop(0)
            except Empty:
                pass

        # Determine if we should keep the panel based on success, failure, and configuration
        success = process.returncode == 0 and not has_errors

        # Logic for whether to show output panel:
        # - Always show on failure (to help user debug)
        # - Hide on success if clear_on_success is True
        # - Show on success if show_output_on_failure is True (for consistency)
        should_show_panel = (
            (not success)
            or (success and not clear_on_success)
            or show_output_on_failure
        )

        if should_show_panel and (has_output or not success):
            # Build final output
            final_output = []

            # Add output lines if any
            if output_lines:
                final_output.extend(output_lines)

            # Always add status message on failure, optionally on success
            if not success:
                # On failure, always show error message
                error_msg = (
                    f"[bold red]✗ Command failed with exit code {process.returncode}[/]"
                )
                final_output.append("")
                final_output.append(error_msg)
            elif show_status_message:
                # On success, only if requested
                final_output.append("")
                final_output.append("[bold green]✓ Command completed successfully[/]")

            # If no output but command failed, show a message
            if not output_lines and not success:
                final_output.insert(0, "[dim]No output captured[/]")

            live.update(
                Panel(
                    "\n".join(final_output),
                    title="Command Output" if success else "[red]Command Failed[/red]",
                    width=panel_width,
                    border_style="red" if not success else "cyan",
                )
            )

            # Stop live display
            live.stop()

            # Print the panel permanently so it stays visible
            # (both on success and failure when we want to show output)
            if final_output:  # Only print if there's actual output
                console.print(
                    Panel(
                        "\n".join(final_output),
                        title=(
                            "[red]Command Failed[/red]"
                            if not success
                            else "Command Output"
                        ),
                        width=panel_width,
                        border_style="red" if not success else "cyan",
                    )
                )
        else:
            # Empty the panel content and stop
            live.update(Panel("", title="Command Output", width=panel_width))
            live.stop()

    finally:
        # Ensure live display is stopped if not already
        if live.is_started:
            live.stop()

    # Join threads
    stdout_thread.join()
    stderr_thread.join()

    # We no longer show any automatic status messages

    # Create a CompletedProcess-like object to return
    stdout_str = "\n".join(stdout_content)
    stderr_str = "\n".join(stderr_content)

    class CompletedProcessLike:
        def __init__(self, returncode, stdout, stderr):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    return CompletedProcessLike(process.returncode, stdout_str, stderr_str)


class OutputCapture:
    """A context manager to capture console output."""

    def __init__(self):
        self.output = []
        self._original_print = console.print

    def __enter__(self):
        def capture_print(*args, **kwargs):
            # Call original print first
            self._original_print(*args, **kwargs)

            # Capture the output
            for arg in args:
                if isinstance(arg, str):
                    self.output.append(arg)

        # Replace console.print with our capturing version
        console.print = capture_print
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original print
        console.print = self._original_print

    def get_output(self):
        """Return the captured output as a string."""
        return "\n".join(self.output)
