# Quick Start: Development Guide

**For**: New contributors ready to jump in  
**Time**: 30 minutes to get started

---

## 🚀 Immediate Action Items

### 1. Fix Bare Except Clauses (EASIEST - Start Here!)

**Find them**:
```bash
cd "/Users/deshonjackson/thesidia ice"
grep -rn "except:" src/ --include="*.py"
```

**Fix pattern**:
```python
# BEFORE (BAD)
try:
    result = some_function()
except:
    return None

# AFTER (GOOD)
try:
    result = some_function()
except (ValueError, KeyError, TypeError) as e:
    logger.error(f"Error in some_function: {e}", exc_info=True)
    return None
```

**Files to check**:
- `src/thesidia_hybrid_adaptive.py`
- `src/metrics_collector.py`
- `src/emergence_tracker.py`

**Time**: 1-2 hours  
**Impact**: 🔴 CRITICAL - Makes debugging possible

---

### 2. Setup Logging Infrastructure

**Create file**: `src/core/logging_config.py`
```python
import logging
import sys
from pathlib import Path

def setup_logging(level=logging.INFO):
    """Setup logging configuration for Thesidia"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / 'thesidia.log')
        ]
    )
    
    return logging.getLogger(__name__)
```

**Replace prints** (start with 10-20 as proof of concept):
```python
# BEFORE
print(f"Processing query: {query}")

# AFTER
import logging
logger = logging.getLogger(__name__)
logger.info(f"Processing query: {query}")
```

**Time**: 2-3 hours  
**Impact**: 🟡 HIGH - Essential for production

---

### 3. Write Your First Test

**Create**: `tests/unit/test_synthesis_basic.py`
```python
import pytest
from src.synthesis.data_synthesizer import DataSynthesizer

def test_synthesize_basic():
    """Test basic synthesis functionality"""
    synthesizer = DataSynthesizer()
    
    sources = [
        {"title": "Source 1", "content": "Test content 1", "url": "http://test1.com"},
        {"title": "Source 2", "content": "Test content 2", "url": "http://test2.com"}
    ]
    
    result = synthesizer.synthesize(
        sources=sources,
        query="Test query"
    )
    
    assert result is not None
    assert "synthesis" in result
    assert "citations" in result
```

**Run it**:
```bash
pytest tests/unit/test_synthesis_basic.py -v
```

**Time**: 1 hour  
**Impact**: 🟡 HIGH - Sets testing foundation

---

### 4. Clean Up One Backup File

**Archive**: `src/thesidia_hybrid_adaptive.py.backup_current`

**Action**:
```bash
mkdir -p src/archive/backups
mv src/thesidia_hybrid_adaptive.py.backup_current src/archive/backups/
```

**Time**: 5 minutes  
**Impact**: 🟢 MEDIUM - Cleaner codebase

---

## 📋 Development Checklist

**Before You Start**:
- [ ] Read `README.md`
- [ ] Read `SCAFFOLDING_ROADMAP.md`
- [ ] Setup virtual environment
- [ ] Install dependencies
- [ ] Run existing tests

**Your First PR**:
- [ ] Pick a task from Quick Wins
- [ ] Create feature branch
- [ ] Make changes
- [ ] Write/update tests
- [ ] Update documentation
- [ ] Submit PR

---

## 🎯 Recommended First Tasks

**Ranked by Impact/Effort**:

1. **Fix Bare Except Clauses** (1-2 hours)
   - High impact, low effort
   - Makes debugging possible
   - Easy to verify

2. **Setup Logging** (2-3 hours)
   - High impact, medium effort
   - Essential for production
   - Clear improvement

3. **Write Unit Tests** (3-4 hours)
   - High impact, medium effort
   - Safety net for refactoring
   - Learning opportunity

4. **Clean Dead Code** (2-3 hours)
   - Medium impact, low effort
   - Cleaner codebase
   - Easy wins

---

## 🛠️ Setup Commands

```bash
# Navigate to project
cd "/Users/deshonjackson/thesidia ice"

# Activate virtual environment
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dev dependencies
pip install pytest pytest-cov black flake8

# Run existing tests
pytest tests/ -v

# Check code style
black src/ --check
flake8 src/
```

---

## 📚 Key Files to Read

**Essential** (30 minutes):
1. `README.md` - Project overview
2. `SCAFFOLDING_ROADMAP.md` - This document's parent
3. `src/synthesis/data_synthesizer.py` - Core synthesis logic

**Deep Dive** (2-3 hours):
1. `ENGINEERING_REVIEW.md` - Technical assessment
2. `src/thesidia_hybrid_adaptive.py` - Main orchestrator (skim)
3. `src/memory/sophia_gnostic_map.py` - Memory system

---

## 🎉 You're Ready!

Pick a task, create a branch, and start coding. The codebase is well-documented and the patterns are clear. Welcome to Thesidia! 🚀


