# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-07-01

### Added

- Added fvm commands: `fvm install` and `fvm uninstall`.
- Added `clear` command to clear the CLI outputs.
- Added comprehensive help system:
  - Global help: `help` or `h`
  - Command-specific help: `command help` or `command --help`
  - Detailed usage instructions and examples
- Added GEMINI-inspired CLI interface:
  - Beautiful ASCII art logo that adapts to terminal width
  - Custom prompt box with improved styling
  - Status bar showing current directory and Git branch
  - Themed panels for messages and dialogs

### Changed

- Changed the Output printing logic, now it is more user friendly.
- Refactored the project structure for better maintainability.
- Enhanced the welcome and goodbye screens with styled ASCII art
- Improved theme management system with GEMINI-inspired themes

### Fixed

- Made the project structure modular.
- Fixed cursor positioning in the prompt box
- Fixed display issues with ASCII art on different terminal widths


## [0.1.1] - 2025-06-15

### Fixed
- Added missing `__main__.py` entry point to fix CLI execution when installed via pip

## [0.1.0] - 2025-06-15

### Added
- Initial project setup
- Basic CLI structure with Typer
- Welcome ASCII art display using pyfiglet
- Interactive command prompt with Rich
- Basic command handlers for help and exit commands
- Support for pip installation with setup.py
- Development mode installation (pip install -e .)

### Changed
- N/A (initial release)

### Fixed
- N/A (initial release)