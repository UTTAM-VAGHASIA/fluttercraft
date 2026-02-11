# FlutterCraft Textual TUI — MVP Implementation Plan

## Context

The `feature/v0.1.3-signature-ui` branch has Phase 1 complete (smart completions, fuzzy matching, persistent history, timing display, multi-line input) — all built on Rich + prompt_toolkit. The project now pivots to a **Textual TUI** that replaces the Rich CLI as the primary interface.

**Why**: A Textual TUI gives us cross-platform support (killing the Windows-only limitation), a real widget-based layout, CSS theming, async workers for subprocess calls, and a foundation that can later integrate AI agents and ADB emulator controls.

**Goal**: A fully working, pretty Textual TUI with all existing commands functional, animated ASCII logo, proper theming (all 13 existing themes), cross-platform support, and robust error handling. No AI agent or emulator integration yet.

## Workflow

**Iterative testing with ralph loop**: After implementation of each step, run `fluttercraft start` manually to test everything. Review and perfect before moving to next step.

---

## Architecture

```
FlutterCraftApp (Textual App)
├── DashboardScreen (default screen)
│   ├── AsciiLogoWidget        — Gradient-animated ASCII logo (responsive to terminal width)
│   ├── SystemInfoBar          — Platform, Python, Flutter, FVM status
│   ├── OutputLog (RichLog)    — Scrollable command output area
│   ├── CommandInput           — Input with fuzzy autocomplete dropdown
│   └── Footer                 — Keybinding hints
├── HelpScreen                 — Push-screen overlay for /help
├── AboutScreen                — Push-screen overlay for /about
└── ThemeSelectorScreen        — Push-screen overlay for /theme with live preview
```

**Key design decisions:**
1. **Reuse entire command system unchanged** — CommandRegistry, CommandExecutor, Command base class, all existing commands
2. **Console capture bridge** — Create a console wrapper that captures Rich output from existing commands and feeds it into the TUI's RichLog widget (zero changes to command code)
3. **Theme bridge** — Map existing 13 Theme objects → Textual CSS variables dynamically
4. **Replace `fluttercraft start`** — TUI becomes the default. Add `--legacy` flag for the old Rich CLI
5. **Remove platform block** — Textual is cross-platform; no more "coming soon" for macOS/Linux
6. **Reuse fuzzy_matcher.py and history_manager.py** directly in TUI input widget

---

## Implementation Steps

Each step is independently testable. After each step, run `fluttercraft start` to verify.

---

### Step 1: Add Dependencies & Create Package Structure

**Goal**: Textual importable, package directories exist.

**Files:**
- MODIFY `setup.py` — Add `textual>=0.85.0` to install_requires
- CREATE `fluttercraft/tui/__init__.py` — Empty package init
- CREATE `fluttercraft/tui/widgets/__init__.py` — Empty package init
- CREATE `fluttercraft/tui/screens/__init__.py` — Empty package init

**Test**: `pip install -e .` succeeds, `python -c "import textual"` works.

---

### Step 2: Theme Bridge — Map Existing Themes to Textual CSS

**Goal**: All 13 existing themes can be converted to Textual CSS variables.

**File:** CREATE `fluttercraft/tui/theme_bridge.py`

**What it does:**
- Takes existing `Theme` object (from `utils/themes/theme.py`)
- Generates Textual CSS string with CSS variables
- Provides a function that applies theme to the running Textual app
- Maps all 13 themes from `professional_themes.py` without changes

**Reuses:**
- `fluttercraft/utils/themes/theme.py` — Theme, SemanticColors dataclasses
- `fluttercraft/utils/themes/theme_manager.py` — ThemeManager, get_theme_manager()
- `fluttercraft/utils/themes/professional_themes.py` — All 13 theme definitions

**Approach:** Each Theme property maps to a Textual color/style:
```css
/* In Textual CSS, we use the theme colors directly in widget styles */
AsciiLogo { color: $accent-cyan; }
SystemInfoBar { background: $background; color: $foreground; }
.status-success { color: $status-success; }
```

**Test**: Unit test that converts each of the 13 themes without error.

---

### Step 3: Console Capture Bridge

**Goal**: Existing commands can execute and their output is capturable for the TUI.

**File:** CREATE `fluttercraft/tui/command_bridge.py`

