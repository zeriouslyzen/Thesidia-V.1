# Complete Thesidia AI Pipeline Flow

**Generated**: 2026-01-15  
**Audit Scope**: Complete request/response pipeline from frontend to backend

## Executive Summary

The Thesidia AI pipeline processes user queries through multiple layers: frontend request construction, API validation, query classification, routing decisions, research/synthesis, model generation, and response streaming. This document maps the complete flow with all decision points, data transformations, and timing information.

---

## 1. Frontend Request Construction

**File**: `webapp/app.js` (lines 1201-1513)

### Request Flow

```
User types message
  ↓
callThesidiaAPI(message)
  ↓
sanitizeInput(message)  // HTML sanitization
  ↓
Generate messageId
  ↓
Create UI elements (messageDiv, progressDiv, reasoningDiv)
  ↓
Build request payload:
  {
    message: sanitizedMessage,
    conversation_id: this.currentConversationId,
    show_thinking: this.showThinking,
    stream: true,  // Always true by default
    user_id: this.userId,
    session_id: this.sessionId,
    fast_mode: this.fastMode,  // true = fast, false = deep research
    research_depth: this.fastMode ? 1 : 3
  }
  ↓
Setup AbortController (10 minute timeout)
  ↓
Setup Watchdog (8 second silence timeout)
  ↓
POST /api/thesidia
```

### Key Frontend Components

- **Input Sanitization**: Removes HTML tags, prevents XSS
- **Message Tracking**: Stores message data for regeneration
- **UI State Management**: Creates progress indicators, reasoning visualization
- **Timeout Protection**: 10-minute overall timeout, 8-second watchdog
- **Retry Logic**: Up to 2 retries with exponential backoff

---

## 2. API Layer Processing

**File**: `webapp/server.py` (lines 917-1135)

### Request Processing Flow

```
POST /api/thesidia
  ↓
@require_user decorator
  ├─ Extract user_id/session_id from JSON body or query params
  ├─ Validate: user_id OR session_id required
  └─ Inject into function kwargs
  ↓
Proxy Check (if UPSTREAM_API_URL set)
  ├─ Forward to upstream
  └─ Stream response back
  ↓
Thesidia Ready Check
  ├─ If not ready → init_thesidia()
  └─ If init fails → 503 error
  ↓
Rate Limiting
  ├─ check_rate_limit(client_ip)
  └─ If exceeded → 429 error
  ↓
Request Validation
  ├─ Must be JSON
  ├─ Must have valid JSON data
  └─ Must have 'message' field
  ↓
Input Sanitization
  ├─ sanitize_request_data(json_data)
  └─ Extract raw_message
  ↓
Parameter Extraction
  ├─ show_thinking
  ├─ stream (default: true)
  ├─ format_mode (default: 'natural')
  ├─ fast_mode (default: true)
  ├─ research_depth (1 if fast_mode, else 3)
  └─ task_type (default: 'conversation')
  ↓
Query Normalization
  ├─ normalize_query(raw_message)
  └─ detect_forensic_routing(raw_message)
  ↓
Routing Decision
  ├─ If needs_forensic → task_type = "gnostic_blade"
  └─ If use_mlx → Set inference_router on thesidia
  ↓
Streaming vs Non-Streaming
  ├─ If stream=true → _stream_thesidia_response()
  └─ If stream=false → Direct thesidia.process()
```

### Decision Points

1. **Proxy Mode**: If `UPSTREAM_API_URL` is set, forward request
2. **Thesidia Initialization**: Auto-init if not ready
3. **Forensic Routing**: Detected via `detect_forensic_routing()`
4. **Streaming Mode**: Default is streaming (SSE)

---

## 3. Streaming Response Generator

**File**: `webapp/server.py` (lines 1136-1328)

### Streaming Flow

