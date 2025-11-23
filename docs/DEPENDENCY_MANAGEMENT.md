# Dependency Management Guide

## Current State

### Root `requirements.txt` (Development)
- Uses **minimum versions** (`>=`) - flexible, allows updates
- Good for: Development, getting latest features
- Current format:
  ```
  flask>=2.3.0
  flask-cors>=4.0.0
  ollama>=0.1.0
  requests>=2.31.0
  beautifulsoup4>=4.12.0
  lxml>=4.9.0
  ```

### `requirements-frozen.txt` (Production)
- Uses **exact versions** (`==`) - frozen, reproducible
- Good for: Production, CI/CD, exact reproducibility
- Generated from: `pip freeze`

## Should Dependencies Be Frozen?

### ✅ YES - For Production
**Benefits**:
- **Reproducibility**: Same versions = same behavior
- **Stability**: No surprise breaking changes
- **Debugging**: Easier to reproduce issues
- **CI/CD**: Consistent builds

**When to use**: Production deployments, CI/CD pipelines, shared environments

### ⚠️ MAYBE - For Development
**Benefits of flexible (`>=`)**:
- Get security patches automatically
- Get new features
- Easier to test with latest versions

**Risks**:
- Breaking changes can sneak in
- Harder to debug version-specific issues
- Team members may have different versions

**Best Practice**: Use frozen for production, flexible for development

## How to Freeze Dependencies

### Generate Frozen Requirements
```bash
# Activate your virtual environment first
source venv/bin/activate  # or: source webapp/venv/bin/activate

# Generate frozen requirements
pip freeze | grep -E "(flask|flask-cors|ollama|requests|beautifulsoup4|lxml)" > requirements-frozen.txt

# Or get all dependencies
pip freeze > requirements-frozen.txt
```

### Install from Frozen Requirements
```bash
pip install -r requirements-frozen.txt
```

### Update Frozen Requirements
```bash
# Update packages
pip install --upgrade package-name

# Regenerate frozen file
pip freeze > requirements-frozen.txt
```

## Current Installed Versions

Based on system check:
- `ollama`: 0.6.0
- `requests`: 2.32.4
- `beautifulsoup4`: 4.14.2
- `lxml`: 6.0.2
- `flask`: (check with `pip show flask`)
- `flask-cors`: (check with `pip show flask-cors`)

## Recommendations

### For This Project

1. **Keep `requirements.txt` flexible** (`>=`)
   - Good for development
   - Allows getting latest features
   - Easier maintenance

2. **Create `requirements-frozen.txt`** (`==`)
   - For production deployments
   - For CI/CD pipelines
   - For exact reproducibility

3. **Document version compatibility**
   - Test with minimum versions
   - Document known working versions
   - Update when breaking changes occur

### Best Practice Workflow

```bash
# Development
pip install -r requirements.txt  # Gets latest compatible versions

# Production
pip install -r requirements-frozen.txt  # Gets exact versions

# Update frozen (after testing)
pip install --upgrade -r requirements.txt
pip freeze > requirements-frozen.txt
git add requirements-frozen.txt
```

## Version Strategy

### Minimum Versions (`>=`)
- **Use for**: Development, libraries, optional features
- **Example**: `flask>=2.3.0` (works with 2.3.0, 2.4.0, 3.0.0, etc.)
- **Risk**: New versions may break things

### Exact Versions (`==`)
- **Use for**: Production, critical dependencies
- **Example**: `flask==3.1.2` (only this version)
- **Risk**: May miss security patches

### Compatible Versions (`~=`)
- **Use for**: Minor updates OK, major updates not
- **Example**: `flask~=3.1.0` (3.1.0, 3.1.1, 3.1.2 OK, but not 3.2.0)
- **Risk**: Medium - allows patches, blocks features

## Webapp Requirements

**Note**: `webapp/requirements.txt` has `chromadb>=0.4.0` but it's **not used** in the codebase.

**Recommendation**: Remove `chromadb` from webapp requirements or add a comment explaining why it's there.

## Summary

| File | Purpose | Format | When to Use |
|------|---------|--------|-------------|
| `requirements.txt` | Development | `>=` (flexible) | Daily development |
| `requirements-frozen.txt` | Production | `==` (exact) | Production, CI/CD |
| `webapp/requirements.txt` | Webapp dev | `>=` (flexible) | Webapp development |

**Answer**: Dependencies are **NOT frozen** (using `>=`). For production, **YES, they should be frozen** (using `==` in `requirements-frozen.txt`).

---

**Last Updated**: 2025-11-21