**What it does:**
- Wraps `CommandExecutor` for TUI usage
- Creates a `Rich Console` that writes to `StringIO` instead of stdout
- After command execution, extracts the captured output
- Returns captured output + CommandResult to TUI for display in RichLog
- All existing commands work unmodified (they still call `console.print()`)

**Reuses:**
- `fluttercraft/commands/core/executor.py` — CommandExecutor
- `fluttercraft/commands/core/models.py` — CommandContext, CommandResult
- `fluttercraft/commands/bootstrap.py` — build_command_system()

**Test**: `python -c "from fluttercraft.tui.command_bridge import TUICommandBridge"` imports.

---

### Step 4: ASCII Logo Widget (Animated)

**Goal**: Beautiful animated gradient ASCII logo in the TUI.

**File:** CREATE `fluttercraft/tui/widgets/ascii_logo.py`

**What it does:**
- Renders the ASCII art logo with gradient colors
- Animates on startup: character-by-character reveal with gradient sweep (using `set_interval`)
- Responsive: uses `select_ascii_art()` based on widget width
- After animation completes, shows static gradient logo

**Reuses:**
- `fluttercraft/utils/themes/ascii_art.py` — FULL/COMPACT/TINY_ASCII_LOGO, select_ascii_art()
- `fluttercraft/utils/themes/gradient.py` — apply_gradient_to_ascii()

**Test**: Widget renders in a minimal test app.

---

### Step 5: System Info Bar Widget

**Goal**: Horizontal bar showing platform/Flutter/FVM status.

**File:** CREATE `fluttercraft/tui/widgets/system_info.py`

**What it does:**
- Horizontal bar: Platform | Python | Flutter (version + update status) | FVM
- Updates after commands that change state (flutter upgrade, fvm install)
- Uses theme colors for status indicators (green ✓, yellow → available, red ✗)
- Uses `@work(thread=True)` for initial data gathering (subprocess calls)
- Graceful fallback if Flutter/FVM not installed

**Reuses:**
- `fluttercraft/utils/platform_utils.py` — get_platform_info(), is_windows(), etc.
- `fluttercraft/commands/flutter_commands.py` — check_flutter_version()
- `fluttercraft/commands/fvm_commands.py` — check_fvm_version()

**Test**: Shows correct system info on current machine.

---

### Step 6: Command Input Widget with Autocomplete

**Goal**: Input field with fuzzy autocomplete and history.

**File:** CREATE `fluttercraft/tui/widgets/command_input.py`

**What it does:**
- Text input with fuzzy autocomplete dropdown (OptionList or custom overlay)
- Shows completion suggestions as user types
- Tab to complete, Enter to submit
- Up/Down for history navigation (when no completions showing)
- Displays execution timing after command runs
- Visual indicators for command state

**Reuses:**
- `fluttercraft/utils/fuzzy_matcher.py` — FuzzyMatcher (exact same class)
- `fluttercraft/utils/history_manager.py` — HistoryManager (exact same class)
- `fluttercraft/utils/beautiful_prompt.py` — SLASH_COMMANDS, FVM_COMMANDS, FLUTTER_COMMANDS dicts (for completion targets)

**Test**: Type commands, see completions, navigate history.

---

### Step 7: Output Log Widget

**Goal**: Scrollable area for command output.

**File:** CREATE `fluttercraft/tui/widgets/output_log.py`

**What it does:**
- Wraps Textual's `RichLog` widget with theme-aware styling
- Receives captured Rich renderables from the console bridge
- Auto-scrolls to bottom on new output
- Supports clear command
- Shows welcome tips on first load

**Test**: Commands produce visible output in the log area.

---

### Step 8: Dashboard Screen (Main Screen)

**Goal**: Compose all widgets into the main screen layout.

**File:** CREATE `fluttercraft/tui/screens/dashboard.py`

**What it does:**
- Composes all widgets: AsciiLogo, SystemInfoBar, OutputLog, CommandInput
- Handles command submission: input → bridge → executor → output
- Manages state updates after commands (refresh Flutter/FVM info)
- Layout via Textual CSS: logo at top, info bar, output area (fill), input at bottom