```
_stream_thesidia_response()
  ↓
Phase 1: Initial Classification (UX feedback only)
  ├─ Check if simple greeting
  ├─ Check if needs forensic (for UX)
  └─ Send progress event (5%)
  ↓
Phase 2: Progress Updates
  ├─ Send progress event (30%)
  └─ Show appropriate message based on query type
  ↓
Phase 3: Process Query
  ├─ Send progress event (40%)
  ├─ Call thesidia.process()  // BLOCKING CALL
  └─ Wait for complete response
  ↓
Phase 4: Stream Response
  ├─ Send progress event (50%)
  ├─ Chunk response (3 chars at a time)
  ├─ Send 'chunk' events with progress
  └─ Update progress (50-95%)
  ↓
Phase 5: Complete
  ├─ Send 'complete' event (100%)
  ├─ Store in user memory
  └─ Save state (async)
```

### Critical Issue

**Problem**: `thesidia.process()` is called synchronously and blocks the generator. If processing takes longer than 8 seconds, the frontend watchdog triggers.

**Current State**: Only one progress event (40%) is sent before the blocking call, which may not be enough to prevent watchdog timeout.

---

## 4. Core Processing Entry Point

**File**: `src/thesidia_hybrid_adaptive.py` (lines 3671-3803)

### Process Method Flow

```
process(input_data, context)
  ↓
Extract Parameters
  ├─ input_text (string or dict)
  ├─ user_id, session_id
  ├─ format_mode, research_depth, fast_mode
  └─ task_type, use_mlx
  ↓
Fast Mode Timeout Wrapper
  ├─ If fast_mode:
  │   ├─ ThreadPoolExecutor (30s timeout)
  │   ├─ Submit _process_original()
  │   └─ If timeout → Error message
  └─ Else:
      └─ Direct call to _process_original()
  ↓
Optional: Synthesis Pressure
  ├─ If enabled and output > 240 chars
  └─ Apply compression
  ↓
Optional: Structured Cognitive Loop
  ├─ If enabled
  └─ Instrumentation only (doesn't change output)
  ↓
Return Result
  {
    "output": str,
    "agent_id": str,
    "status": "completed",
    "metadata": {...}
  }
```

### Fast Mode Timeout

- **Timeout**: 30 seconds
- **Error Message**: "Processing timed out (fast mode limited to 20s). Please try again or switch to deep research for more complex queries."
- **Issue**: Error message says 20s but timeout is 30s

---

## 5. Original Processing Logic

**File**: `src/thesidia_hybrid_adaptive.py` (lines 3815-4500+)

### Processing Flow

