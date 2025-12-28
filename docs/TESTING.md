# Testing Guide

**Last Updated**: 2025-12-27

Comprehensive testing guide for the Thesidia project including testing philosophy, how to run tests, and guidelines for writing new tests.

---

## Testing Philosophy

### Core Principles

1. **Test What Matters**: Focus on critical paths and user-facing functionality
2. **Fast Feedback**: Tests should run quickly to encourage frequent execution
3. **Clear Failures**: Test failures should clearly indicate what broke
4. **Maintainable**: Tests should be easy to understand and update

### Testing Pyramid

```
      /\
     /  \      E2E Tests (Manual + Browser)
    /────\     ────────────────────────────
   /      \    Integration Tests
  /────────\   ────────────────────────────
 /          \  Unit Tests
/────────────\ ────────────────────────────
```

**Unit Tests** (70%): Test individual functions/classes
**Integration Tests** (20%): Test component interactions
**E2E Tests** (10%): Test complete workflows

---

## Test Structure

### Directory Organization

```
tests/
├── __pycache__/                    # Compiled test files
├── social/                         # Social feature tests
│   ├── test_feed_system.py
│   └── test_bot_generation.py
├── test_conversation_store.py      # Conversation persistence
├── test_emergence_scoring.py       # Sophia emergence
├── test_gnostic_principles.py      # Gnostic system
├── test_model_client.py            # Model integration
├── test_security.py                # Security features
├── test_sophia_gnostic_map.py      # Sophia memory
└── test_thesidia_comprehensive.py  # Comprehensive tests
```

### Test File Naming

**Pattern**: `test_<module_name>.py`

```python
# Tests for src/sophia_gnostic_map.py
tests/test_sophia_gnostic_map.py

# Tests for src/thesidia_hybrid_adaptive.py
tests/test_thesidia_comprehensive.py

# Tests for webapp/routes/social_routes.py
tests/social/test_feed_system.py
```

---

## Running Tests

### All Tests

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=src --cov=webapp --cov-report=html

# Run with output to terminal (see print statements)
python -m pytest tests/ -v -s
```

### Specific Tests

```bash
# Single test file
python -m pytest tests/test_sophia_gnostic_map.py -v

# Single test class
python -m pytest tests/test_sophia_gnostic_map.py::TestSophiaGnosticMap -v

# Single test method
python -m pytest tests/test_sophia_gnostic_map.py::TestSophiaGnosticMap::test_store_redaction -v

# Tests matching pattern
python -m pytest tests/ -k "gnostic" -v
```

### Test Options

```bash
# Stop on first failure
python -m pytest tests/ -x

# Run last failed tests
python -m pytest tests/ --lf

# Run tests in parallel (requires pytest-xdist)
python -m pytest tests/ -n auto

# Show local variables on failure
python -m pytest tests/ -l

# Generate HTML report
python -m pytest tests/ --html=report.html
```

---

## Existing Test Suites

### 1. Sophia Gnostic Map Tests (`test_sophia_gnostic_map.py`)

**Coverage**:
- Redaction storage and retrieval
- Archon tracking
- Fragment management
- Version management
- Pattern recognition

**Example**:
```python
def test_store_redaction():
    """Test storing and retrieving redactions"""
    map = SophiaGnosticMap()
    map.store_redaction("Council of Nicaea", "Book removal", "325 CE")
    
    redactions = map.get_redactions()
    assert len(redactions) > 0
    assert redactions[0]['event'] == "Council of Nicaea"
```

### 2. Comprehensive Thesidia Tests (`test_thesidia_comprehensive.py`)

**Coverage**:
- Two-mode system (Regular/Narrative)
- Gnostic blade triggering
- Response generation
- State persistence

**Example**:
```python
def test_two_mode_system():
    """Test regular vs narrative modes"""
    thesidia = ThesidiaHybridAdaptive()
    
    # Regular mode (short)
    regular = thesidia.process("What is Genesis?")
    
    # Narrative mode (longer)
    narrative = thesidia.process("Tell me about Genesis extensively")
    
    assert len(narrative) > len(regular)
```

### 3. Gnostic Principles Tests (`test_gnostic_principles.py`)

**Coverage**:
- Cross-referencing
- Pattern recognition
- Gnosis-episteme synthesis
- Framework creation

**Example**:
```python
def test_cross_reference_principle():
    """Test cross-referencing across domains"""
    result = apply_gnostic_principles(
        "Egyptian hieroglyphics",
        principle="cross_reference"
    )
    
    assert "multiple sources" in result.lower()
