# FlutterCraft — Architecture Reference

> Detailed architecture for the v0.2.0 TUI rewrite.

---

## Layers

```
┌─────────────────────────────────────────────────┐
│                  Presentation                    │
│  app.py, screens/, widgets/                      │
│  Textual App, Screens, Widgets, CSS              │
├─────────────────────────────────────────────────┤
│                    Plugins                        │
│  plugins/base.py + plugins/*/                     │
│  Feature modules: FVM, Flutter, Git, Creator...  │
├─────────────────────────────────────────────────┤
│                   Adapters                        │
│  adapters/base.py + adapters/*/                   │
│  External CLI integration: Claude, Gemini, etc.  │
├─────────────────────────────────────────────────┤
│                     Core                          │
│  core/events.py, config.py, state.py, keymap.py │
│  Event bus, config, state, keybindings, platform │
├─────────────────────────────────────────────────┤
│                   Commands                        │
│  commands/core/                                   │
│  Registry, Executor, Command base (from v0.1.x) │
├─────────────────────────────────────────────────┤
│                    Themes                         │
│  themes/                                          │
│  Theme data, manager, built-in themes, CSS       │
└─────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Presentation Layer

**FlutterCraftApp** (`app.py`):
- Extends `textual.app.App`
- Manages screen stack (Dashboard, ProjectWizard, Settings)
- Owns the plugin registry and adapter registry
- Handles global keybindings (Ctrl+P palette, Ctrl+Q quit, ? help)

**Dashboard Screen** (`screens/dashboard.py`):
- Main layout: Header | Sidebar | Content | Footer
- Sidebar shows plugin tabs
- Content area renders the active plugin's `compose()` output
- Command input at bottom for text commands

**Widgets** (`widgets/`):
- `Header`: Status bar — project name, Flutter/FVM version, git branch, platform
- `Footer`: Context-aware keybinding hints — changes per focused plugin
- `Sidebar`: Plugin tab list with icons, numbers (1-9), active highlight
- `CommandInput`: Text input with fuzzy autocomplete from command registry
- `OutputPanel`: Scrollable rich text with ANSI support, real-time streaming
- `Modal`: Declarative builder with priority stack
- `Spinner`: Loading indicators for async operations

### 2. Plugin System

**Plugin Interface** (`plugins/base.py`):
```python
class Plugin(ABC):
    @abstractmethod
    def id(self) -> str: ...
    @abstractmethod
    def name(self) -> str: ...
    @abstractmethod
    def icon(self) -> str: ...
    @abstractmethod
    def init(self, ctx: PluginContext) -> None: ...
    @abstractmethod
    def start(self) -> None: ...
    @abstractmethod
    def stop(self) -> None: ...
    @abstractmethod
    def compose(self) -> ComposeResult: ...
    def update(self, event: Event) -> None: ...
    def commands(self) -> list[Command]: ...
    @property
    def is_focused(self) -> bool: ...
    @property
    def focus_context(self) -> str: ...
```

**Plugin Context** (`plugins/base.py`):
```python
@dataclass(slots=True)
class PluginContext:
    work_dir: Path
    project_root: Path
    config: ConfigManager
    state: StateManager
    event_bus: EventBus
    adapters: dict[str, CLIAdapter]
    keymap: KeymapRegistry
```

**Plugin Registry** (`plugins/base.py`):
- `register(plugin)` — init with context, catch exceptions (silent degradation)
- `start_all()` / `stop_all()` — lifecycle management
- `reinit(new_context)` — stop all, update context, restart (for project switching)
- `get(id)` — lookup by ID
- `list_plugins()` — all active plugins in registration order (= tab order)

**Registered Plugins** (in order = tab order):
1. FVM Manager (`fvm_manager/`)
2. Flutter Commands (`flutter_commands/`)
3. Git Control (`git_control/`)
4. File Browser (`file_browser/`)
5. Project Creator (`project_creator/`)
6. Workspace Manager (`workspace/`)
7. CLI Adapters (`cli_adapter/`)

### 3. Adapter System

**CLIAdapter Interface** (`adapters/base.py`):
```python
class CLIAdapter(ABC):
    @abstractmethod
    def id(self) -> str: ...
    @abstractmethod
    def name(self) -> str: ...
    @abstractmethod
    def icon(self) -> str: ...
    @abstractmethod
    def detect(self) -> bool: ...
    @abstractmethod
    def start_session(self, project_root: Path) -> Session: ...
    @abstractmethod
    def send(self, session_id: str, message: str) -> None: ...
    @abstractmethod
    def stream_output(self, session_id: str) -> Iterator[str]: ...
    @abstractmethod
    def stop(self, session_id: str) -> None: ...
    def sessions(self) -> list[Session]: ...
    def messages(self, session_id: str) -> list[Message]: ...