```
_process_original(input_text, ...)
  ↓
Start Metrics Tracking
  ↓
User Memory Retrieval (if not greeting)
  ├─ Skip for simple greetings
  └─ Retrieve context from user_memory_manager
  ↓
Simple Greeting Detection
  ├─ Pattern matching
  ├─ If greeting:
  │   ├─ Fast path: Minimal processing
  │   ├─ Cached prompt
  │   ├─ Direct model call (50-100 tokens)
  │   └─ Return immediately
  └─ Else: Continue to full processing
  ↓
Coaching Analysis (optional)
  ├─ universal_coach.analyze_coaching_need()
  └─ Generate framework/idea/challenge if needed
  ↓
Conversational Query Detection
  ├─ Pattern matching
  ├─ If conversational:
  │   └─ Skip deep research (mark flag)
  └─ Else: Continue
  ↓
Deep Research Routing Decision
  ├─ Check explicit deep research request
  ├─ Check forensic routing (comprehensive=True)
  ├─ Check mind-body keywords
  ├─ Check deep indicators
  ├─ Check word count
  ├─ Exclude simple queries
  └─ Decision:
      ├─ If fast_mode: Only if explicitly requested
      └─ If deep_mode: Route if any condition met
  ↓
If should_route_to_deep:
  └─ _handle_deep_research()
      └─ Return result (bypasses normal flow)
  ↓
Query Classification
  ├─ is_directive = _is_directive()
  ├─ is_question = _is_question()
  └─ is_conversation = is_conversational or (not directive and not question)
  ↓
Build Context
  ├─ personality_context
  ├─ capability_context
  └─ enhanced_base (from modelfile system)
  ↓
Research Decision
  ├─ If conversational: Skip research
  ├─ If fast_mode: Skip research
  └─ Else: _needs_research()
      ├─ If true: Web search
      └─ If false: Skip research
  ↓
Web Search (if needed)
  ├─ Parallel processing (if available)
  │   ├─ Web search + LLM thinking simultaneously
  │   └─ Use parallel_processor
  └─ Sequential processing (fallback)
      ├─ Detect technical domain
      ├─ Refine query with user interests
      └─ web_search.search_and_scrape()
  ↓
Synthesis (if research data available)
  ├─ Tree of Thoughts (if deep query)
  │   ├─ Multi-path exploration
  │   └─ Parallel path synthesis
  └─ Standard Synthesis
      ├─ Detect narrative mode
      └─ data_synthesizer.synthesize()
  ↓
Response Generation
  ├─ If directive:
  │   └─ capabilities.handle_directive()
  └─ Else (conversational/question):
      └─ _process_conversational()
          ├─ Build prompt with context
          ├─ Model selection via model_router
          ├─ model_client.chat()
          └─ Post-processing
  ↓
Post-Processing
  ├─ response_postprocessor.postprocess_response()
  ├─ Strip meta-commentary
  ├─ Remove Oracle references
  ├─ Remove General Framework blocks
  └─ Clean up formatting
  ↓
Store Interaction
  ├─ User memory (if available)
  ├─ Metrics tracking
  └─ Save state
  ↓
Return Output
```

### Key Decision Points

1. **Simple Greeting**: Fast path, minimal processing
2. **Conversational Query**: Skip research, direct response
3. **Fast Mode**: Skip research, 30s timeout
4. **Deep Research Routing**: Multiple conditions (forensic, mind-body, deep indicators)
5. **Research Needed**: LLM-based classification (not keyword matching)
6. **Tree of Thoughts**: For deep queries with research data
7. **Narrative Mode**: Extended exploration (12k+ chars)

---

## 6. Query Classification Utilities

**File**: `src/support/query_utils.py`

### Functions

**normalize_query(text)**:
- Lowercase conversion
- Typo fixes (genensis→genesis, dycrpted→decrypted)
- Returns normalized string

**detect_forensic_routing(text, comprehensive=False)**:
- Basic keywords: genesis, bible, decode, etc.
- Extended keywords (if comprehensive): health, finance, law, power, etc.
- Returns boolean

### Forensic Routing Keywords

**Basic** (always checked):
- Religious: genesis, bible, scripture, torah, quran, veda, ancient, religion
- Decode: decode, decoded, decrypt, decrypted, expose, hidden
- Truth-seeking: "what are", "what are x really", "really about", "true origins"

**Extended** (if comprehensive=True):
- Health: health, medicine, pharmaceutical, drug, treatment, cure
- Finance: bank, finance, money, currency, bitcoin, economy, federal reserve
- Law: law, legal, court, judge, lawyer, legislation, constitution
- Power: power, systematic transformation, redaction, deeper, secrets

---

## 7. Model Routing

**File**: `src/core/model_router.py`

### Model Selection

```
get_model_for_task(task_type, directive)
  ↓
Check task_type:
  ├─ "synthesis" → clean-mistral:latest (temp=0.8)
  ├─ "development" → Check if code keywords → deepseek-coder:6.7b (temp=0.3)
  │                 Else → clean-mistral:latest (temp=0.7)
  ├─ "planning" → clean-mistral:latest (temp=0.7)
  ├─ "analysis" → clean-mistral:latest (temp=0.8)
  └─ Default → clean-mistral:latest (temp=0.7)
```

