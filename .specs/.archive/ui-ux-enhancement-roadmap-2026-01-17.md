# FlutterCraft v0.1.3 Signature UI/UX Enhancement
# Single Release with Phase-Based Commits

**Animation Style:** Sleek & Professional (Claude Code / OpenCode level)  
**Timeline:** 2-3 weeks  
**Strategy:** Git commits track phases, single v0.1.3 release  
**Date:** 2026-01-17

---

## 🎯 Vision

Transform FlutterCraft into a **sleek, professional CLI** with:
- ✨ Subtle, purposeful animations (Claude Code / OpenCode style)
- 🎨 Perfect theming with instant hot-reload
- 🚀 All Flutter/FVM commands working
- 💻 Cross-platform excellence
- ⚡ Smart fuzzy completions
- 📊 Clean progress indicators
- ⚙️ Elegant settings interface

---

## 📋 Phase-Based Development (Git Commits)

### **Branch Strategy:**
```
main
  └─> feature/v0.1.3-signature-ui
      ├─> phase1: Foundation (commits 1-5)
      ├─> phase2: Animations & Settings (commits 6-10)
      ├─> phase3: Commands (commits 11-15)
      ├─> phase4: Cross-platform & Polish (commits 16-20)
      └─> phase5: Final Integration (commits 21-22)
          └─> merge → tag v0.1.3
```

---

## 🚀 Phase 1: Foundation (Commits 1-5)

**Focus:** Core UX improvements  
**Platform:** Windows (primary development)  
**Testing:** Quick smoke test on Mac/Linux

### Commit 1: Smart Completion Menu
**File:** `utils/beautiful_prompt.py`

**Changes:**
- Hybrid visibility mode:
  - Auto-show when typing `/` (slash commands)
  - Manual toggle with `Ctrl+Space` for other commands
  - Hide when idle or exact match typed
  - Hide with `Esc`
- Fix Enter key behavior:
  - Submit input if no completion selected
  - Select completion if menu active and item highlighted
- Add visual indicator: "Press Ctrl+Space for suggestions" when menu hidden

**Animation:** Smooth 200ms fade-in/out for menu

---

### Commit 2: Persistent Command History
**Files:** 
- Create: `utils/history_manager.py`
- Modify: `utils/beautiful_prompt.py`, `commands/start.py`

**Changes:**
- Save history to `~/.fluttercraft/history`
- Max 10,000 entries (configurable)
- Deduplication (consecutive duplicates removed)
- `Ctrl+R` reverse search with fuzzy matching
- Up/Down arrows for sequential history
- History loaded on startup, saved after each command

**Animation:** Smooth 150ms slide-up for history search panel

---

### Commit 3: Command Execution Timing
**Files:** 
- Modify: `commands/core/executor.py`, `commands/start.py`

**Changes:**
- Add timer to CommandExecutor
- Display execution time after commands:
  - `✓ Completed in 1.23s` (green)
  - `✗ Failed after 5.67s` (red)
- Format: <1s = milliseconds, >=1s = seconds with 2 decimals

**Animation:** Gentle fade-in for timing display (150ms)

---

### Commit 4: Fuzzy Completion Matching
**Files:**
- Modify: `utils/beautiful_prompt.py`
- Add dependency: `rapidfuzz>=3.0.0`

**Changes:**
- Implement fuzzy matching:
  - Type `fvmr` → matches `fvm releases`
  - Type `flut` → matches `flutter upgrade`
- Highlight matched characters in results
- Sort by relevance score (exact > prefix > fuzzy)
- Show match percentage in meta (optional)
- Cache results for performance

**Animation:** Smooth reflow of completion list (no animation, instant update)

---

### Commit 5: Enhanced Text Input Area
**Files:**
- Modify: `utils/beautiful_prompt.py`

**Changes:**
- Multi-line input support
- `Shift+Enter` for new line (Enter still submits)
- Syntax highlighting for commands (basic)
- Line numbers in multi-line mode (optional)
- Auto-grow input area (1-5 lines max)

**Animation:** Smooth height transition when expanding input (200ms ease-out)

---

## ✨ Phase 2: Animations & Settings (Commits 6-10)

**Focus:** Sleek animations + Settings UI  
**Platform:** Windows  
**Testing:** Visual verification

### Commit 6: Animation Foundation
**Files:**
- Create: `utils/animations/engine.py`
- Create: `utils/animations/effects.py`

**Animation Engine:**
- Frame-based animation system (30fps, not 60fps - smoother on slower terminals)
- Easing functions: ease-in, ease-out, ease-in-out
- Transitions: fade, slide, scale
- No particles, no confetti, no sparkles

