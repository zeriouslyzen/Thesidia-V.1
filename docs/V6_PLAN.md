# Thesidia V6.0 Plan
## Modular Architecture, Performance Optimization, and Vibecode Compliance

**Version**: 6.0  
**Status**: Planning  
**Current File Size**: 5,626 lines (monolithic)  
**Target**: Modular architecture with <500 lines per file

---

## Executive Summary

V6.0 addresses critical architectural issues identified in Vibecode.txt and current system limitations:

1. **Monolithic File**: 5,626 lines → Modular architecture
2. **Vibecode Compliance**: Address all 9 hidden problems
3. **Performance Bottlenecks**: Optimize startup, response time, memory
4. **Maintainability**: Clean architecture for faster development

---

## Current Problems

### Problem 1: Monolithic File (5,626 lines)

**Impact**:
- Hard to navigate
- Slow development
- Difficult debugging
- High cognitive load
- Merge conflicts

**Solution**: Modular architecture (see below)

### Problem 2: Vibecode Compliance Issues

**9 Hidden Problems from Vibecode.txt**:

1. ✅ **Prompt Assembly Drift** - Fixed (ModelClient sanitization)
2. ✅ **Implicit Context Bleed** - Fixed (context sanitization)
3. ❌ **Race Conditions** - Not addressed
4. ✅ **Prompt Shadowing/Overload** - Partially fixed (needs prompt budget)
5. ✅ **Mixing Internal Notes** - Fixed (sanitization)
6. ❌ **Memory Reinsertion Bugs** - Not fully addressed
7. ❌ **CSS/HTML Layer Injection** - Not addressed (webapp only)
8. ❌ **Mode Switching Without Reset** - Not addressed
9. ❌ **UI Echoing Old Output** - Not addressed (webapp only)

**Status**: 3/9 fully fixed, 1/9 partially fixed, 5/9 not addressed

### Problem 3: Performance Bottlenecks

**Startup Time**: 2-3 seconds
- Loading all modules at once
- No lazy loading for some components
- Heavy initialization

**Response Time**: 2-8 seconds
- Sequential processing
- No true parallelization
- Cache misses

**Memory Usage**: 300MB+
- All modules loaded
- No memory optimization
- Large state files

**Solution**: Lazy loading, parallelization, memory optimization

---

## V6.0 Architecture

### New Directory Structure

