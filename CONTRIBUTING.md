# Contributing to FlutterCraft

Thanks for considering contributing! Here's how to help:

## Setup

```bash
git clone https://github.com/UTTAM-VAGHASIA/fluttercraft.git
cd fluttercraft
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
# source venv/bin/activate
pip install -e .
```

## Development Process

1. Set up your environment using the steps above
2. Choose a task from the upcoming features in the implementation roadmap
3. Make your changes, following the existing code style
4. Update relevant documentation to reflect your changes
5. Add relevant tests (when test framework is established)

## Documentation Updates

Each code change should be accompanied by appropriate documentation updates:
- Add new features to `docs/api-reference.md`
- Update implementation status in `docs/development-progress.md`
- Update the roadmap in `docs/implementation-roadmap.md` if applicable
- Create examples in `docs/examples/` for significant features

## Branching
- Use feature branches: feature/your-feature
- Use Conventional Commits: feat: add X, fix: bug in Y

## Pull Requests
- Keep PRs small and focused
- Include tests and documentation where possible
- Ensure documentation is updated to match your changes
