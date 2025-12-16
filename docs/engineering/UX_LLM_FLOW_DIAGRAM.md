# UX → LLM Flow Diagram: Next 5 Messages

## Complete Message Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE (UX)                            │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  User Types Message → app.js:callThesidiaAPI()                 │  │
│  │  - Sanitizes input                                               │  │
│  │  - Creates message div                                            │  │
│  │  - Shows reasoning visualization (always)                        │  │
│  │  - Sends: {message, fast_mode, research_depth, stream:true}    │  │
│  └───────────────────────┬─────────────────────────────────────────┘  │
│                          │                                              │
│                          ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  Fetch API → POST /api/thesidia                                │  │
│  │  - Headers: Content-Type: application/json                       │  │
│  │  - Body: JSON with message + params                              │  │
│  └───────────────────────┬─────────────────────────────────────────┘  │
└──────────────────────────┼────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLASK SERVER (webapp/server.py)                      │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  @app.route('/api/thesidia', methods=['POST'])                  │  │
│  │  - Parses: message, fast_mode, research_depth, stream           │  │
│  │  - Calls: _stream_thesidia_response()                          │  │
│  └───────────────────────┬─────────────────────────────────────────┘  │
│                          │                                              │
│                          ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  _stream_thesidia_response()                                    │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  CHECKPOINT 1: Simple Greeting?                           │  │  │
│  │  │  - Pattern: ['hi', 'hello', 'hey'] or len <= 2           │  │  │
│  │  │  - If YES: Skip forensic check                            │  │  │
│  │  │  - If NO: Check forensic routing                          │  │  │
│  │  └───────────────────────┬───────────────────────────────────┘  │  │
│  │                          │                                        │  │
│  │                          ▼                                        │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  CHECKPOINT 2: Conversational?                            │  │  │
│  │  │  - Patterns: 'what.*?your favorite', etc.                │  │  │
│  │  │  - If YES: Skip research, skip deep routing               │  │  │
│  │  │  - If NO: Continue to routing                             │  │  │
│  │  └───────────────────────┬───────────────────────────────────┘  │  │
│  │                          │                                        │  │
│  │                          ▼                                        │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  PROGRESS EVENTS (SSE)                                      │  │  │
│  │  │  - Phase 1: 'input_received' → "Processing your query..." │  │  │
│  │  │  - Phase 2: 'web_search' (if needed)                      │  │  │
│  │  │  - Phase 3: 'processing' (if not greeting/conversational)   │  │  │
│  │  │  - Phase 4: 'preparing' → "Preparing response..."          │  │  │
│  │  │  - Phase 5: 'streaming' → "Generating response..."         │  │  │
│  │  └───────────────────────┬───────────────────────────────────┘  │  │
│  │                          │                                        │  │
│  │                          ▼                                        │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  CALL: thesidia.process()                                  │  │  │
│  │  │  - input_text: message                                     │  │  │
│  │  │  - fast_mode: from UI toggle                                │  │  │
│  │  │  - research_depth: 1 (fast) or 3 (deep)                   │  │  │
│  │  └───────────────────────┬───────────────────────────────────┘  │  │
│  └──────────────────────────┼──────────────────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              THESIDIA CORE (src/thesidia_hybrid_adaptive.py)             │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  process(input_text, fast_mode, research_depth, ...)          │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  CHECKPOINT 1: Simple Greeting? (DUPLICATE CHECK)          │  │  │
│  │  │  - Pattern: greeting_only_patterns + len <= 4               │  │  │
│  │  │  - If YES: Fast greeting path → Return immediately         │  │  │
│  │  │  - If NO: Continue                                          │  │  │
│  │  └───────────────────────┬───────────────────────────────────┘  │  │
│  │                          │                                        │  │
│  │                          ▼                                        │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  CHECKPOINT 2: Conversational? (DUPLICATE CHECK)          │  │  │
│  │  │  - Patterns: conversational_patterns                       │  │  │
│  │  │  - If YES: Skip deep research, skip web research           │  │  │
│  │  │  - If NO: Continue                                          │  │  │
│  │  └───────────────────────┬───────────────────────────────────┘  │  │
│  │                          │                                        │  │
│  │                          ▼                                        │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  CHECKPOINT 3: Deep Research Routing?                     │  │  │
│  │  │  - If fast_mode: Only if explicit request                 │  │  │
│  │  │  - If deep_mode: Check forensic, mind-body, deep indicators│  │  │
│  │  │  - If YES: _handle_deep_research() → Return               │  │  │
│  │  │  - If NO: Continue to regular path                        │  │  │
│  │  └───────────────────────┬───────────────────────────────────┘  │  │
│  │                          │                                        │  │
│  │                          ▼                                        │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  CHECKPOINT 4: Needs Research?                             │  │  │
│  │  │  - _needs_research() checks patterns FIRST                │  │  │
│  │  │  - Conversational patterns → Return False (no LLM call)    │  │  │
│  │  │  - Deep indicators → Return True (no LLM call)              │  │  │
│  │  │  - Otherwise: LLM classification (slow path)               │  │  │
│  │  │  - If YES: Web search + parallel processing                │  │  │
│  │  │  - If NO: Skip research                                     │  │  │
│  │  └───────────────────────┬───────────────────────────────────┘  │  │
│  │                          │                                        │  │
│  │                          ▼                                        │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  BUILD ENHANCED PROMPT                                      │  │  │
│  │  │  - get_enhanced_prompt(query)                               │  │  │
│  │  │  - Includes: personality, voice, preset, memory context    │  │  │
│  │  └───────────────────────┬───────────────────────────────────┘  │  │
│  │                          │                                        │  │
│  │                          ▼                                        │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  CALL: model_client.chat()                                │  │  │
│  │  │  - model: self.model (from config)                        │  │  │
│  │  │  - input_text: message + context                           │  │  │
│  │  │  - enhanced_base: system prompt                            │  │  │
│  │  │  - options: temperature, num_predict, etc.                 │  │  │
│  │  └───────────────────────┬───────────────────────────────────┘  │  │
│  └──────────────────────────┼──────────────────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    OLLAMA (Local LLM Server)                            │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  POST /api/chat                                                  │  │
│  │  - Receives: messages array with system + user prompts          │  │
│  │  - Generates: response tokens                                    │  │
│  │  - Returns: {message: {content: "..."}}                        │  │
│  └───────────────────────┬─────────────────────────────────────────┘  │
└──────────────────────────┼────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    RESPONSE FLOW (Back to UX)                           │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  thesidia.process() → Returns: response string                   │  │
│  └───────────────────────┬─────────────────────────────────────────┘  │
│                          │                                              │
│                          ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  _stream_thesidia_response() → Streams response                │  │
│  │  - Chunks response into small pieces (chunk_size=3)              │  │
│  │  - Sends 'chunk' events via SSE                                  │  │
│  │  - Sends 'complete' event when done                              │  │
│  └───────────────────────┬─────────────────────────────────────────┘  │
│                          │                                              │
│                          ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  app.js: SSE EventSource → Receives chunks                       │  │
│  │  - 'progress' events → Update reasoning visualization            │  │
│  │  - 'chunk' events → Type text character-by-character              │  │
│  │  - 'thinking' events → Store for sources panel                   │  │
│  │  - 'complete' event → Add action buttons                         │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Message Type Routing Matrix