```
src/
├── __init__.py
│
├── core/                          # Core system
│   ├── __init__.py
│   ├── thesidia_core.py          # Main orchestrator (<300 lines)
│   ├── model_client.py           # ModelClient (moved from main)
│   ├── prompt_builder.py         # Prompt assembly (Vibecode compliant)
│   ├── context_manager.py        # Context management (prevents bleed)
│   └── mode_router.py            # Mode detection and routing
│
├── research/                      # Research capabilities
│   ├── __init__.py
│   ├── web_search.py             # WebSearchEngine (moved)
│   ├── deep_research.py          # DeepResearchEngine (moved)
│   ├── parallel_processor.py     # ParallelProcessor (moved)
│   └── research_coordinator.py   # Coordinates all research
│
├── memory/                        # Memory systems
│   ├── __init__.py
│   ├── sophia_memory.py          # Sophia memory wrapper
│   ├── user_memory.py            # UserMemoryManager (moved)
│   ├── knowledge_base.py         # KnowledgeBase (moved)
│   └── memory_reinsertion.py     # Vibecode-compliant reinsertion
│
├── synthesis/                     # Analysis & synthesis
│   ├── __init__.py
│   ├── data_synthesizer.py       # DataSynthesizer (moved)
│   ├── gnostic_blade.py          # Gnostic Blade mode
│   ├── skepticism_engine.py     # IntuitiveSkepticism (moved)
│   └── quality_filter.py         # DataQualityFilter (moved)
│
├── modes/                         # Specialized modes
│   ├── __init__.py
│   ├── csi_investigator.py       # CSIInvestigator (moved)
│   ├── health_coach.py           # HealthCoach (moved)
│   ├── scientific_simulator.py   # ScientificSimulator (moved)
│   ├── reporter_mode.py          # ReporterMode (moved)
│   ├── archaeologist_mode.py     # ArchaeologistMode (moved)
│   ├── psychologist_mode.py      # PsychologistMode (moved)
│   └── mode_registry.py          # Mode registration and selection
│
├── adaptive/                      # Adaptive systems
│   ├── __init__.py
│   ├── personality.py            # AdaptivePersonality (moved)
│   ├── learning.py               # AdaptiveLearning (moved)
│   ├── capabilities.py            # AdaptiveCapabilities (moved)
│   └── adaptation_coordinator.py # Coordinates adaptation
│
├── cosmos/                        # Cosmos framework
│   ├── __init__.py
│   ├── knowledge_base.py         # CosmosKnowledgeBase (moved)
│   ├── number_theory.py          # NumberTheoryEngine (moved)
│   ├── pattern_analyzer.py       # CosmosPatternAnalyzer (moved)
│   └── cosmos_coordinator.py     # Coordinates cosmos modules
│
├── linguistic/                    # Linguistic intelligence
│   ├── __init__.py
│   ├── etymology.py              # EtymologyLinguistic (moved)
│   ├── prose_synthesizer.py      # NaturalProseSynthesizer (moved)
│   └── symbolic_processor.py     # Symbolic processing
│
├── quality/                       # Quality & reliability
│   ├── __init__.py
│   ├── hallucination_tracker.py  # HallucinationTracker (moved)
│   ├── quality_metrics.py        # QualityMetricsTracker (moved)
│   ├── reasoning_analyzer.py     # ReasoningAnalyzer (moved)
│   └── quality_coordinator.py    # Coordinates quality systems
│
├── user/                          # User interaction
│   ├── __init__.py
│   ├── action_proposer.py        # ActionProposer (moved)
│   ├── information_builder.py    # InformationBuilder (moved)
│   ├── interest_tracker.py       # UserInterestTracker (moved)
│   ├── journey_detector.py       # TechnicalJourneyDetector (moved)
│   └── user_coordinator.py       # Coordinates user systems
│
├── output/                        # Output & formatting
│   ├── __init__.py
│   ├── response_generator.py     # Response generation
│   ├── postprocessor.py          # ResponsePostprocessor (moved)
│   ├── enhancements.py           # ResponseEnhancements (moved)
│   └── output_mode_manager.py    # Output mode management
│
├── performance/                   # Performance systems
│   ├── __init__.py
│   ├── metrics_collector.py      # MetricsCollector (moved)
│   ├── engineering_dashboard.py  # EngineeringDashboard (moved)
│   ├── cache_manager.py          # Centralized caching
│   └── performance_monitor.py   # Performance monitoring
│
├── state/                         # State management
│   ├── __init__.py
│   ├── state_manager.py          # State persistence
│   ├── async_saver.py            # Async state saving
│   └── state_validator.py        # State validation
│
├── support/                       # Support systems
│   ├── __init__.py
│   ├── ally_mechanics.py         # AllyMechanics (moved)
│   ├── aha_tracker.py            # AhaMomentTracker (moved)
│   ├── gentle_truth.py           # GentleTruthEngine (moved)
│   └── recursion_guard.py       # RecursionGuard (moved)
│
├── vibecode/                      # Vibecode compliance
│   ├── __init__.py
│   ├── prompt_sanitizer.py       # Prompt sanitization
│   ├── context_sanitizer.py      # Context sanitization
│   ├── memory_reinsertion.py     # Memory reinsertion protocol
│   ├── mode_reset.py             # Mode switching reset
│   ├── request_queue.py          # Request queue (race condition fix)
│   └── ui_sanitizer.py           # UI sanitization (webapp)
│
└── thesidia_hybrid_adaptive.py   # Main entry point (<200 lines)
```

**Target**: Each file <500 lines, most <300 lines

---

## Phase 1: Vibecode Compliance (Weeks 1-2)

### 1.1 Request Queue System (Race Condition Fix)

**Problem**: UI sends multiple requests in parallel, backend processes out of order

