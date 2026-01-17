---
# Feature Specification Template
# Copy this template to .specs/features/<feature-name>/spec.md
---

# Feature: [Feature Name]

**Status:** Draft | In Progress | Under Review | Completed | Cancelled  
**Created:** YYYY-MM-DD  
**Owner:** [Your Name or AI Agent Session ID]  
**Target Version:** vX.Y.Z  
**Priority:** High | Medium | Low

---

## 1. Objective

**What are we building?**

[Clear, concise description of the feature in 1-2 sentences]

**Example:**
> Add a `fvm use <version>` command that allows users to switch between installed Flutter SDK versions managed by FVM.

---

## 2. Context

**Why is this needed?**

[Provide background and motivation for this feature]

**User Story:**
```
As a [type of user]
I want to [do something]
So that [achieve some goal]
```

**Background:**
- [Current state or problem]
- [Related features or dependencies]
- [User feedback or requests (if any)]

---

## 3. Acceptance Criteria

**How do we know when this is done?**

- [ ] [Criterion 1: Specific, testable requirement]
- [ ] [Criterion 2: Specific, testable requirement]
- [ ] [Criterion 3: Specific, testable requirement]
- [ ] [Criterion 4: Specific, testable requirement]

**Example:**
- [ ] User can run `fvm use stable` to switch to stable Flutter version
- [ ] Error message displays if version not installed: "Flutter version 'X' is not installed. Run 'fvm install X' first."
- [ ] Success message shows: "Switched to Flutter X.Y.Z"
- [ ] Help text available via `fvm use --help`
- [ ] Command works on Windows, macOS, and Linux (if cross-platform)

---

## 4. Technical Design

### 4.1. Architecture

**Which layer does this belong to?**
- [ ] Domain (business logic)
- [ ] Application (use cases)
- [ ] Infrastructure (external systems)
- [ ] Presentation (UI/CLI)
- [ ] Core (shared kernel)

**Components Affected:**
```
fluttercraft/
├── application/commands/fvm/
│   └── use.py (NEW)           # FVM use command implementation
├── .context/components/
│   └── commands.md             # Update with new command
└── .context/dependencies.yaml  # Update dependencies
```

### 4.2. Data Flow

```
User Input: "fvm use stable"
  └─> CommandExecutor (presentation layer)
      └─> FVMUseCommand (application layer)
          └─> FVMService.switch_version() (domain layer)
              └─> FVMRepository.get_installed_versions() (infrastructure layer)
                  └─> FileSystem (external)
```

### 4.3. Public API

**New Classes/Functions:**

```python
class FVMUseCommand(Command):
    """Command to switch Flutter SDK versions."""
    
    name: str = "fvm use"
    category: str = "fvm"
    
    def execute(self, context: CommandContext) -> CommandResult:
        """Switch to specified Flutter version."""
        pass
```

**New Methods:**
- `FVMService.switch_version(version: str) -> Result`
- `FVMRepository.get_installed_versions() -> List[str]`

### 4.4. Database/Storage Changes

**Configuration Changes:**
- [ ] New config key: `fvm.current_version`
- [ ] Config location: `~/.fluttercraft/config.json`

**File System Changes:**
- [ ] Read from: `~/.fvm/versions/`
- [ ] Write to: `.fvmrc` in project root (if applicable)

---

## 5. Implementation Plan

### Phase 1: Setup (Estimated: 30 min)
1. Create `.specs/features/fvm-use/spec.md` (this file)
2. Load context from `.context/components/commands.md`
3. Review `dependencies.yaml` for FVM module dependencies

### Phase 2: Implementation (Estimated: 2 hours)
1. Create `fluttercraft/application/commands/fvm/use.py`
2. Implement `FVMUseCommand` class
3. Add command to FVM command registry in `bootstrap.py`
4. Implement version switching logic
5. Add error handling for invalid versions

### Phase 3: Testing (Estimated: 1 hour)
1. Write unit tests in `tests/unit/commands/fvm/test_use.py`
2. Write integration test in `tests/integration/test_fvm_use.py`
3. Manual testing on local machine
4. Cross-platform testing (if applicable)

### Phase 4: Documentation (Estimated: 30 min)
1. Update `.context/components/commands.md`
2. Update `.context/dependencies.yaml`
3. Update `README.md` with new command
4. Update `CHANGELOG.md`

### Phase 5: Review (Estimated: 30 min)
1. Self-review against acceptance criteria
2. Run full test suite
3. Lint and format code
4. Create PR with spec reference

**Total Estimated Time:** 4-5 hours

---

## 6. Testing Strategy

### 6.1. Unit Tests

**Location:** `tests/unit/commands/fvm/test_use.py`

**Test Cases:**
```python
def test_fvm_use_switches_to_installed_version():
    """Test switching to an installed version succeeds."""
    pass

def test_fvm_use_fails_for_uninstalled_version():
    """Test error when version not installed."""
    pass

def test_fvm_use_shows_help_text():
    """Test help text is displayed correctly."""
    pass

def test_fvm_use_updates_config():
    """Test that current version is saved to config."""
    pass
```