**Core Animations:**
- `fade(duration=200ms)` - Opacity 0→1 or 1→0
- `slide(direction, duration=300ms)` - Slide in/out
- `scale(from=0.95, to=1.0, duration=200ms)` - Subtle scale
- `pulse(duration=150ms)` - Single pulse (not repeating)

---

### Commit 7: Sleek Startup Animation
**Files:**
- Modify: `commands/start.py`
- Modify: `utils/themed_display.py`

**Startup Sequence:**
1. ASCII logo fades in (300ms)
2. Version info slides in from left (200ms, staggered)
3. System info fades in (150ms)
4. Ready indicator pulses once (100ms)

**No:** Particles, typewriter effect, sparkles

**Animation:** Clean, professional, fast (<1 second total)

---

### Commit 8: Command Feedback Animations
**Files:**
- Modify: `commands/core/executor.py`
- Modify: `commands/start.py`

**Success Animation:**
- Green checkmark fades in (150ms)
- Subtle scale pulse (0.95→1.0→0.98→1.0, 300ms total)
- Message fades in (100ms)

**Error Animation:**
- Red X fades in (150ms)
- Very subtle horizontal shake (5px, 200ms)
- Error panel slides in from right (200ms)

**Warning Animation:**
- Yellow warning icon pulses once (150ms)
- Message fades in (100ms)

**No:** Confetti, particles, excessive movement

---

### Commit 9: Progress Indicators
**Files:**
- Create: `utils/progress.py`
- Modify: `commands/fvm/install.py`, `commands/flutter/flutter_command.py`

**Progress Bars (for deterministic operations):**
- Clean Rich progress bars
- Smooth percentage updates
- ETA display
- Themed colors
- No shimmer/wave effects (just clean bars)

**Spinners (for indeterminate operations):**
- Simple, clean spinners (dots, line, arc)
- Theme-colored
- Context-specific icons (⬇ download, ⚙ processing, 📦 installing)

**Animation:** Smooth progress updates (100ms intervals)

---

### Commit 10: Settings Panel
**Files:**
- Create: `commands/settings/settings_ui.py`
- Create: `commands/settings/settings_command.py`
- Create: `infrastructure/storage/config_manager.py`

**Settings UI (Simple TUI):**
```
╭─── Settings ────────────────────────────────╮
│ [ General ] Appearance  Keybindings         │
│ ──────────────────────────────────────────│
│                                             │
│  Theme:           [gradient ▼]              │
│  Animations:      [ON  / OFF]               │
│  Compact Mode:    [OFF / ON ]               │
│  Show Tips:       [ON  / OFF]               │
│                                             │
│         [Save]  [Cancel]  [Reset]           │
╰─────────────────────────────────────────────╯
```

**Features:**
- Tab navigation between sections
- Live preview (some settings)
- Persist to `~/.fluttercraft/config.json`
- Keyboard-only navigation

**Animation:** Panel slides in from center (300ms ease-out)

---

## 🎯 Phase 3: Commands (Commits 11-15)

**Focus:** Complete Flutter/FVM command set  
**Platform:** Windows base, test on all platforms  
**Testing:** Comprehensive on all platforms

### Commit 11: Flutter Doctor Command
**Files:**
- Create: `commands/flutter/doctor.py`

**Features:**
- Run `flutter doctor -v`
- Colored output (✓ green, ⚠ yellow, ✗ red)
- Categorized issues
- Links to fix documentation

**Animation:** Results fade in (150ms)

---

### Commit 12: Flutter Version Command
**Files:**
- Modify: `commands/flutter/version.py`

**Features:**
- Show Flutter version with ASCII art
- Display Dart version
- Display engine version
- Cached for 1 hour

**Animation:** Version info slides in (200ms)

---

### Commit 13: FVM Advanced Commands
**Files:**
- Create: `commands/fvm/use.py`
- Create: `commands/fvm/remove.py`
- Create: `commands/fvm/current.py`

**Features:**
- `fvm use <version>` - Switch version (with confirmation)
- `fvm remove <version>` - Delete version (with confirmation)
- `fvm current` - Show active version

**Animation:** Confirmation dialog slides in (200ms)

---

### Commit 14: Theme Hot-Reload
**Files:**
- Modify: `commands/theme/interactive_selector.py`
- Modify: `utils/themes/theme_manager.py`

**Features:**
- Apply themes instantly without restart
- Smooth transition (fade old→new, 500ms)
- Preview mode before applying
- Comparison view (split-screen)

