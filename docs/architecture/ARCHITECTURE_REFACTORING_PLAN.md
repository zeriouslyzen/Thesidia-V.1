# Architecture Refactoring Plan

**Current State**: Monolithic (5,500+ lines)  
**Target State**: Modular (<500 lines per file)  
**Timeline**: 6 weeks (incremental)

---

## 📊 Current Architecture

### Current Structure (Monolithic)

```
src/thesidia_hybrid_adaptive.py (5,500+ lines)
├── ThesidiaHybridAdaptive (main class)
│   ├── Personality Management (500 lines)
│   ├── Query Routing (400 lines)
│   ├── Response Generation (600 lines)
│   ├── Learning System (400 lines)
│   ├── State Management (300 lines)
│   ├── Memory Integration (500 lines)
│   ├── Research Coordination (400 lines)
│   ├── Synthesis Orchestration (500 lines)
│   └── Utility Functions (900 lines)
└── Helper Classes (12 classes, 1,000+ lines)
```

**Problems**:
- ❌ Hard to navigate
- ❌ Difficult to test
- ❌ Merge conflicts
- ❌ High cognitive load
- ❌ Slow development

---

## 🎯 Target Architecture

### Target Structure (Modular)

```
src/thesidia/
├── __init__.py
├── core.py (300 lines)
│   └── ThesidiaCore - Main orchestrator
│
├── personality.py (400 lines)
│   ├── PersonalityManager
│   ├── TraitEvolution
│   └── ConversationStage
│
├── routing.py (300 lines)
│   ├── QueryRouter
│   ├── IntentDetector
│   └── ModeSelector
│
├── response.py (400 lines)
│   ├── ResponseGenerator
│   ├── FormatHandler
│   └── PostProcessor
│
├── learning.py (300 lines)
│   ├── LearningSystem
│   ├── StrategyAdapter
│   └── OutcomeTracker
│
├── state.py (200 lines)
│   ├── StateManager
│   ├── StatePersistence
│   └── StateLoader
│
└── integration.py (300 lines)
    ├── MemoryIntegrator
    ├── ResearchCoordinator
    └── SynthesisOrchestrator
```

**Benefits**:
- ✅ Easy to navigate
- ✅ Easy to test
- ✅ Clear separation of concerns
- ✅ Faster development
- ✅ Better collaboration

---

## 🔄 Refactoring Strategy

### Week 1: Extract PersonalityManager

**Current Location**: `src/thesidia_hybrid_adaptive.py` (lines ~400-900)

**Extract To**: `src/thesidia/personality.py`

**Classes to Extract**:
- `AdaptivePersonality` → `PersonalityManager`
- Personality trait management
- Conversation stage tracking
- Trait evolution logic

**Dependencies**:
- State persistence (keep in main for now)
- Memory systems (inject as dependency)

**Tests**:
- `tests/unit/test_personality.py`

---

### Week 2: Extract QueryRouter

**Current Location**: `src/thesidia_hybrid_adaptive.py` (lines ~3500-3800)

**Extract To**: `src/thesidia/routing.py`

**Classes to Extract**:
- Query routing logic
- Intent detection
- Mode selection
- Deep research detection

**Dependencies**:
- Intent detector (already separate)
- Research engine (inject)

**Tests**:
- `tests/unit/test_routing.py`

---

### Week 3: Extract ResponseGenerator

**Current Location**: `src/thesidia_hybrid_adaptive.py` (lines ~3800-4400)

**Extract To**: `src/thesidia/response.py`

**Classes to Extract**:
- Response generation logic
- Format handling
- Post-processing
- Streaming support

**Dependencies**:
- Synthesis engine (inject)
- Model client (inject)
- Memory systems (inject)

**Tests**:
- `tests/unit/test_response.py`

---

### Week 4: Extract LearningSystem

**Current Location**: `src/thesidia_hybrid_adaptive.py` (lines ~500-800)

**Extract To**: `src/thesidia/learning.py`

**Classes to Extract**:
- Adaptive learning logic
- Strategy adaptation
- Outcome tracking
- Learning from interactions

**Dependencies**:
- State persistence (inject)
- Metrics collector (inject)

**Tests**:
- `tests/unit/test_learning.py`

---

### Week 5: Extract StateManager

**Current Location**: `src/thesidia_hybrid_adaptive.py` (lines ~2900-3400)

**Extract To**: `src/thesidia/state.py`

**Classes to Extract**:
- State persistence
- State loading
- State management
- Backup/restore

**Dependencies**:
- File I/O (isolated)
- JSON serialization (isolated)

**Tests**:
- `tests/unit/test_state.py`

---

### Week 6: Refactor Main Orchestrator

**Current**: `src/thesidia_hybrid_adaptive.py` (5,500+ lines)

**Target**: `src/thesidia/core.py` (300 lines)

**What Remains**:
- Main `ThesidiaCore` class
- Component initialization
- High-level orchestration
- Public API

