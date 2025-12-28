# Duplicate Code Analysis

## Summary

This document identifies all duplicate code patterns in the Thesidia codebase, their locations, and refactoring status.

## Status Overview

**Refactored** (✅): Query normalization, forensic routing detection, profile loading  
**Still Duplicated** (⚠️): User data retrieval pattern, init_thesidia function, backup files

---

## 1. Query Normalization & Forensic Routing (✅ REFACTORED)

### Status: ✅ Refactored to `src/support/query_utils.py`

**Original Duplication** (3 locations):
- `webapp/server.py:369-389` (non-streaming endpoint)
- `webapp/server.py:525-535` (streaming endpoint)  
- `src/thesidia_hybrid_adaptive.py:3511-3517, 3626-3632` (main processing - appeared twice)

**Current State**: All locations now import from `src/support/query_utils.py`:
```python
from src.support.query_utils import normalize_query, detect_forensic_routing
```

**Functions Extracted**:
- `normalize_query(text: str) -> str` - Fixes typos (genensis → genesis, etc.)
- `detect_forensic_routing(text: str, comprehensive: bool = False) -> bool` - Detects if query needs forensic analysis

**Lines Removed**: ~150 lines of duplicate code eliminated

---

## 2. Profile Loading (✅ REFACTORED)

### Status: ✅ Refactored to `webapp/utils/profile_loader.py`

**Original Duplication** (2 locations):
- `webapp/server.py:1292-1331` (get_posts endpoint)
- `webapp/server.py:1426-1456` (get_feed endpoint)

**Current State**: Both locations now use shared utility:
```python
from webapp.utils.profile_loader import attach_author_to_post
attach_author_to_post(post, project_root, include_legacy_fields=True)
```

**Functions Extracted**:
- `load_author_profile(author_id, project_root, include_legacy_fields)` - Loads profile from JSON
- `attach_author_to_post(post, project_root, include_legacy_fields)` - Attaches profile to post

**Lines Removed**: ~80 lines of duplicate code eliminated

---

## 3. User Data Retrieval Pattern (⚠️ STILL DUPLICATED)

### Status: ⚠️ Still duplicated - needs refactoring

**Location**: `webapp/server.py` - 33 instances found

**Pattern**: Repeated `user_memory_manager.get_user_data()` calls with similar error handling:

```python
# Pattern appears in multiple endpoints:
user_id = request.args.get('user_id') or data.get('user_id')
session_id = request.args.get('session_id') or data.get('session_id')

if not user_id and not session_id:
    return jsonify({'error': 'user_id or session_id required'}), 400

try:
    user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
    # ... use user_data ...
except Exception as e:
    return jsonify({'error': str(e)}), 500
```

**Affected Endpoints** (examples):
- Line 775-789: `/api/knowledge/search`
- Line 848-852: `/api/user/data`
- Line 874-878: `/api/stream/feed`
- Line 918-922: `/api/posts` (create)
- Line 989-993: `/api/posts/<post_id>/like`
- Line 1026-1030: `/api/posts/<post_id>/comment`
- Line 1064-1068: `/api/users/<username>/follow`
- ... and 26 more locations

**Recommended Fix**: Create decorator or middleware:
```python
# webapp/middleware/user_auth.py
def require_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.args.get('user_id') or request.json.get('user_id')
        session_id = request.args.get('session_id') or request.json.get('session_id')
        
        if not user_id and not session_id:
            return jsonify({'error': 'user_id or session_id required'}), 400
        
        try:
            user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
            kwargs['user_data'] = user_data
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return decorated_function
```

**Usage**:
```python
@app.route('/api/posts', methods=['POST'])
@require_user
def create_post(user_data):
    # user_data is automatically available
    user_id = user_data.get('user_id')
    # ... rest of endpoint ...
```

**Estimated Impact**: ~200 lines of duplicate code could be eliminated

---

## 4. init_thesidia Function (⚠️ DUPLICATED)

### Status: ⚠️ Duplicated across 2 files

**Locations**:
1. `webapp/server.py:192` - Main webapp server
2. `api/api_server.py:52` - Standalone API server

**Code**:
```python
def init_thesidia():
    """Initialize Thesidia system"""
    global thesidia, thesidia_ready, knowledge_base, user_memory_manager, ...
    
    try:
        # Check Ollama
        import ollama
        try:
            ollama.list()
        except:
            print("Warning: Ollama not running...")
            return False
        
        # Initialize components
        knowledge_base = KnowledgeBase(base_dir=project_root)
        user_memory_manager = UserMemoryManager(base_dir=project_root)
        # ... more initialization ...
        
        thesidia = ThesidiaHybridAdaptive(model="clean-mistral:latest")
        thesidia.load_state()
        thesidia_ready = True
        return True
    except Exception as e:
        print(f"Error initializing Thesidia: {e}")
        return False
```