**Animation:** Cross-fade between themes (500ms ease-in-out)

---

### Commit 15: Context Awareness
**Files:**
- Create: `utils/project_detector.py`
- Modify: `commands/start.py`, `utils/beautiful_prompt.py`

**Features:**
- Detect Flutter project (pubspec.yaml)
- Show project info in header
- Project-specific completions
- FVM project version detection (.fvmrc)

**Animation:** Project info slides in when detected (200ms)

---

## 💻 Phase 4: Cross-Platform & Polish (Commits 16-20)

**Focus:** Mac/Linux support + final polish  
**Platform:** All platforms  
**Testing:** Comprehensive cross-platform

### Commit 16: Mac-Specific Fixes
**Platform:** macOS (Sonoma+)

**Tasks:**
- Test all features on Mac
- Fix path separators
- Fix terminal compatibility (Terminal.app, iTerm2)
- Fix Homebrew integration (if needed)
- Fix keybindings (Mac vs Windows)

---

### Commit 17: Linux-Specific Fixes
**Platform:** Linux (Ubuntu 22.04+)

**Tasks:**
- Test all features on Linux
- Fix apt/snap integration
- Fix terminal compatibility (gnome-terminal, Alacritty)
- Fix path handling
- Fix permissions issues

---

### Commit 18: Enhanced Error Handling
**Files:**
- Modify: `commands/core/executor.py`

**Features:**
- "Did you mean...?" suggestions (fuzzy match)
- Links to documentation
- Common fix suggestions
- Copy error to clipboard option

**Animation:** Suggestions slide in (200ms)

---

### Commit 19: Signature UI Flourishes
**Files:**
- Create: `utils/ui/search.py`
- Modify: `commands/start.py`

**Features:**
- Search in output (`Ctrl+F`)
- Collapsible sections (help, long output)
- Optional status bar (toggleable)

**Animation:** Search bar slides up from bottom (200ms)

---

### Commit 20: Performance & Accessibility
**Files:**
- Multiple files

**Optimizations:**
- Lazy load completions
- Virtual scrolling for long lists
- Cache platform/version info (1 hour TTL)
- Debounce fuzzy matching (100ms)

**Accessibility:**
- High-contrast theme
- Keyboard-only navigation (no mouse required)
- Reduce motion option (disable animations)
- Screen reader labels

---

## 🎉 Phase 5: Final Integration (Commits 21-22)

**Focus:** Documentation + release prep  
**Platform:** All  
**Testing:** Final QA

### Commit 21: Documentation Updates
**Files:**
- Update: `CHANGELOG.md`, `README.md`, `AGENTS.md`
- Create demo GIFs/videos

**Updates:**
- Comprehensive v0.1.3 changelog
- Updated README with new features
- Screenshots/demos of new UI

---

### Commit 22: Final Polish & Release
**Tasks:**
- Final testing on all platforms
- Performance profiling
- Bug fixes
- Tag v0.1.3

---

## 🎨 Animation Style Guide (Sleek)

### **Timing:**
- **Instant:** <100ms (feels instant)
- **Fast:** 100-200ms (quick but smooth)
- **Normal:** 200-300ms (standard)
- **Slow:** 300-500ms (deliberate)

### **Easing:**
- **ease-out:** Fast start, slow end (entering)
- **ease-in:** Slow start, fast end (exiting)
- **ease-in-out:** Smooth both ends (transitions)

### **Examples:**
```python
# Sleek fade-in (like Claude Code)
fade_in(element, duration=200, easing='ease-out')

# Sleek slide (like OpenCode)
slide_in(panel, direction='right', duration=300, easing='ease-out')

# Subtle pulse (one-time, not looping)
pulse(checkmark, scale=1.05, duration=150)
```

### **What to Animate:**
✅ Panel entrances/exits
✅ Menu show/hide
✅ Success/error feedback
✅ Theme transitions
✅ Search/filter results

❌ Background elements
❌ Continuous loops
❌ Excessive movement
❌ Distracting effects

---

## ✅ Success Criteria (v0.1.3)

- ✅ Sleek, professional animations (Claude Code / OpenCode level)
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ All Flutter/FVM commands working
- ✅ Smart fuzzy completions
- ✅ Persistent history with Ctrl+R search
- ✅ Theme hot-reload (instant)
- ✅ Settings panel (clean TUI)
- ✅ Performance optimized (smooth, no lag)
- ✅ Accessible (keyboard-only, reduced motion)
- ✅ Ready for production

---

**Plan Status:** ✅ Updated for Sleek Animations  
**Ready to Build:** Yes 🚀