### 6.2. Integration Tests

**Location:** `tests/integration/test_fvm_use.py`

**Test Cases:**
- End-to-end: Install version, then use it
- Error handling: Try to use non-existent version
- Config persistence: Verify config is updated

### 6.3. Manual Testing

**Test Scenarios:**
1. Install Flutter stable and beta, switch between them
2. Try to use version that's not installed
3. Check help text display
4. Verify success/error messages
5. Check config file is updated

---

## 7. Dependencies

### 7.1. Prerequisites

**Must exist before implementation:**
- [ ] FVM installation system (`fvm install`)
- [ ] FVM version listing (`fvm list`)
- [ ] Command registry system
- [ ] Configuration management

### 7.2. Depends On

**This feature depends on:**
- `fluttercraft.commands.core.base.Command`
- `fluttercraft.commands.core.models.CommandContext`
- `fluttercraft.commands.fvm.list` (to get installed versions)
- `fluttercraft.infrastructure.storage.config_repository`

### 7.3. Depended By

**Future features that will depend on this:**
- `fvm current` - Show currently active version
- `fvm doctor` - Check FVM setup and active version
- Project-specific version management

---

## 8. Security Considerations

**Potential Security Issues:**
- [ ] Path traversal when reading version directories
- [ ] Command injection in version names
- [ ] Permissions when writing config files

**Mitigations:**
- Validate version names against regex: `^[\w.-]+$`
- Use Path library for safe file operations
- Check write permissions before attempting config update

---

## 9. Performance Considerations

**Expected Performance:**
- Command execution: < 1 second
- Version validation: < 100ms
- Config update: < 50ms

**Optimization Opportunities:**
- Cache installed versions list
- Lazy load FVM configuration

---

## 10. Documentation

### 10.1. User-Facing Documentation

**Update Files:**
- `README.md` - Add to FVM commands section
- `docs/usage.md` - Add usage examples
- `docs/api-reference.md` - Add command reference

**Example Usage:**
```bash
# Switch to stable version
fvm use stable

# Switch to specific version
fvm use 3.19.0

# Show help
fvm use --help
```

### 10.2. Developer Documentation

**Update Files:**
- `.context/components/commands.md` - Add FVMUseCommand
- `.context/dependencies.yaml` - Add dependencies
- `CHANGELOG.md` - Add feature entry

---

## 11. Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| FVM not installed | Medium | High | Check FVM installation before execution |
| Version not found | High | Medium | Validate version exists before switching |
| Config write failure | Low | Medium | Handle write errors gracefully |
| Platform compatibility | Medium | High | Test on Windows, macOS, Linux |

---

## 12. Alternatives Considered

**Alternative 1: Auto-switching based on .fvmrc**
- **Pros:** Automatic, project-specific
- **Cons:** More complex, requires project context
- **Decision:** Defer to future version

**Alternative 2: Interactive version selector**
- **Pros:** User-friendly, visual
- **Cons:** Not scriptable, slower
- **Decision:** Keep as separate `fvm switch` command

---

## 13. Success Metrics

**How do we measure success?**

- [ ] Feature implemented with all acceptance criteria met
- [ ] 100% test coverage for new code
- [ ] Zero new bugs reported related to this feature (first 2 weeks)
- [ ] Positive user feedback on GitHub/Discord
- [ ] Command used successfully in CI/CD environments

---

## 14. Timeline

| Phase | Start Date | End Date | Status |
|-------|------------|----------|--------|
| Spec Creation | YYYY-MM-DD | YYYY-MM-DD | ✅ |
| Implementation | YYYY-MM-DD | YYYY-MM-DD | ⏳ |
| Testing | YYYY-MM-DD | YYYY-MM-DD | ⏳ |
| Documentation | YYYY-MM-DD | YYYY-MM-DD | ⏳ |
| Review | YYYY-MM-DD | YYYY-MM-DD | ⏳ |
| Merge | YYYY-MM-DD | YYYY-MM-DD | ⏳ |

---

## 15. Sign-off

**Spec Approved By:**
- [ ] Technical Lead: [Name]
- [ ] Product Owner: [Name] (if applicable)
- [ ] AI Agent: [Session ID] (if AI-driven)

**Implementation Completed By:**
- [ ] Developer: [Name]
- [ ] Reviewer: [Name]
- [ ] QA: [Name] (if applicable)

---

## 16. Notes and Updates

**YYYY-MM-DD:** Initial spec created  
**YYYY-MM-DD:** [Note any significant changes or decisions made during implementation]

---

## 17. Related Specs

**Related Features:**
- `.specs/features/fvm-install/spec.md` - FVM installation
- `.specs/features/fvm-list/spec.md` - FVM version listing

**Related Fixes:**
- None yet

**Related Refactoring:**
- None yet

---

**Template Version:** 1.0.0  
**Last Updated:** 2026-01-17
