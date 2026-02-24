# Sidecar Architecture Reference
## Source: https://github.com/marcus/sidecar

A comprehensive reference of the Sidecar TUI (Terminal User Interface) codebase architecture, patterns, and design decisions. Use this as a reference for planning features in FlutterCraft.

---

## 1. Project Overview

**Sidecar** is a Go-based TUI dashboard for AI coding agents (Claude Code, Cursor, Gemini CLI, etc.). It uses the [Bubble Tea](https://github.com/charmbracelet/bubbletea) framework (Elm Architecture for terminals).

- **Language:** Go (92.2%)
- **Framework:** Bubble Tea (charmbracelet/bubbletea)
- **Styling:** Lipgloss (charmbracelet/lipgloss)
- **License:** MIT
- **661 source files**, well-organized modular architecture

---

## 2. Directory Structure

```
sidecar/
├── cmd/sidecar/
│   └── main.go                    # Entry point, bootstraps everything
├── internal/
│   ├── adapter/                   # Data source adapters (AI agent integrations)
│   │   ├── adapter.go             # Core Adapter interface
│   │   ├── detect.go              # Auto-detection of available adapters
│   │   ├── search.go              # Cross-adapter search
│   │   ├── claudecode/            # Claude Code adapter
│   │   ├── cursor/                # Cursor adapter
│   │   ├── codex/                 # OpenAI Codex adapter
│   │   ├── geminicli/             # Gemini CLI adapter
│   │   ├── kiro/                  # Kiro adapter
│   │   ├── opencode/              # OpenCode adapter
│   │   ├── warp/                  # Warp terminal adapter
│   │   ├── pi/                    # Pi adapter
│   │   ├── piagent/               # Pi Agent adapter
│   │   ├── amp/                   # Amp adapter
│   │   ├── cache/                 # Adapter-level caching
│   │   ├── pricing/               # Token cost calculation
│   │   └── tieredwatcher/         # Fsnotify + polling hybrid watcher
│   ├── app/                       # Root application model (Bubble Tea)
│   │   ├── model.go               # Main Model struct, Init(), modal management
│   │   ├── update.go              # Update() message handler
│   │   ├── view.go                # View() renderer
│   │   ├── ui.go                  # UIState (header/footer)
│   │   ├── commands.go            # App-level commands
│   │   ├── intro.go               # Intro animation
│   │   └── *_modal.go             # Various modal implementations
│   ├── plugin/                    # Plugin system
│   │   ├── plugin.go              # Plugin interface definition
│   │   ├── registry.go            # Plugin lifecycle management
│   │   └── context.go             # Shared context for plugins
│   ├── plugins/                   # Concrete plugin implementations
│   │   ├── gitstatus/             # Git status plugin (~40 files)
│   │   ├── conversations/         # AI conversation viewer (~25 files)
│   │   ├── filebrowser/           # File browser plugin (~20 files)
│   │   ├── workspace/             # Workspace manager plugin (~45 files)
│   │   ├── tdmonitor/             # Task manager plugin
│   │   └── notes/                 # Notes plugin
│   ├── config/                    # Configuration system
│   │   ├── config.go              # Config struct definitions
│   │   ├── loader.go              # Load from ~/.config/sidecar/config.json
│   │   └── saver.go               # Save config changes
│   ├── state/                     # Persistent user preferences
│   │   └── state.go               # State struct, JSON persistence
│   ├── styles/                    # Theming and styling
│   │   ├── styles.go              # Global style variables (Lipgloss)
│   │   ├── themes.go              # Built-in theme definitions
│   │   ├── borders.go             # Gradient border rendering
│   │   └── contrast.go            # WCAG contrast utilities
│   ├── theme/                     # Theme resolution (per-project themes)
│   ├── community/                 # 453 community color schemes
│   ├── event/                     # Event bus (pub/sub)
│   │   ├── event.go               # Event types
│   │   └── dispatcher.go          # Fan-out dispatcher
│   ├── keymap/                    # Key binding system
│   │   ├── bindings.go            # Default key bindings
│   │   ├── registry.go            # Dynamic binding registry
│   │   └── config.go              # User override support
│   ├── modal/                     # Declarative modal system
│   │   ├── modal.go               # Modal builder (sections, buttons)
│   │   ├── layout.go              # Modal positioning/centering
│   │   └── options.go             # Modal configuration options
│   ├── palette/                   # Command palette (fuzzy search)
│   ├── mouse/                     # Mouse hit-testing
│   ├── tty/                       # Terminal I/O, tmux integration
│   │   ├── tty.go                 # Interactive tmux session model
│   │   ├── keymap.go              # Key-to-tmux mapping
│   │   ├── polling.go             # Adaptive polling
│   │   └── output_buffer.go       # Scrollback buffer
│   ├── ui/                        # Reusable UI components
│   │   ├── modal.go               # Modal overlay rendering
│   │   ├── scrollbar.go           # Scrollbar widget
│   │   ├── selection.go           # List selection model
│   │   ├── buttons.go             # Button rendering
│   │   ├── confirm_dialog.go      # Confirmation dialog
│   │   ├── skeleton.go            # Loading skeleton
│   │   └── braille_spinner.go     # Braille animation spinner
│   ├── markdown/                  # Markdown rendering
│   ├── image/                     # Terminal image rendering
│   ├── version/                   # Version checking, auto-update
│   ├── features/                  # Feature flags
│   └── fdmonitor/                 # File descriptor monitoring
├── configs/
│   └── default.json               # Default config template
├── scripts/                       # Build/dev scripts
└── website/                       # Documentation site
```

---

## 3. Core Architecture Patterns

### 3.1 Elm Architecture (Bubble Tea)

Every component follows the Model-Update-View pattern:

```
Model (state) → Update(msg) → (Model, Cmd) → View(width, height) → string
```

- **Model**: Immutable state struct
- **Update**: Pure function that handles messages and returns new state + side-effect commands
- **View**: Pure function that renders state to a string
- **Cmd**: Async side-effects (I/O, timers) that produce messages

### 3.2 Plugin System

**Plugin Interface** (`internal/plugin/plugin.go`):
```go
type Plugin interface {
    ID() string
    Name() string
    Icon() string
    Init(ctx *Context) error
    Start() tea.Cmd
    Stop()
    Update(msg tea.Msg) (Plugin, tea.Cmd)
    View(width, height int) string
    IsFocused() bool
    SetFocused(bool)
    Commands() []Command
    FocusContext() string
}
```

**Plugin Context** (`internal/plugin/context.go`):
```go
type Context struct {
    WorkDir     string                     // Current project directory
    ProjectRoot string                     // Main repo root
    ConfigDir   string
    Config      *config.Config
    Adapters    map[string]adapter.Adapter // All AI adapters
    EventBus    *event.Dispatcher          // Pub/sub event bus
    Logger      *slog.Logger
    Keymap      BindingRegistrar           // Dynamic key binding registration
    Epoch       uint64                     // Invalidation counter for async messages
}
```

**Plugin Registry** (`internal/plugin/registry.go`):
- Manages plugin lifecycle (Init → Start → Stop)
- Panic recovery on all plugin calls (silent degradation)
- `Reinit()` for project switching (stops all, updates context, restarts)
- Thread-safe with `sync.RWMutex`

**Registration Order = Tab Order** (in `main.go`):
1. TD Monitor
2. Git Status
3. File Browser
4. Conversations
5. Workspace
6. Notes (feature-flagged)

### 3.3 Adapter System

**Adapter Interface** (`internal/adapter/adapter.go`):
```go
type Adapter interface {
    ID() string
    Name() string
    Icon() string
    Detect(projectRoot string) (bool, error)
    Capabilities() CapabilitySet
    Sessions(projectRoot string) ([]Session, error)
    Messages(sessionID string) ([]Message, error)
    Usage(sessionID string) (*UsageStats, error)
    Watch(projectRoot string) (<-chan Event, io.Closer, error)
}
```

Each adapter is auto-registered via Go's `init()` function (blank imports in `main.go`):
```go
_ "github.com/marcus/sidecar/internal/adapter/claudecode"
_ "github.com/marcus/sidecar/internal/adapter/cursor"
// etc.
```

**Optional Interfaces**:
- `ProjectDiscoverer` — Discover related project dirs (deleted worktrees)
- `TargetedRefresher` — Refresh single session by ID
- `WatchScopeProvider` — Global vs per-project watching

### 3.4 Event System

**Event Bus** (`internal/event/`):
- Typed events with pub/sub fan-out
- Event types: `file_changed`, `git_changed`, `session_update`, `td_update`, `focus_changed`, `refresh_needed`, `error`

### 3.5 Epoch-based Staleness Detection

When switching projects, `Context.Epoch` is incremented. Async messages embed an epoch, and handlers discard messages from previous epochs:

```go
func IsStale(ctx *Context, msg EpochMessage) bool {
    return ctx != nil && msg.GetEpoch() != ctx.Epoch
}
```

---

## 4. Configuration System

**Config file**: `~/.config/sidecar/config.json`

**Root Config Structure**:
```go
type Config struct {
    Projects ProjectsConfig   // Project list for switcher
    Plugins  PluginsConfig    // Per-plugin settings
    Keymap   KeymapConfig     // Key binding overrides
    UI       UIConfig         // Theme, clock, Nerd Fonts
    Features FeaturesConfig   // Feature flags
}
```

**Per-plugin configs**: Each plugin has its own config struct (enabled, refresh interval, etc.)

**Per-project themes**: Projects can have their own theme via `ProjectConfig.Theme`

---

## 5. State Management

**State file**: `~/.config/sidecar/state.json`

Persists user preferences across sessions:
- Diff mode (unified vs side-by-side)
- Pane widths (draggable pane positions)
- Per-project plugin state (file browser selections, workspace selections)
- Active plugin per project
- Last active worktree per repo

All state access is thread-safe via `sync.RWMutex`.

---

## 6. Theming System

**Approach**: Global mutable style variables in `internal/styles/styles.go`

```go
var (
    Primary   = lipgloss.Color("#7C3AED")
    Secondary = lipgloss.Color("#3B82F6")
    // ... 50+ themeable color variables
)
```

`ApplyTheme()` updates all global variables + rebuilds all Lipgloss styles.

**Theme Resolution Priority**:
1. Per-project theme (if configured)
2. Global theme
3. Community scheme overlay
4. User overrides

**Tab rendering**: Supports gradient, per-tab color, solid, and minimal styles with automatic contrast calculation.

---

## 7. Modal System

**Declarative Modal Builder** (`internal/modal/`):
```go
modal.New("Title",
    modal.WithWidth(50),
    modal.WithVariant(modal.VariantDefault),
    modal.WithPrimaryAction("submit"),
).
    AddSection(modal.Text("Description")).
    AddSection(modal.Spacer()).
    AddSection(modal.Buttons(
        modal.Btn("OK", "submit"),
        modal.Btn("Cancel", "cancel"),
    ))
```

**App-level Modal Priority** (in `model.go`):
```go
const (
    ModalPalette          // Highest priority
    ModalHelp
    ModalUpdate
    ModalDiagnostics
    ModalQuitConfirm
    ModalProjectSwitcher
    ModalWorktreeSwitcher
    ModalThemeSwitcher
    ModalIssueInput
    ModalIssuePreview     // Lowest priority
)
```

---

## 8. Key Binding System

- **Registry**: Central registry with default bindings
- **User Overrides**: Via config `keymap.overrides` map
- **Plugin Bindings**: Plugins register bindings dynamically via `BindingRegistrar`
- **Context-aware**: Bindings activate based on focus context (e.g., "git-status", "file-browser")

---

## 9. UI Components (Reusable)

Located in `internal/ui/`:
- **Selection**: Generic list selection with cursor, scrolling, viewport
- **Scrollbar**: Visual scrollbar with track/thumb
- **Buttons**: Styled button rendering (normal, focused, hover, danger)
- **Confirm Dialog**: Yes/No confirmation with keyboard nav
- **Skeleton**: Loading placeholder animation
- **Braille Spinner**: Animated loading indicator
- **Overlay**: Centered overlay on top of content
- **Modal**: Modal overlay with backdrop

---

## 10. Terminal Integration (TTY)

Located in `internal/tty/`:
- **Interactive Mode**: Forwards keystrokes to tmux sessions
- **Adaptive Polling**: Polls tmux output with decay (fast when typing, slow when idle)
- **Escape Handling**: Double-escape exit, CSI sequence filtering
- **Mouse Forwarding**: SGR mouse protocol support
- **Output Buffer**: Scrollback buffer with change detection
- **Terminal Mode Detection**: Bracketed paste, mouse reporting

---

## 11. Key Design Decisions

### Silent Degradation
Plugins that fail to initialize are silently skipped:
```go
func (r *Registry) Register(p Plugin) error {
    if err := r.safeInit(p); err != nil {
        r.unavailable[p.ID()] = err.Error()
        return nil // Not an error
    }
    r.plugins = append(r.plugins, p)
    return nil
}
```

### Panic Recovery
All plugin lifecycle calls are wrapped in `defer recover()`:
```go
func (r *Registry) safeInit(p Plugin) (err error) {
    defer func() {
        if rec := recover(); rec != nil {
            err = fmt.Errorf("panic: %v", rec)
        }
    }()
    return p.Init(r.ctx)
}
```

### Auto-Registration Pattern
Adapters register themselves via `init()` functions, activated by blank imports in `main.go`.

### Worktree Awareness
The entire system is worktree-aware: plugins track both `WorkDir` (actual path) and `ProjectRoot` (main repo root). State is keyed by project root for sharing across worktrees.

### Feature Flags
Toggle features at runtime via config or CLI flags:
```go
features.IsEnabled("notes_plugin")
features.SetOverride("notes_plugin", true)
```

---

## 12. Dependencies (Key Libraries)

| Library | Purpose |
|---------|---------|
| `charmbracelet/bubbletea` | TUI framework (Elm architecture) |
| `charmbracelet/lipgloss` | Terminal styling |
| `charmbracelet/bubbles` | UI components (text input, etc.) |
| `charmbracelet/glamour` | Markdown rendering |
| `alecthomas/chroma` | Syntax highlighting |
| `fsnotify/fsnotify` | File system watching |
| `mattn/go-sqlite3` | SQLite for Cursor adapter |
| `modernc/sqlite` | Pure-Go SQLite alternative |
| `sahilm/fuzzy` | Fuzzy search matching |
| `atotto/clipboard` | System clipboard access |
| `golang.org/x/term` | Terminal detection |

---

## 13. Patterns Worth Adopting

1. **Plugin Architecture**: Clean interface with context injection, lifecycle management, panic recovery
2. **Adapter Pattern**: Uniform interface for multiple data sources with auto-detection
3. **Epoch-based Staleness**: Simple counter to invalidate stale async messages on context switch
4. **Declarative Modals**: Builder pattern for consistent modal UI
5. **Tiered Watching**: Hot (fsnotify) + Cold (polling) for efficient file watching
6. **Per-project Theming**: Theme resolution chain with project-specific overrides
7. **State Persistence**: Simple JSON state file with thread-safe accessors
8. **Silent Degradation**: Components that fail don't crash the app
9. **Context-aware Key Bindings**: Bindings activate based on current focus context
10. **Adaptive Polling**: Poll frequency decays based on user activity
