# Thesidia Architecture

## System Overview

Thesidia is a multi-stage research pipeline, not a single LLM wrapper. Every query passes through classification, optional web search, synthesis, and streaming. The system is designed to run with zero external API dependencies (local Ollama LLM + DuckDuckGo scraping) but scales up when additional services are available (Brave API, SearXNG).

```
                          USER QUERY
                              |
                    +---------v---------+
                    |   Flask Server    |
                    |   (server.py)     |
                    +-------|----------+
                            |
                    +-------v----------+
                    |  Mode Router     |
                    |  auto/research/  |
                    |  conversational/ |
                    |  stream          |
                    +-------|----------+
                            |
              +-------------+-------------+
              |                           |
    +---------v---------+     +-----------v-----------+
    |  Conversational   |     |   Research Pipeline   |
    |  (personality +   |     |                       |
    |   LLM direct)     |     |  1. QueryClassifier   |
    |                   |     |  2. MultiSearch        |
    +---------|---------+     |  3. ResultReranker     |
              |               |  4. DataSynthesizer    |
              |               |  5. CognitiveFramework |
              |               +-----------|-----------+
              |                           |
              +-------------+-------------+
                            |
                    +-------v----------+
                    |  SSE Streaming   |
                    |  progress ->     |
                    |  sources ->      |
                    |  chunks ->       |
                    |  complete        |
                    +----------|-------+
                               |
                    +----------v---------+
                    |   Frontend (v3)    |
                    |   Routing status   |
                    |   Triangle grid    |
                    |   Source blocks    |
                    |   Notebook panel   |
                    +--------------------+
```

---

## Component Map

### 1. Flask Server (`webapp/server.py`)

Entry point. Handles HTTP routing, authentication, SSE streaming.

**Key function**: `_stream_thesidia_response()` -- The SSE generator that:
- Classifies the query for UX feedback (greeting vs forensic vs regular)
- Calls `thesidia.process()` which does all actual work
- Extracts `_last_search_sources` from the engine after processing
- Emits SSE events: `progress`, `sources`, `chunk`, `complete`, `error`
- Streams response text in 3-character chunks for typing animation

**Important**: The server layer does NOT do routing or research. It only provides UX progress messages while `process()` runs. Actual routing happens inside the core engine.

### 2. Core Engine (`src/thesidia_hybrid_adaptive.py`)

~5,800 lines. The brain. Responsible for:

**`process()`** -- Main entry point.
- Validates mode parameter
- Routes to `_process_original()` (auto/research), conversational handler, or `stream_analyze()`
- Applies mode-based timeouts (120s auto, None research)
- Returns `{"output": str, "metadata": dict, "status": "completed"}`

**`_process_original()`** -- The primary processing pipeline:
1. Typo correction
2. Greeting detection (short-circuits to fast response)
3. Conversational pattern detection
4. Forensic routing check (via `detect_forensic_routing()`)
5. Research need assessment (via `_needs_research()`)
6. If research needed: `MultiSearch.quick_search()` or legacy `parallel_processor`
7. Personality context assembly
8. Capability context assembly
9. LLM synthesis call via `ModelClient`
10. Response cleanup (meta-commentary stripping)
11. Cognitive framework storage (cache findings for reuse)

**`_handle_deep_research()`** -- Deep research path:
1. Check cognitive framework for cached findings
2. Refine query based on user interests
3. `MultiSearch.deep_search()` (up to 15 results)
4. If results found: full synthesis with `DataSynthesizer`
5. If Gnostic Blade format requested: structured `::EXPOSURE::` output
6. Store findings in cognitive framework for future queries

### 3. Search Layer (`src/search/`)

**`QueryClassifier`** -- Rule-based, zero-latency query categorization:
- `greeting` -- "hi", "hello", "hey" (2 words or fewer)
- `conversational` -- "what do you think", "tell me a random", "how are you"
- `factual_quick` -- "what is X", "define Y", "who is Z"
- `deep_research` -- "origins of", "hidden history", "power structures", "trace the"
- `technical` -- "implement", "code", "algorithm", "debug"

**`MultiSearch`** -- Parallel fan-out search:
- Uses `ThreadPoolExecutor(max_workers=4)` to query all engines simultaneously
- Engines: Brave (API), DuckDuckGo (HTML scrape), SearXNG (local metasearch), Wikipedia (REST API)
- `quick_search()`: 8 results max, for auto mode
- `deep_search()`: 20 results max, wider net, for research mode
- Results normalized to `{"url", "title", "snippet", "source"}` schema

