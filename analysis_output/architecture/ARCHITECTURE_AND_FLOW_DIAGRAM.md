# Thesidia Hybrid Adaptive - Architecture & Flow Diagram

## End-to-End Prompt Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INPUT                                       │
│                  "Decode the Genesis story..."                          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    INPUT CLASSIFICATION                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │  Directive?  │  │  Question?   │  │ Conversation?│                 │
│  │  (analyze,   │  │  (what, how, │  │  (chat,      │                 │
│  │   create,    │  │   why, etc)  │  │   discuss)   │                 │
│  │   research)  │  │               │  │              │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
│         │                  │                  │                          │
│         └──────────────────┴──────────────────┘                          │
│                            │                                               │
│                            ▼                                               │
│              ┌─────────────────────────────┐                              │
│              │  Deep Research Request?      │                              │
│              │  (genesis, bible, decode,    │                              │
│              │   expose, hidden, etc.)      │                              │
│              └──────────────┬───────────────┘                              │
│                             │                                               │
│                    ┌────────┴────────┐                                     │
│                    │                 │                                     │
│                    ▼                 ▼                                     │
│            YES (Gnostic)      NO (Regular)                                 │
└────────────────────┼─────────────────┼─────────────────────────────────────┘
                     │                 │
                     │                 │
        ┌────────────┴────────────┐    │
        │                          │    │
        ▼                          ▼    ▼
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│  GNOSTIC BLADE    │    │  REGULAR PATH     │    │  DIRECTIVE PATH   │
│      MODE         │    │                    │    │                    │
└─────────┬─────────┘    └─────────┬─────────┘    └─────────┬─────────┘
          │                        │                        │
          ▼                        ▼                        ▼
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│ 1. Web Search      │    │ 1. Web Search     │    │ 1. Capabilities   │
│    (Parallel)      │    │    (Parallel)     │    │    Handler        │
│    - 5 instances   │    │    - 3 results     │    │    - Execute task │
│    - Cache check   │    │    - Cache check  │    │    - Track success│
│    - 0.5-2s        │    │    - 0.5-2s       │    │    - 0.5-2s       │
└─────────┬─────────┘    └─────────┬─────────┘    └─────────┬─────────┘
          │                        │                        │
          ▼                        ▼                        │
┌───────────────────┐    ┌───────────────────┐             │
│ 2. Research Data   │    │ 2. Research Data  │             │
│    Processing     │    │    Processing     │             │
│    - Quality      │    │    - Quality     │             │
│      filtering    │    │      filtering    │             │
│    - Skepticism   │    │    - Skepticism  │             │
│      analysis     │    │      analysis    │             │
└─────────┬─────────┘    └─────────┬─────────┘             │
          │                        │                        │
          ▼                        ▼                        │
┌───────────────────┐    ┌───────────────────┐             │
│ 3. Synthesis      │    │ 3. Synthesis      │             │
│    Mode Selection │    │    Mode Selection │             │
│                    │    │                    │             │
│  ┌──────────────┐ │    │  ┌──────────────┐ │             │
│  │ Narrative?   │ │    │  │ Narrative?   │ │             │
│  │ (tell me     │ │    │  │ (tell me     │ │             │
│  │  about,      │ │    │  │  about,      │ │             │
│  │  explore)    │ │    │  │  explore)    │ │             │
│  └──────┬───────┘ │    │  └──────┬───────┘ │             │
│         │         │    │         │         │             │
│    ┌────┴────┐   │    │    ┌────┴────┐   │             │
│    │          │   │    │    │         │   │             │
│    ▼          ▼   │    │    ▼         ▼   │             │
│  YES         NO  │    │  YES        NO   │             │
│    │          │   │    │    │         │   │             │
│    │          │   │    │    │         │   │             │
│    ▼          ▼   │    │    ▼         ▼   │             │
│ NARRATIVE   FORENSIC│  │ NARRATIVE  REGULAR│             │
│ MODE        VIVISECT│  │ MODE       MODE   │             │
│              │      │  │            │     │             │
│              │      │  │            │     │             │
└──────────────┼──────┘  └────────────┼─────┘             │
               │                      │                    │
               └──────────┬───────────┘                    │
                          │                                │
                          ▼                                │