**Layout:**
```
┌─────────────────────────────────────────────┐
│  ███████╗██╗     ... (animated gradient)     │  <- AsciiLogoWidget (auto height)
│                                              │
│  Platform: Linux | Python: 3.10 | Flutter... │  <- SystemInfoBar (3 lines)
│──────────────────────────────────────────────│
│                                              │
│  [Output area - scrollable, fills space]     │  <- OutputLog (1fr)
│  > fvm releases                              │
│  ⚡ Executed in 250ms                        │
│  [table of releases]                         │
│                                              │
│──────────────────────────────────────────────│
│  > Type a command...                         │  <- CommandInput (auto)
│──────────────────────────────────────────────│
│  q Quit  ? Help  t Theme  Tab Complete       │  <- Footer (1 line)
└─────────────────────────────────────────────┘
```

**Key bindings:**
- `q` / `ctrl+q` — Quit (only when input not focused, or via /quit command)
- `?` / `f1` — Push HelpScreen
- `ctrl+t` — Push ThemeSelectorScreen
- `ctrl+l` — Clear output log
- `escape` — Pop current screen (for overlays)

**Test**: Full TUI launches, commands work end-to-end.

---

### Step 9: Help Screen (Overlay)

**Goal**: Modal screen showing all available commands.

**File:** CREATE `fluttercraft/tui/screens/help_screen.py`

**What it does:**
- Modal/overlay screen showing all available commands
- Organized by category (Slash, FVM, Flutter)
- Themed with current theme colors
- Press `escape` or `q` to dismiss

**Test**: Press `?` or `F1` → help overlay appears. Press `escape` → dismisses.

---

### Step 10: About Screen (Overlay)

**Goal**: Modal showing version and project info.

**File:** CREATE `fluttercraft/tui/screens/about_screen.py`

**What it does:**
- Modal/overlay showing version info, features, author, links
- Themed with current theme

**Test**: Type `/about` → about overlay appears.

---

### Step 11: Theme Selector Screen (Overlay)

**Goal**: Interactive theme picker with live preview.

**File:** CREATE `fluttercraft/tui/screens/theme_selector.py`

**What it does:**
- Lists all 13 themes with color previews
- Arrow keys to navigate, Enter to select
- Live preview: hovering a theme immediately applies it
- Saves selection via ThemeManager (persists to `~/.fluttercraft/theme.json`)
- Press escape to cancel (reverts to previous theme)

**Reuses:**
- `fluttercraft/utils/themes/theme_manager.py` — get_theme_manager()
- `fluttercraft/utils/themes/professional_themes.py` — PROFESSIONAL_THEMES dict

**Test**: `Ctrl+T` → theme list. Navigate → see preview. Enter → theme persists.

---

### Step 12: Main App Class

**Goal**: The Textual App that ties everything together.

**File:** CREATE `fluttercraft/tui/app.py`

**What it does:**
- Main `FlutterCraftApp(App)` class
- Loads theme on startup via ThemeManager
- Initializes command system via build_command_system()
- Sets DashboardScreen as default
- Handles app-level keybindings and screen management
- Title: "FlutterCraft"
- Sub title: version string

**Test**: `python -m fluttercraft.tui.app` launches the full TUI.

---

### Step 13: Entry Point Integration

**Goal**: `fluttercraft start` launches TUI by default.

**Files:**
- MODIFY `fluttercraft/main.py` — Change `start` command to launch TUI. Add `--legacy` flag for old Rich CLI.
- MODIFY `fluttercraft/commands/start.py` — Remove macOS/Linux platform block. Rename to `start_legacy_command()`. Keep as fallback.

**Test**: `fluttercraft start` → TUI. `fluttercraft start --legacy` → old Rich CLI.

---

### Step 14: Cross-Platform Edge Cases & Error Handling

**Goal**: Robust handling of all edge cases.