**`ResultReranker`** -- Post-search quality filter:
- URL normalization (strip tracking params, trailing slashes)
- Domain extraction and per-domain cap (max 2 results per domain)
- Scoring: title/snippet word overlap with query, source trust tier, freshness bonus
- Deduplication by normalized URL

### 4. Synthesis (`src/synthesis/data_synthesizer.py`)

Takes raw search results + query and produces a synthesized response.

- Constructs a system prompt with evidence passages
- Calls Ollama LLM with structured instructions
- Gnostic Blade format: `::EXPOSURE::`, `::ETYMOLOGICAL INCISION::`, `::PATTERN RECOGNITION::`, `::TRANSMISSION::`
- Natural format: prose paragraphs with inline source references
- Token limit calculation based on query complexity

### 5. Frontend (`webapp/`)

**Message lifecycle:**
1. User types in `th-prompt-input`, presses Enter
2. `sendMessage()` fires: hero hides, chat activates, routing status appears, grid animates
3. `callThesidiaAPI()` opens fetch stream to `/api/thesidia`
4. SSE events arrive:
   - `progress` -> updates routing status bar text + progress fill
   - `sources` -> stores sources, updates routing text ("Found 10 sources"), populates notebook
   - `chunk` -> appends text to message body, hides routing status on first chunk
   - `complete` -> appends source block to message, adds action buttons
5. Grid animation transitions: searching -> ranking -> synthesizing -> complete -> idle

**Isolation strategy:** All chat styles scoped under `#thesidia-app`. All mini-chat styles under `#thesidia-mini`. Neither can leak to or from site-wide `styles.css`.

---

## Data Flow: Research Query

```
User: "what is happening in brazil today 2026"
  |
  v
[server.py] POST /api/thesidia
  |-- SSE: progress "Processing your query..." (5%)
  |-- SSE: progress "Processing query..." (30%)
  |
  v
[thesidia_hybrid_adaptive.py] process()
  |-- mode="auto", routes to _process_original()
  |-- _needs_research() -> True (question about current events)
  |-- Keyword match -> needs_forensic_analysis=True
  |-- Routes to _handle_deep_research()
  |
  v
[multi_search.py] deep_search("what is happening in brazil today 2026")
  |-- ThreadPoolExecutor fires:
  |   |-- brave_search()   -> 0 results (no API key)
  |   |-- duckduckgo()     -> 10 results
  |   |-- searxng()        -> 0 results (no instance)
  |   |-- wikipedia()      -> 2 results
  |-- Merge: 12 raw results
  |-- Reranker: deduplicate, domain-cap, score -> 10 ranked
  |-- Store in self._last_search_sources
  |-- Return research_data (2.6s)
  |
  v
[data_synthesizer.py] synthesize(sources=research_data, query=...)
  |-- Build evidence passages from top results
  |-- Construct system prompt with ::EXPOSURE:: format instructions
  |-- Call Ollama (clean-mistral:latest)
  |-- Return synthesis (3,406 chars)
  |
  v
[thesidia_hybrid_adaptive.py]
  |-- Cognitive framework stores 6 findings
  |-- Return {"output": "::EXPOSURE::...", length: 5,796}
  |
  v
[server.py]
  |-- _strip_general_framework_block(response)
  |-- SSE: sources [{url, title, snippet, source}, ...]
  |-- SSE: progress "Streaming response... (10 sources found)" (50%)
  |-- SSE: chunk "::E" ... chunk "XPO" ... chunk "SUR" ... (3 chars each)
  |-- SSE: complete
  |
  v
[app.js]
  |-- Routing status shows "Found 10 sources, synthesizing..."
  |-- Triangle grid pulses gold
  |-- Text streams into message body
  |-- Source block appended with numbered citations
  |-- Notebook Sources tab populated
```

---

## Dependency Chain

```
Ollama (local LLM)          -- REQUIRED for any response generation
DuckDuckGo (HTML scrape)    -- REQUIRED for web search (free, no key)
Brave Search API             -- OPTIONAL (set BRAVE_API_KEY for higher quality)
SearXNG (local metasearch)   -- OPTIONAL (run locally for additional source diversity)
Wikipedia REST API           -- ACTIVE (free, factual baseline)
WebLLM (browser)             -- OPTIONAL (client-side inference when server unavailable)
```

No cloud LLM APIs are used. No OpenAI, no Anthropic, no Google. Everything runs through Ollama with local models. This is a deliberate architectural choice for sovereignty, privacy, and cost.
