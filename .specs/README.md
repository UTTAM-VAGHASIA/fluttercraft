# Spec-Driven Development for FlutterCraft

## Overview

FlutterCraft follows a **spec-driven development workflow** where every feature, fix, and refactoring starts with a written specification. This ensures:

- Clear objectives and acceptance criteria
- Proper context for AI coding agents
- Trackable progress and decisions
- Consistent development patterns
- Easy code review and maintenance

## Directory Structure

```
.specs/
├── README.md                    # This file
├── .templates/                  # Spec templates
│   ├── feature.md              # Feature spec template
│   ├── fix.md                  # Bug fix spec template
│   └── refactor.md             # Refactoring spec template
├── features/                    # Feature specifications
│   └── <feature-name>/
│       ├── spec.md             # Main specification
│       ├── context.md          # Additional context
│       ├── decisions.md        # Design decisions log
│       └── implementation.md   # Implementation notes
├── fixes/                       # Bug fix specifications
│   └── <bug-id>/
│       ├── spec.md             # Bug fix specification
│       ├── root-cause.md       # Root cause analysis
│       └── testing.md          # Testing strategy
└── refactoring/                 # Refactoring specifications
    └── <refactor-name>/
        ├── spec.md             # Refactoring specification
        ├── before.md           # Current state documentation
        └── after.md            # Target state documentation
```

## Workflow

### For Features

1. **Create Feature Spec**
   ```bash
   mkdir -p .specs/features/<feature-name>
   cp .specs/.templates/feature.md .specs/features/<feature-name>/spec.md
   # Fill in the spec
   ```

2. **Load Context**
   ```bash
   # Review relevant component context
   cat .context/components/<relevant-component>.md
   cat .context/dependencies.yaml
   ```

3. **Implement**
   - Follow the spec strictly
   - Update tests as you go (TDD encouraged)
   - Log decisions in `decisions.md`
   - Track implementation progress in `implementation.md`

4. **Review and Merge**
   - PR must reference the spec
   - All acceptance criteria must be met
   - Component context must be updated
   - Dependencies.yaml updated if needed

### For Bug Fixes

1. **Create Fix Spec**
   ```bash
   mkdir -p .specs/fixes/<bug-id>
   cp .specs/.templates/fix.md .specs/fixes/<bug-id>/spec.md
   # Fill in the spec
   ```

2. **Root Cause Analysis**
   - Document the root cause in `root-cause.md`
   - Identify affected components
   - Load relevant component context

3. **Implement Fix**
   - Write failing test first
   - Implement fix
   - Verify all tests pass
   - Update documentation

4. **Review and Merge**
   - PR must reference the fix spec
   - Root cause must be documented
   - Test coverage for the bug must be added

### For Refactoring

1. **Create Refactoring Spec**
   ```bash
   mkdir -p .specs/refactoring/<refactor-name>
   cp .specs/.templates/refactor.md .specs/refactoring/<refactor-name>/spec.md
   # Fill in the spec
   ```

2. **Document Current State**
   - Capture current architecture in `before.md`
   - Ensure 100% test coverage before starting
   - Document all affected components

3. **Implement Refactoring**
   - Refactor incrementally
   - Run tests after each change
   - Update architecture docs as you go
   - Document target state in `after.md`

4. **Review and Merge**
   - All tests must still pass
   - Performance must not degrade
   - Architecture docs must be updated
   - Component context must be updated

## AI Agent Usage

### For OpenCode/Cursor/Copilot

**Before making any changes:**

1. Load the architecture:
   ```
   Read .context/architecture.yaml
   Read .context/dependencies.yaml
   ```

2. Load component context:
   ```
   Read .context/components/<component>.md (for relevant components)
   ```

3. Load or create spec:
   ```
   If spec exists:
     Read .specs/<type>/<name>/spec.md
   Else:
     Create spec from template
     Fill in required sections
   ```

4. Implement following the spec
5. Update context and dependencies
6. Log decisions and changes

### Spec Sections (Required)

Every spec must have:

1. **Objective** - What are we trying to achieve?
2. **Context** - Why is this needed? What's the background?
3. **Acceptance Criteria** - How do we know when it's done?
4. **Implementation Plan** - High-level approach
5. **Testing Strategy** - How will we test this?
6. **Components Affected** - What parts of the codebase will change?
7. **Dependencies** - What does this depend on? What depends on this?

## Examples

### Example: Feature Spec

See `.specs/.templates/feature.md` for a complete template.

**Feature:** Add `fvm use <version>` command

```yaml
objective: "Allow users to switch between installed Flutter SDK versions"
context: "FVM can install multiple versions, but users need a way to switch"
acceptance_criteria:
  - "fvm use <version> switches to the specified version"
  - "Error message if version not installed"
  - "Success message with new version displayed"
  - "Help text available with fvm use --help"
components_affected:
  - "fluttercraft/application/commands/fvm/"
  - ".context/components/commands.md"
dependencies:
  - "FVM must be installed"
  - "Version must be installed via fvm install"
```

### Example: Fix Spec

See `.specs/.templates/fix.md` for a complete template.

**Fix:** Version check timeout on slow connections

```yaml
bug_id: "GH-42"
objective: "Fix timeout issue when checking Flutter version on slow connections"
root_cause: "Hardcoded 10s timeout insufficient for slow networks"
solution: "Increase timeout to 30s and make it configurable"
components_affected:
  - "fluttercraft/infrastructure/terminal/executor.py"
testing_strategy:
  - "Add test with mocked slow network"
  - "Verify timeout is respected"
  - "Test with different timeout values"
```

## Rules

### Strict Requirements

1. **Every change must have a spec** (feature/fix/refactor)
2. **Specs must be approved before implementation** (for major changes)
3. **PR must reference the spec** in description
4. **Component context must be updated** if public API changes
5. **Dependencies.yaml must be updated** if dependencies change
6. **Tests must be written** for all new code
7. **Documentation must be updated** for user-facing changes

### Exceptions

Small changes that don't need a spec:
- Typo fixes in comments
- Formatting changes (Black/flake8)
- Documentation updates
- Version bumps
- Dependency updates (security patches)

**Note:** Even for exceptions, the change must be clear and focused.

## Validation

### Pre-commit

- Spec exists for the change (or is an exception)
- Spec sections are complete
- Component context loaded and understood

### CI/CD

- Spec referenced in commit message or PR
- All acceptance criteria met
- Tests cover the changes
- Documentation updated

### Code Review

- Spec followed during implementation
- Decisions logged if deviating from spec
- Context and dependencies updated

## Benefits

### For Developers
- Clear objectives before coding
- Better architecture decisions
- Easier code review
- Traceable changes

### For AI Agents
- Complete context for changes
- Clear rules and constraints
- Systematic approach
- Continuity across sessions

### For Maintainers
- Understand why changes were made
- Review changes against specs
- Track decisions over time
- Maintain system coherence

## Template Usage

### Creating a New Spec

```bash
# For a feature
cp .specs/.templates/feature.md .specs/features/my-feature/spec.md

# For a fix
cp .specs/.templates/fix.md .specs/fixes/bug-123/spec.md

# For a refactor
cp .specs/.templates/refactor.md .specs/refactoring/clean-commands/spec.md
```

### Filling in a Spec

1. Open the template
2. Read each section carefully
3. Fill in all required fields
4. Add optional sections as needed
5. Review for completeness
6. Commit the spec before implementing

### Reviewing a Spec

Before approving:
- [ ] Objective is clear and specific
- [ ] Context explains the "why"
- [ ] Acceptance criteria are measurable
- [ ] Implementation plan is sound
- [ ] Testing strategy is comprehensive
- [ ] Components affected are identified
- [ ] Dependencies are documented

## Version History

- **1.0.0** (2026-01-17): Initial spec-driven development framework
- All future changes will be spec-driven following this framework

---

**Remember:** Specs are living documents. Update them as you learn more during implementation. The goal is clarity and traceability, not bureaucracy.
