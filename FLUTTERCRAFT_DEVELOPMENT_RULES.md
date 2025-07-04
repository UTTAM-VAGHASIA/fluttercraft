# FlutterCraft v0.1.2 - Development Rules & Guidelines

## Core Development Principles

### 1. **NEVER DEVIATE FROM THE PLAN**
- The `FLUTTERCRAFT_V0_1_2_PLAN.md` is the single source of truth
- Any changes to scope must be explicitly approved and documented
- Follow the milestone-based approach strictly
- Implement features in the exact order specified

### 2. **CROSS-PLATFORM FIRST**
- Every feature must work on Windows, Linux, and macOS
- Test platform-specific paths and behaviors
- Use `pathlib.Path` for all file system operations
- Handle platform differences gracefully

### 3. **THEMING IS CORE, NOT OPTIONAL**
- Every output must respect the current theme
- No hardcoded colors or styles
- All UI components must be themeable
- Theme switching must be seamless and immediate

## Technology Stack Rules

### 1. **Mandatory Framework Usage**
```python
# REQUIRED: Use these frameworks exactly as specified
import typer
from rich.console import Console
from rich.theme import Theme
from rich import print
from rich.panel import Panel
from rich.table import Table

# FORBIDDEN: Do not use alternatives like Click, argparse, etc.
# FORBIDDEN: Do not use print() without Rich
```

### 2. **Dependencies Management**
- **ONLY** use dependencies listed in the plan
- **NO** additional dependencies without explicit approval
- All dependencies must be compatible with Python 3.10+
- Prefer dependencies with MIT/Apache licenses

### 3. **Import Organization**
```python
# Standard library imports
import asyncio
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party imports
import typer
from rich.console import Console
from rich.theme import Theme

# Local imports
from fluttercraft.cli.core import FlutterCraftApp
from fluttercraft.themes.manager import ThemeManager
```

## Code Quality Rules

### 1. **Type Hints Are Mandatory**
```python
# CORRECT: Full type annotations
async def execute_command(self, args: Dict[str, Any]) -> bool:
    pass

def get_themes(self) -> List[Theme]:
    pass

# FORBIDDEN: Missing type hints
def execute_command(self, args):
    pass
```

### 2. **Docstring Requirements**
```python
class BaseCommand:
    """Base class for all FlutterCraft commands.
    
    This class provides the foundation for implementing commands
    with consistent theming, error handling, and user interaction.
    
    Attributes:
        console: Rich console instance for output
        theme_manager: Theme management system
        
    Example:
        >>> command = BaseCommand(console, theme_manager)
        >>> await command.execute({"verbose": True})
        True
    """
    
    async def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the command with given arguments.
        
        Args:
            args: Dictionary of command arguments and options
            
        Returns:
            True if command executed successfully, False otherwise
            
        Raises:
            CommandExecutionError: If command execution fails
            ValidationError: If arguments are invalid
        """
        pass
```

### 3. **Error Handling Standards**
```python
# CORRECT: Specific exception handling with recovery
try:
    result = await self.execute_fvm_command(args)
except CommandExecutionError as e:
    self.console.print(f"[red]Error:[/red] {e.message}")
    if e.suggestions:
        self.show_recovery_suggestions(e.suggestions)
    return False
except Exception as e:
    self.console.print(f"[red]Unexpected error:[/red] {str(e)}")
    self.log_error(e)
    return False

# FORBIDDEN: Bare except clauses
try:
    do_something()
except:
    pass
```

## Architecture Rules

### 1. **Command Pattern Implementation**
```python
# MANDATORY: All commands must inherit from BaseCommand
class FVMSetupCommand(BaseCommand):
    """FVM setup command implementation."""
    
    async def execute(self, args: Dict[str, Any]) -> bool:
        # Implementation here
        pass
    
    def get_help(self) -> str:
        return "Install and configure Flutter Version Manager"
    
    def validate_prerequisites(self) -> bool:
        # Validation logic
        return True
```

### 2. **Theme Integration Rules**
```python
# CORRECT: Always use theme manager for styling
panel = Panel(
    content,
    title="Command Output",
    border_style=self.theme_manager.current_theme.primary,
    title_style=self.theme_manager.current_theme.header_style
)

# FORBIDDEN: Hardcoded styles
panel = Panel(content, border_style="blue", title_style="bold red")
```

### 3. **Configuration Management**
```python
# MANDATORY: Use platform-appropriate config directories
def get_config_directory(self) -> Path:
    """Get platform-appropriate configuration directory."""
    if platform.system() == "Windows":
        return Path.home() / "AppData" / "Local" / "FlutterCraft"
    elif platform.system() == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "FlutterCraft"
    else:  # Linux and others
        return Path.home() / ".config" / "fluttercraft"
```

## User Experience Rules

