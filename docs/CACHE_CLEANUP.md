# Development Cache Cleanup

## Cache Files That Were Cleared

### Python Cache (Safe to Clear)
- **`__pycache__/` directories**: Python bytecode cache
  - `src/__pycache__/` (293.4 KB)
  - `tests/__pycache__/` (6.9 KB)
  - These are automatically regenerated when Python runs
- **`.pyc` files**: Compiled Python bytecode
  - Automatically regenerated
  - Total: ~300 KB cleared

### Test Cache (Safe to Clear)
- **`.pytest_cache/`**: Pytest test cache (20 KB)
  - Regenerated on next test run
  - Safe to delete

### Temporary Files (Safe to Clear)
- **`.DS_Store` files**: macOS Finder metadata
  - Not needed for development
  - Safe to delete

### Files NOT Cleared (Preserved)
- **`genesis_test_run.log`**: Test log file (kept for reference)
- **`venv/` cache**: Virtual environment cache (needed for dependencies)
- **`node_modules/` cache**: Node.js dependencies (if any)
- **Data files**: All state and analysis files preserved

## Cache Cleanup Script

A cleanup script is available at:
```bash
./scripts/clear_dev_cache.sh
```

**What it does**:
- Clears `__pycache__` directories (excluding venv)
- Clears `.pyc`, `.pyo` files
- Clears `.pytest_cache`
- Clears `.mypy_cache` (if exists)
- Clears `.cache` directories
- Clears `.DS_Store` files
- Clears temporary files (`.tmp`, `.swp`, `.swo`, `*~`)

**What it preserves**:
- `venv/` directory (virtual environment)
- `node_modules/` directory
- Log files (optional - can be enabled)
- All data files

## When to Clear Cache

Clear cache when:
- ✅ Code changes aren't being picked up
- ✅ Import errors after refactoring
- ✅ Stale bytecode causing issues
- ✅ Before committing code
- ✅ After major refactoring

## Manual Cleanup

If you need to clear cache manually:

```bash
# Python cache
find . -type d -name "__pycache__" ! -path "*/venv/*" -exec rm -rf {} +
find . -type f -name "*.pyc" ! -path "*/venv/*" -delete

# Pytest cache
rm -rf .pytest_cache

# Mypy cache
rm -rf .mypy_cache

# macOS files
find . -name ".DS_Store" ! -path "*/venv/*" -delete
```

## Cache Regeneration

All cleared cache will be automatically regenerated:
- **Python cache**: Regenerated on next import
- **Pytest cache**: Regenerated on next test run
- **Mypy cache**: Regenerated on next type check

No data loss - cache is purely for performance.