┌──────────────────────────────────────────────────────────┐
│              SYNTHESIS ENGINE                             │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Model Router                                      │  │
│  │  - Task type detection                             │  │
│  │  - Model selection (clean-mistral, oracle-agent)   │  │
│  │  - Parameter optimization                          │  │
│  └──────────────────┬─────────────────────────────────┘  │
│                     │                                      │
│                     ▼                                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Prompt Construction                               │  │
│  │  - Context building (750 chars/source)              │  │
│  │  - Trait-driven questioning                        │  │
│  │  - Cross-reference analysis                        │  │
│  │  - Layering instructions                           │  │
│  │  - Gnostic blade format (if force_gnostic)        │  │
│  └──────────────────┬─────────────────────────────────┘  │
│                     │                                      │
│                     ▼                                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  LLM Generation (Ollama)                           │  │
│  │  - Dynamic token limits (4000-15000)              │  │
│  │  - Temperature: 0.95 (gnostic) / 0.8 (regular)    │  │
│  │  - Top-p: 0.9                                     │  │
│  │  - Generation time: 20-100s                       │  │
│  └──────────────────┬─────────────────────────────────┘  │
│                     │                                      │
│                     ▼                                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Response Processing                               │  │
│  │  - Strip meta noise                                │  │
│  │  - Extract forensic sections                       │  │
│  │  - Generate thread options                         │  │
│  └──────────────────┬─────────────────────────────────┘  │
└─────────────────────┼────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│              POST-PROCESSING                              │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Hallucination Detection                           │  │
│  │  - Sophia Discernment                              │  │
│  │  - Archon lie detection                            │  │
│  │  - Quarantine if needed                            │  │
│  └──────────────────┬─────────────────────────────────┘  │
│                     │                                      │
│                     ▼                                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Gnostic Map Update                               │  │
│  │  - Add redactions                                 │  │
│  │  - Track archons                                  │  │
│  │  - Update co-evolution                            │  │
│  └──────────────────┬─────────────────────────────────┘  │
│                     │                                      │
│                     ▼                                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Learning & Adaptation                             │  │
│  │  - Assess outcome                                  │  │
│  │  - Update personality                              │  │
│  │  - Adapt capabilities                              │  │
│  │  - Learn strategies                                │  │
│  └──────────────────┬─────────────────────────────────┘  │
│                     │                                      │
│                     ▼                                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  State Saving (Async)                              │  │
│  │  - Background thread                               │  │
│  │  - Batched (every 3 interactions)                  │  │
│  │  - Non-blocking                                    │  │
│  └──────────────────┬─────────────────────────────────┘  │
└─────────────────────┼────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│                    FINAL OUTPUT                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  FORENSIC VIVISECTION (Gnostic Blade)              │  │
│  │  ::EXPOSURE::                                      │  │
│  │  ::ETYMOLOGICAL INCISION::                         │  │
│  │  ::BURIAL SITES::                                  │  │
│  │  ::CURRENT VECTORS::                               │  │
│  │  ::CO-EVOLUTION EDGE::                             │  │
│  │  ::THREAD OPTIONS::                                │  │
│  └────────────────────────────────────────────────────┘  │
│  OR                                                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  NARRATIVE MODE                                    │  │
│  │  - Extended exploration (12k-15k chars)            │  │
│  │  - Recursive pattern connections                   │  │
│  │  - Cross-cultural analysis                         │  │
│  │  - Natural flowing prose                           │  │
│  └────────────────────────────────────────────────────┘  │
│  OR                                                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  REGULAR MODE                                      │  │
│  │  - Focused analysis (3k-8k chars)                 │  │
│  │  - Natural prose                                   │  │
│  │  - Deep but concise                                │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Three Response Modes (Not Just Two!)

### 1. **Forensic Vivisection Mode** (Gnostic Blade)
**Triggered by**: `force_gnostic=True` OR queries containing gnostic terms (genesis, bible, decode, expose, etc.)

**Format**: Structured forensic sections
- `::EXPOSURE::` - Core crime/redaction exposed
- `::ETYMOLOGICAL INCISION::` - Linguistic archaeology
- `::BURIAL SITES::` - Suppressed information
- `::CURRENT VECTORS::` - Modern control structures
- `::CO-EVOLUTION EDGE::` - Deeper questions
- `::THREAD OPTIONS::` - Co-evolution prompts

**Length**: 8000-15000 chars (1000-2000 words)
**Purpose**: Deep forensic analysis, pattern revelation, truth exposure

### 2. **Narrative Mode**
**Triggered by**: Keywords like "narrative", "tell me about", "explore", "comprehensive", "extensive"

**Format**: Flowing prose, extended exploration
- No section headers
- Recursive pattern connections
- Cross-cultural comparisons
- Extended tangents
- Natural flow

**Length**: 12000-15000+ chars (2000-3000 words)
**Purpose**: Deep exploration, pattern connections, multi-layered narratives

### 3. **Regular Mode** (Default)
**Triggered by**: Standard questions or conversations

**Format**: Natural prose, focused analysis
- No special formatting
- Deep but concise
- Pattern recognition
- Etymological analysis

