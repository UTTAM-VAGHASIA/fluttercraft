# FlutterCraft Context Management System

This `.context/` directory contains essential metadata for AI coding agents and developers to understand the codebase architecture, component relationships, and development workflows.

## 📁 Directory Structure

```
.context/
├── README.md                    # This file
├── architecture.yaml            # System architecture specification
├── components/                  # Component-level context
│   ├── commands.md             # Command system documentation
│   ├── themes.md               # Theming system documentation
│   └── utils.md                # Utilities documentation
├── dependencies.yaml            # Dependency graph
├── rules/                       # Development rules
│   ├── code-style.md           # Code style enforcement
│   ├── commit-conventions.md   # Git commit rules
│   └── pr-guidelines.md        # Pull request requirements
└── sessions/                    # Development session tracking
    └── .gitkeep

```

## 🎯 Purpose

### For AI Coding Agents
- **Quick Context Loading**: Load component context before making changes
- **Dependency Awareness**: Understand what modules depend on what you're changing
- **Rule Enforcement**: Follow strict development rules
- **Session Continuity**: Track development sessions for context preservation

### For Human Developers
- **Onboarding**: Quick understanding of system architecture
- **Impact Analysis**: See what's affected by your changes
- **Best Practices**: Enforced code style and conventions
- **Documentation**: Always up-to-date architecture docs

## 🔄 How to Use

### Before Making Changes
1. Read `architecture.yaml` to understand the system
2. Check `components/<relevant>.md` for component-specific context
3. Review `dependencies.yaml` to see impact of your changes
4. Follow rules in `rules/` directory

### When Adding Features
1. Create a spec in `.specs/features/<feature-name>/`
2. Update relevant component documentation
3. Update `dependencies.yaml` if adding new dependencies
4. Follow the spec-driven development workflow

### When Fixing Bugs
1. Create a spec in `.specs/fixes/<bug-id>/`
2. Document the root cause
3. Implement fix following component context
4. Update tests and documentation

## 🚀 Quick Start

**For AI Agents:**
```bash
# Load full context
cat .context/architecture.yaml
cat .context/dependencies.yaml
cat .context/components/*.md

# Start a development session
mkdir .context/sessions/<session-id>
# Track your changes and context there
```

**For Developers:**
```bash
# Review architecture
cat .context/architecture.yaml

# Check component you're working on
cat .context/components/commands.md  # for command changes
cat .context/components/themes.md    # for theme changes
```

## 📊 Maintenance

This context system is **auto-maintained** by:
1. Pre-commit hooks (coming in v0.2.0)
2. CI/CD validation
3. Manual updates during major refactoring

**Last Updated:** 2026-01-17
**Version:** 1.0.0 (FINAL Architecture)
