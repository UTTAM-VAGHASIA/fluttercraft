"""Start command for FlutterCraft CLI."""

from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live
from rich.panel import Panel
import platform
import os
import sys
import subprocess
import re
import time
import threading
from queue import Queue, Empty
import shutil

from fluttercraft.utils.platform_utils import get_platform_info

console = Console()


def _read_stream_output(stream, queue):
    """Read output from stream and put it in queue."""
    for line in iter(stream.readline, b''):
        queue.put(line.decode('utf-8', errors='replace').rstrip())
    stream.close()


def run_with_loading(
    cmd, 
    status_message=None, 
    shell=True, 
    should_display_command=True, 
    clear_on_success=True, 
    show_output_on_failure=False,  # Don't show output panel on failure by default
    show_status_message=False     # Don't show status messages by default
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
        target=_read_stream_output, 
        args=(process.stdout, stdout_queue)
    )
    stderr_thread = threading.Thread(
        target=_read_stream_output, 
        args=(process.stderr, stderr_queue)
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
    
    # Use Live display with transient=True to allow removing the panel completely
    # We'll manually manage when to show/hide it
    live = Live(
        Panel(f"{status_message}\n", title="Command Output", width=panel_width),
        console=console,
        refresh_per_second=10,
        transient=True  # This allows the panel to be removed completely when stopped
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
                    live.update(Panel("\n".join(output_lines), title="Command Output", width=panel_width))
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
                    live.update(Panel("\n".join(output_lines), title="Command Output", width=panel_width))
            except Empty:
                pass
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.1)
        
        # Final check for any remaining output
        for queue, content, color in [(stdout_queue, stdout_content, "dim"), (stderr_queue, stderr_content, "red")]:
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
        # - Hide on success if clear_on_success is True
        # - Show on failure if show_output_on_failure is True
        should_hide_panel = (success and clear_on_success) or (not success and not show_output_on_failure)
        
        if not should_hide_panel and has_output:
            # Only add status message if requested
            if show_status_message:
                status = "[bold green]Command completed successfully[/]" if success else f"[bold red]Command failed with exit code {process.returncode}[/]"
                final_output = output_lines + [status]
            else:
                final_output = output_lines
                
            live.update(Panel("\n".join(final_output), title="Command Output", width=panel_width))
            
            # Brief pause to ensure the panel is visible
            time.sleep(0.2)
        else:
            # Empty the panel content
            live.update(Panel("", title="Command Output", width=panel_width))
    
    finally:
        # Always stop the live display to clean up
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


def check_flutter_version():
    """Check if Flutter is installed and get version information."""
    flutter_installed = False
    current_version = None
    latest_version = None

    try:
        # Check if Flutter is installed and get version
        flutter_version_process = run_with_loading(
            ["flutter", "--version"],
            status_message="[bold yellow]Checking Flutter installation...[/]",
            should_display_command=False,
            clear_on_success=True,
            show_output_on_failure=False,
        )

        if flutter_version_process.returncode == 0:
            flutter_installed = True
            # Parse version from output (e.g., "Flutter 3.32.0 • channel stable")
            version_match = re.search(
                r"Flutter (\d+\.\d+\.\d+)", flutter_version_process.stdout
            )
            if version_match:
                current_version = version_match.group(1)

            # Check for the latest version
            upgrade_process = run_with_loading(
                ["flutter", "upgrade", "--verify-only"],
                status_message="[bold yellow]Checking for Flutter updates...[/]",
                should_display_command=False,
                clear_on_success=True,
                show_output_on_failure=False,
            )

            if upgrade_process.returncode == 0:
                output = upgrade_process.stdout

                # Case 1: When there's an update available
                if "A new version of Flutter is available" in output:
                    # Latest version check
                    latest_match = re.search(
                        r"The latest version: (\d+\.\d+\.\d+)", output
                    )
                    if latest_match:
                        latest_version = latest_match.group(1)

                    # Current version check (from the upgrade output)
                    # This is more accurate than the version from flutter --version
                    current_match = re.search(
                        r"Your current version: (\d+\.\d+\.\d+)", output
                    )
                    if current_match:
                        current_version = current_match.group(1)

                # Case 2: When Flutter is already up to date
                elif "Flutter is already up to date" in output:
                    # In this case, the current version is also the latest version
                    version_match = re.search(r"Flutter (\d+\.\d+\.\d+) •", output)
                    if version_match:
                        current_version = version_match.group(1)
                        latest_version = current_version  # Same version
    except FileNotFoundError:
        flutter_installed = False

    return {
        "installed": flutter_installed,
        "current_version": current_version,
        "latest_version": latest_version,
    }


def check_fvm_version():
    """Check if FVM is installed and get version information."""
    fvm_installed = False
    fvm_version = None

    try:
        # Check if FVM is installed and get version
        fvm_version_process = run_with_loading(
            ["fvm", "--version"],
            status_message="[bold yellow]Checking FVM installation...[/]",
            should_display_command=False,
            clear_on_success=True,
            show_output_on_failure=False,
        )

        if fvm_version_process.returncode == 0:
            fvm_installed = True
            # Clean up version string (remove whitespace)
            fvm_version = fvm_version_process.stdout.strip()
    except FileNotFoundError:
        fvm_installed = False

    return {"installed": fvm_installed, "version": fvm_version}


def check_chocolatey_installed():
    """Check if Chocolatey is installed on Windows."""
    choco_installed = False

    try:
        # Check if Chocolatey is installed by running choco --version
        choco_version_process = run_with_loading(
            ["choco", "--version"],
            status_message="[bold yellow]Checking Chocolatey installation...[/]",
            should_display_command=False,
            clear_on_success=True,
            show_output_on_failure=False,
        )

        if choco_version_process.returncode == 0:
            choco_installed = True
            version = choco_version_process.stdout.strip()
            return {"installed": True, "version": version}
    except FileNotFoundError:
        pass

    return {"installed": False, "version": None}


def fvm_install_command():
    """
    Install Flutter Version Manager (FVM) based on the platform.
    For Windows: Uses Chocolatey
    For macOS/Linux: Uses curl installation script
    """
    # First check if FVM is already installed
    fvm_info = check_fvm_version()
    
    if fvm_info["installed"]:
        console.print(f"[bold green]FVM is already installed (version: {fvm_info['version']})[/]")
        return

    console.print("[bold blue]Installing Flutter Version Manager (FVM)...[/]")
    
    # Get platform information
    platform_info = get_platform_info()
    
    # Windows installation (using Chocolatey)
    if platform_info["system"].lower().startswith("windows"):
        # Check if Chocolatey is installed
        choco_info = check_chocolatey_installed()
        
        if not choco_info["installed"]:
            console.print("[bold yellow]Chocolatey package manager is required but not installed.[/]")
            install_choco = Prompt.ask(
                "[bold yellow]Would you like to install Chocolatey? (requires admin privileges)[/]", 
                choices=["y", "n"], 
                default="y"
            )
            
            if install_choco.lower() != "y":
                console.print("[red]FVM installation aborted. Chocolatey is required to install FVM on Windows.[/]")
                return
                
            console.print("[bold yellow]Installing Chocolatey. This requires administrative privileges...[/]")
            console.print("[bold yellow]Please allow the UAC prompt if it appears...[/]")
            
            # Command to install Chocolatey
            choco_install_cmd = (
                "Set-ExecutionPolicy Bypass -Scope Process -Force; iwr https://community.chocolatey.org/install.ps1 -UseBasicParsing | iex"
            )
            
            # Need to run as admin
            # Use PowerShell's Start-Process with -Verb RunAs to request elevation
            admin_cmd = f'powershell -Command "Start-Process powershell -ArgumentList \'-NoProfile -ExecutionPolicy Bypass -Command {choco_install_cmd}\' -Verb RunAs -Wait"'
            
            result = run_with_loading(
                admin_cmd,
                status_message="[bold yellow]Installing Chocolatey package manager...[/]",
                clear_on_success=True,
                show_output_on_failure=True,
            )
            
            # Check if installation was successful
            choco_info = check_chocolatey_installed()
            if not choco_info["installed"]:
                console.print("[bold red]Failed to install Chocolatey. Please install it manually.[/]")
                return
            else:
                console.print(f"[bold green]Chocolatey installed successfully (version: {choco_info['version']})![/]")
        
        # Install FVM using Chocolatey
        console.print("[bold yellow]Installing FVM using Chocolatey...[/]")
        console.print("[bold yellow]This requires administrative privileges. Please allow the UAC prompt if it appears...[/]")
        
        # Use PowerShell's Start-Process with -Verb RunAs to request elevation
        admin_cmd = 'powershell -Command "Start-Process powershell -ArgumentList \'-NoProfile -ExecutionPolicy Bypass -Command choco install fvm -y\' -Verb RunAs -Wait"'
        
        result = run_with_loading(
            admin_cmd,
            status_message="[bold yellow]Installing FVM via Chocolatey...[/]",
            clear_on_success=True,
            show_output_on_failure=True,
        )
        
        # Verify installation
        fvm_info = check_fvm_version()
        if fvm_info["installed"]:
            console.print(f"[bold green]FVM installed successfully (version: {fvm_info['version']})![/]")
        else:
            console.print("[bold red]Failed to install FVM. Please try installing it manually.[/]")
            console.print("[yellow]You can try: choco install fvm -y[/]")
    
    # macOS and Linux installation (using curl)
    else:
        console.print("[bold yellow]Installing FVM using curl...[/]")
        
        curl_cmd = "curl -fsSL https://fvm.app/install.sh | bash"
        
        result = run_with_loading(
            curl_cmd,
            status_message="[bold yellow]Installing FVM via curl...[/]",
            clear_on_success=True,
            show_output_on_failure=True,
        )
        
        if result.returncode != 0:
            console.print("[bold red]Failed to install FVM. Error:[/]")
            console.print(result.stderr)
            console.print("[yellow]You can try installing manually: curl -fsSL https://fvm.app/install.sh | bash[/]")
            return
        
        # Verify installation
        fvm_info = check_fvm_version()
        if fvm_info["installed"]:
            console.print(f"[bold green]FVM installed successfully (version: {fvm_info['version']})![/]")
        else:
            console.print("[bold yellow]FVM may have been installed but needs a terminal restart to be detected.[/]")
            console.print("[yellow]Please restart your terminal and run 'fvm --version' to verify installation.[/]")


def fvm_uninstall_command():
    """
    Uninstall Flutter Version Manager (FVM) based on the platform.
    For Windows: Uses Chocolatey
    For macOS/Linux: Uses install.sh --uninstall
    
    Optionally removes cached Flutter versions with 'fvm destroy' first.
    """
    # First check if FVM is installed
    fvm_info = check_fvm_version()
    
    if not fvm_info["installed"]:
        console.print("[bold yellow]FVM is not installed. Nothing to uninstall.[/]")
        return

    console.print(f"[bold blue]Flutter Version Manager (FVM) version {fvm_info['version']} is installed.[/]")
    
    # Ask if user wants to remove cached Flutter versions
    remove_cache = Prompt.ask(
        "[bold yellow]Do you want to remove all cached Flutter versions before uninstalling? (recommended)[/]",
        choices=["y", "n"],
        default="y"
    )
    
    if remove_cache.lower() == "y":
        console.print("[bold yellow]Removing cached Flutter versions...[/]")
        
        # For 'fvm destroy', we can't use run_with_loading directly because it requires interactive input
        # Instead we'll handle the process differently to automatically provide "y" to the prompt
        try:
            # Use subprocess directly to handle interactive input
            console.print("[bold yellow]Running 'fvm destroy' and automatically confirming...[/]")
            
            # Check platform for appropriate command
            platform_info = get_platform_info()
            
            if platform_info["system"].lower().startswith("windows"):
                # On Windows, use echo y | fvm destroy
                destroy_cmd = "echo y | fvm destroy"
                shell = True
            else:
                # On Unix-like systems, use echo y | fvm destroy or printf "y\n" | fvm destroy
                destroy_cmd = "printf 'y\\n' | fvm destroy"
                shell = True
            
            # Execute the command with output displayed
            destroy_result = run_with_loading(
                destroy_cmd,
                status_message="[bold yellow]Running 'fvm destroy'...[/]",
                shell=shell,
                clear_on_success=True,
                show_output_on_failure=True,
            )
            
            if destroy_result.returncode == 0:
                console.print("[bold green]Successfully removed all cached Flutter versions.[/]")
            else:
                console.print("[bold red]Failed to remove cached Flutter versions.[/]")
                console.print(destroy_result.stderr)
                
                # Ask if the user wants to continue with uninstallation
                continue_uninstall = Prompt.ask(
                    "[bold yellow]Do you want to continue with FVM uninstallation?[/]",
                    choices=["y", "n"],
                    default="y"
                )
                
                if continue_uninstall.lower() != "y":
                    console.print("[yellow]FVM uninstallation aborted.[/]")
                    return
        except Exception as e:
            console.print(f"[bold red]Error when removing cached Flutter versions: {str(e)}[/]")
            
            # Ask if the user wants to continue with uninstallation despite the error
            continue_uninstall = Prompt.ask(
                "[bold yellow]Do you want to continue with FVM uninstallation?[/]",
                choices=["y", "n"],
                default="y"
            )
            
            if continue_uninstall.lower() != "y":
                console.print("[yellow]FVM uninstallation aborted.[/]")
                return
    
    # Get platform information
    platform_info = get_platform_info()
    
    # Windows uninstallation (using Chocolatey)
    if platform_info["system"].lower().startswith("windows"):
        # Check if Chocolatey is installed
        choco_info = check_chocolatey_installed()
        
        if not choco_info["installed"]:
            console.print("[bold yellow]Chocolatey is not installed. Cannot use choco to uninstall FVM.[/]")
            console.print("[yellow]Please uninstall FVM manually.[/]")
            return
                
        console.print("[bold yellow]Uninstalling FVM using Chocolatey...[/]")
        console.print("[bold yellow]This requires administrative privileges. Please allow the UAC prompt if it appears...[/]")
        
        # Use PowerShell's Start-Process with -Verb RunAs to request elevation
        admin_cmd = 'powershell -Command "Start-Process powershell -ArgumentList \'-NoProfile -ExecutionPolicy Bypass -Command choco uninstall fvm -y\' -Verb RunAs -Wait"'
        
        result = run_with_loading(
            admin_cmd,
            status_message="[bold yellow]Uninstalling FVM via Chocolatey...[/]",
            clear_on_success=True,
            show_output_on_failure=True,
        )
        
        # Verify uninstallation
        fvm_info_after = check_fvm_version()
        if not fvm_info_after["installed"]:
            console.print("[bold green]FVM uninstalled successfully![/]")
        else:
            console.print("[bold red]Failed to uninstall FVM. Please try uninstalling it manually.[/]")
            console.print("[yellow]You can try: choco uninstall fvm -y[/]")
    
    # macOS and Linux uninstallation
    else:
        console.print("[bold yellow]Uninstalling FVM...[/]")
        
        # Try to locate the install.sh script (usually in ~/.fvm/bin)
        install_script_path = os.path.expanduser("~/.fvm/bin/install.sh")
        
        if not os.path.exists(install_script_path):
            console.print("[bold yellow]Cannot find the FVM install script.[/]")
            console.print("[yellow]Attempting to download the uninstaller...[/]")
            
            download_cmd = "curl -fsSL https://fvm.app/install.sh -o /tmp/fvm_uninstall.sh && chmod +x /tmp/fvm_uninstall.sh"
            download_result = run_with_loading(
                download_cmd,
                status_message="[bold yellow]Downloading FVM installer/uninstaller...[/]",
                clear_on_success=True,
                show_output_on_failure=True,
            )
            
            if download_result.returncode == 0:
                install_script_path = "/tmp/fvm_uninstall.sh"
            else:
                console.print("[bold red]Failed to download FVM uninstaller.[/]")
                console.print("[yellow]Please try uninstalling manually with: curl -fsSL https://fvm.app/install.sh | bash -- --uninstall[/]")
                return
        
        # Run the uninstall command
        uninstall_cmd = f"{install_script_path} --uninstall"
        
        result = run_with_loading(
            uninstall_cmd,
            status_message="[bold yellow]Uninstalling FVM...[/]",
            clear_on_success=True,
            show_output_on_failure=True,
        )
        
        # Verify uninstallation
        fvm_info_after = check_fvm_version()
        if not fvm_info_after["installed"]:
            console.print("[bold green]FVM uninstalled successfully![/]")
        else:
            console.print("[bold yellow]FVM may still be installed or needs a terminal restart to reflect changes.[/]")
            console.print("[yellow]Please restart your terminal and check with 'fvm --version'.[/]")


def start_command():
    """
    Start the interactive CLI session.
    This is the main command that users will use to start creating Flutter apps.
    """
    # Get platform information using the utility function
    platform_info = get_platform_info()

    console.print("[bold green]FlutterCraft CLI started![/]")
    console.print(f"[bold blue]Platform: {platform_info['system']}[/]")
    console.print(f"[bold blue]Shell: {platform_info['shell']}[/]")
    console.print(f"[bold blue]Python version: {platform_info['python_version']}[/]")

    # Check Flutter installation and version
    flutter_info = check_flutter_version()

    if flutter_info["installed"]:
        if flutter_info["current_version"]:
            version_str = (
                f"[bold green]Flutter version: {flutter_info['current_version']}"
            )

            if flutter_info["latest_version"]:
                if flutter_info["current_version"] != flutter_info["latest_version"]:
                    version_str += f" [yellow](Latest version available: {flutter_info['latest_version']})[/]"
            else:
                version_str += " [green](up to date)[/]"

            console.print(version_str)
        else:
            console.print(
                "[yellow]Flutter is installed, but version could not be determined[/]"
            )
    else:
        console.print("[bold red]Flutter is not installed[/]")

    # Check FVM installation
    fvm_info = check_fvm_version()

    if fvm_info["installed"]:
        console.print(f"[bold green]FVM version: {fvm_info['version']}[/]")
    else:
        console.print("[yellow]FVM is not installed[/]")

    console.print("[bold]Enter commands or type 'exit' or 'quit' or 'q' to quit[/]")

    # Simple REPL for demonstration
    while True:
        command = Prompt.ask("[bold cyan]fluttercraft>[/]")

        if command.lower() in ["exit", "quit", "q"]:
            console.print("[yellow]Thank you for using FlutterCraft! Goodbye![/]")
            break
        elif command.lower() in ["help", "h"]:
            console.print("[green]Available commands:[/]")
            console.print("[bold cyan]Implemented commands:[/]")
            console.print("  [bold]fvm install[/] - Install Flutter Version Manager")
            console.print("  [bold]fvm uninstall[/] - Uninstall Flutter Version Manager")
            console.print("  [bold]help, h[/] - Show this help message")
            console.print("  [bold]exit, quit, q[/] - Exit the CLI")
            
            console.print("\n[bold yellow]Coming in future updates:[/]")
            console.print("  [bold]create[/] - Create a new Flutter project")
            console.print("  [bold]flutter install[/] - Install Flutter")
            console.print("  [bold]fvm setup[/] - Setup Flutter Version Manager")
            console.print("  [bold]flutter version[/] - Check and switch Flutter versions")
        elif command.lower() == "create":
            console.print(
                "[yellow]In a future update, this would start the Flutter app "
                "creation wizard![/]"
            )
        elif command.lower() == "fvm install":
            fvm_install_command()
        elif command.lower() == "fvm uninstall":
            fvm_uninstall_command()
        elif command.lower().startswith("flutter"):
            console.print(
                "[yellow]In a future update, this would handle Flutter commands![/]"
            )
        elif command.lower().startswith("fvm"):
            if command.lower() == "fvm install":
                # Already handled above
                pass
            elif command.lower() == "fvm uninstall":
                # Already handled above
                pass
            else:
                console.print(
                    "[yellow]In a future update, this would handle additional FVM commands![/]"
                )
        else:
            console.print(f"[red]Unknown command: {command}[/]")
            console.print("Type 'help' to see available commands")