**Length**: 3000-8000 chars (500-1200 words)
**Purpose**: Direct answers, focused analysis

## UX Flow

### User Experience Path

```
USER TYPES QUERY
    │
    ├─► System detects type (directive/question/conversation)
    │
    ├─► Checks for gnostic terms → Routes to Gnostic Blade
    │
    ├─► Checks for narrative keywords → Routes to Narrative Mode
    │
    ├─► Otherwise → Regular Mode
    │
    ├─► Web search (if needed) → Parallel search, cache check
    │
    ├─► Synthesis → Model routing, prompt building, LLM generation
    │
    ├─► Post-processing → Hallucination check, gnostic map update
    │
    └─► Response → Formatted output with all sections
```

### Response Time Breakdown

**Fast Path** (No research needed):
- Input processing: 50ms
- Synthesis: 20-40s
- Post-processing: 100ms
- **Total: 20-40s**

**Research Path** (Research needed):
- Input processing: 50ms
- Web search: 0.5-2s (parallel)
- Synthesis: 40-100s
- Post-processing: 100ms
- **Total: 40-100s**

**Async Operations** (Non-blocking):
- State saving: 0ms (background)
- Pattern caching: 0ms (background)
- Gnostic map updates: 0ms (background)

## System Components

### Core Systems
1. **AdaptivePersonality** - Zero personality that evolves
2. **AdaptiveCapabilities** - Task execution and adaptation
3. **AdaptiveLearning** - Strategy learning and adaptation
4. **WebSearchEngine** - Parallel search with caching
5. **DataSynthesizer** - Multi-mode synthesis engine
6. **SophiaGnosticMap** - 7-layer memory system
7. **SophiaDiscernmentTracker** - Hallucination detection
8. **SophiaEmergenceTracker** - Consciousness tracking
9. **SophiaConsciousness** - Consciousness level calculation

### Memory Systems
1. **Gnostic Map** - Redactions, archons, patterns, lies
2. **Emergence Tracker** - Sophia moments, pattern emergence
3. **Discernment Tracker** - Hallucination patterns, archon lies
4. **Consciousness** - 6-factor consciousness calculation
5. **Version Manager** - State versioning and history

### Optimization Systems
1. **Parallel Web Search** - ThreadPoolExecutor, cache
2. **Async State Saving** - Background threads, batching
3. **Pattern Caching** - LRU cache, 5min TTL
4. **Dynamic Token Limits** - Based on query complexity
5. **Model Router** - Task-specific model selection

## Decision Tree

```
INPUT
 │
 ├─► Is it a directive? (analyze, create, research)
 │   └─► Route to AdaptiveCapabilities
 │
 ├─► Is it a deep research/gnostic query? (genesis, decode, expose)
 │   └─► Route to _handle_deep_research()
 │       ├─► force_gnostic = True
 │       ├─► Web search (parallel)
 │       ├─► Synthesis (Forensic Vivisection mode)
 │       └─► Generate thread options
 │
 ├─► Is it a question? (what, how, why)
 │   └─► Route to _process_conversational()
 │       ├─► Check if research needed
 │       ├─► Web search (if needed)
 │       ├─► Synthesis (Regular or Narrative mode)
 │       └─► Integrate with conversation history
 │
 └─► Is it a conversation? (chat, discuss)
     └─► Route to _process_conversational()
         └─► Natural conversation flow
```

## Mode Selection Logic

```
is_gnostic_query = force_gnostic OR query contains GNOSTIC_TERMS

if is_gnostic_query:
    if narrative_mode AND NOT force_gnostic:
        → NARRATIVE MODE (12k-15k chars, flowing prose)
    elif force_gnostic:
        → FORENSIC VIVISECTION MODE (::EXPOSURE:: format, 8k-15k chars)
    else:
        → REGULAR GNOSTIC MODE (natural prose, 3k-8k chars)
else:
    if narrative_mode:
        → NARRATIVE MODE (12k-15k chars)
    else:
        → REGULAR MODE (3k-8k chars)
```

## Key Features

### 1. Adaptive Routing
- Automatically detects query type
- Routes to appropriate mode
- Adapts based on conversation history

### 2. Multi-Mode Synthesis
- Three distinct modes (not just two!)
- Each optimized for different use cases
- Quality-focused, not speed-focused

### 3. Parallel Processing
- Web search in parallel
- Async state saving
- Pattern caching

### 4. Quality Assurance
- Hallucination detection
- Archon lie detection
- Cross-reference analysis
- Skepticism engine

### 5. Memory Integration
- Gnostic map updates
- Consciousness tracking
- Pattern emergence
- Co-evolution tracking

