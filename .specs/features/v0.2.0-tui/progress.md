# FlutterCraft v0.2.0 — Progress Tracker

> **Last Updated:** 2026-03-05
> **Overall Progress:** 10/10 Phases (100%)
> **Current Phase:** COMPLETE — v0.2.0 ready
> **Branch:** `feature/v0.2.0-tui`

---

## Phase Status

| Phase | Name | Status | Steps Done | Pushed |
|-------|------|--------|------------|--------|
| 1 | TUI Shell & Core Infrastructure | COMPLETE | 14/14 | No |
| 2 | Plugin Architecture & Core Systems | COMPLETE | 8/8 | No |
| 3 | FVM Manager Plugin | COMPLETE | 8/8 | No |
| 4 | Flutter Command Runner Plugin | COMPLETE | 11/11 | No |
| 5 | Git Control Plugin | COMPLETE | 10/10 | No |
| 6 | Project Creator + Templates + Icons | COMPLETE | 9/9 | No |
| 7 | File Browser Plugin | COMPLETE | 7/7 | No |
| 8 | Workspace Manager Plugin | COMPLETE | 7/7 | No |
| 9 | CLI Adapter Plugin | COMPLETE | 12/12 | No |
| 10 | Polish & Release v0.2.0 | COMPLETE | 9/9 | No |

---

## Detailed Step Tracking

### Phase 1 — TUI Shell & Core Infrastructure

- [x] 1.1 Textual App skeleton
- [x] 1.2 Event bus
- [x] 1.3 Config manager
- [x] 1.4 State persistence
- [x] 1.5 Platform utils
- [x] 1.6 Header widget
- [x] 1.7 Footer widget
- [x] 1.8 Command input widget
- [x] 1.9 Output panel widget
- [x] 1.10 Sidebar widget
- [x] 1.11 Draggable panes
- [x] 1.12 Mouse support
- [x] 1.13 Theme integration
- [x] 1.14 Cross-platform

### Phase 2 — Plugin Architecture & Core Systems

- [x] 2.1 Plugin interface
- [x] 2.2 Plugin registry
- [x] 2.3 Plugin context
- [x] 2.4 Declarative modal system
- [x] 2.5 Command palette
- [x] 2.6 Keybinding registry
- [x] 2.7 Feature flags
- [x] 2.8 Notification system

### Phase 3 — FVM Manager Plugin

- [x] 3.1 Plugin shell
- [x] 3.2 Install/Uninstall FVM
- [x] 3.3 Releases browser
- [x] 3.4 Version install
- [x] 3.5 Version switching
- [x] 3.6 Version removal
- [x] 3.7 FVM doctor
- [x] 3.8 FVM config

### Phase 4 — Flutter Command Runner Plugin

- [x] 4.1 Plugin shell
- [x] 4.2 flutter doctor
- [x] 4.3 flutter upgrade
- [x] 4.4 flutter devices
- [x] 4.5 flutter run
- [x] 4.6 flutter build
- [x] 4.7 flutter test
- [x] 4.8 flutter analyze
- [x] 4.9 flutter pub
- [x] 4.10 flutter clean
- [x] 4.11 flutter create

### Cross-Phase Enhancements (done during Phase 3–4)

- [x] Command registry wiring — slash commands (/help, /clear, /theme, /quit), plugin routing via `handle_command`
- [x] Output panel resizable — mouse drag (OutputResizeHandle) + Ctrl+Up/Down keyboard shortcuts
- [x] Live theme preview — theme picker (Ctrl+T) applies theme on every Up/Down, restores original on Escape
- [x] Navigation — Escape to go home (double-Escape from input), digit shortcuts 0–7 from command input

### Phase 5 — Git Control Plugin

- [x] 5.1 Plugin shell — branch bar + file list (left) + diff viewer (right)
- [x] 5.2 Status display — staged/unstaged/untracked with icons and colors
- [x] 5.3 Diff viewer — colorized unified diff, auto-shows on navigation
- [x] 5.4 Stage/Unstage — per-file (s/u keys), bulk stage-all (a key)
- [x] 5.5 Commit — modal with message input and amend option
- [x] 5.6 Push/Pull/Fetch — with confirmations and rebase option for pull
- [x] 5.7 Branch management — list (b), create (n), switch/delete via handle_command
- [x] 5.8 Log viewer — recent commits with hash/author/date/message (l key)
- [x] 5.9 Stash — push (z), pop (Z), list via handle_command
- [x] 5.10 File watching — watchdog observer + 10s polling fallback

