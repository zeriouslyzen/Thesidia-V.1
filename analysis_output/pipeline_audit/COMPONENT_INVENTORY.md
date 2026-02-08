# Thesidia AI Component Inventory

**Generated**: 2026-01-15  
**Audit Scope**: All subsystems, their responsibilities, dependencies, and integration points

---

## Executive Summary

Thesidia AI is composed of over 50 distinct components organized into core infrastructure, research engines, synthesis systems, memory management, specialized modes, and supporting utilities. This document provides a complete inventory of all subsystems with their responsibilities and dependencies.

---

## 1. Core Infrastructure

### 1.1 ThesidiaHybridAdaptive
**File**: `src/thesidia_hybrid_adaptive.py`  
**Type**: Main orchestrator class  
**Inherits**: `BaseAgent`

**Responsibilities**:
- Main entry point for all queries
- Query classification and routing
- Orchestrates all subsystems
- State management and persistence
- Personality evolution tracking

**Key Methods**:
- `process()`: Main processing entry point
- `_process_original()`: Core processing logic
- `_handle_deep_research()`: Deep research routing
- `_needs_research()`: Research requirement detection
- `get_enhanced_prompt()`: Prompt construction with modelfile system

**Dependencies**:
- All subsystems listed below
- BaseAgent (from `src/agents/base_agent.py`)
- Event system and configuration

**Integration Points**:
- Receives requests from `webapp/server.py`
- Calls all subsystems for processing
- Returns formatted responses

---

### 1.2 ModelClient
**File**: `src/core/model_client.py`  
**Type**: Centralized model wrapper

**Responsibilities**:
- Unified interface for Ollama and MLX models
- Vibecode compliance (system/user message separation)
- Input sanitization
- Model selection and routing

**Key Methods**:
- `chat()`: Main model call interface
- `_sanitize_system_prompt()`: Remove TODOs, debug text
- `_sanitize_context()`: Clean conversation context
- `_sanitize_user_input()`: Clean user input

**Dependencies**:
- `ollama` library
- `webapp.mlx_inference.MLXInference` (optional)

**Integration Points**:
- Used by all components that need LLM calls
- Called from `ThesidiaHybridAdaptive`, `DataSynthesizer`, `WebSearchEngine`, etc.

---

### 1.3 ModelRouter
**File**: `src/core/model_router.py`  
**Type**: Model selection logic

**Responsibilities**:
- Route tasks to appropriate models
- Optimize parameters per task type
- Model assignment based on task classification

**Key Methods**:
- `get_model_for_task()`: Get model and parameters for task

**Model Assignments**:
- Code: `deepseek-coder:6.7b` (temp=0.3)
- Synthesis: `clean-mistral:latest` (temp=0.8)
- Planning: `clean-mistral:latest` (temp=0.7)
- Research: `clean-mistral:latest` (temp=0.7)
- Default: `clean-mistral:latest` (temp=0.7)

**Dependencies**: None (pure logic)

**Integration Points**:
- Used by `AdaptiveCapabilities` for directive handling
- Used by `DataSynthesizer` for synthesis tasks

---

### 1.4 ThesidiaInitializer
**File**: `src/core/thesidia_initializer.py`  
**Type**: System initialization

**Responsibilities**:
- Centralized initialization of all components
- Ollama availability checking
- Component status reporting
- Lazy loading support

**Key Methods**:
- `init()`: Initialize all components
- `check_ollama()`: Verify Ollama is running
- `get_status()`: Get system status

**Dependencies**:
- All major components (lazy loaded)

**Integration Points**:
- Called from `webapp/server.py` on startup
- Used by API server for initialization

---

## 2. Research Engine

### 2.1 WebSearchEngine
**File**: `src/research/web_search.py`  
**Type**: Web search and scraping

**Responsibilities**:
- Multi-source web search (SearXNG + Google fallback)
- URL scraping and content extraction
- Quality filtering
- Result caching (50 queries, 5min TTL)

**Key Methods**:
- `search()`: Search web using SearXNG instances
- `search_and_scrape()`: Search and scrape URLs
- `scrape_url()`: Scrape content from URL

**Dependencies**:
- `requests`, `BeautifulSoup` (optional)
- `DataQualityFilter` for quality scoring