**Solution**:
```python
# src/vibecode/request_queue.py
class RequestQueue:
    def __init__(self):
        self.queue = Queue()
        self.processing = False
        self.request_ids = {}
    
    async def enqueue(self, request_id: str, request: dict):
        """Add request to queue with ID"""
        self.queue.put((request_id, request))
        await self._process_queue()
    
    async def _process_queue(self):
        """Process queue sequentially"""
        if self.processing:
            return
        self.processing = True
        while not self.queue.empty():
            request_id, request = self.queue.get()
            await self._process_request(request_id, request)
        self.processing = False
```

**Integration**: Add to `ThesidiaCore.process()` method

### 1.2 Prompt Budget System (Prompt Shadowing Fix)

**Problem**: Too many things in prompt → token competition → unreliable behavior

**Solution**:
```python
# src/core/prompt_builder.py
class PromptBuilder:
    PROMPT_BUDGET = {
        "system": 2000,      # System instructions
        "context": 1000,     # Context/memory
        "research": 1500,    # Research data
        "user": 500,         # User query
        "total": 5000        # Total budget
    }
    
    def build_prompt(self, components: dict) -> str:
        """Build prompt within budget"""
        # Prioritize: system > user > context > research
        # Truncate if over budget
        # Use embeddings for context if too large
```

**Integration**: Replace all prompt building with `PromptBuilder`

### 1.3 Memory Reinsertion Protocol

**Problem**: Memory reinserted wrong → personality drift, wrong memories

**Solution**:
```python
# src/vibecode/memory_reinsertion.py
class MemoryReinsertionProtocol:
    RULES = {
        "role": "user",           # ALWAYS user role, never system
        "position": "after_system_before_user",  # After system, before user
        "max_items": 2,          # Max 2 memory items
        "max_length": 500,       # Max 500 chars per item
        "format": "extract",      # Small extracts, not full text
        "relevance": 0.7          # Min relevance score
    }
    
    def reinsert_memory(self, memory_items: list, system_prompt: str, user_query: str) -> list:
        """Reinsert memory following protocol"""
        # Filter by relevance
        # Truncate to max_length
        # Insert in correct position
        # Use user role
```

**Integration**: Replace all memory reinsertion with protocol

### 1.4 Mode Switching Reset

**Problem**: Mode switching without prompt reset → instructions leak between modes

**Solution**:
```python
# src/vibecode/mode_reset.py
class ModeResetProtocol:
    def reset_for_mode(self, mode: str, previous_mode: str = None):
        """Reset prompt and context for mode switch"""
        # Clear contextual variables
        # Rebuild prompt from scratch
        # Reset mode-specific state
        # Never reuse previous prompt
```

**Integration**: Add to mode switching logic

### 1.5 UI Sanitization (Webapp)

**Problem**: CSS/HTML leaks into prompt, UI echoes old output

**Solution**:
```python
# src/vibecode/ui_sanitizer.py
class UISanitizer:
    def sanitize_input(self, text: str) -> str:
        """Remove HTML, CSS, UI artifacts"""
        # Remove HTML tags
        # Remove CSS classes
        # Remove React fragments
        # Remove button labels
        # Remove debug IDs
        # Keep only raw text
    
    def sanitize_output(self, text: str) -> str:
        """Prevent UI from echoing old output"""
        # Don't reinsert assistant messages
        # Keep only user messages
        # Keep only last 2-3 turns
```

**Integration**: Add to webapp API endpoints

---

## Phase 2: Modular Architecture (Weeks 3-5)

### 2.1 Extract Core Classes

**Step 1**: Extract `ModelClient` to `src/core/model_client.py`
- Move lines 192-368
- Update imports
- Test isolation

**Step 2**: Extract `WebSearchEngine` to `src/research/web_search.py`
- Move lines 1167-1450
- Update imports
- Test isolation

**Step 3**: Extract `DataSynthesizer` to `src/synthesis/data_synthesizer.py`
- Move lines 1483-1834
- Update imports
- Test isolation