### Phase 6 — Project Creator + Templates + Icons

- [x] 6.1 Multi-step wizard (name → org → platforms → template → features → review)
- [x] 6.2 Platform auto-detection (Android SDK, Xcode, Chrome, Linux/Windows)
- [x] 6.3 Template registry (simple, bloc, riverpod, provider, getx, mobx, mvvm, clean_arch)
- [x] 6.4 State management deps auto-added to pubspec.yaml
- [x] 6.5 Folder structure per template (with .gitkeep)
- [x] 6.6 App icon setup — flutter_launcher_icons config
- [x] 6.7 Splash screen setup — flutter_native_splash config
- [x] 6.8 Post-creation guide + open in editor (E key)
- [x] 6.9 Template preview (P key — folder tree + deps)

### Phase 7 — File Browser Plugin

- [x] 7.1 Tree view
- [x] 7.2 File preview
- [x] 7.3 Quick open
- [x] 7.4 File operations
- [x] 7.5 Open in editor
- [x] 7.6 Git integration
- [x] 7.7 Filter/search

### Phase 8 — Workspace Manager Plugin

- [x] 8.1 Project list
- [x] 8.2 Project switching
- [x] 8.3 Project discovery
- [x] 8.4 Per-project state
- [x] 8.5 Per-project theme
- [x] 8.6 Recent projects
- [x] 8.7 Project health

### Phase 9 — CLI Adapter Plugin

- [x] 9.1 Adapter interface
- [x] 9.2 Auto-detection
- [x] 9.3 Claude Code adapter
- [x] 9.4 Gemini CLI adapter
- [x] 9.5 OpenCode adapter
- [x] 9.6 CLI panel
- [x] 9.7 Session management
- [x] 9.8 Session persistence
- [x] 9.9 Session history
- [x] 9.10 Conversation viewer
- [x] 9.11 Context auto-passing
- [x] 9.12 Embedded terminal

### Phase 10 — Polish & Release

- [x] 10.1 Settings screen (Ctrl+, or /settings — feature flags, theme shortcut)
- [x] 10.2 Error handling (global on_exception → ~/.fluttercraft/error.log)
- [x] 10.3 Intro animation (SplashScreen — 1.4s logo before dashboard)
- [x] 10.4 Help system (HelpScreen modal — ? key or /help, full keyboard reference)
- [x] 10.5 Tests (42 adapter tests, 66 file browser tests, 48 workspace tests)
- [x] 10.6 Performance (lazy plugin mounting, deferred focus, thread workers)
- [x] 10.7 Accessibility (keyboard-only nav, focus management, context hints in footer)
- [x] 10.8 Docs (GUIDE.md — full user guide with all plugins, keybindings, troubleshooting)
- [x] 10.9 Release v0.2.0 (version confirmed at 0.2.0 in __init__.py)

---

## Commit Log

_Commits will be logged here as they are made._

| Commit | Phase | Step | Message | Date |
|--------|-------|------|---------|------|
| — | — | — | — | — |

---

## Test Log

_Track test results after each feature implementation._

**Workflow:** Agent implements → Agent writes tests → User runs tests → Report results here → Debug if needed → Commit

| Date | Step | Test File | Auto Result | Manual Result | Notes |
|------|------|-----------|-------------|---------------|-------|
| — | — | — | — | — | — |

### Test Commands Quick Reference

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/core/test_events.py -v

# Run specific test
python -m pytest tests/core/test_events.py::test_event_bus_subscribe -v

# Run with coverage
python -m pytest tests/ --cov=fluttercraft --cov-report=term-missing

# Run only unit tests (fast)
python -m pytest tests/ -v -m "not manual"

# Launch app for manual testing
python -m fluttercraft start
```

---

## Blockers & Notes

_Track any blockers, decisions, or notes here._

| Date | Type | Description | Resolution |
|------|------|-------------|------------|
| — | — | — | — |