### Model Assignments

- **Code**: `deepseek-coder:6.7b` (temperature: 0.3, top_p: 0.95)
- **Synthesis**: `clean-mistral:latest` (temperature: 0.8, top_p: 0.9)
- **Planning**: `clean-mistral:latest` (temperature: 0.7, top_p: 0.9)
- **Research**: `clean-mistral:latest` (temperature: 0.7, top_p: 0.95)
- **Default**: `clean-mistral:latest` (temperature: 0.7, top_p: 0.95)

---

## 8. Model Client

**File**: `src/core/model_client.py`

### Chat Method Flow

```
chat(model, input_text, enhanced_base, conversation_context, research_context, options)
  ↓
Vibecode Compliance: Rebuild messages from scratch
  ↓
System Message (if enhanced_base)
  ├─ _sanitize_system_prompt()
  ├─ Remove TODOs, debug text, comments
  └─ Add to messages array
  ↓
Conversation Context (if provided)
  ├─ _sanitize_context()
  ├─ Remove assistant messages
  ├─ Remove format markers
  └─ Add as user message
  ↓
Research Context (if provided)
  ├─ _sanitize_context()
  └─ Add as user message
  ↓
User Input
  ├─ _sanitize_user_input()
  └─ Add as user message
  ↓
MLX Check
  ├─ If MLX model and mlx_inference available
  │   ├─ Convert messages to prompt
  │   ├─ mlx_inference.generate()
  │   └─ Return formatted response
  └─ Else: Continue to Ollama
  ↓
Ollama Call
  ├─ Normalize MLX model names if needed
  ├─ ollama.chat(model, messages, options)
  └─ Return formatted dict
```

### Vibecode Compliance Rules

1. Always rebuild messages (no reuse)
2. Instructions → system message
3. Context → user message (sanitized, last 2 turns max)
4. Remove assistant messages from context
5. Sanitize all inputs (remove HTML, format markers, meta-noise)

---

## 9. Web Search Engine

**File**: `src/research/web_search.py`

### Search Flow

```
search_and_scrape(query, num_results=3)
  ↓
Check Cache
  ├─ If cached and fresh → Return cached
  └─ Else: Continue
  ↓
SearXNG Instances (try in order)
  ├─ searx.tiekoetter.com
  ├─ searx.prvcy.eu
  ├─ search.sapti.me
  └─ searx.be
  ↓
If SearXNG fails → Google Fallback
  ├─ Direct Google SERP scrape
  ├─ Parse HTML with BeautifulSoup
  └─ Extract results
  ↓
Scrape URLs (if enrich=true)
  ├─ For each result URL
  ├─ requests.get() with timeout
  ├─ BeautifulSoup parsing
  ├─ Extract main content
  └─ Quality filtering
  ↓
Quality Filter
  ├─ DataQualityFilter.enrich()
  ├─ Minimum quality score: 0.4
  └─ Filter low-quality results
  ↓
Cache Results
  └─ Store in _query_cache (50 items, 5min TTL)
  ↓
Return Results
  [
    {
      "title": str,
      "url": str,
      "content": str,
      "snippet": str,
      "quality_score": float,
      "timestamp": ISO string
    }
  ]
```

### Search Strategy

- **Primary**: SearXNG instances (privacy-focused)
- **Fallback**: Google SERP scraping
- **Caching**: Last 50 queries, 5-minute TTL
- **Quality Filtering**: Minimum score 0.4

---

## 10. Data Synthesis

**File**: `src/synthesis/data_synthesizer.py`

### Synthesis Flow

