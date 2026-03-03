# FlutterCraft v0.2.0 — Progress Tracker

> **Last Updated:** 2026-03-03
> **Overall Progress:** 4/10 Phases (40%)
> **Current Phase:** Phase 5 — Git Control Plugin
> **Branch:** `feature/v0.2.0-tui`

---

## Phase Status

| Phase | Name | Status | Steps Done | Pushed |
|-------|------|--------|------------|--------|
| 1 | TUI Shell & Core Infrastructure | COMPLETE | 14/14 | No |
| 2 | Plugin Architecture & Core Systems | COMPLETE | 8/8 | No |
| 3 | FVM Manager Plugin | COMPLETE | 8/8 | No |
| 4 | Flutter Command Runner Plugin | COMPLETE | 11/11 | No |
| 5 | Git Control Plugin | NOT STARTED | 0/10 | No |
| 6 | Project Creator + Templates + Icons | NOT STARTED | 0/9 | No |
| 7 | File Browser Plugin | NOT STARTED | 0/7 | No |
| 8 | Workspace Manager Plugin | NOT STARTED | 0/7 | No |
| 9 | CLI Adapter Plugin | NOT STARTED | 0/12 | No |
| 10 | Polish & Release v0.2.0 | NOT STARTED | 0/9 | No |

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

- [ ] 5.1 Plugin shell
- [ ] 5.2 Status display
- [ ] 5.3 Diff viewer
- [ ] 5.4 Stage/Unstage
- [ ] 5.5 Commit
- [ ] 5.6 Push/Pull
- [ ] 5.7 Branch management
- [ ] 5.8 Log viewer
- [ ] 5.9 Stash
- [ ] 5.10 File watching

### Phase 6 — Project Creator + Templates + Icons

- [ ] 6.1 Wizard screen
- [ ] 6.2 Platform detection
- [ ] 6.3 Template registry
- [ ] 6.4 State management setup
- [ ] 6.5 Folder structure generation
- [ ] 6.6 App icon setup
- [ ] 6.7 Splash screen setup
- [ ] 6.8 Post-creation
- [ ] 6.9 Template preview

### Phase 7 — File Browser Plugin

- [ ] 7.1 Tree view
- [ ] 7.2 File preview
- [ ] 7.3 Quick open
- [ ] 7.4 File operations
- [ ] 7.5 Open in editor
- [ ] 7.6 Git integration
- [ ] 7.7 Filter/search

### Phase 8 — Workspace Manager Plugin

- [ ] 8.1 Project list
- [ ] 8.2 Project switching
- [ ] 8.3 Project discovery
- [ ] 8.4 Per-project state
- [ ] 8.5 Per-project theme
- [ ] 8.6 Recent projects
- [ ] 8.7 Project health

### Phase 9 — CLI Adapter Plugin

- [ ] 9.1 Adapter interface
- [ ] 9.2 Auto-detection
- [ ] 9.3 Claude Code adapter
- [ ] 9.4 Gemini CLI adapter
- [ ] 9.5 OpenCode adapter
- [ ] 9.6 CLI panel
- [ ] 9.7 Session management
- [ ] 9.8 Session persistence
- [ ] 9.9 Session history
- [ ] 9.10 Conversation viewer
- [ ] 9.11 Context auto-passing
- [ ] 9.12 Embedded terminal

### Phase 10 — Polish & Release

- [ ] 10.1 Settings screen
- [ ] 10.2 Error handling
- [ ] 10.3 Intro animation
- [ ] 10.4 Help system
- [ ] 10.5 Tests
- [ ] 10.6 Performance
- [ ] 10.7 Accessibility
- [ ] 10.8 Docs
- [ ] 10.9 Release v0.2.0

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
