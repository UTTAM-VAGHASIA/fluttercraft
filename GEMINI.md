I have read and understood the entire project. Here's a summary of the project and its current implementation state.

# GEMINI.md

## Project: FlutterCraft

**Description:** FlutterCraft is a CLI tool designed to automate the setup and management of Flutter applications. It aims to streamline the development process by handling everything from project scaffolding and dependency management to backend integration and deployment preparation.

**Core Technologies:**
- **Language:** Python 3.10+
- **CLI Framework:** Typer
- **UI/Display:** Rich, pyfiglet, colorama
- **Packaging:** setuptools

### Current Implementation State

The project is in its early stages of development, with a focus on establishing the core CLI structure and integrating with the Flutter Version Manager (FVM).

#### Implemented Features:
- **Interactive CLI:** A REPL (Read-Evaluate-Print Loop) is available via the `fluttercraft start` command.
- **FVM Integration:**
    - `fvm install`: Installs FVM on the user's system (supports Windows, macOS, and Linux).
    - `fvm uninstall`: Uninstalls FVM.
- **Environment Detection:** The CLI automatically detects the user's operating system, shell, Python version, and existing Flutter/FVM installations.
- **UI/UX:** The CLI uses the Rich library to provide a visually appealing and user-friendly interface with formatted tables, colored output, and loading indicators.

#### Code Structure:
- **`main.py`:** The entry point for the Typer-based CLI application.
- **`commands/start.py`:** Implements the interactive REPL and contains the logic for all CLI commands.
- **`utils/`:** A collection of utility modules for platform detection and display formatting.

### Future Development (Roadmap)

The project has a clear roadmap for future development, which includes:
- **Enhanced FVM Management:** Adding functionality to list, remove and set up specific Flutter versions.
- **Project Creation Wizard:** An interactive `create` command to scaffold new Flutter projects with various configurations.
- **Backend Integration:** Support for integrating with Firebase and Supabase.
- **GitHub Automation:** Automating the creation of GitHub repositories for new projects.
- **App Icon Generation:** A feature to automatically generate app icons for all supported platforms.

### How to Run

1.  **Installation:**
    ```bash
    pip install -e .
    ```
2.  **Start the CLI:**
    ```bash
    fluttercraft start
    ```