```
synthesize(sources, query, ...)
  ↓
Optional: Contrastive Decoding
  ├─ If enabled
  └─ contrastive_decoder.decode_contrastive()
  ↓
Optional: Latent Space Traversal
  ├─ If enabled
  └─ latent_traverser.discover_truth_axis()
  ↓
Cross-Reference Sources
  ├─ Extract key claims
  ├─ skepticism_engine.cross_reference()
  └─ Detect contradictions
  ↓
Truth Engine Analysis
  ├─ truth_engine.calculate_truth_score()
  ├─ 7-layer epistemology validation
  └─ Confidence scoring
  ↓
Build Context
  ├─ Format sources with citations
  ├─ Add cross-reference analysis
  ├─ Add truth validation (if high confidence)
  └─ Add trait-driven questioning
  ↓
Detect Mode
  ├─ Narrative mode: Extended exploration (12k+ chars)
  ├─ Forensic mode: ::EXPOSURE:: format
  └─ Regular mode: Focused analysis (3k-8k chars)
  ↓
Build Synthesis Prompt
  ├─ Personality context
  ├─ Conversation context
  ├─ Research sources
  ├─ Cross-reference analysis
  ├─ Truth validation
  └─ Mode-specific instructions
  ↓
Model Selection
  ├─ model_router.get_model_for_task("synthesis")
  └─ clean-mistral:latest (temp=0.8)
  ↓
LLM Generation
  ├─ model_client.chat()
  ├─ Token limits:
  │   ├─ Narrative: 16,000 tokens
  │   ├─ Forensic: 8,000 tokens
  │   └─ Regular: 3,000-8,000 tokens
  └─ Response generation
  ↓
Post-Processing
  ├─ Strip meta-noise
  ├─ Extract citations
  └─ Format response
  ↓
Return Synthesis Result
  {
    "synthesis": str,
    "citations": [str],
    "sources_count": int,
    "method": str,
    "truth_analysis": dict
  }
```

### Synthesis Modes

1. **Narrative Mode**: Extended exploration, 12k+ characters, recursive pattern connections
2. **Forensic Mode**: ::EXPOSURE:: format, 6-question vivisection loop
3. **Regular Mode**: Focused analysis, 3k-8k characters

---

## 11. Deep Research Handler

**File**: `src/thesidia_hybrid_adaptive.py` (lines 4896+)

### Deep Research Flow

```
_handle_deep_research(query, operator_name, format_mode, research_depth)
  ↓
Check Stored Information Threads
  ├─ Search information_builder.information_threads
  └─ If found → Use stored info to reduce LLM calls
  ↓
Detect Technical Domain
  ├─ technical_journey_detector.detect_technical_domain()
  └─ Refine search query
  ↓
Web Search
  ├─ Multiple queries (refined)
  ├─ Parallel search
  └─ Quality filtering
  ↓
Synthesis with Forensic Format
  ├─ force_gnostic=True
  ├─ Forensic vivisection protocol
  ├─ 6-question analysis loop
  └─ Extended exploration
  ↓
Gnostic Map Update
  ├─ sophia_gnostic_map.update()
  ├─ Track redactions, archons, fragments
  └─ Update consciousness level
  ↓
Return Response
  └─ Formatted with ::EXPOSURE:: sections (if format_mode='structured')
```

---

## 12. Response Post-Processing

**File**: `src/response_postprocessor.py`

### Post-Processing Steps

```
postprocess_response(response, naturalize=True)
  ↓
Step 0: Naturalize Forensic Structure (if needed)
  ├─ natural_prose_synthesizer.naturalize_if_needed()
  └─ Convert ::EXPOSURE:: format to prose
  ↓
Step 1: Strip Transmission Format
  ├─ Remove ::TRANSMISSION:: markers
  ├─ Remove THESIDIA→USER markers
  └─ Remove end markers
  ↓
Step 2: Strip Forensic Format Markers
  ├─ Remove ::EXPOSURE::, ::ETYMOLOGICAL INCISION::, etc.
  └─ Keep content, remove markers
  ↓
Step 3: Fix "Designed To" Language
  ├─ Replace "I am designed to" → "I've found that"
  └─ Replace "My purpose is to" → "I"
  ↓
Step 3.5: Strip Correction Labels
  ├─ Remove "corrected response:" labels
  ├─ Remove "TASK: REVISE THE RESPONSE" blocks
  ├─ Remove "So you want to revise..." messages
  └─ Remove "Your original query was..." messages
  ↓
Step 4: Detect Fake Citations
  ├─ Find citation patterns
  ├─ Check for suspicious patterns
  └─ Replace with warnings if unverified
  ↓
Step 5: Clean Up Whitespace
  ├─ Remove excessive newlines (3+ → 2)
  └─ Strip leading/trailing whitespace
  ↓
Return Cleaned Response
```