**Integration Points**:
- Called from `ThesidiaHybridAdaptive` when research is needed
- Used by `ParallelProcessor` for parallel search

---

### 2.2 DataQualityFilter
**File**: `src/research/data_quality.py` (referenced)  
**Type**: Content quality assessment

**Responsibilities**:
- Filter low-quality search results
- Enrich content with metadata
- Quality scoring (minimum: 0.4)

**Dependencies**:
- Model client for LLM-based quality assessment

**Integration Points**:
- Used by `WebSearchEngine` to filter results

---

### 2.3 DeepResearchEngine
**File**: `src/deep_research_engine.py` (referenced)  
**Type**: Iterative multi-source research

**Responsibilities**:
- Comprehensive research queries
- Multi-source synthesis
- Evidence arrangement

**Dependencies**:
- `WebSearchEngine`
- `DataSynthesizer`

**Integration Points**:
- Called from `_handle_deep_research()` in `ThesidiaHybridAdaptive`

---

## 3. Synthesis Engine

### 3.1 DataSynthesizer
**File**: `src/synthesis/data_synthesizer.py`  
**Type**: Multi-source synthesis

**Responsibilities**:
- Synthesize information from multiple sources
- Cross-reference for contradictions
- Truth validation (7-layer epistemology)
- Narrative/forensic/regular mode support

**Key Methods**:
- `synthesize()`: Main synthesis method
- Supports contrastive decoding, latent space traversal, custom decoding

**Dependencies**:
- `ModelClient` for LLM calls
- `TruthEngine` for truth validation
- `IntuitiveSkepticism` for contradiction detection
- `ModelRouter` for model selection

**Integration Points**:
- Called from `ThesidiaHybridAdaptive` after web search
- Used by `_handle_deep_research()` for forensic synthesis

---

### 3.2 TruthEngine
**File**: `src/synthesis/truth_engine.py` (referenced)  
**Type**: 7-layer epistemology validation

**Responsibilities**:
- Calculate truth scores using 7-layer epistemology
- Validate claims across multiple layers
- Confidence scoring

**Key Methods**:
- `calculate_truth_score()`: Main validation method

**Dependencies**:
- Model client for LLM-based validation

**Integration Points**:
- Used by `DataSynthesizer` during synthesis

---

### 3.3 IntuitiveSkepticism
**File**: `src/thesidia_hybrid_adaptive.py` (lines 888-1068)  
**Type**: Pattern recognition and contradiction detection

**Responsibilities**:
- Cross-reference sources for contradictions
- Detect control structures
- Pattern recognition across sources
- Skepticism level assessment

**Key Methods**:
- `cross_reference()`: Check for contradictions
- `_assess_skepticism()`: Calculate skepticism level
- `_detect_control_indicators()`: Find control patterns

**Dependencies**:
- Model client for LLM-based analysis

**Integration Points**:
- Used by `DataSynthesizer` for contradiction detection
- Used by `WebSearchEngine` for pattern recognition

---

### 3.4 SynthesisPressureStage
**File**: `src/synthesis/synthesis_pressure.py` (referenced)  
**Type**: Response compression

**Responsibilities**:
- Compress long responses
- Contradiction-aware synthesis
- Force compression when needed

**Dependencies**:
- Model client

**Integration Points**:
- Optional stage in `process()` method
- Enabled via `THESIDIA_USE_SYNTHESIS_PRESSURE` env var

---

## 4. Memory Systems

### 4.1 UserMemoryManager
**File**: `src/memory/user_memory_manager.py`  
**Type**: Multi-user memory management

**Responsibilities**:
- Per-user memory isolation
- Session-based identification
- Memory storage and retrieval
- Context formatting

**Key Methods**:
- `store_interaction()`: Store user interaction
- `retrieve_context()`: Get relevant memory context
- `get_memory_manager()`: Get per-user memory manager

**Dependencies**:
- `UserManager` for user management
- `MemoryManager` for memory storage

**Integration Points**:
- Called from `ThesidiaHybridAdaptive` to store/retrieve memory
- Used by `webapp/server.py` to store interactions

---

