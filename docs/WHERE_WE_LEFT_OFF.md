# Where We Left Off - V2.0 Planning Session

**Date**: 2025-01-XX  
**Status**: Planning Complete, Ready for Implementation

---

## Current State

### Completed (V1.0)
- ✅ Core Thesidia system with gnostic blade
- ✅ Two-mode system (Regular/Narrative)
- ✅ Sophia memory system (7-layer gnostic map)
- ✅ Nuclear web search
- ✅ Model router optimization
- ✅ Server caching and lazy-loading optimizations
- ✅ UX improvements (streaming, thinking indicators, spacing)

### In Progress
- 🔄 V2.0 Roadmap planning
- 🔄 Modelfile system design (complete, ready for integration)

### Next Steps (V2.0 Phase 0)

**Priority 1: Modular Architecture Refactoring**
- Split `src/thesidia_hybrid_adaptive.py` (4,196 lines) into clean modules
- Create `src/core/`, `src/reasoning/`, `src/knowledge/`, `src/tools/` directories
- Extract research engine, synthesis engine, memory system, personality system

**Priority 2: Modelfile System Integration**
- Create `src/thesidia_modelfile.py` with complete modelfile dictionaries
- Create `src/core/personality_system.py` wrapper class
- Integrate into `src/core/thesidia_core.py` to replace hardcoded base_prompt

---

## Key Decisions Made

### Hardware Optimization
- **Target**: Apple Silicon (M1/M4) with Neural Engine
- **Batch Size**: 2 (not 4) for beam search due to unified memory limits
- **Framework**: MLX for efficient batch processing on unified memory
- **Strategy**: Single model instance, multiple prompts (not multiple instances)

### Architecture Strategy
- **Order**: Refactoring FIRST (Phase 0), then features (Phase 1+)
- **Rationale**: M1 allows fast iteration, but only if code is navigable
- **Risk Mitigation**: Clean modules prevent debugging nightmares when adding complex features

### Modelfile System
- **Structure**: 3 layers (Voice + Preset + Persona)
- **Voices**: 14 personalities (thesidia, sophia, luna, seraphina, iris, aurora, celeste, sage, nova, lyra, athena, cassandra, diana, artemis)
- **Presets**: 3 cognitive styles (concise, formal, socratic)
- **Personas**: 9 role specializations (news, romance, friend, tutor, doctor, unhinged, therapist, scientist, coder)
- **Integration**: Replace hardcoded base_prompt with dynamic modelfile assembly

---

## Files Ready for Implementation

### New Files to Create
1. `src/thesidia_modelfile.py` - Complete modelfile dictionaries and ThesidiaSystem class
2. `src/core/__init__.py` - Core module init
3. `src/core/thesidia_core.py` - Core ThesidiaHybridAdaptive class
4. `src/core/research_engine.py` - Web search & research coordination
5. `src/core/synthesis_engine.py` - Response synthesis
6. `src/core/memory_system.py` - State & history management
7. `src/core/personality_system.py` - Personality/voice/persona system wrapper
8. `src/reasoning/__init__.py` - Reasoning module init
9. `src/reasoning/tree_of_thoughts.py` - TreeOfThoughts (move from streaming_processor)
10. `src/reasoning/beam_search.py` - MLX-based ParallelBeamSearch
11. `src/reasoning/reasoning_analyzer.py` - Enhanced reasoning analyzer
12. `src/knowledge/__init__.py` - Knowledge module init
13. `src/knowledge/vector_db.py` - SemanticVectorDB
14. `src/knowledge/cache_manager.py` - Advanced caching
15. `src/tools/__init__.py` - Tools module init
16. `src/tools/tool_registry.py` - ToolRegistry
17. `src/tools/tool_selector.py` - ToolSelector

### Files to Modify
1. `src/thesidia_hybrid_adaptive.py` - Simplify to facade pattern, import from modules
2. `src/streaming_processor.py` - Move TreeOfThoughts to `src/reasoning/tree_of_thoughts.py`
3. `requirements.txt` - Add `mlx-lm`, `chromadb`, `sentence-transformers`

---

## Implementation Order

### Week 1-2: Phase 0 (Modular Architecture + Modelfile)
1. Create directory structure (`core/`, `reasoning/`, `knowledge/`, `tools/`)
2. Extract research engine → `core/research_engine.py`
3. Extract synthesis engine → `core/synthesis_engine.py`
4. Extract memory system → `core/memory_system.py`
5. Create modelfile system → `thesidia_modelfile.py`
6. Create personality system → `core/personality_system.py`
7. Refactor main file → `thesidia_hybrid_adaptive.py` (facade)
8. Test: Verify all existing functionality works

### Week 3-6: Phase 1 (Advanced Reasoning)
1. Integrate Tree of Thoughts
2. Implement MLX-based beam search (batch=2)
3. Enhance reasoning analyzer

### Week 7-10: Phase 2 (Semantic Vector DB)
1. Set up ChromaDB infrastructure
2. Integrate semantic search
3. Implement hybrid search (semantic + keyword)

### Week 11-14: Phase 3 (Function Calling / Tools)
1. Implement tool registry
2. Implement tool selector
3. Integrate tools into main pipeline

### Week 15-16: Phase 4 (Optimization & Polish)
1. Performance monitoring
2. Error recovery & resilience
3. Final testing & validation

---

## Success Criteria

### Quality Metrics
- Reasoning quality: 30-40% improvement (Tree of Thoughts)
- Response quality: 40-50% improvement (Beam Search)
- Hallucination rate: <2% (Enhanced Analyzer)
- Source accuracy: >95% (Vector DB + Analyzer)

### Performance Metrics
- Response time: <15s average (Vector DB caching)
- Simple queries: <2s (Vector DB + caching)
- Cache hit rate: >40% (Vector DB)

### Architecture Metrics
- Main file: <500 lines (down from 4,196)
- Modular structure: Clear separation of concerns
- Test coverage: >80% for new modules

---

## Risks & Mitigations

**Risk 1**: Breaking existing functionality during refactoring  
**Mitigation**: Incremental refactoring, comprehensive testing, feature flags

**Risk 2**: Performance regression  
**Mitigation**: Benchmark before/after, performance monitoring, rollback plan

**Risk 3**: Complexity increase  
**Mitigation**: Clear module boundaries, documentation, code reviews

**Risk 4**: M1 memory limits  
**Mitigation**: Batch size 2 (not 4), MLX unified memory optimization, monitor RAM usage

---

## Dependencies to Add

```txt
mlx-lm>=0.0.1          # Apple Silicon MLX framework
chromadb>=0.4.0        # Vector database
sentence-transformers>=2.2.0  # Embeddings
```

---

## Notes

- Modelfile system is complete and ready for integration
- M1 optimization strategy is defined (MLX, batch=2, unified memory)
- Refactoring must happen FIRST before adding new features
- All existing functionality must be preserved during refactoring

---

**Next Session**: Begin Phase 0 implementation (modular architecture refactoring)

