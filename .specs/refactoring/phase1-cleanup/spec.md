---
# Cleanup and Consolidation - v0.1.3
# Phase 1 of FINAL Architecture Migration
---

# Refactor: Cleanup and Consolidation

**Status:** In Progress  
**Created:** 2026-01-17  
**Owner:** OpenCode AI Agent  
**Target Version:** v0.1.3  
**Priority:** High  
**Scope:** Medium

---

## 1. Objective

Clean up the FlutterCraft codebase by removing duplicate code, consolidating overlapping modules, and fixing version inconsistencies **without** changing the current directory structure. This prepares for future migration to FINAL architecture.

---

## 2. Scope of Phase 1

### What We're Doing:
- ✅ Remove duplicate theme selector modules (keep only one)
- ✅ Remove legacy `command_handler.py` (replaced by executor)
- ✅ Consolidate duplicate utility functions (git info, path utils)
- ✅ Remove deprecated `display_utils.py`
- ✅ Synchronize version numbers across all files
- ✅ Clean up orphaned imports
- ✅ Consolidate documentation (remove redundant/outdated docs)

### What We're NOT Doing:
- ❌ Reorganizing into domain/application/infrastructure layers (saved for v0.2.0+)
- ❌ Moving files between directories
- ❌ Changing public APIs
- ❌ Major refactoring

**Risk Level:** Low - only removing unused code and fixing duplicates

---

## 3. Tasks

### Task 1: Remove Duplicate Theme Selectors

**Keep:**
- `fluttercraft/commands/theme/interactive_selector.py`

**Remove:**
- `fluttercraft/commands/theme/interactive_theme_selector.py`
- `fluttercraft/commands/theme/live_theme_selector.py`
- `fluttercraft/commands/theme/rich_theme_selector.py`

**Verification:**
- Check no imports of removed files exist
- Theme selection still works

### Task 2: Remove Legacy Command Handler

**Remove:**
- `fluttercraft/commands/command_handler.py` (430 lines - replaced by executor pattern)

**Verification:**
- Search for imports: `from fluttercraft.commands.command_handler`
- Remove any lingering imports
- All commands work via new executor

### Task 3: Consolidate Display Utilities

**Remove:**
- `fluttercraft/utils/display_utils.py` (deprecated)
- Duplicate functions in `beautiful_display.py`

**Migrate to:**
- Move `get_git_info()` → `fluttercraft/utils/platform_utils.py`
- Move `get_current_path()` → `fluttercraft/utils/platform_utils.py`

**Update Callers:**
- Update imports in `beautiful_prompt.py`
- Update imports in `beautiful_display.py`

### Task 4: Synchronize Version Numbers

**Current Issue:**
- `__init__.py` says 0.1.2
- `setup.py` says 0.1.3
- `CHANGELOG.md` latest is 0.1.2

**Fix:**
- Set all to 0.1.3
- Add entry to CHANGELOG.md for v0.1.3

### Task 5: Clean Up Documentation

**Remove:**
- `v0.1.3-roadmap.md` (outdated, now in .specs/)
- Move to `docs/archive/`:
  - `docs/BUGS_FIXED.md`
  - `docs/development-progress.md`
  - `docs/CLI_REDESIGN.md`
  - `docs/GEMINI_INTERFACE.md`

**Update:**
- `docs/README.md` - Remove references to archived docs

### Task 6: Update Context System

**Update:**
- `.context/dependencies.yaml` - Remove orphaned modules
- Create `.context/components/commands.md`
- Create `.context/components/themes.md`
- Create `.context/components/utils.md`

---

## 4. Acceptance Criteria

- [ ] All duplicate theme selectors removed
- [ ] Legacy command_handler.py removed
- [ ] Duplicate utility functions consolidated
- [ ] Version numbers synchronized (all say 0.1.3)
- [ ] Outdated docs moved to archive/
- [ ] Context system updated
- [ ] All tests pass
- [ ] CLI works identically to before
- [ ] No broken imports
- [ ] Flake8 passes
- [ ] Black formatting passes

---

## 5. Testing Strategy

**Before Changes:**
1. Run full test suite (if tests exist)
2. Manual CLI test: `fluttercraft start`
3. Test all commands work

**After Changes:**
1. Run full test suite again
2. Manual CLI test again
3. Verify no import errors
4. Test theme selection
5. Test all FVM commands
6. Test all Flutter commands

---

## 6. Timeline

- Task 1: 15 min
- Task 2: 10 min
- Task 3: 30 min
- Task 4: 10 min
- Task 5: 20 min
- Task 6: 30 min
- Testing: 20 min

**Total:** ~2 hours

---

## 7. Success Metrics

- Code reduction: ~1000+ lines removed
- Duplicate code: 0%
- Version consistency: 100%
- Tests passing: 100%
- CLI working: 100%

---

**Let's execute this cleanup!**