```

### 4. Security Tests (`test_security.py`)

**Coverage**:
- Input validation
- Username validation
- Reserved name checking
- SQL injection prevention

**Example**:
```python
def test_validate_username():
    """Test username validation"""
    from webapp.middleware.security import validate_username
    
    # Valid username
    is_valid, error = validate_username("user123")
    assert is_valid
    
    # Reserved username
    is_valid, error = validate_username("admin")
    assert not is_valid
    assert "reserved" in error.lower()
```

### 5. Model Client Tests (`test_model_client.py`)

**Coverage**:
- Model initialization
- Response generation
- Error handling
- Stream parsing

---

## Writing New Tests

### Test Structure Template

```python
import pytest
from src.module_name import ClassToTest

class TestClassName:
    """Tests for ClassName"""
    
    @pytest.fixture
    def instance(self):
        """Create test instance"""
        return ClassToTest()
    
    def test_basic_functionality(self, instance):
        """Test basic functionality works"""
        result = instance.method()
        assert result is not None
    
    def test_edge_case(self, instance):
        """Test edge case handling"""
        with pytest.raises(ValueError):
            instance.method(invalid_input)
    
    def test_state_change(self, instance):
        """Test state changes correctly"""
        instance.update_state("new_value")
        assert instance.state == "new_value"
```

### Using Fixtures

**Simple Fixture**:
```python
@pytest.fixture
def sample_data():
    """Provide sample test data"""
    return {
        "user_id": "test_user",
        "message": "Hello, Thesidia"
    }

def test_process_message(sample_data):
    """Test message processing"""
    result = process(sample_data["message"])
    assert len(result) > 0
```

**Setup/Teardown Fixture**:
```python
@pytest.fixture
def temp_file(tmp_path):
    """Create temporary file for testing"""
    file_path = tmp_path / "test_data.json"
    file_path.write_text('{"test": true}')
    yield file_path
    # Cleanup happens automatically
```

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock_ollama():
    """Test without actually calling Ollama"""
    with patch('ollama.chat') as mock_chat:
        mock_chat.return_value = {"message": {"content": "Mocked response"}}
        
        result = generate_response("test input")
        assert result == "Mocked response"
        mock_chat.assert_called_once()
```

### Parameterized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("test", "TEST"),
])
def test_uppercase(input, expected):
    """Test uppercase conversion"""
    assert input.upper() == expected
```

---

## Testing Best Practices

### 1. Arrange-Act-Assert Pattern

```python
def test_user_creation():
    # Arrange: Set up test data
    username = "test_user"
    email = "test@example.com"
    
    # Act: Execute the functionality
    user = create_user(username, email)
    
    # Assert: Verify results
    assert user.username == username
    assert user.email == email
    assert user.created_at is not None
```

### 2. Test One Thing Per Test

```python
# GOOD: Single responsibility
def test_user_username_stored():
    user = create_user("test_user")
    assert user.username == "test_user"

def test_user_has_creation_timestamp():
    user = create_user("test_user")
    assert user.created_at is not None

# BAD: Testing multiple things
def test_user_creation():
    user = create_user("test_user")
    assert user.username == "test_user"  # Multiple assertions
    assert user.created_at is not None   # Testing different things
    assert user.is_active == True       # Becomes hard to debug
```

### 3. Use Descriptive Test Names

```python
# GOOD: Describes what is being tested
def test_gnostic_blade_triggers_on_ancient_text_keyword():
    pass

def test_narrative_mode_produces_longer_response_than_regular():
    pass

# BAD: Unclear what is being tested
def test_blade_works():
    pass

def test_modes():
    pass
```

### 4. Test Edge Cases

```python
def test_process_with_various_inputs():
    thesidia = ThesidiaHybridAdaptive()
    
    # Empty input
    assert thesidia.process("") == ""
    
    # Very long input
    long_input = "word " * 10000
    result = thesidia.process(long_input)
    assert len(result) > 0
    
    # Special characters
    assert thesidia.process("!@#$%^&*()") is not None
    
    # Unicode
    assert thesidia.process("こんにちは") is not None