| Message Type | Server Check | Thesidia Check | Research? | Deep Research? | UX Message |
|-------------|--------------|----------------|-----------|----------------|------------|
| **Simple Greeting** ("hi") | ✅ Line 605 | ✅ Line 3512 | ❌ Skip | ❌ Skip | "Processing your query..." → Direct response |
| **Conversational** ("whats your favorite movie?") | ✅ Line 656 | ✅ Line 3717 | ❌ Skip | ❌ Skip | "Processing your query..." → Direct response |
| **Fast Mode + Regular** | ✅ Line 605, 656 | ✅ Line 3717, 3775 | ✅ If needed | ❌ Skip | "Processing query..." → "Searching..." (if needed) → Response |
| **Fast Mode + Explicit Deep** | ✅ Line 605, 656 | ✅ Line 3721, 3777 | ✅ Yes | ✅ Yes | "Detected forensic..." → Deep research → Response |
| **Deep Mode + Regular** | ✅ Line 605, 656 | ✅ Line 3717, 3780 | ✅ If needed | ✅ If indicators | "Processing query..." → "Searching..." → Response |
| **Deep Mode + Forensic** | ✅ Line 612 | ✅ Line 3732 | ✅ Yes | ✅ Yes | "Detected forensic..." → Deep research → Response |