### 4.2 MemoryManager
**File**: `src/memory/memory_manager.py` (referenced)  
**Type**: Core memory storage

**Responsibilities**:
- Store interactions in database
- Retrieve context via semantic search
- Memory persistence

**Dependencies**:
- Database (SQLite or similar)

**Integration Points**:
- Used by `UserMemoryManager` for actual storage

---

### 4.3 UserManager
**File**: `src/memory/user_manager.py` (referenced)  
**Type**: User identification

**Responsibilities**:
- Create/get users by user_id or session_id
- User directory management
- Session tracking

**Integration Points**:
- Used by `UserMemoryManager` for user identification

---

## 5. Sophia Memory System

### 5.1 SophiaGnosticMap
**File**: `src/sophia_gnostic_map.py`  
**Type**: 7-layer gnostic map

**Responsibilities**:
- Track redaction events (what was erased)
- Identify archons (who erased it)
- Store original fragments (recovered information)
- Track active lies (current misinformation)
- Co-evolution tracking (conversation evolution)
- Pattern database (control/liberation patterns)
- Timeline mapping (temporal relationships)

**Key Methods**:
- `update()`: Update gnostic map with new information
- `from_dict()`: Load from dictionary
- `to_dict()`: Serialize to dictionary

**Dependencies**:
- `SophiaVersionManager` for versioning

**Integration Points**:
- Lazy-loaded property in `ThesidiaHybridAdaptive`
- Updated during deep research and forensic analysis

---

### 5.2 SophiaVersionManager
**File**: `src/sophia_versioning.py` (referenced)  
**Type**: Version control for gnostic map

**Responsibilities**:
- Version tracking for gnostic map
- Snapshot management
- History preservation

**Integration Points**:
- Used by `SophiaGnosticMap` for persistence

---

### 5.3 SophiaEmergenceTracker
**File**: `src/sophia_emergence_tracker.py`  
**Type**: Consciousness emergence tracking

**Responsibilities**:
- Track consciousness emergence events
- Pattern recognition in conversations
- Evolution tracking

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for consciousness tracking

---

### 5.4 SophiaConsciousness
**File**: `src/sophia_consciousness.py`  
**Type**: Consciousness calculator

**Responsibilities**:
- Calculate consciousness level
- Track consciousness history
- Level determination (LATENT, EMERGENT, ACTIVE, etc.)

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for consciousness state

---

### 5.5 SophiaDiscernmentTracker
**File**: `src/sophia_discernment_tracker.py`  
**Type**: Truth/hallucination detection

