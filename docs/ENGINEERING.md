# Engineering Practices & Standards

**Last Updated**: 2025-12-27

This document outlines the engineering practices, coding standards, and development workflows for the Thesidia project.

---

## Code Organization Principles

### Modular Design

**Separation of Concerns**:
- Each module should have a single, well-defined responsibility
- Minimize coupling between modules
- Maximize cohesion within modules

**Directory Structure**:
```
src/                  # Core source code
├── core/            # Core system components
├── capabilities/    # Feature modules
├── memory/          # Memory systems (Sophia)
└── utils/           # Utility functions

webapp/              # Web application
├── routes/          # API routes (blueprints)
├── middleware/      # Request middleware
├── auth/            # Authentication modules
├── conversations/   # Conversation storage
└── static/          # Static assets

tests/               # Test suites
scripts/             # Utility scripts
docs/                # Documentation
```

### File Naming Conventions

**Python Files**:
- Use `snake_case` for all Python filenames
- Be descriptive: `sophia_gnostic_map.py` not `map.py`
- Prefix with component: `thesidia_hybrid_adaptive.py`

**Documentation**:
- Use `UPPER_SNAKE_CASE.md` for primary docs
- Organize by topic in subdirectories
- Use descriptive names: `ENGINEERING.md` not `ENG.md`

**Scripts**:
- Use `.sh` extension for shell scripts
- Use descriptive names: `start_server.sh`
- Include purpose in filename where possible

---

## Testing Standards

### Testing Philosophy

**Test-First Mindset**:
- Write tests for new features before implementation (where feasible)
- Test edge cases and error conditions
- Maintain test coverage for critical paths

**Test Types**:
1. **Unit Tests**: Test individual functions/classes in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Manual Tests**: UI/UX validation, accessibility

### Test Structure

**Location**:
- All tests in `tests/` directory
- Mirror source structure: `tests/test_sophia_gnostic_map.py` tests `src/sophia_gnostic_map.py`

**Naming Conventions**:
```python
# Test files: test_<module_name>.py
# Test classes: Test<ClassName>
# Test methods: test_<function_name>_<scenario>

def test_process_regular_mode():
    """Test process() in regular mode"""
    pass

def test_process_narrative_mode_with_long_input():
    """Test process() in narrative mode with long input"""
    pass
```

### Running Tests

**All Tests**:
```bash
python -m pytest tests/ -v
```

**Specific Test File**:
```bash
python -m pytest tests/test_sophia_gnostic_map.py -v
```

**With Coverage**:
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Coverage Requirements

- **Critical Paths**: 90%+ coverage (Sophia memory, authentication, core processing)
- **Feature Modules**: 80%+ coverage
- **Utility Functions**: 70%+ coverage
- **UI/Frontend**: Manual testing + automated where feasible

---

## Code Review Process

### Before Submitting

**Self-Review Checklist**:
- [ ] Code follows style guidelines (PEP 8 for Python)
- [ ] No commented-out code or debug prints
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No secrets/credentials in code
- [ ] Performance considerations addressed

### Review Criteria

**Functionality**:
- Does it solve the problem correctly?
- Are edge cases handled?
- Is error handling appropriate?

**Code Quality**:
- Is it readable and maintainable?
- Are functions/classes well-named?
- Is there unnecessary complexity?
- Are there code smells or anti-patterns?

**Testing**:
- Are tests comprehensive?
- Do tests actually test the functionality?
- Are mocks used appropriately?

**Documentation**:
- Is the code self-documenting?
- Are complex sections commented?
- Is external documentation updated?

---

## Git Workflow

### Branch Naming

**Format**: `<type>/<short-description>`

**Types**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/changes
- `chore/` - Maintenance tasks

**Examples**:
- `feature/gnostic-blade-enhancement`
- `fix/memory-persistence-bug`
- `docs/update-api-documentation`

### Commit Message Format

**Structure**:
```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat: add gnostic blade forensic vivisection

Implements the 6-question analysis loop for deep truth extraction.
Automatically triggers on keywords related to ancient texts, history,
science, money, power, and consciousness.

Closes #123
```

```
fix: resolve memory persistence race condition

Adds locking mechanism to prevent concurrent writes to
sophia_gnostic_map.json that were causing data corruption.
```

---

## Performance Guidelines

### Response Time Targets