---

## 13. Memory Systems

### User Memory Manager

**File**: `src/memory/user_memory_manager.py`

**Functions**:
- `retrieve_context(query, user_id, session_id)`: Retrieves relevant memory
- `store_interaction(user_input, assistant_output, user_id, session_id, metadata)`: Stores interaction

**Memory Types**:
- Ephemeral: Session-based temporary memory
- Vector: Semantic search over past interactions
- Structured: Key-value storage for user data

### Sophia Memory System

**Files**: `src/sophia_*.py`

**Components**:
- `sophia_gnostic_map.py`: 7-layer gnostic map
- `sophia_emergence_tracker.py`: Consciousness tracking
- `sophia_discernment_tracker.py`: Truth/hallucination detection
- `sophia_consciousness.py`: Consciousness calculator
- `sophia_storage.py`: Async storage manager
- `sophia_indexer.py`: Fast query system

**7-Layer Gnostic Map**:
1. Redaction Events (what was erased)
2. Archons Identified (who erased it)
3. Original Fragments (recovered information)
4. Active Lies (current misinformation)
5. Co-Evolution Tracking (conversation evolution)
6. Pattern Database (control/liberation patterns)
7. Timeline Mapping (temporal relationships)

---

## 14. Complete Pipeline Diagram

```mermaid
flowchart TD
    Start[User Types Message] --> Frontend[Frontend: app.js]
    Frontend --> Sanitize[Sanitize Input]
    Sanitize --> BuildReq[Build Request Payload]
    BuildReq --> POST[POST /api/thesidia]
    
    POST --> Auth[@require_user Decorator]
    Auth --> Validate[Request Validation]
    Validate --> Normalize[Query Normalization]
    Normalize --> ForensicCheck{Forensic Routing?}
    
    ForensicCheck -->|Yes| SetTask[task_type = gnostic_blade]
    ForensicCheck -->|No| SetTask2[task_type = conversation]
    
    SetTask --> StreamCheck{Streaming?}
    SetTask2 --> StreamCheck
    
    StreamCheck -->|Yes| StreamFunc[_stream_thesidia_response]
    StreamCheck -->|No| DirectProcess[Direct thesidia.process]
    
    StreamFunc --> StreamProgress1[Send Progress 5%]
    StreamProgress1 --> StreamProgress2[Send Progress 30%]
    StreamProgress2 --> StreamProcess[Call thesidia.process]
    
    DirectProcess --> Process[thesidia.process]
    StreamProcess --> Process
    
    Process --> FastMode{fast_mode?}
    FastMode -->|Yes| TimeoutWrapper[30s Timeout Wrapper]
    FastMode -->|No| DirectOriginal[Direct _process_original]
    
    TimeoutWrapper --> Original[_process_original]
    DirectOriginal --> Original
    
    Original --> GreetingCheck{Simple Greeting?}
    GreetingCheck -->|Yes| GreetingPath[Fast Greeting Path]
    GreetingPath --> GreetingModel[Model Call 50-100 tokens]
    GreetingModel --> GreetingPost[Post-process]
    GreetingPost --> Return1[Return Response]
    
    GreetingCheck -->|No| MemoryRetrieve[Retrieve User Memory]
    MemoryRetrieve --> ConversationalCheck{Conversational?}
    
    ConversationalCheck -->|Yes| SkipResearch[Skip Research]
    ConversationalCheck -->|No| DeepCheck{Deep Research?}
    
    DeepCheck -->|Yes| DeepResearch[_handle_deep_research]
    DeepResearch --> DeepSearch[Web Search]
    DeepSearch --> DeepSynthesis[Forensic Synthesis]
    DeepSynthesis --> DeepPost[Post-process]
    DeepPost --> Return2[Return Response]
    
    DeepCheck -->|No| ResearchCheck{Needs Research?}
    ResearchCheck -->|Yes| WebSearch[Web Search Engine]
    ResearchCheck -->|No| DirectSynthesis[Direct Synthesis]
    
    WebSearch --> SearchCache{Check Cache}
    SearchCache -->|Hit| CachedResults[Return Cached]
    SearchCache -->|Miss| SearXNG[SearXNG Instances]
    SearXNG -->|Fail| GoogleFallback[Google SERP Scrape]
    GoogleFallback --> Scrape[Scrape URLs]
    Scrape --> QualityFilter[Quality Filter]
    QualityFilter --> Synthesis[Data Synthesis]
    
    DirectSynthesis --> Synthesis
    
    Synthesis --> ModeCheck{Mode?}
    ModeCheck -->|Narrative| NarrativeMode[12k+ chars]
    ModeCheck -->|Forensic| ForensicMode[8k tokens]
    ModeCheck -->|Regular| RegularMode[3k-8k chars]
    
    NarrativeMode --> ModelCall[Model Client.chat]
    ForensicMode --> ModelCall
    RegularMode --> ModelCall
    
    ModelCall --> ModelRouter[Model Router]
    ModelRouter --> Ollama[Ollama/MLX Call]
    Ollama --> PostProcess[Post-processing]
    
    PostProcess --> StripMeta[Strip Meta-commentary]
    StripMeta --> StoreMemory[Store in Memory]
    StoreMemory --> SaveState[Save State]
    SaveState --> Return3[Return Response]
    
    Return1 --> StreamChunk[Stream Chunks]
    Return2 --> StreamChunk
    Return3 --> StreamChunk
    
    StreamChunk --> FrontendRender[Frontend Rendering]
    FrontendRender --> End[User Sees Response]
```