```

**Auto-detection** (`adapters/detect.py`):
- Scans PATH for known binaries: `claude`, `gemini`, `opencode`
- Returns dict of available adapters
- Called at app startup and on project switch

### 4. Core Infrastructure

**Event Bus** (`core/events.py`):
- Typed events: `FileChanged`, `GitChanged`, `SessionUpdate`, `FocusChanged`, `RefreshNeeded`, `Error`
- `subscribe(event_type, callback)` / `publish(event)`
- Fan-out to all subscribers of that event type

**Config Manager** (`core/config.py`):
- File: `~/.fluttercraft/config.json`
- Dot-notation access: `config.get("completion.fuzzy_enabled")`
- Deep merge on load with defaults
- Default schema:
  ```json
  {
    "version": "0.2.0",
    "theme": "default_dark",
    "editor": "code",
    "animations": {"enabled": true, "reduced_motion": false},
    "completion": {"fuzzy_enabled": true},
    "history": {"max_entries": 10000},
    "ui": {"show_tips": true, "show_timing": true},
    "keymap": {"overrides": {}},
    "features": {},
    "projects": []
  }
  ```

**State Manager** (`core/state.py`):
- File: `~/.fluttercraft/state.json`
- Per-project state keyed by project root
- Thread-safe via `threading.RLock`
- Tracks: active plugin, pane widths, file selections, last session

**Keymap Registry** (`core/keymap.py`):
- Default bindings for all global and plugin-specific keys
- User overrides from `config.keymap.overrides`
- Context-aware: bindings activate based on `focus_context`
- Plugins register additional bindings dynamically

### 5. Command System (reused from v0.1.x)

**CommandRegistry** — stores `Command` instances keyed by name + aliases
**CommandExecutor** — `dispatch(raw_input, context)` → tokenize → resolve → execute → `CommandResult`
**Command** — ABC with `execute(context, args) -> CommandResult`
**CommandResult** — `success`, `message`, `payload`, `should_continue`, `execution_time`
**CommandContext** — runtime bag: platform_info, flutter_info, fvm_info, console

### 6. Theme System (migrated from v0.1.x)

**Theme** dataclass — colors, accents, gradients, semantic colors
**ThemeManager** — singleton, persists to `~/.fluttercraft/theme.json`
**13 built-in themes** — 7 dark (default: VS Code Dark), 6 light
**Textual CSS** — themes map to CSS variables for Textual widgets

---

## Data Flow

```
User Input → CommandInput widget
  → CommandExecutor.dispatch()
    → Command.execute(context, args)
      → CommandResult
        → OutputPanel (display result)
        → EventBus.publish(event) (if state changed)
          → Subscribed plugins update their views
          → Header refreshes (Flutter/FVM/git info)
```

```
File System Change → watchdog observer
  → EventBus.publish(FileChanged)
    → Git Control plugin refreshes status
    → File Browser plugin refreshes tree
```

```
Project Switch → Workspace plugin
  → PluginRegistry.reinit(new_context)
    → All plugins stop → update context → restart
    → State loaded for new project
    → Header refreshes
```

---

## Key Design Decisions

1. **Textual over prompt_toolkit**: Full widget system, CSS styling, built-in mouse support, screens, proper layout engine. prompt_toolkit is limited to input widgets.

2. **Plugin architecture**: Every feature is isolated. Plugins can fail without crashing the app. New features = new plugins, no touching existing code.

3. **Event bus over direct calls**: Plugins don't import each other. Git plugin doesn't know about File Browser. They communicate via events.

4. **Adapter pattern for CLIs**: Same interface for Claude, Gemini, OpenCode. Adding a new CLI = one new file implementing CLIAdapter.

5. **Reuse command registry**: The v0.1.x command system works well. Don't rewrite it — plug it into the TUI's CommandInput widget.

6. **Per-project everything**: State, theme, active plugin — all scoped per project. Switching projects feels like switching workspaces.