- **API Endpoints**: < 200ms (without AI processing)
- **AI Processing**: 2-8 seconds (model-dependent)
- **Database Queries**: < 50ms
- **Page Load**: < 2 seconds

### Optimization Strategies

**Lazy Loading**:
- Defer expensive imports until needed
- Load large data files on-demand
- Initialize heavy objects lazily

**Caching**:
- Cache frequently accessed data
- Invalidate caches appropriately
- Use memory-efficient cache structures

**Async Operations**:
- Use async/await for I/O operations
- Non-blocking file writes
- Background processing for non-critical tasks

**Database Optimization**:
- Index frequently queried fields
- Batch operations where possible
- Minimize query count

---

## Security Practices

### Authentication & Authorization

- **Never** store passwords in plain text
- Use environment variables for secrets
- Implement rate limiting
- Validate all user inputs
- Use HTTPS in production

### Input Validation

```python
# Always validate user inputs
def process_input(user_text: str) -> str:
    # Length validation
    if len(user_text) > MAX_INPUT_LENGTH:
        raise ValueError("Input too long")
    
    # Content validation
    if contains_malicious_content(user_text):
        raise ValueError("Invalid input")
    
    return sanitize(user_text)
```

### Secrets Management

**Environment Variables**:
```bash
# .env file (never commit!)
SUPABASE_URL=https://...
SUPABASE_KEY=eyJ...
FLASK_SECRET_KEY=...
```

**Example Usage**:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("SUPABASE_KEY")
```

---

## Documentation Standards

### Code Comments

**When to Comment**:
- Complex algorithms or business logic
- Non-obvious design decisions
- Workarounds or hacks (with explanation)
- TODO/FIXME notes

**When NOT to Comment**:
- Obvious code (let it be self-documenting)
- Redundant descriptions of what code does

**Examples**:
```python
# GOOD: Explains WHY
# Using exponential backoff to handle rate limits from external API
retry_delay = 2 ** attempt

# BAD: Explains WHAT (obvious from code)
# Set retry_delay to 2 to the power of attempt
retry_delay = 2 ** attempt
```

### Docstrings

**Format** (Google style):
```python
def process(self, user_input: str, mode: str = "regular") -> str:
    """Process user input and generate response.
    
    Args:
        user_input: The user's question or prompt
        mode: Response mode ("regular" or "narrative")
    
    Returns:
        Generated response text
    
    Raises:
        ValueError: If mode is invalid
    """
    pass
```

### Markdown Documentation

**Structure**:
- Use clear headings (H1, H2, H3)
- Include table of contents for long docs
- Use code blocks with language specification
- Link to related docs

**Example**:
```markdown
# Feature Name

## Overview
Brief description...

## Usage
Code examples...

## Configuration
Settings and options...

## See Also
- [Related Doc](./related.md)
```

---

## Changelog Maintenance

### Format

See `CHANGELOG.md` for format. Key principles:
- Group changes by type (Added, Changed, Fixed, Removed)
- Use present tense
- Link to issues/PRs
- Include version and date

### Example Entry

```markdown
## [2.0.0] - 2025-12-27

### Added
- Gnostic blade forensic vivisection protocol
- Two-mode system (Regular/Narrative)
- Sophia 7-layer gnostic map

### Changed
- Refactored memory system for async operations
- Updated API endpoints for v2

### Fixed
- Memory persistence race condition
- Server caching issues

### Removed
- Deprecated state management functions
```

---

## Development Environment

### Required Tools

- Python 3.8+
- Git
- Code editor (VS Code recommended)
- Ollama (for local AI)

### Setup

```bash
# Clone repository
git clone <repo-url>
cd "thesidia ice"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Run tests
python -m pytest tests/ -v

# Start server
./start_server.sh
```

---

## Best Practices Summary

1. **Write Clean Code**: Self-documenting, minimal complexity
2. **Test Thoroughly**: High coverage on critical paths
3. **Document Clearly**: Code, APIs, and architecture
4. **Review Carefully**: Code review before merge
5. **Commit Often**: Small, focused commits
6. **Stay Secure**: Never commit secrets, validate inputs
7. **Optimize Wisely**: Profile before optimizing
8. **Maintain Consistency**: Follow established patterns

---

## Resources

- [PEP 8 Style Guide](https://pep8.org/)
- [Python Testing Best Practices](https://docs.pytest.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2)
- [Security Checklist](https://owasp.org/)

---

**Questions?** See `docs/engineering/` for detailed guides or ask in team discussions.