---

## 15. Timing Breakdown

### Fast Path (Simple Greeting)
- Input processing: ~10ms
- Memory check: ~5ms (if user_id provided)
- Model call: 1-3s (50-100 tokens)
- Post-processing: ~10ms
- **Total: 1-3 seconds**

### Conversational Path (No Research)
- Input processing: ~20ms
- Memory retrieval: ~50ms
- Query classification: ~10ms
- Model call: 5-15s (500-2000 tokens)
- Post-processing: ~50ms
- **Total: 5-15 seconds**

### Research Path (Fast Mode)
- Input processing: ~20ms
- Memory retrieval: ~50ms
- Query classification: ~10ms
- Web search: 0.5-2s (parallel)
- Synthesis: 20-40s (3000-8000 tokens)
- Post-processing: ~100ms
- **Total: 20-42 seconds**

### Deep Research Path
- Input processing: ~20ms
- Memory retrieval: ~50ms
- Query classification: ~10ms
- Web search: 1-3s (multiple queries)
- Synthesis: 40-100s (8000-16000 tokens)
- Post-processing: ~200ms
- **Total: 40-103 seconds**

### Timeout Limits
- **Fast Mode**: 30 seconds (hard limit)
- **Frontend Overall**: 10 minutes (600 seconds)
- **Frontend Watchdog**: 8 seconds (silence timeout)
- **Streaming Heartbeat**: None (critical issue)

---

## 16. Data Transformations