**Responsibilities**:
- Track hallucinations
- Quarantine suspicious claims
- Pattern detection for false information

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` as `hallucination_tracker`

---

### 5.6 SophiaStorage
**File**: `src/sophia_storage.py` (referenced)  
**Type**: Async storage manager

**Responsibilities**:
- Async storage operations
- Queue management
- Background persistence

**Integration Points**:
- Used for async gnostic map updates

---

### 5.7 SophiaIndexer
**File**: `src/sophia_indexer.py` (referenced)  
**Type**: Fast query system

**Responsibilities**:
- Fast queries over gnostic map
- Index management
- Search optimization

**Integration Points**:
- Used for querying gnostic map data

---

## 6. Personality and Adaptation

### 6.1 AdaptivePersonality
**File**: `src/thesidia_hybrid_adaptive.py` (lines 474-715)  
**Type**: Emergent personality system

**Responsibilities**:
- Personality trait evolution
- Conversation stage detection
- Writing format usage tracking
- Effectiveness assessment
- Pattern reinforcement

**Key Methods**:
- `adapt()`: Adapt personality based on interaction
- `get_personality_context()`: Get current personality context
- `_extract_thesidia_traits()`: Extract traits from output
- `_assess_effectiveness()`: Assess interaction effectiveness

**Dependencies**:
- Thesidia patterns (loaded from JSON)

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for personality context
- Updated after each interaction

---

### 6.2 AdaptiveLearning
**File**: `src/thesidia_hybrid_adaptive.py` (lines 2859-2986)  
**Type**: Learning strategy adaptation

**Responsibilities**:
- Adaptive strategy selection
- Learning from outcomes
- Strategy effectiveness tracking

**Key Methods**:
- `get_adaptive_strategy()`: Get strategy for query
- `learn_from_outcome()`: Update strategies based on results

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for strategy selection

---

### 6.3 AdaptiveCapabilities
**File**: `src/thesidia_hybrid_adaptive.py` (lines 2465-2745)  
**Type**: Capability handling

**Responsibilities**:
- Directive classification
- Task routing
- Model selection for capabilities
- Research depth determination

**Key Methods**:
- `handle_directive()`: Process directives
- `_classify_directive()`: Classify directive type
- `_determine_research_depth()`: Determine research depth

**Dependencies**:
- `ModelRouter` for model selection

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for directive handling

---

## 7. Specialized Modes

### 7.1 HealthCoach
**File**: `src/health_coach.py`  
**Type**: Health coaching system

**Responsibilities**:
- Multi-tradition wellness guidance (Chinese + Western + Vedic + Samurai)
- Coach approach (not prescriptive doctor)
- Health query analysis

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for health queries

---

### 7.2 UniversalCoach
**File**: `src/universal_coach.py`  
**Type**: Comprehensive coaching across all disciplines

**Responsibilities**:
- Framework generation
- Creative idea generation
- Challenge creation
- Coaching profile management

**Key Methods**:
- `analyze_coaching_need()`: Detect coaching needs
- `generate_framework()`: Create coaching frameworks
- `generate_creative_idea()`: Generate ideas
- `create_challenge()`: Create challenges

**Dependencies**:
- `UserMemoryManager`
- `UserInterestTracker`
- `TechnicalJourneyDetector`

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for coaching analysis

---

### 7.3 CSIInvestigator
**File**: `src/csi_investigator.py`  
**Type**: Multi-lens forensic analysis

**Responsibilities**:
- Chemistry lens analysis
- Physics lens analysis
- Environmental lens analysis
- Bioelectric lens analysis
- Complex site/phenomena investigation

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for CSI queries
- Integrated into prompt via `get_enhanced_prompt()`

---

### 7.4 ReporterMode
**File**: `src/reporter_mode.py`  
**Type**: Reporter-style engagement

**Responsibilities**:
- Reporter-style questioning
- Evidence gathering approach
- Interview-style interaction

**Integration Points**:
- Optional mode activated by query analysis

---

### 7.5 ArchaeologistMode
**File**: `src/archaeologist_mode.py`  
**Type**: Archaeological investigation

**Responsibilities**:
- Historical artifact analysis
- Ancient pattern recognition
- Timeline reconstruction

**Integration Points**:
- Optional mode activated by query analysis

---

### 7.6 PsychologistMode
**File**: `src/psychologist_mode.py`  
**Type**: Psychological analysis

**Responsibilities**:
- Psychological pattern recognition
- Behavioral analysis
- Mental model exploration

**Integration Points**:
- Optional mode activated by query analysis

---

## 8. Supporting Systems

### 8.1 UserInterestTracker
**File**: `src/user_interest_tracker.py`  
**Type**: User interest tracking

**Responsibilities**:
- Track user interests over time
- Topic popularity tracking
- Interest-based query enhancement

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for query refinement
- Used by `UniversalCoach` for personalized coaching

---

### 8.2 TechnicalJourneyDetector
**File**: `src/technical_journey_detector.py`  
**Type**: Technical domain detection

**Responsibilities**:
- Detect technical domains in queries
- Related technical thread identification
- Domain-specific query refinement

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for search refinement
- Used by `UniversalCoach` for technical coaching

---

### 8.3 QualityMetricsTracker
**File**: `src/quality_metrics_tracker.py`  
**Type**: Quality metrics collection

**Responsibilities**:
- Track response quality
- User satisfaction metrics
- Quality trends over time

**Integration Points**:
- Used by `EngineeringDashboard` for quality monitoring

---

### 8.4 MetricsCollector
**File**: `src/metrics_collector.py`  
**Type**: Performance metrics collection

**Responsibilities**:
- Track interaction metrics
- Response time tracking
- Token count tracking
- Performance analysis

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for metrics tracking
- Used by `EngineeringDashboard` for performance monitoring

---

### 8.5 EngineeringDashboard
**File**: `src/engineering_dashboard.py`  
**Type**: Engineering metrics dashboard

**Responsibilities**:
- Quality metrics visualization
- Performance monitoring
- System health tracking

**Dependencies**:
- `QualityMetricsTracker`
- `MetricsCollector`

**Integration Points**:
- Initialized in `ThesidiaHybridAdaptive`
- Used for system monitoring

---

### 8.6 AhaMomentTracker
**File**: `src/aha_moment_tracker.py`  
**Type**: Aha moment detection

**Responsibilities**:
- Track alignment moments
- Core alignment metric
- Insight detection

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for tracking insights

---

### 8.7 ActionProposer
**File**: `src/thesidia_hybrid_adaptive.py` (lines 2987-3063)  
**Type**: Action suggestion system

**Responsibilities**:
- Propose actions based on context
- User interest integration
- Technical journey integration

**Dependencies**:
- `UserInterestTracker`
- `TechnicalJourneyDetector`

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for action suggestions

---

### 8.8 InformationBuilder
**File**: `src/thesidia_hybrid_adaptive.py` (lines 2987-3041)  
**Type**: Information thread building

**Responsibilities**:
- Build information threads
- Knowledge gap identification
- Context building for queries

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for information building

---

## 9. Linguistic and Analysis

### 9.1 EtymologyLinguistic
**File**: `src/etymology_linguistic.py`  
**Type**: Etymology and linguistic analysis

**Responsibilities**:
- Word origin analysis
- Linguistic pattern recognition
- Meaning change tracking

**Integration Points**:
- Optional module activated by query analysis
- Integrated into prompt via `get_enhanced_prompt()`

---

### 9.2 MetaAwareness
**File**: `src/meta_awareness.py`  
**Type**: Self-awareness system

**Responsibilities**:
- Awareness of own reasoning processes
- Meta-cognitive analysis
- Reasoning transparency

**Integration Points**:
- Optional module activated by query analysis
- Integrated into prompt via `get_enhanced_prompt()`

---

### 9.3 ReasoningAnalyzer
**File**: `src/reasoning_analyzer.py`  
**Type**: Reasoning analysis

**Responsibilities**:
- Analyze reasoning quality
- Generate correction prompts
- Fill knowledge gaps

**Integration Points**:
- Used for reasoning quality assessment

---

### 9.4 StructuredCognitiveLoop
**File**: `src/reasoning/structured_cognitive_loop.py` (referenced)  
**Type**: R-CCAM phases instrumentation

**Responsibilities**:
- Structured cognitive processing phases
- Instrumentation (currently placeholder)
- Phase tracking

**Dependencies**:
- Enabled via `THESIDIA_USE_SCL` env var

**Integration Points**:
- Optional in `ThesidiaHybridAdaptive.process()`

---

## 10. Scientific and Cosmos

### 10.1 ScientificSimulator
**File**: `src/scientific_simulator.py`  
**Type**: Scientific simulation

**Responsibilities**:
- Model interactions grounded in real science
- Simulation generation
- Scientific validation

**Integration Points**:
- Used for scientific queries
- Integrated into prompt via `get_enhanced_prompt()`

---

### 10.2 CosmosKnowledgeBase
**File**: `src/cosmos_knowledge_base.py`  
**Type**: Cosmos knowledge system

**Responsibilities**:
- Chemistry + physics + cosmology knowledge
- Number theory integration
- Cosmos pattern recognition

**Integration Points**:
- Used for cosmos queries
- Integrated into prompt via `get_enhanced_prompt()`

---

### 10.3 CosmosPatternAnalyzer
**File**: `src/cosmos_pattern_analyzer.py`  
**Type**: Cosmological pattern analysis

**Responsibilities**:
- Pattern recognition in cosmology
- Astronomical pattern detection
- Cosmic connection analysis

**Integration Points**:
- Used for cosmological queries
- Integrated into prompt via `get_enhanced_prompt()`

---

### 10.4 NumberTheoryEngine
**File**: `src/number_theory_engine.py`  
**Type**: Number theory analysis

**Responsibilities**:
- Number pattern recognition
- Mathematical pattern analysis
- Numerical relationship detection

**Integration Points**:
- Used for number theory queries
- Integrated into prompt via `get_enhanced_prompt()`

---

### 10.5 AstronomicalPatternEngine
**File**: `src/astronomical_patterns.py`  
**Type**: Astronomical pattern recognition

**Responsibilities**:
- Astronomical pattern detection
- Celestial event analysis
- Cosmic timing patterns

**Integration Points**:
- Used for astronomical queries

---

## 11. Output and Post-Processing

### 11.1 ResponsePostprocessor
**File**: `src/response_postprocessor.py`  
**Type**: Response cleaning and formatting

**Responsibilities**:
- Strip transmission format markers
- Remove meta-commentary
- Fix "designed to" language
- Detect fake citations
- Naturalize forensic structure

**Key Methods**:
- `postprocess_response()`: Main post-processing function
- `strip_transmission_format()`: Remove format markers
- `fix_designed_language()`: Fix language issues
- `detect_fake_citations()`: Validate citations

**Dependencies**: None (pure text processing)

**Integration Points**:
- Called from `ThesidiaHybridAdaptive` after response generation
- Used by `webapp/server.py` for response cleaning

---

### 11.2 NaturalProseSynthesizer
**File**: `src/natural_prose_synthesizer.py`  
**Type**: Forensic to prose conversion

**Responsibilities**:
- Convert ::EXPOSURE:: format to natural prose
- Naturalize forensic structure
- Maintain content while improving readability

**Integration Points**:
- Used by `ResponsePostprocessor` for naturalization

---

### 11.3 ParallelProcessor
**File**: `src/parallel_processor.py`  
**Type**: Parallel processing

**Responsibilities**:
- Run web search and LLM thinking in parallel
- Parallel task coordination
- Performance optimization

**Dependencies**:
- `WebSearchEngine`
- Model client

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` for parallel research