## Current Issues Found

### 1. **DUPLICATE CHECKS** (Bandaid Fix)
- **Location**: `webapp/server.py` lines 605 and 649
- **Issue**: `is_simple_greeting` is checked twice
- **Impact**: Redundant computation, potential inconsistency
- **Fix**: Remove duplicate check at line 649

### 2. **DUPLICATE CONVERSATIONAL CHECK** (Bandaid Fix)
- **Location**: `webapp/server.py` line 656 AND `thesidia_hybrid_adaptive.py` line 3717
- **Issue**: Conversational patterns checked in both places
- **Impact**: Server checks but then Thesidia checks again
- **Fix**: Server should only check for UX messages, Thesidia does actual routing

### 3. **RESEARCH CHECK BEFORE PROCESS** (Ghost Code)
- **Location**: `webapp/server.py` line 634
- **Issue**: `thesidia._needs_research()` called BEFORE `thesidia.process()`
- **Impact**: Duplicate work - `process()` will check again
- **Fix**: Remove this check, let `process()` handle it

### 4. **PROGRESS EVENTS DON'T MATCH REALITY** (UX Mismatch)
- **Location**: `webapp/server.py` lines 596-695
- **Issue**: Progress events sent BEFORE actual processing happens
- **Impact**: UX shows "Processing..." but nothing is happening yet
- **Fix**: Move progress events to AFTER actual processing starts

### 5. **HARDCODED MESSAGE REMOVED BUT STILL IN .BAK** (Ghost Code)
- **Location**: `webapp/server.py.bak` line 571
- **Issue**: Backup file still has old message
- **Impact**: None (backup file), but cleanup needed
- **Fix**: Delete or update backup file

## Next 5 Messages: Expected Behavior

### Message 1: "hi"
- **Server**: Detects greeting (line 605) → Skips forensic
- **Thesidia**: Detects greeting (line 3512) → Fast path → Returns immediately
- **UX**: Shows "Processing your query..." → Response appears quickly
- **Research**: ❌ None
- **Deep Research**: ❌ None

### Message 2: "whats your favorite movie?"
- **Server**: Detects conversational (line 656) → Skips research check
- **Thesidia**: Detects conversational (line 3717) → Skips deep research → Skips research
- **UX**: Shows "Processing your query..." → Direct response
- **Research**: ❌ None
- **Deep Research**: ❌ None

### Message 3: "what is consciousness?" (Fast Mode)
- **Server**: Not greeting, not conversational → Checks forensic (line 612) → May detect
- **Thesidia**: Not greeting, not conversational → Checks deep routing (line 3775) → Fast mode → Only if explicit
- **UX**: Shows "Processing query..." → "Searching..." (if research needed) → Response
- **Research**: ✅ If `_needs_research()` returns True
- **Deep Research**: ❌ Skip (fast mode, not explicit)

### Message 4: "deep research: what is consciousness?" (Fast Mode)
- **Server**: Not greeting, not conversational → Checks forensic
- **Thesidia**: Detects explicit deep research (line 3721) → Routes to deep research
- **UX**: Shows "Detected forensic..." → Deep research → Response
- **Research**: ✅ Yes
- **Deep Research**: ✅ Yes (explicit request)

### Message 5: "what is consciousness?" (Deep Mode)
- **Server**: Not greeting, not conversational → Checks forensic (line 612) → Detects
- **Thesidia**: Not greeting, not conversational → Checks deep routing (line 3780) → Deep mode → Detects forensic → Routes to deep
- **UX**: Shows "Detected forensic..." → Deep research → Response
- **Research**: ✅ Yes
- **Deep Research**: ✅ Yes (automatic in deep mode)

## Consistency Guarantees

1. **No Mismatch**: UX messages match actual processing state
2. **No Duplicates**: Each check happens once, in the right place
3. **No Ghost Code**: All checks are necessary and used
4. **No Bandaids**: All fixes are proper architectural solutions