**Step 4**: Extract `AdaptivePersonality` to `src/adaptive/personality.py`
- Move lines 369-610
- Update imports
- Test isolation

**Step 5**: Extract specialized modes to `src/modes/`
- Move all mode classes
- Create `ModeRegistry`
- Test mode switching

### 2.2 Create Main Orchestrator

**File**: `src/core/thesidia_core.py`

```python
class ThesidiaCore:
    """Main orchestrator - coordinates all subsystems"""
    
    def __init__(self, model: str = "clean-mistral:latest"):
        # Initialize subsystems (lazy loading)
        self.model_client = ModelClient(model)
        self.prompt_builder = PromptBuilder()
        self.context_manager = ContextManager()
        self.mode_router = ModeRouter()
        # ... other subsystems
    
    def process(self, query: str, operator_name: str = "OPERATOR"):
        """Main processing pipeline"""
        # 1. Sanitize input (Vibecode)
        # 2. Detect mode
        # 3. Build prompt (within budget)
        # 4. Route to appropriate handler
        # 5. Generate response
        # 6. Postprocess
        # 7. Update memory
        # 8. Return response
```

**Target**: <300 lines

### 2.3 Create Facade

**File**: `src/thesidia_hybrid_adaptive.py` (new, simplified)

```python
"""Thesidia Hybrid Adaptive - Main Entry Point"""

from .core.thesidia_core import ThesidiaCore

class ThesidiaHybridAdaptive(ThesidiaCore):
    """Backward-compatible facade"""
    pass

# For backward compatibility
__all__ = ['ThesidiaHybridAdaptive']
```

**Target**: <200 lines

---

## Phase 3: Performance Optimization (Weeks 6-7)

### 3.1 Lazy Loading

**Problem**: All modules loaded at startup → slow startup

**Solution**:
```python
# src/core/thesidia_core.py
class ThesidiaCore:
    def __init__(self):
        self._web_search = None
        self._deep_research = None
        # ... other lazy-loaded components
    
    @property
    def web_search(self):
        if self._web_search is None:
            from .research.web_search import WebSearchEngine
            self._web_search = WebSearchEngine(self.model)
        return self._web_search
```

**Impact**: Startup time: 2-3s → 0.5-1s

### 3.2 Parallel Processing

**Problem**: Sequential processing → slow response

**Solution**:
```python
# src/research/research_coordinator.py
class ResearchCoordinator:
    async def research_parallel(self, query: str):
        """Parallel research execution"""
        # Web search + LLM thinking in parallel
        # Multiple source scraping in parallel
        # Synthesis after all complete
```

**Impact**: Response time: 2-8s → 1-4s

### 3.3 Advanced Caching

**Problem**: Cache misses → redundant work

**Solution**:
```python
# src/performance/cache_manager.py
class CacheManager:
    def __init__(self):
        self.semantic_cache = SemanticCache()  # Similar queries reuse results
        self.query_cache = QueryCache()        # Exact query cache
        self.synthesis_cache = SynthesisCache() # Synthesis results
    
    def get_cached(self, query: str) -> Optional[str]:
        """Get cached result if available"""
        # Try exact match first
        # Try semantic match
        # Return None if miss
```

**Impact**: Cache hit rate: 20% → 60%+

### 3.4 Memory Optimization

**Problem**: Large state files → slow save/load

**Solution**:
```python
# src/state/state_manager.py
class StateManager:
    def save_state(self, state: dict):
        """Optimized state saving"""
        # Compress large data
        # Incremental updates
        # Async background save
        # Only save changed components
```

**Impact**: Save time: 1-2s → 0.1-0.3s

---

## Phase 4: Testing & Validation (Week 8)

### 4.1 Unit Tests

**Coverage**:
- Each module in isolation
- Vibecode compliance
- Performance benchmarks
- Memory management

### 4.2 Integration Tests

**Coverage**:
- End-to-end queries
- Mode switching
- Memory persistence
- Research workflows

### 4.3 Performance Tests

**Metrics**:
- Startup time: <1s
- Response time: <4s (with research)
- Memory usage: <200MB
- Cache hit rate: >60%