**Handles:**
- **No Flutter installed**: SystemInfoBar shows "Not installed" gracefully, commands show helpful error
- **No FVM installed**: Same graceful degradation
- **Subprocess timeouts**: Workers with timeout, show error in output log
- **Terminal too small**: Responsive layout, minimum size check with message
- **Permission errors**: Catch and display in output log (e.g., can't write history file)
- **Network errors**: FVM releases fails → themed error panel
- **Color support**: Textual auto-detects; fallback for minimal terminals
- **Keyboard compatibility**: Textual handles cross-platform key events natively
- **Ctrl+C handling**: Graceful, doesn't crash the app

**Test**: Resize terminal, disconnect network, test on Linux (this machine). Verify no crashes.

---

## Files Summary

| # | Action | File | Purpose |
|---|--------|------|---------|
| 1 | MODIFY | `setup.py` | Add textual dependency |
| 2 | CREATE | `fluttercraft/tui/__init__.py` | Package init |
| 3 | CREATE | `fluttercraft/tui/widgets/__init__.py` | Widgets package |
| 4 | CREATE | `fluttercraft/tui/screens/__init__.py` | Screens package |
| 5 | CREATE | `fluttercraft/tui/theme_bridge.py` | Theme → Textual CSS |
| 6 | CREATE | `fluttercraft/tui/command_bridge.py` | Console capture for commands |
| 7 | CREATE | `fluttercraft/tui/widgets/ascii_logo.py` | Animated gradient logo |
| 8 | CREATE | `fluttercraft/tui/widgets/system_info.py` | Platform/Flutter/FVM bar |
| 9 | CREATE | `fluttercraft/tui/widgets/command_input.py` | Input + fuzzy autocomplete |
| 10 | CREATE | `fluttercraft/tui/widgets/output_log.py` | Scrollable command output |
| 11 | CREATE | `fluttercraft/tui/screens/dashboard.py` | Main dashboard screen |
| 12 | CREATE | `fluttercraft/tui/screens/help_screen.py` | Help overlay |
| 13 | CREATE | `fluttercraft/tui/screens/about_screen.py` | About overlay |
| 14 | CREATE | `fluttercraft/tui/screens/theme_selector.py` | Theme picker with preview |
| 15 | CREATE | `fluttercraft/tui/app.py` | Main Textual App class |
| 16 | MODIFY | `fluttercraft/main.py` | TUI entry point |
| 17 | MODIFY | `fluttercraft/commands/start.py` | Remove platform block, rename |

**Total: 12 new files, 3 modified files**

---

## Reuse Map (Existing Code → TUI)

| Existing Module | Reused In | How |
|---|---|---|
| `commands/core/*` (registry, executor, base, models) | `tui/command_bridge.py` | Unchanged — bridge wraps executor |
| `commands/bootstrap.py` | `tui/app.py` | Called directly to build command system |
| `commands/fvm_command.py`, `flutter_command.py` | Via executor | Unchanged — output captured by bridge |
| `commands/slash_commands.py` | Partially bypassed | /quit, /clear, /help, /about, /theme handled natively by TUI screens |
| `utils/themes/theme.py` | `tui/theme_bridge.py` | Theme dataclass mapped to CSS |
| `utils/themes/professional_themes.py` | `tui/theme_bridge.py` | All 13 themes mapped |
| `utils/themes/theme_manager.py` | `tui/app.py`, `tui/screens/theme_selector.py` | Persistence unchanged |
| `utils/themes/ascii_art.py` | `tui/widgets/ascii_logo.py` | Logo strings + selection logic |
| `utils/themes/gradient.py` | `tui/widgets/ascii_logo.py` | Gradient rendering |
| `utils/fuzzy_matcher.py` | `tui/widgets/command_input.py` | Exact same FuzzyMatcher class |
| `utils/history_manager.py` | `tui/widgets/command_input.py` | Exact same HistoryManager class |
| `utils/platform_utils.py` | `tui/widgets/system_info.py` | get_platform_info() |
| `commands/flutter_commands.py` | `tui/widgets/system_info.py` | check_flutter_version() |
| `commands/fvm_commands.py` | `tui/widgets/system_info.py` | check_fvm_version() |

---

## Verification Checklist (Final)

After all steps complete:

- [ ] `pip install -e . && fluttercraft start` opens the TUI
- [ ] Animated gradient ASCII logo renders on startup, responsive to terminal width
- [ ] System info bar shows correct Platform, Python, Flutter, FVM status
- [ ] `fvm releases`, `flutter upgrade --verify-only`, `/help`, `/about` all produce output in the log
- [ ] Type `fvm` → see completions with fuzzy matching
- [ ] Up/Down arrows navigate previous commands, persists across restarts
- [ ] Commands show execution time
- [ ] `Ctrl+T` opens theme selector, changing theme updates UI live
- [ ] Works on Linux (current machine) — no "coming soon" block
- [ ] `fvm releases` with no internet → graceful error in output log
- [ ] Resize terminal → layout adapts. Very small terminal → minimum size message
- [ ] `q`, `Ctrl+Q`, or `/quit` exits cleanly
- [ ] `flake8 fluttercraft/` passes
- [ ] `fluttercraft start --legacy` launches old Rich CLI