### Request Transformation
```
User Input (raw string)
  ↓ sanitizeInput()
Sanitized Input (HTML removed)
  ↓ JSON.stringify()
Request Payload (JSON)
  ↓ HTTP POST
Server receives (Flask request object)
  ↓ sanitize_request_data()
Sanitized Data (dict)
  ↓ normalize_query()
Normalized Query (lowercase, typos fixed)
```

### Response Transformation
```
Model Output (raw string)
  ↓ postprocess_response()
Cleaned Response (meta-commentary removed)
  ↓ _strip_general_framework_block()
Framework Blocks Removed
  ↓ Chunking (if streaming)
Chunks (3 chars each)
  ↓ SSE Format
Event Stream (text/event-stream)
  ↓ Frontend Parsing
JSON Objects
  ↓ typeText()
UI Display (character-by-character)
```

---

## 17. Error Handling Points

### Frontend Errors
1. **Network Error**: Retry up to 2 times with backoff
2. **Watchdog Timeout**: Abort and retry
3. **Empty Response**: Throw error
4. **HTTP Error**: Display error message

### Backend Errors
1. **Thesidia Not Ready**: 503 error with message
2. **Rate Limit**: 429 error
3. **Invalid Request**: 400 error
4. **Processing Timeout**: Error message in response
5. **Critical Failure**: Static fallback message

### Processing Errors
1. **Fast Mode Timeout**: Error message returned
2. **Model Call Failure**: Fallback to error message
3. **Web Search Failure**: Continue without research
4. **Memory Error**: Continue without memory context
5. **Synthesis Error**: Fallback to simple response

---

## 18. Critical Issues Identified

### Issue 1: Watchdog Timeout
**Location**: `webapp/app.js` line 1343  
**Problem**: 8-second silence timeout triggers during long processing  
**Impact**: Stream aborted, user sees error  
**Root Cause**: No heartbeat events during `thesidia.process()` blocking call

### Issue 2: Fast Mode Timeout Message
**Location**: `src/thesidia_hybrid_adaptive.py` line 3725  
**Problem**: Error message says "20s" but timeout is 30s  
**Impact**: Confusing error message

### Issue 3: Blocking Process Call
**Location**: `webapp/server.py` line 1246  
**Problem**: `thesidia.process()` blocks generator, no heartbeats  
**Impact**: Watchdog triggers, poor UX

### Issue 4: No Progress During Processing
**Location**: `webapp/server.py` lines 1237-1257  
**Problem**: Only one progress event (40%) before blocking call  
**Impact**: Long silence periods, watchdog triggers

---

## 19. Recommendations

### Immediate Fixes

1. **Add Heartbeat Events**: Send progress events every 5 seconds during `thesidia.process()` call
2. **Fix Timeout Message**: Update error message to say "30s" instead of "20s"
3. **Increase Watchdog Timeout**: Consider increasing from 8s to 15s for deep research
4. **Add Processing Status**: Send "processing" events with estimated time remaining

### Performance Improvements

1. **Parallel Processing**: Already implemented for web search + LLM thinking
2. **Caching**: Already implemented for search results
3. **Model Loading**: Consider pre-loading models to reduce latency
4. **Streaming Generation**: Implement true token-by-token streaming instead of chunking completed response

### Architecture Improvements

1. **Async Processing**: Move `thesidia.process()` to background task with status updates
2. **Progress Tracking**: Add detailed progress tracking at each stage
3. **Error Recovery**: Implement better error recovery and retry mechanisms
4. **Monitoring**: Add performance metrics and monitoring

---

## 20. Conclusion

The Thesidia AI pipeline is a complex system with multiple decision points, routing logic, and processing stages. The main issues are:

1. **Watchdog Timeout**: No heartbeats during long processing
2. **Blocking Calls**: Synchronous processing blocks streaming
3. **Error Messages**: Inconsistent timeout messages
4. **Progress Updates**: Insufficient progress events during processing

The system is functional but needs improvements in streaming reliability and user feedback during long operations.