---

## Migration Plan

### Step 1: Create New Structure

```bash
# Create new directories
mkdir -p src/{core,research,memory,synthesis,modes,adaptive,cosmos,linguistic,quality,user,output,performance,state,support,vibecode}

# Create __init__.py files
touch src/{core,research,memory,synthesis,modes,adaptive,cosmos,linguistic,quality,user,output,performance,state,support,vibecode}/__init__.py
```

### Step 2: Extract Classes (One at a Time)

1. Extract `ModelClient` → test → commit
2. Extract `WebSearchEngine` → test → commit
3. Extract `DataSynthesizer` → test → commit
4. ... continue for all classes

### Step 3: Update Imports

```python
# Old
from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

# New (backward compatible)
from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
# Still works, but now uses modular architecture
```

### Step 4: Add Vibecode Compliance

1. Add request queue
2. Add prompt budget
3. Add memory reinsertion protocol
4. Add mode reset
5. Add UI sanitization

### Step 5: Performance Optimization

1. Add lazy loading
2. Add parallel processing
3. Add advanced caching
4. Add memory optimization

---

## Success Metrics

### Architecture

- ✅ File size: <500 lines per file (most <300)
- ✅ Module count: 50+ files (vs 1 monolithic)
- ✅ Import depth: <3 levels
- ✅ Test coverage: >80%

### Vibecode Compliance

- ✅ All 9 problems addressed
- ✅ Prompt budget enforced
- ✅ Memory reinsertion protocol followed
- ✅ Mode reset on switch
- ✅ Request queue prevents race conditions
- ✅ UI sanitization prevents injection

### Performance

- ✅ Startup time: <1s (from 2-3s)
- ✅ Response time: <4s (from 2-8s)
- ✅ Memory usage: <200MB (from 300MB+)
- ✅ Cache hit rate: >60% (from 20%)

### Maintainability

- ✅ Easy to navigate
- ✅ Easy to test
- ✅ Easy to extend
- ✅ Easy to debug

---

## Risk Mitigation

### Risk 1: Breaking Existing Functionality

**Mitigation**:
- Incremental extraction (one class at a time)
- Comprehensive testing after each extraction
- Backward-compatible facade
- Feature flags for new code

### Risk 2: Performance Regression

**Mitigation**:
- Benchmark before/after
- Performance tests in CI
- Rollback plan
- Gradual rollout

### Risk 3: Complexity Increase

**Mitigation**:
- Clear module boundaries
- Comprehensive documentation
- Code reviews
- Architecture diagrams

### Risk 4: Migration Time

**Mitigation**:
- Phased approach (8 weeks)
- Parallel development (old + new)
- Gradual migration
- Backward compatibility

---

## Timeline

### Week 1-2: Vibecode Compliance
- Request queue
- Prompt budget
- Memory reinsertion protocol
- Mode reset
- UI sanitization

### Week 3-5: Modular Architecture
- Extract core classes
- Create orchestrator
- Create facade
- Update imports

### Week 6-7: Performance Optimization
- Lazy loading
- Parallel processing
- Advanced caching
- Memory optimization

### Week 8: Testing & Validation
- Unit tests
- Integration tests
- Performance tests
- Documentation

**Total**: 8 weeks

---

## Next Steps

1. **Review and approve plan**
2. **Set up development branch** (`v6-development`)
3. **Create new directory structure**
4. **Begin Phase 1** (Vibecode compliance)
5. **Set up CI/CD** (automated testing)
6. **Begin incremental migration**

---

## Conclusion

V6.0 transforms Thesidia from a monolithic 5,626-line file into a **modular, performant, Vibecode-compliant architecture**:

- **Modular**: 50+ focused files (<500 lines each)
- **Compliant**: All 9 Vibecode problems addressed
- **Performant**: 2-3x faster startup, 2x faster responses
- **Maintainable**: Easy to navigate, test, extend, debug

**Result**: A system that's faster, more reliable, and easier to develop.

---

**Last Updated**: 2025-01-XX  
**Document Version**: 1.0

