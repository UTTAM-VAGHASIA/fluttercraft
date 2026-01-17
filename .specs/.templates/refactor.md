---
# Refactoring Specification Template
# Copy this template to .specs/refactoring/<refactor-name>/spec.md
---

# Refactor: [Refactoring Name]

**Status:** Planning | In Progress | Under Review | Completed | Cancelled  
**Created:** YYYY-MM-DD  
**Owner:** [Your Name or AI Agent Session ID]  
**Target Version:** vX.Y.Z  
**Priority:** High | Medium | Low  
**Scope:** Small | Medium | Large

---

## 1. Objective

**What are we refactoring?**

[Clear description of what's being refactored and why]

**Example:**
> Consolidate three separate display utility modules (`beautiful_display.py`, `display_utils.py`, `themed_display.py`) into a single, cohesive display service that follows the theme service pattern.

---

## 2. Motivation

**Why refactor this now?**

- [ ] Code duplication
- [ ] Performance issues
- [ ] Difficult to maintain
- [ ] Poor architecture
- [ ] Preparing for new feature
- [ ] Technical debt reduction
- [ ] Other: [Explain]

**Specific Problems:**
1. [Problem 1]
2. [Problem 2]
3. [Problem 3]

**Example:**
1. Three modules have duplicate functions (get_git_info, get_current_path)
2. Unclear which module to use for display operations
3. Theming logic scattered across multiple files
4. Testing is difficult due to tight coupling

---

## 3. Current State

### 3.1. Architecture (Before)

**Current Structure:**

```
fluttercraft/utils/
├── beautiful_display.py (402 lines)
│   ├── ASCII art functions
│   ├── Git info functions
│   ├── Path utilities
│   └── Display helpers
├── display_utils.py (114 lines)
│   ├── Legacy display functions
│   └── Welcome art
└── themed_display.py (78 lines)
    └── Facade to ThemeDisplayService
```

**Current Dependencies:**

```yaml
beautiful_display.py:
  depends_on:
    - pyfiglet
    - rich
    - subprocess
  depended_by:
    - commands/start.py
    - commands/bootstrap.py

display_utils.py:
  depends_on:
    - pyfiglet
    - rich
  depended_by:
    - main.py (deprecated usage)

themed_display.py:
  depends_on:
    - utils/themes/service.py
  depended_by:
    - commands/start.py
    - commands/core/executor.py
```

### 3.2. Problems Identified

| Issue | Severity | Impact |
|-------|----------|--------|
| Function duplication | High | Maintenance burden |
| Unclear API | Medium | Developer confusion |
| Scattered theming logic | Medium | Inconsistent UI |
| Legacy code | Low | Technical debt |

### 3.3. Current Test Coverage

- `beautiful_display.py`: 45% coverage
- `display_utils.py`: 0% coverage (legacy)
- `themed_display.py`: 80% coverage

**Total Coverage:** 42% (needs improvement)

---

## 4. Target State

### 4.1. Architecture (After)

**Target Structure:**

```
fluttercraft/presentation/ui/
├── display_service.py (NEW)
│   └── DisplayService (unified interface)
└── components/
    ├── header.py (NEW)
    ├── footer.py (NEW)
    └── panels.py (NEW)

fluttercraft/infrastructure/platform/
├── git_utils.py (NEW - moved from beautiful_display)
└── path_utils.py (NEW - moved from beautiful_display)

# REMOVE:
# - fluttercraft/utils/beautiful_display.py
# - fluttercraft/utils/display_utils.py
# - fluttercraft/utils/themed_display.py (replaced by display_service)
```

**Target Dependencies:**

```yaml
presentation/ui/display_service.py:
  depends_on:
    - presentation/ui/components/*
    - presentation/themes/renderer.py
  depended_by:
    - commands/start.py
    - commands/core/executor.py

infrastructure/platform/git_utils.py:
  depends_on:
    - subprocess
  depended_by:
    - presentation/ui/components/footer.py

infrastructure/platform/path_utils.py:
  depends_on:
    - pathlib
  depended_by:
    - presentation/ui/components/footer.py
```

### 4.2. Benefits

1. **Single Responsibility:** Each module has one clear purpose
2. **No Duplication:** Shared utilities moved to infrastructure layer
3. **Clean Architecture:** Proper layer separation (presentation/infrastructure)
4. **Testable:** Small, focused modules are easier to test
5. **Maintainable:** Clear where to add new display features

### 4.3. Target Test Coverage

- `display_service.py`: 95% coverage
- `git_utils.py`: 100% coverage
- `path_utils.py`: 100% coverage
- `components/*.py`: 90% coverage

**Total Coverage:** 95%+

---

## 5. Implementation Plan

### Phase 1: Preparation (Estimated: 1 hour)

**Goal:** Ensure we can safely refactor

1. **Achieve 100% Test Coverage (Current State)**
   - [ ] Add tests for `beautiful_display.py` untested functions
   - [ ] Add tests for `display_utils.py`
   - [ ] Ensure all tests pass

2. **Document Current Behavior**
   - [ ] Create `before.md` with current API
   - [ ] Document all public functions
   - [ ] List all callers

3. **Create Refactoring Spec**
   - [ ] This file
   - [ ] Review and approve

### Phase 2: Create New Structure (Estimated: 2 hours)

**Goal:** Build new modules without breaking existing code

1. **Create New Modules**
   - [ ] `presentation/ui/display_service.py`
   - [ ] `presentation/ui/components/header.py`
   - [ ] `presentation/ui/components/footer.py`
   - [ ] `presentation/ui/components/panels.py`
   - [ ] `infrastructure/platform/git_utils.py`
   - [ ] `infrastructure/platform/path_utils.py`

2. **Migrate Functions**
   - [ ] Move ASCII art → `components/header.py`
   - [ ] Move git info → `git_utils.py`
   - [ ] Move path utilities → `path_utils.py`
   - [ ] Move display helpers → `display_service.py`

3. **Write Tests for New Modules**
   - [ ] Test each new module independently
   - [ ] Achieve 95%+ coverage
   - [ ] All tests passing

### Phase 3: Update Callers (Estimated: 2 hours)

**Goal:** Switch callers to new API

1. **Identify All Callers**
   ```bash
   grep -r "from fluttercraft.utils.beautiful_display" .
   grep -r "from fluttercraft.utils.display_utils" .
   grep -r "from fluttercraft.utils.themed_display" .
   ```

2. **Update Imports (One by One)**
   - [ ] `commands/start.py`
   - [ ] `commands/bootstrap.py`
   - [ ] `commands/core/executor.py`
   - [ ] `main.py`
   - [ ] Any other callers

3. **Update Tests**
   - [ ] Update test imports
   - [ ] Update mocks
   - [ ] All tests still pass

### Phase 4: Remove Old Code (Estimated: 30 min)

**Goal:** Clean up deprecated modules

1. **Remove Old Modules**
   - [ ] Delete `beautiful_display.py`
   - [ ] Delete `display_utils.py`
   - [ ] Delete `themed_display.py`

2. **Update Documentation**
   - [ ] Update `.context/components/utils.md`
   - [ ] Update `.context/dependencies.yaml`
   - [ ] Update `CHANGELOG.md`

3. **Final Verification**
   - [ ] Run full test suite
   - [ ] Manual CLI testing
   - [ ] No broken imports

### Phase 5: Quality Assurance (Estimated: 1 hour)

1. **Code Quality**
   - [ ] Run flake8 - no errors
   - [ ] Run black - all formatted
   - [ ] Run mypy - no type errors

2. **Integration Testing**
   - [ ] CLI starts successfully
   - [ ] All commands work
   - [ ] Display looks correct
   - [ ] No regressions

3. **Documentation**
   - [ ] Create `after.md` with new API
   - [ ] Update architecture docs
   - [ ] Write migration guide

**Total Estimated Time:** 6-7 hours

---

## 6. Migration Guide

### For Developers

**Old API:**
```python
# Before
from fluttercraft.utils.beautiful_display import display_header, get_git_info
from fluttercraft.utils.themed_display import display

display_header()
git_info = get_git_info()
display.success("Done!")
```

**New API:**
```python
# After
from fluttercraft.presentation.ui import DisplayService
from fluttercraft.infrastructure.platform import get_git_info

display = DisplayService()
display.show_header()
git_info = get_git_info()
display.success("Done!")
```

### For AI Agents

**Context to Load:**
1. Read `.context/components/presentation.md` (updated with new structure)
2. Read `.context/dependencies.yaml` (updated dependencies)
3. Read `.specs/refactoring/consolidate-display/after.md` (new API reference)

**Development Pattern:**
- Use `DisplayService` for all UI operations
- Use `infrastructure/platform/*` for system utilities
- No direct imports from old `utils/` modules

---

## 7. Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing functionality | Medium | High | 100% test coverage before starting |
| Performance regression | Low | Medium | Benchmark display operations |
| Missed callers during migration | Medium | High | Automated search for imports |
| Complex merge conflicts | Low | Medium | Work in isolated branch |

---

## 8. Rollback Plan

**If refactoring causes issues:**

1. **Immediate Rollback (< 1 hour)**
   - Revert the merge commit
   - Deploy previous version
   - Investigate issues

2. **Partial Rollback (2-3 hours)**
   - Keep new modules
   - Restore old modules temporarily
   - Gradual migration

**Rollback Risk:** Low - comprehensive tests protect against breakage

---

## 9. Success Criteria

**Refactoring is successful when:**

- [ ] No duplicate code across display modules
- [ ] Clear single-purpose modules
- [ ] 95%+ test coverage
- [ ] All tests passing
- [ ] No performance degradation
- [ ] CLI works identically to before
- [ ] Documentation updated
- [ ] Code review approved

---

## 10. Performance Benchmarks

**Before Refactoring:**
```
Header display: 45ms
Git info retrieval: 12ms
Success message: 5ms
Total CLI startup: 150ms
```

**After Refactoring:**
```
Header display: ≤ 45ms
Git info retrieval: ≤ 12ms
Success message: ≤ 5ms
Total CLI startup: ≤ 150ms
```

**Target:** No performance regression

---

## 11. Documentation Updates

**Files to Create:**
- `.specs/refactoring/consolidate-display/before.md` - Current state documentation
- `.specs/refactoring/consolidate-display/after.md` - Target state documentation
- `.specs/refactoring/consolidate-display/migration-guide.md` - How to migrate

**Files to Update:**
- `.context/components/presentation.md` - Document new UI structure
- `.context/components/utils.md` - Remove old display utilities
- `.context/dependencies.yaml` - Update dependency graph
- `CHANGELOG.md` - Add refactoring entry
- `AGENTS.md` - Update development guidelines

---

## 12. Testing Strategy

### 12.1. Test Coverage Requirements

**Before Starting:**
- Achieve 100% coverage of code being refactored
- All tests must pass

**During Refactoring:**
- Write tests for new modules before migrating code
- Maintain test coverage above 90% at all times

**After Completion:**
- Achieve 95%+ coverage for refactored code
- All tests passing (unit + integration)

### 12.2. Test Types

1. **Unit Tests**
   - Test each new module independently
   - Mock external dependencies
   - Test edge cases

2. **Integration Tests**
   - Test display service with theme service
   - Test git utils with subprocess
   - Test full header rendering

3. **Regression Tests**
   - Verify CLI behavior unchanged
   - Test all commands still work
   - Compare output before/after

---

## 13. Timeline

| Phase | Estimated Time | Start Date | End Date | Status |
|-------|---------------|------------|----------|--------|
| Preparation | 1 hour | YYYY-MM-DD | YYYY-MM-DD | ⏳ |
| Create New Structure | 2 hours | YYYY-MM-DD | YYYY-MM-DD | ⏳ |
| Update Callers | 2 hours | YYYY-MM-DD | YYYY-MM-DD | ⏳ |
| Remove Old Code | 30 min | YYYY-MM-DD | YYYY-MM-DD | ⏳ |
| Quality Assurance | 1 hour | YYYY-MM-DD | YYYY-MM-DD | ⏳ |
| **Total** | **6-7 hours** | | | |

---

## 14. Sign-off

**Refactoring Plan Approved By:**
- [ ] Technical Lead: [Name]
- [ ] Team: [Names]

**Refactoring Completed By:**
- [ ] Developer: [Name]
- [ ] Reviewer: [Name]
- [ ] QA: [Name]

---

## 15. Lessons Learned

**Post-Refactoring Review:**

- What went well?
- What challenges did we face?
- What would we do differently next time?
- Any unexpected issues?

[Fill in after completion]

---

## 16. Notes and Updates

**YYYY-MM-DD:** Refactoring spec created  
**YYYY-MM-DD:** [Track significant decisions and changes here]

---

**Template Version:** 1.0.0  
**Last Updated:** 2026-01-17
