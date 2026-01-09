# Contributing to Thesidia

Thank you for your interest in contributing to Thesidia!

## Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `python -m pytest tests/ -v`
5. Submit a pull request

## Code Style

- **Python**: Follow PEP 8, use type hints
- **JavaScript**: ES6+, use `const`/`let` (no `var`)
- **CSS**: Use CSS variables from the design system
- **Files**: Use `snake_case` for Python, `kebab-case` for JS/CSS

## Commit Messages

Format: `type: subject`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

Example: `feat: add user profile editing`

## Pull Request Process

1. Update docs if needed
2. Add tests for new features
3. Ensure all tests pass
4. Request review from maintainers

## Testing Requirements

- New features need tests
- Bug fixes need regression tests
- Target 80%+ coverage on critical paths

## Questions?

Open an issue for discussion before major changes.
