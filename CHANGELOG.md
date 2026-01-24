# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-01-17 (In Progress)

### 🎨 UI/UX Enhancement - Phase 2: Animations & Settings

**Sleek animation system** and startup transitions to match modern professional CLIs!

### Added

#### 🎭 Animation Engine Foundation
- **New Animation Engine** using `rich.live`
  - High-performance render loop (configurable FPS)
  - Time-based frame updates using `time.perf_counter()`
  - Generic `animate` method for custom property transitions
- **Standard Easing Functions**
  - Linear, Quadratic (In/Out/InOut), Cubic (In/Out/InOut)
  - Smooth pulse effect for periodic transitions
- **Advanced Transition Effects**
  - **Slide In**: Elements glide into view from any direction (left, right, top, bottom) with offset control
  - **Wipe In**: Sophisticated reveal effect (typewriter reveal for text and ASCII art)
- **Animation Documentation**: New `.context/components/animations.md` guide for developers

#### 🎬 Sleek Startup Experience
- **Animated Welcome Header**
  - **Logo Wipe-in**: Colorful ASCII art logo reveals from top to bottom (300ms)
  - **Info Slide-in**: System information lines glide in from the left (150ms per line)
- **Zero-Wait Feel**: Animations are optimized for speed (< 1s total) to ensure no productivity impact
- **Dynamic Content**: Animated header maintains all real-time version checks (Flutter, FVM, Python)
- **Seamless Transition**: Screen clears instantly before animation for a professional "app-like" startup

#### ⚡ Command Feedback Animations
- **Context-Aware Animations** for command results
  - **Success Slide-up**: Successful commands trigger a subtle 200ms upward slide to feel "activated"
  - **Error Shake**: Invalid commands or errors trigger a 200ms horizontal shake to provide visual negative feedback
- **Universal Exception Handling**: Integrated animation engine into the command executor to animate unexpected Python exceptions
- **Markup Support**: Animations support Rich markup and stylized text

#### ⏳ Modern Progress Indicators
- **Themed Progress Bars**: Replaced generic spinners with beautiful, theme-aware progress bars
  - Uses project accent colors (Cyan default)
  - Indeterminate state support ("pulsing" bars)
  - Clean "transient" behavior (disappears on completion)
- **Unified Experience**: Consistent progress UI across all long-running operations
  - **FVM Install**: "Installing FVM..." with visual feedback
  - **Flutter Upgrade**: "Upgrading Flutter SDK..." with status tracking
- **Simplified API**: New `run_with_progress` utility for developers

### Fixed

- **Linux Platform Support**: Removed unnecessary platform exclusion for Linux, allowing full CLI access on Ubuntu/Debian/Fedora

---

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

#### 📜 Persistent Command History
- **File-based command history** stored in `~/.fluttercraft/history`
  - Persists across CLI restarts
  - Automatic directory creation
  - Plain text format (one command per line)
- **Arrow key navigation** through command history
  - Up/Down arrows to navigate previous commands
  - Context-aware: Switches between menu navigation OR history
  - Real-time file updates
- **Smart history management**
  - Max 10,000 entries with FIFO (First In, First Out)
  - Consecutive duplicate command deduplication
  - Case-insensitive search functionality
  - Empty commands not saved
- **Toolbar hints** for history navigation (⬆️⬇️)

#### ⚡ Command Execution Timing
- **High-precision timing** using `time.perf_counter()`
  - Microsecond accuracy for performance tracking
  - Displayed after every successful command execution
- **Smart time formatting**
  - < 1ms: "0.25ms" (2 decimal places)
  - < 1s: "150ms" (no decimals)
  - ≥ 1s: "2.45s" (2 decimal places)
- **Color-coded performance indicators**
  - Green ⚡: < 1 second (fast)
  - Yellow ⏱️: 1-3 seconds (moderate)
  - Red 🐌: ≥ 3 seconds (slow)
- **Non-intrusive display** with dim styling

#### 🔍 Fuzzy Completion Matching
- **Intelligent fuzzy matching** for command completions
  - Fast matching using rapidfuzz library (WRatio scorer)
  - Smart ranking: Exact matches first, then fuzzy matches
  - Minimum query length (2+ chars) to avoid poor matches
- **Clean completion display**
  - No technical noise (scores, labels)
  - Just command and description
  - Configurable quality threshold (70% minimum)
- **Enhanced discoverability**
  - Type 'fvmr' → Shows 'fvm releases', 'fvm install', etc.
  - Type 'flr' → Shows 'flutter upgrade', 'flutter' commands
  - Fast and responsive (<50ms for typical command sets)

#### ⌨️ Enhanced Text Input Area
- **Multi-line input support** with dynamic height (1-10 lines)
  - Input box expands automatically as user types
  - 10 line maximum to prevent excessive screen usage
- **Multiple keybindings for multi-line input**
  - **Ctrl+J** - Universal cross-platform (guaranteed)
  - **Alt+Enter** - Press Escape then Enter (works on most terminals)
- **Visual toolbar hints** for multi-line input
  - Clear indicator: "Alt+Enter / Ctrl+J for multi-line"
- **Proper key handling** using prompt_toolkit Keys enum
  - Reliable key binding with no escape sequence errors
  - Clean implementation with no technical debt

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