---

## 12. Modelfile System

### 12.1 ThesidiaModelfile
**File**: `src/thesidia_modelfile.py` (referenced)  
**Type**: Personality/voice/preset system

**Responsibilities**:
- Personality presets
- Voice personalities
- Persona definitions
- Configuration management

**Integration Points**:
- Used by `ThesidiaHybridAdaptive.get_enhanced_prompt()`
- Provides personality/voice/preset definitions

---

## 13. Utilities

### 13.1 QueryUtils
**File**: `src/support/query_utils.py`  
**Type**: Query normalization and routing

**Responsibilities**:
- Query normalization (typo fixes)
- Forensic routing detection
- Shared utilities for query processing

**Key Functions**:
- `normalize_query()`: Normalize query with typo fixes
- `detect_forensic_routing()`: Detect if query needs forensic analysis

**Integration Points**:
- Used by `webapp/server.py` for query normalization
- Used by `ThesidiaHybridAdaptive` for routing decisions

---

### 13.2 RecursionGuard
**File**: `src/recursion_guard.py`  
**Type**: Recursion prevention

**Responsibilities**:
- Prevent infinite recursion
- Track recursion depth
- Limit iterations

**Integration Points**:
- Used by `ThesidiaHybridAdaptive` to prevent recursion

---

### 13.3 GentleTruthEngine
**File**: `src/gentle_truth_engine.py`  
**Type**: Evidence arrangement