### 1. **Interactive Shell Requirements**
- **MUST** feel like chatting with GEMINI CLI
- **MUST** provide immediate feedback for all actions
- **MUST** show progress indicators for long operations
- **MUST** handle interruptions gracefully (Ctrl+C)

### 2. **Help System Standards**
```python
# CORRECT: Contextual, themed help
def show_command_help(self, command_name: str):
    """Display help with current theme styling."""
    help_panel = Panel(
        self.format_help_content(command_name),
        title=f"Help: {command_name}",
        border_style=self.theme_manager.current_theme.info
    )
    self.console.print(help_panel)

# FORBIDDEN: Plain text help without theming
print(f"Help for {command_name}: {help_text}")
```

### 3. **Error Message Guidelines**
```python
# CORRECT: Helpful, themed error messages with suggestions
def show_error(self, error: FlutterCraftError):
    """Display error with recovery suggestions."""
    error_panel = Panel(
        f"[bold]{error.message}[/bold]\n\n" + 
        "💡 Suggestions:\n" + 
        "\n".join(f"• {suggestion}" for suggestion in error.suggestions),
        title="❌ Error",
        border_style=self.theme_manager.current_theme.error
    )
    self.console.print(error_panel)

# FORBIDDEN: Cryptic error messages
print("Error occurred")
```

## Testing Rules

### 1. **Test Coverage Requirements**
- **Minimum 85% code coverage** for all modules
- **100% coverage** for critical paths (command execution, theme switching)
- **Platform-specific tests** for Windows, Linux, macOS

### 2. **Test Organization**
```python
# MANDATORY: Test structure
tests/
├── unit/
│   ├── test_commands/
│   │   ├── test_base_command.py
│   │   ├── test_theme_commands.py
│   │   ├── test_fvm_commands.py
│   │   └── test_flutter_commands.py
│   ├── test_themes/
│   │   ├── test_theme_manager.py
│   │   └── test_theme_presets.py
│   └── test_utils/
├── integration/
│   ├── test_cli_integration.py
│   └── test_theme_switching.py
└── e2e/
    └── test_complete_workflows.py
```

### 3. **Test Implementation Standards**
```python
# CORRECT: Comprehensive test with setup and teardown
class TestFVMCommands:
    """Test suite for FVM commands."""
    
    @pytest.fixture
    def console(self):
        return Console()
    
    @pytest.fixture
    def theme_manager(self):
        return ThemeManager()
    
    @pytest.fixture
    def fvm_command(self, console, theme_manager):
        return FVMSetupCommand(console, theme_manager)
    
    async def test_fvm_setup_success(self, fvm_command):
        """Test successful FVM setup."""
        args = {"verbose": True}
        result = await fvm_command.execute(args)
        assert result is True
    
    async def test_fvm_setup_missing_prerequisites(self, fvm_command):
        """Test FVM setup with missing prerequisites."""
        with patch.object(fvm_command, 'validate_prerequisites', return_value=False):
            result = await fvm_command.execute({})
            assert result is False

# FORBIDDEN: Tests without proper setup or assertions
def test_something():
    do_something()
```

## Security Rules

### 1. **Input Validation**
```python
# CORRECT: Validate all user inputs
def validate_flutter_version(self, version: str) -> bool:
    """Validate Flutter version format."""
    if not version:
        raise ValidationError("Version cannot be empty")
    
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        raise ValidationError("Version must be in format X.Y.Z")
    
    return True

# FORBIDDEN: Using user input without validation
subprocess.run(f"flutter install {user_input}")
```

### 2. **Command Execution Safety**
```python
# CORRECT: Safe command execution
async def execute_system_command(self, command: List[str]) -> bool:
    """Execute system command safely."""
    # Validate command components
    validated_command = self.validate_command(command)
    
    try:
        result = await asyncio.create_subprocess_exec(
            *validated_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return result.returncode == 0
    except Exception as e:
        self.log_error(f"Command execution failed: {e}")
        return False

# FORBIDDEN: Shell injection vulnerabilities
os.system(f"some_command {user_input}")
```

## Performance Rules

### 1. **Startup Performance**
- CLI must start in **< 2 seconds**
- Use **lazy loading** for non-essential components
- **Cache** theme and configuration data
- **Minimize imports** in main entry point

### 2. **Memory Management**
```python
# CORRECT: Efficient resource management
class ThemeManager:
    def __init__(self):
        self._theme_cache: Dict[str, Theme] = {}
        self._current_theme: Optional[Theme] = None
    
    def get_theme(self, name: str) -> Theme:
        """Get theme with caching."""
        if name not in self._theme_cache:
            self._theme_cache[name] = self._load_theme(name)
        return self._theme_cache[name]
    
    def cleanup(self):
        """Clean up resources."""
        self._theme_cache.clear()
        self._current_theme = None

# FORBIDDEN: Memory leaks and resource waste
themes = []
for theme_file in theme_files:
    themes.append(load_entire_theme_into_memory(theme_file))
```