**Structure**:
```python
class ThesidiaCore:
    def __init__(self, ...):
        self.personality = PersonalityManager(...)
        self.router = QueryRouter(...)
        self.response = ResponseGenerator(...)
        self.learning = LearningSystem(...)
        self.state = StateManager(...)
    
    def process(self, input_text: str) -> str:
        # High-level orchestration only
        route = self.router.route(input_text)
        response = self.response.generate(route)
        self.learning.adapt(response)
        return response
```

---

## 📋 Extraction Checklist

**For Each Module**:

1. **Identify Code** (1-2 hours)
   - Find all related code
   - Identify dependencies
   - Map data flow

2. **Create Module** (2-3 hours)
   - Create new file
   - Extract classes/functions
   - Update imports

3. **Update Main File** (1-2 hours)
   - Remove extracted code
   - Add imports
   - Update references

4. **Write Tests** (2-3 hours)
   - Unit tests for module
   - Integration tests
   - Update existing tests

5. **Verify** (1 hour)
   - Run all tests
   - Test manually
   - Check performance

**Total per Module**: 7-11 hours

---

## 🧪 Testing Strategy

### Before Refactoring
- ✅ Write tests for current behavior
- ✅ Document expected behavior
- ✅ Create test fixtures

### During Refactoring
- ✅ Keep tests passing
- ✅ Add tests for new modules
- ✅ Update integration tests

### After Refactoring
- ✅ All tests passing
- ✅ Coverage maintained/increased
- ✅ Performance maintained

---

## 🔗 Dependency Injection Pattern

### Current (Tight Coupling)
```python
class ThesidiaHybridAdaptive:
    def __init__(self):
        self.synthesizer = DataSynthesizer()
        self.memory = SophiaGnosticMap()
        self.research = WebSearchEngine()
```

### Target (Dependency Injection)
```python
class ThesidiaCore:
    def __init__(
        self,
        synthesizer: Optional[DataSynthesizer] = None,
        memory: Optional[SophiaGnosticMap] = None,
        research: Optional[WebSearchEngine] = None
    ):
        self.synthesizer = synthesizer or DataSynthesizer()
        self.memory = memory or SophiaGnosticMap()
        self.research = research or WebSearchEngine()
```

**Benefits**:
- ✅ Easy to test (inject mocks)
- ✅ Easy to swap implementations
- ✅ Clear dependencies

---

## 📈 Progress Tracking

### Week 1: PersonalityManager
- [ ] Extract personality code
- [ ] Create `src/thesidia/personality.py`
- [ ] Update main file
- [ ] Write tests
- [ ] Verify functionality

### Week 2: QueryRouter
- [ ] Extract routing code
- [ ] Create `src/thesidia/routing.py`
- [ ] Update main file
- [ ] Write tests
- [ ] Verify functionality

### Week 3: ResponseGenerator
- [ ] Extract response code
- [ ] Create `src/thesidia/response.py`
- [ ] Update main file
- [ ] Write tests
- [ ] Verify functionality

### Week 4: LearningSystem
- [ ] Extract learning code
- [ ] Create `src/thesidia/learning.py`
- [ ] Update main file
- [ ] Write tests
- [ ] Verify functionality

### Week 5: StateManager
- [ ] Extract state code
- [ ] Create `src/thesidia/state.py`
- [ ] Update main file
- [ ] Write tests
- [ ] Verify functionality

### Week 6: Main Orchestrator
- [ ] Refactor main class
- [ ] Update to use modules
- [ ] Reduce to <500 lines
- [ ] Update all tests
- [ ] Final verification

---

## 🎯 Success Criteria

**Module Extraction Success**:
- ✅ Module <500 lines
- ✅ Clear single responsibility
- ✅ Well-tested (>80% coverage)
- ✅ No circular dependencies
- ✅ All tests passing

**Overall Refactoring Success**:
- ✅ Main file <500 lines
- ✅ All modules <500 lines
- ✅ Test coverage >60%
- ✅ Performance maintained
- ✅ All functionality working

---

## 🚨 Risk Mitigation

### Risk 1: Breaking Changes
**Mitigation**: 
- Incremental refactoring
- Comprehensive tests
- Feature flags for new code

### Risk 2: Merge Conflicts
**Mitigation**:
- Small, focused PRs
- Clear communication
- Regular integration

### Risk 3: Performance Regression
**Mitigation**:
- Performance tests
- Benchmark before/after
- Profile critical paths

---

## 📚 Resources

**Reference Documents**:
- `SCAFFOLDING_ROADMAP.md` - Overall roadmap
- `ENGINEERING_REVIEW.md` - Technical assessment
- `QUICK_START_DEVELOPMENT.md` - Getting started

**Code Examples**:
- `src/synthesis/` - Good modular example
- `src/memory/` - Good modular example
- `src/core/` - Good modular example

---

## 🎉 Ready to Refactor?

**Start Here**:
1. Read this document
2. Pick Week 1 task (PersonalityManager)
3. Create feature branch
4. Start extracting!

**Questions?** Check `SCAFFOLDING_ROADMAP.md` for detailed guidance.