**Why Duplicated**: 
- Two separate servers (webapp vs API) need same initialization
- Different global variable contexts
- Slight variations in error handling

**Recommended Fix**: Extract to shared module:
```python
# src/core/thesidia_initializer.py
def initialize_thesidia_system(project_root: Path, model: str = "clean-mistral:latest"):
    """Initialize Thesidia system components"""
    # ... shared initialization logic ...
    return {
        'thesidia': thesidia,
        'knowledge_base': knowledge_base,
        'user_memory_manager': user_memory_manager,
        # ... etc ...
    }
```

**Estimated Impact**: ~50 lines of duplicate code

---

## 5. Backup Files (⚠️ DEAD CODE)

### Status: ⚠️ Should be archived/deleted

**Files**:
1. `src/thesidia_hybrid_adaptive.py.backup_current`
2. `src/thesidia_hybrid_adaptive.py.restored`
3. `src/thesidia_hybrid_adaptive.py.with_grok`
4. `webapp/server.py.bak`

**Action**: Archive to `archive/` directory or delete if no longer needed

**Impact**: Confusion, maintenance burden, repository bloat

---

## 6. Legacy Archive Files (⚠️ POTENTIALLY UNUSED)

### Status: ⚠️ Verify usage, then archive if unused

**Files in `src/archive/`**:
1. `thesidia_core.py` - Legacy core implementation
2. `thesidia_enhanced.py` - Legacy enhanced version
3. `thesidia_frontier.py` - Legacy frontier version
4. `thesidia_emergent.py` - Legacy emergent version
5. `thesidia_metrics_integration.py` - Legacy metrics integration

**Action**: 
1. Verify if any are imported/used: `grep -r "from.*archive" .`
2. If unused, move to `archive/` or document why they're kept
3. If used, document dependencies

**Impact**: Codebase clarity, reduced confusion

---

## 7. Similar Functionality Across Archive Files

### Status: ⚠️ Architectural duplication (not code duplication)

**Pattern**: Multiple Thesidia implementations with similar methods:
- `process_question()` / `process()` - Query processing
- `save_state()` / `load_state()` - State persistence
- `process_symbolic_language()` - Symbol processing

**Why**: Different versions/experiments, not active code duplication

**Action**: Document differences or consolidate if possible

---

## Summary Statistics

| Category | Status | Locations | Lines Affected | Priority |
|----------|--------|-----------|----------------|----------|
| Query Normalization | ✅ Refactored | 3 → 1 | ~150 removed | - |
| Profile Loading | ✅ Refactored | 2 → 1 | ~80 removed | - |
| User Data Retrieval | ⚠️ Needs Fix | 33 | ~200 | High |
| init_thesidia | ⚠️ Needs Fix | 2 | ~50 | Medium |
| Backup Files | ⚠️ Cleanup | 4 | N/A | Low |
| Archive Files | ⚠️ Verify | 5 | N/A | Low |

**Total Duplicate Code Remaining**: ~250 lines (user data retrieval + init_thesidia)

---

## Refactoring Priority

### High Priority 🔴
1. **User Data Retrieval Pattern** (33 instances)
   - Create `@require_user` decorator
   - Apply to all affected endpoints
   - Impact: ~200 lines removed, better error handling

### Medium Priority 🟡
2. **init_thesidia Function** (2 instances)
   - Extract to `src/core/thesidia_initializer.py`
   - Impact: ~50 lines removed, shared initialization logic

### Low Priority 🟢
3. **Backup Files Cleanup**
   - Archive or delete backup files
   - Impact: Cleaner repository

4. **Archive Files Verification**
   - Verify usage, document or archive
   - Impact: Codebase clarity

---

## Root Causes

1. **Hotfix Culture**: Production bugs fixed quickly with copy-paste
2. **No Shared Utilities**: Missing abstraction layer for common patterns
3. **Time Pressure**: "Fix now, refactor later" (later never came)
4. **No Code Review**: Duplication not caught before merge
5. **Generator Functions**: Made sharing code harder (streaming endpoint)

---

## Prevention Strategies

1. **Code Review**: Require review before merge
2. **Shared Utilities**: Create `webapp/utils/` and `src/support/` modules
3. **Decorators/Middleware**: Use Flask decorators for common patterns
4. **DRY Principle**: "Don't Repeat Yourself" - extract after 2nd duplication
5. **Refactoring Time**: Allocate time for technical debt reduction

---

## References

- `docs/engineering/DUPLICATION_ROOT_CAUSE_ANALYSIS.md` - Detailed root cause analysis
- `docs/engineering/REFACTORING_COMPLETE.md` - Completed refactoring documentation
- `docs/architecture/PROJECT_ASSESSMENT.md` - Project assessment with duplication notes