```

### 5. Keep Tests Independent

```python
# GOOD: Each test is independent
class TestGnosticMap:
    @pytest.fixture
    def fresh_map(self):
        """Create fresh map for each test"""
        return SophiaGnosticMap()
    
    def test_store_redaction(self, fresh_map):
        fresh_map.store_redaction("Event", "Detail", "Date")
        assert len(fresh_map.get_redactions()) == 1
    
    def test_store_archon(self, fresh_map):
        fresh_map.store_archon("Name", "Domain", "Method")
        assert len(fresh_map.get_archons()) == 1

# BAD: Tests depend on order
class TestGnosticMapBad:
    map = SophiaGnosticMap()  # Shared state
    
    def test_store_redaction(self):
        self.map.store_redaction("Event", "Detail", "Date")
        # This affects the next test!
```

---

## Integration Testing

### Server Integration Tests

```python
import pytest
from webapp.server import app

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_status_endpoint(client):
    """Test /api/status returns correctly"""
    response = client.get('/api/status')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'thesidia_ready' in data
    assert 'timestamp' in data

def test_api_process_endpoint(client):
    """Test /api/process handles requests"""
    response = client.post('/api/process', json={
        'message': 'Hello, Thesidia',
        'mode': 'regular'
    })
    assert response.status_code == 200
```

### Database Integration Tests

```python
def test_conversation_storage():
    """Test conversation persistence"""
    from webapp.conversations.storage import build_store
    
    store = build_store()
    
    # Create conversation
    conv_id = "test_conv_001"
    store.upsert_conversation(
        conversation_id=conv_id,
        title="Test Conversation",
        messages=[{"role": "user", "content": "Test"}]
    )
    
    # Retrieve conversation
    conv = store.get_conversation(conv_id)
    assert conv is not None
    assert conv['title'] == "Test Conversation"
    assert len(conv['messages']) == 1
```

---

## Manual Testing Procedures

### Server Startup Test

1. Start server: `./start_server.sh`
2. Verify no errors in console
3. Access http://localhost:5002
4. Verify landing page loads

### Admin Dashboard Test

1. Navigate to http://localhost:5002/admin
2. Verify Nexus dashboard loads
3. Check all widgets display data
4. Verify no console errors

### Authentication Flow Test

1. Navigate to login page
2. Test OAuth providers (Google, GitHub)
3. Test email/password login
4. Test phone authentication
5. Verify session persistence

### Response Generation Test

1. Open stream interface
2. Enter test prompts:
   - Regular: "What is consciousness?"
   - Narrative: "Tell me about consciousness extensively"
   - Gnostic blade trigger: "What were the Dead Sea Scrolls?"
3. Verify appropriate response lengths
4. Verify gnostic blade formatting

---

## Test Coverage

### Current Coverage

Run coverage report:
```bash
python -m pytest tests/ --cov=src --cov=webapp --cov-report=term-missing
```

### Coverage Goals

| Component | Target | Priority |
|-----------|--------|----------|
| **Sophia Gnostic Map** | 90%+ | High |
| **Authentication** | 90%+ | High |
| **Core Processing** | 85%+ | High |
| **API Routes** | 80%+ | Medium |
| **Utilities** | 75%+ | Medium |
| **Frontend** | Manual | Low |

### Improving Coverage

**Identify Gaps**:
```bash
# Generate HTML coverage report
python -m pytest tests/ --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html
```

**Write Missing Tests**:
1. Check HTML report for red (uncovered) lines
2. Focus on critical paths first
3. Write tests for uncovered code
4. Re-run coverage to verify

---

## Continuous Integration

### Pre-Commit Checks

```bash
# Run before committing
python -m pytest tests/ -v
python -m pytest tests/ --cov=src --cov-report=term
```

### Automated Testing (Future)

**GitHub Actions** (example):
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/ -v --cov
```

---

## Troubleshooting Tests

### Common Issues

**Import Errors**:
```bash
# Make sure to run from project root
cd /Users/deshonjackson/thesidia\ ice
python -m pytest tests/ -v
```

**Ollama Not Available**:
```python
# Skip tests requiring Ollama
@pytest.mark.skipif(not ollama_available(), reason="Ollama not running")
def test_with_ollama():
    pass
```

**File System Issues**:
```python
# Use tmp_path fixture for temporary files
def test_file_operations(tmp_path):
    test_file = tmp_path / "test.json"
    # File automatically cleaned up
```

**Async Tests**:
```python
# Install pytest-asyncio
# pip install pytest-asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

---

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Engineering Practices](ENGINEERING.md)
- [Architecture Overview](ARCHITECTURE.md)

---

**Questions?** Consult existing test files for examples or refer to pytest documentation.