## Git Workflow Rules

### 1. **Branch Naming Convention**
```bash
# CORRECT: Feature branches
feature/milestone-1-theming-system
feature/milestone-2-fvm-commands
feature/milestone-3-flutter-commands
bugfix/theme-switching-issue
hotfix/critical-startup-error

# FORBIDDEN: Unclear branch names
fix-stuff
new-feature
temp-branch
```

### 2. **Commit Message Format**
```bash
# CORRECT: Conventional commits
feat(themes): implement GEMINI-inspired theme collection
fix(cli): resolve startup performance issue on Windows
docs(api): update command documentation
test(fvm): add integration tests for FVM commands
refactor(core): improve command registry architecture

# FORBIDDEN: Unclear commit messages
fixed bug
added stuff
changes
wip
```

### 3. **Pull Request Requirements**
- **Required**: All tests passing
- **Required**: Code coverage maintained (>85%)
- **Required**: Documentation updated
- **Required**: Platform testing completed
- **Required**: Review from at least one maintainer

## Documentation Rules

### 1. **API Documentation**
```python
# CORRECT: Comprehensive API docs
class ThemeManager:
    """Manages themes for FlutterCraft CLI.
    
    The ThemeManager handles loading, switching, and caching of themes.
    It provides a unified interface for all theme-related operations
    and ensures consistent styling across the application.
    
    Attributes:
        current_theme: Currently active theme
        available_themes: List of all available themes
        
    Example:
        >>> manager = ThemeManager()
        >>> manager.set_theme("gemini-dark")
        >>> current = manager.get_current_theme()
        >>> print(current.primary)
        "#1a73e8"
    """
```

### 2. **User Documentation**
- **Command guides** with examples
- **Theme customization** tutorials
- **Troubleshooting** sections
- **Platform-specific** instructions

## Forbidden Practices

### 1. **Never Do These**
```python
# FORBIDDEN: Global variables
GLOBAL_CONSOLE = Console()

# FORBIDDEN: Hardcoded paths
config_path = "/home/user/.fluttercraft"

# FORBIDDEN: Platform assumptions
if os.name == "posix":  # Wrong way to check platform

# FORBIDDEN: Silent failures
try:
    risky_operation()
except:
    pass  # Never do this

# FORBIDDEN: Magic numbers/strings
if status == 42:  # What does 42 mean?
    do_something()

# FORBIDDEN: Mixed responsibilities
class CommandAndThemeManager:  # Single responsibility violation
    def execute_command(self): pass
    def change_theme(self): pass
```

### 2. **Code Smells to Avoid**
- **Long functions** (>50 lines)
- **Deep nesting** (>3 levels)
- **Circular imports**
- **Tight coupling** between modules
- **Missing error handling**
- **Inconsistent naming conventions**

## Milestone Compliance Rules

### 1. **Milestone 1 Deliverables**
- [ ] Complete CLI framework with Typer + Rich
- [ ] Theme management system with 10+ themes
- [ ] Interactive shell implementation
- [ ] Theme commands (list, set, preview)
- [ ] Cross-platform configuration management
- [ ] Unit tests for all core components

### 2. **Milestone 2 Deliverables**
- [ ] FVM command implementation (setup, remove, list, releases, install, remove)
- [ ] Interactive command guidance system
- [ ] Developer context gathering functionality
- [ ] Progress indicators and error recovery
- [ ] Integration tests for FVM workflows

### 3. **Milestone 3 Deliverables**
- [ ] Flutter command implementation (setup, remove, doctor, config, validate)
- [ ] Enhanced flutter doctor integration
- [ ] Complete error handling system
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Documentation completion

## Quality Gates

### 1. **Before Any Commit**
- [ ] All tests pass
- [ ] Code coverage >85%
- [ ] Type checking passes (mypy)
- [ ] Linting passes (black, isort)
- [ ] Security scan passes (bandit)

### 2. **Before Any Release**
- [ ] All milestones completed
- [ ] Cross-platform testing completed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] User acceptance testing completed

## Emergency Procedures

### 1. **If Stuck on Implementation**
1. Review the plan document
2. Check existing similar implementations
3. Consult framework documentation
4. Ask for clarification on specific requirements
5. Document any assumptions made

### 2. **If Performance Issues Arise**
1. Profile the application
2. Identify bottlenecks
3. Apply optimization strategies from the plan
4. Measure improvements
5. Document changes

### 3. **If Cross-Platform Issues Found**
1. Isolate platform-specific code
2. Test on all supported platforms
3. Implement platform abstractions
4. Add platform-specific tests
5. Update documentation

These rules are **MANDATORY** and **NON-NEGOTIABLE**. Every line of code must follow these guidelines. Any deviation must be explicitly approved and documented.
