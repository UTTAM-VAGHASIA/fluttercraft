# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-01-17 (In Progress)

### 🎨 UI/UX Enhancement - Phase 1: Foundation

**Signature UI/UX overhaul** with smart completions, persistent history, animations, and cross-platform polish!

### Added

#### 🎯 Smart Auto-Completion Menu
- **Auto-show completion menu** for all commands (slash and regular commands)
  - Intelligent display: Shows when typing, hides for exact matches
  - Conditional rendering: No empty boxes or clutter
- **Ctrl+M toggle** to manually show/hide menu (M for Menu)
  - Works reliably on Windows, macOS, and Linux
  - Persistent state across command inputs
- **Smart Enter key behavior**
  - Navigated to completion → Selects that completion
  - At index 0 with exact match → Submits command
  - Automatic index reset after selection (prevents wrong selections)
- **Visual hints**
  - Toolbar shows "💡 Ctrl+M to show menu" when manually hidden
  - Clean, bordered menu with cyan highlight
- **Enhanced UX**
  - Up/Down arrow navigation
  - Escape to hide menu
  - Tab/Right Arrow to fill completion
  - Smooth transitions

---

### 🏗️ Architecture - FINAL System Implementation

**Major architectural improvement** introducing spec-driven development, context management, and comprehensive cleanup!

### Added

#### 📁 Context Management System (`.context/`)
- **Architecture Specification** (`.context/architecture.yaml`)
  - Complete FINAL architecture design with 5 clean layers
  - Dependency rules and enforcement
  - Migration plan to clean architecture
  - AI agent compatibility guidelines
- **Dependency Tracking** (`.context/dependencies.yaml`)
  - Complete module dependency graph
  - Impact analysis for changes
  - Orphaned/duplicate module identification
  - External dependency tracking
- **Component Documentation** (`.context/components/`)
  - Detailed component-level context
  - Public API documentation
  - Change history tracking

#### 📋 Spec-Driven Development (`.specs/`)
- **Development Framework** (`.specs/README.md`)
  - Complete workflow for features/fixes/refactoring
  - AI agent integration guide
  - Validation and quality gates
- **Specification Templates**
  - Feature template (17 sections, comprehensive)
  - Bug fix template (18 sections)
  - Refactoring template (16 sections)
- **Active Specs**
  - Phase 1 Cleanup specification

#### 📚 Enhanced Documentation
- **AGENTS.md** - Complete AI coding agent development guide
  - Build/lint/test commands
  - Code style guidelines
  - Architecture patterns
  - Development workflow

### Changed

#### 🧹 Code Cleanup and Consolidation
- **Removed Duplicate Theme Selectors** (3 files, ~24KB)
  - Kept: `interactive_selector.py`
  - Removed: `interactive_theme_selector.py`, `live_theme_selector.py`, `rich_theme_selector.py`
- **Removed Legacy Code**
  - `command_handler.py` (430 lines) - Replaced by executor pattern
  - `display_utils.py` (114 lines) - Deprecated utilities
- **Consolidated Utilities**
  - Moved `get_git_info()` to `platform_utils.py`
  - Moved `get_current_path()` to `platform_utils.py`
  - Eliminated duplicate code across modules
- **Documentation Reorganization**
  - Moved planning/historical docs to `docs/archive/`
  - Archived: `BUGS_FIXED.md`, `development-progress.md`, `CLI_REDESIGN.md`, `GEMINI_INTERFACE.md`
  - Removed: `v0.1.3-roadmap.md` (outdated)

### Fixed

#### 🐛 Smart Completion Menu Bugs
- **Empty menu boxes** - Menu container now only renders when there are completions
- **Ctrl+Space not working on Windows** - Switched to Ctrl+M (reliable across platforms)
- **Commands not submitting** - Enter now properly detects exact matches and submits
- **Wrong completion selected after fill** - Selection index resets to 0 after filling
- **Menu showing for exact match + space** - Better exact match detection (e.g., "/help ")

#### 🏗️ Architecture Cleanup
- **Version Synchronization**
  - All version numbers now consistent at `0.1.3`
  - Synchronized: `__init__.py`, `setup.py`, `CHANGELOG.md`
- **Dependency Graph**
  - Updated to reflect removed modules
  - No circular dependencies
  - Clean import structure

### Infrastructure

- **AI Agent Support**
  - Context loading before changes
  - Spec-driven development workflow
  - Session continuity tracking
  - Strict rule enforcement
- **Quality Gates**
  - Pre-commit checks (format, lint, type check)
  - Pre-push validation (tests, coverage, docs)
  - PR requirements (spec, context update, review)

### Developer Experience

- **Development Workflow**
  - Every change starts with a spec
  - Clear component context
  - Impact analysis before changes
  - Systematic approach to features/fixes

### Metrics

- **Code Reduction**: ~1000+ lines removed
- **Duplicate Code**: 0% (down from ~15%)
- **Version Consistency**: 100%
- **Architecture Documentation**: Comprehensive

### Notes

This release establishes the foundation for the FINAL architecture. Future releases (v0.2.0+) will gradually migrate to the complete clean architecture with domain/application/infrastructure/presentation/core layers.

For development guidelines, see:
- `AGENTS.md` - AI agent development guide
- `.context/architecture.yaml` - Complete architecture specification
- `.specs/README.md` - Spec-driven development workflow

---

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