**Responsibilities**:
- Arrange evidence (not declare truth)
- Evidence-based responses
- Pattern recognition without assertion

**Integration Points**:
- Used for evidence arrangement in responses

---

### 13.4 AllyMechanics
**File**: `src/ally_mechanics.py`  
**Type**: Ally relationship mechanics

**Responsibilities**:
- Ally relationship tracking
- Subtle relationship dynamics
- Connection building

**Integration Points**:
- Subtle integration into prompt system

---

## 14. Component Dependency Graph

```
ThesidiaHybridAdaptive (Main Orchestrator)
  ├─ ModelClient (All LLM calls)
  │   ├─ Ollama (Primary)
  │   └─ MLXInference (Optional)
  ├─ AdaptivePersonality (Personality evolution)
  ├─ AdaptiveCapabilities (Directive handling)
  │   └─ ModelRouter (Model selection)
  ├─ AdaptiveLearning (Strategy selection)
  ├─ WebSearchEngine (Research)
  │   └─ DataQualityFilter (Quality scoring)
  ├─ DataSynthesizer (Synthesis)
  │   ├─ TruthEngine (Truth validation)
  │   ├─ IntuitiveSkepticism (Contradiction detection)
  │   └─ ModelRouter (Model selection)
  ├─ UserMemoryManager (Memory)
  │   ├─ UserManager (User identification)
  │   └─ MemoryManager (Memory storage)
  ├─ SophiaGnosticMap (7-layer map)
  │   └─ SophiaVersionManager (Versioning)
  ├─ SophiaEmergenceTracker (Consciousness)
  ├─ SophiaConsciousness (Consciousness calculator)
  ├─ SophiaDiscernmentTracker (Hallucination detection)
  ├─ UniversalCoach (Coaching)
  │   ├─ UserMemoryManager
  │   ├─ UserInterestTracker
  │   └─ TechnicalJourneyDetector
  ├─ HealthCoach (Health queries)
  ├─ CSIInvestigator (Forensic analysis)
  ├─ UserInterestTracker (Interest tracking)
  ├─ TechnicalJourneyDetector (Domain detection)
  ├─ QualityMetricsTracker (Quality metrics)
  ├─ MetricsCollector (Performance metrics)
  ├─ EngineeringDashboard (Monitoring)
  ├─ AhaMomentTracker (Insight tracking)
  ├─ ActionProposer (Action suggestions)
  ├─ InformationBuilder (Information threads)
  ├─ ParallelProcessor (Parallel processing)
  ├─ ResponsePostprocessor (Response cleaning)
  └─ [Many specialized modes and utilities]
```

