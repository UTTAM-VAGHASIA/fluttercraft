# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-10-16

### 🎨 Major Update - Enhanced Features & Flutter Integration

**Comprehensive update** with Flutter command support, improved error handling, loading indicators, and version tracking!

### Added

#### 🚀 Flutter Commands
- **`flutter upgrade`** - Full support for upgrading Flutter
  - Support for parameters: `--force`, `--verify-only`, `--continue`, `--verbose`
  - Real-time output display with loading indicators
  - Automatic version update after successful upgrade
  - `flutter upgrade --help` for detailed help
- **Animated Loading Indicators**: Braille spinner animation (10 FPS) during command execution
- **Flutter Version Tracking**: 
  - Shows current version and available updates in system info
  - Visual indicators: `3.32.6 (→ 3.35.6 available)` or `3.35.6 ✓`
  - Single command check using `flutter upgrade --verify-only`

#### 📋 New Slash Commands
- **`/about`** - Display comprehensive CLI information
  - Version information (auto-fetched from package metadata)
  - Features list
  - Working commands overview
  - Repository link with star prompt
  - Quick start guide
- **`/quit`** - Exit CLI (removed `/exit` and `/q` for consistency)

#### 🎨 UI/UX Improvements
- **Error Panel Visibility**: Command output panels now stay visible on failure
  - Red border for failed commands
  - Shows exit code and error output
  - Permanent display for debugging
- **Adaptive Success Messages**: Context-aware messages based on command type
  - "Flutter update check completed!" for `--verify-only`
  - "Flutter upgrade completed successfully!" for actual upgrades
- **Better Help System**: 
  - `flutter upgrade --help` shows detailed command help
  - Updated `/help` to show working vs. coming soon commands
  - Clear status indicators: ✓ Working, ⚠ Partial Support, Coming Soon

#### 🛠️ FVM Commands
- Added `fvm install` and `fvm uninstall` commands
- Added `fvm releases` command with enhanced UI
  - Support for channel filtering: `fvm releases --channel [stable|beta|dev|all]`
  - Improved version sorting and presentation
- Added `fvm list` command with enhanced formatting
  - Shows cache directory location and size
  - Highlights global and project-specific Flutter versions
  - Enhanced visual presentation with colored borders

#### 📚 Help System
- Comprehensive help system with `/help` command
- Command-specific help: `<command> --help`
- Detailed usage instructions and examples
- Context-aware help messages

#### 🎯 New Dependencies
- `prompt_toolkit>=3.0.0` - Powers beautiful prompt and auto-completion
- `pygments>=2.0.0` - Syntax highlighting support

### Changed

- **Optimized Flutter Version Check**: Now uses single command (`flutter upgrade --verify-only`) instead of two
  - 50% faster startup time
  - Fewer network calls
  - Better performance
- **Command Routing Logic**: Fixed help command routing to prevent conflicts
  - `flutter upgrade --help` now shows correct help instead of general help
  - Proper command precedence handling
- **Error Handling**: Comprehensive error handling across all commands
  - Clear error messages with helpful suggestions
  - Unknown command guidance
  - Better FVM error handling with recovery suggestions
- **System Info Display**: Enhanced with update indicators and version tracking
- **Panel Display Logic**: Improved to show output on both success and failure when needed

### Fixed

#### 🐛 Critical Bugs Fixed
- **Error panels disappearing on failure** → Now stay visible with red border and error output
- **Command output not showing** → Fixed panel visibility logic for both success and failure
- **Help command conflicts** → Fixed routing so `flutter upgrade --help` works correctly
- **Slow startup** → Optimized Flutter version check (50% faster)
- **No loading feedback** → Added animated spinner during command execution
- **Version info not updating** → System info now updates after `flutter upgrade`
- **Generic error messages** → Context-aware, helpful error messages with suggestions

#### 🔧 Minor Fixes
- Removed `/exit` and `/q` commands (kept only `/quit` for consistency)
- Fixed ASCII art alignment
- Improved panel border styling for errors (red) vs success (cyan)
- Better pause timing on errors (0.5s) vs success (0.2s)
- Version now auto-fetched from package metadata
- Fixed command parameter passing for `flutter upgrade`

### Documentation

- Added `docs/CLI_REDESIGN.md` - Comprehensive CLI redesign documentation
- Added `docs/BUGS_FIXED.md` - Detailed list of bugs fixed and improvements
- Added `TESTING_GUIDE.md` - Complete testing checklist and guide
- Updated `README.md` - Highlighted new beautiful interface features

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