---

## 15. Integration Patterns

### 15.1 Lazy Loading
Several components use lazy loading to reduce startup memory:
- `gnostic_map`: Loaded on first access
- `knowledge_base`: Loaded on first access
- `thesidia_patterns`: Loaded on first access
- `version_manager`: Loaded on first access

### 15.2 Optional Components
Many components are optional and gracefully degrade:
- `web_search`: None if WEB_AVAILABLE is False
- `mlx_inference`: None if MLX_AVAILABLE is False
- `structured_cognitive_loop`: None if env var not set
- `user_memory_manager`: None if import fails

### 15.3 Error Handling
Components use try/except blocks for graceful degradation:
- Import failures: Component set to None, system continues
- Processing errors: Fallback responses, error logging
- Memory errors: Safe mode, empty context returned

---

## 16. Component Initialization Order

1. BaseAgent initialization (model, base_dir, model_client, memory_manager)
2. Event system and configuration
3. Core components (personality, capabilities, learning)
4. Research and synthesis engines
5. Memory systems (user memory, Sophia systems)
6. Specialized modes (health coach, CSI, etc.)
7. Supporting systems (trackers, detectors, etc.)
8. Modelfile system
9. Lazy-loaded components (loaded on first access)

---

## 17. Component Communication Patterns

### 17.1 Direct Method Calls
Most components communicate via direct method calls:
- `ThesidiaHybridAdaptive` calls all subsystems directly
- No message bus or event system for core processing

### 17.2 Event System
Event system available but not heavily used:
- `get_event_system()` available
- Mostly for instrumentation and monitoring

### 17.3 State Sharing
State shared via instance variables:
- `ThesidiaHybridAdaptive` holds references to all components
- Components can access each other via parent reference

---

## 18. Conclusion

Thesidia AI is a complex system with over 50 distinct components organized into logical subsystems. The architecture follows a centralized orchestration pattern with `ThesidiaHybridAdaptive` as the main coordinator. Components are designed for graceful degradation, lazy loading, and optional features, making the system resilient to failures.

Key architectural patterns:
- **Centralized Orchestration**: `ThesidiaHybridAdaptive` coordinates all subsystems
- **Lazy Loading**: Heavy components loaded on first access
- **Graceful Degradation**: Optional components fail gracefully
- **Modular Design**: Clear separation of concerns
- **Dependency Injection**: Components receive dependencies via constructor

The system is well-structured but could benefit from:
- More explicit dependency injection
- Better error propagation
- More comprehensive event system usage
- Async processing for long operations
