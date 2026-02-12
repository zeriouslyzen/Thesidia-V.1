# Thesidia Changelog

All notable architectural, behavioral, and interface changes to the Thesidia subsystem.

---

## v3.0 -- UX Overhaul & Source Surfacing (2026-02-12)

### Frontend -- Complete Interface Rebuild

**New files:**
- `webapp/css/tokens.css` -- Shared design token system (Cursor-dark palette, Katanx gold `#ffd700` / blue `#00d4ff`, Inter + Inconsolata typography, 4px spacing grid, transition curves, z-index scale)
- `webapp/css/thesidia-chat.css` -- Full chat stylesheet scoped under `#thesidia-app`. Zero bleed to/from other site pages. Covers header, mode selector, welcome hero, message threading, routing status, prompt bar, notebook drawer, responsive breakpoints.
- `webapp/css/thesidia-mini.css` -- Mini-chat widget scoped under `#thesidia-mini`. FAB button, expandable drawer, compact message thread.
- `webapp/js/thesidia-animations.js` -- Triangle grid SVG generator (12x8 tessellated mesh, ~96 triangles, wave-propagation delay from center). Gear SVG generator (two interlocking counter-rotating gears). State machine: idle/searching/ranking/synthesizing/complete.
- `webapp/js/thesidia-mini.js` -- Self-contained floating chat widget for platform-wide embedding. Auto-injects on non-chat pages.

**Modified files:**
- `webapp/index.html` / `webapp/app.html` -- Complete body rewrite. Old `#app` root replaced with `#thesidia-app`. New: welcome hero with prompt chips, `th-header` with pill mode selector, `th-chat` area with routing status + typing indicator, `th-notebook` drawer, `th-prompt-container`, conversation sidebar. All legacy orb/glow markup removed.
- `webapp/app.js` -- `initHeaderToolbar()` rewritten for v3 DOM (triangle grid init, prompt chip handlers, send button ready state, settings dropdown). `addMessage()` rewritten with v3 structure (`th-msg`, `th-msg-user`, `th-msg-ai`, gold-dot label, inline actions). Added `showRoutingStatus()`, `updateRoutingStatus()`, `hideRoutingStatus()`. Added `renderSourceBlock()` and `populateNotebookSources()`. SSE handler now routes `progress` events to v3 routing bar and `sources` events to message source blocks + notebook. `setMode()` updated for both v2/v3 class names. Streaming message creation uses v3 markup. Fixed `sendMessage()` -> `handleSend()` reference in chip handlers.
- `webapp/styles.css` -- Added `@import url('./css/tokens.css')` at top.

### Backend -- Source Surfacing & Response Cleanup

- `src/thesidia_hybrid_adaptive.py` -- Added `self._last_search_sources` storage in both `_process_original()` (quick search path) and `_handle_deep_research()` (deep search path). After MultiSearch returns results, URLs/titles/snippets are captured for frontend consumption.
- `webapp/server.py` -- Streaming function now emits `sources` SSE event after `process()` returns, containing up to 10 source objects. Enhanced `_strip_general_framework_block()` to strip "Business Framework:", "Market Research:", "MVP:", "Launch:", "I can also:" blocks, and "As an AI" disclaimers.

### Visual Design

- Cursor-aligned dark theme (`#0a0a0a` base, `#111` panels, `#1a1a1a` cards)
- Katanx brand accents (gold `#ffd700`, blue `#00d4ff`)
- Triangle grid signature animation (replaces generic orb effects)
- Professional message threading with gold-dot labels, 15px Inter, left-aligned
- Source blocks with numbered citations, domain links, collapsible overflow
- Routing status bar with real-time SSE-driven text and gold progress fill

---

## v2.0 -- Search Engine Overhaul (2026-02-11)

### New Module: `src/search/`

Created a complete multi-source parallel search layer:

- `src/search/__init__.py` -- Package exports
- `src/search/multi_search.py` -- Central aggregator. Fan-out to Brave, SearXNG, DuckDuckGo, Wikipedia via `ThreadPoolExecutor`. Merge, deduplicate, rerank. `quick_search()` for auto mode (8 results), `deep_search()` for research mode (20 results). Fixed DuckDuckGo redirect URL parsing.
- `src/search/brave_search.py` -- Brave Web Search API wrapper with structured result extraction.
- `src/search/wikipedia_search.py` -- Wikipedia REST API (search + page summary). Fixed 403 errors by adding descriptive User-Agent header.
- `src/search/query_classifier.py` -- Fast rule-based query router. Categories: greeting, conversational, factual_quick, deep_research, technical. No LLM call -- pure regex decision tree.
- `src/search/reranker.py` -- Deduplication (URL normalization), per-domain cap (max 2), scoring by title/snippet relevance overlap, source trust tiers, freshness extraction.

### Core Changes

- `src/thesidia_hybrid_adaptive.py`:
  - Removed 30-second fast-mode timeout entirely
  - Replaced with mode-based timeouts: 120s for `auto`, None for `research`
  - Simplified `effective_fast_mode` logic
  - Replaced `parallel_processor.process_parallel()` with `multi_search.quick_search()` for auto mode
  - Replaced `_handle_deep_research()` internals with `multi_search.deep_search()`
  - Fixed `stream_analyze()` bug (wrong method call on `deep_research_engine`)

### Testing

- `scripts/tests/search_benchmark.py` -- Benchmark harness testing classifier accuracy, quick search latency/result count, deep search coverage, and end-to-end API pipeline.

---

## v1.5 -- Mode System & UI Overhaul (2026-02-10)

### Mode Architecture

- Introduced explicit `mode` parameter: `auto`, `research`, `conversational`, `stream`
- Backend `process()` method routes based on mode instead of `fast_mode` boolean
- Conversational mode skips all research, uses personality module directly
- Research mode forces deep search with no timeout
- Stream mode handles social post analysis (fact-checking, truth verification)

### Frontend -- First UI Overhaul

- Header toolbar with mode selector (Auto/Research/Chat)
- Settings dropdown (thinking steps, voice, edge AI model selection)
- Research notebook panel (right drawer with Sources/Findings/Notes tabs)
- Voice toggle (Web Speech API TTS)
- Edge AI integration (WebLLM model loading, client-side inference path)
- Server health check with fallback to edge-only mode

### Edge AI (Client-Side)

- `webapp/edge_inference.js` -- WebLLM integration for browser-based inference
- Tiered model system: Qwen 2.5 3B (high), Llama 3.2 3B (medium), Llama 3.2 1B (light)
- VRAM detection for automatic model selection
- Server health check triggers edge-only mode when backend unavailable

---

## v1.0 -- Foundation (pre-2026-02-10)

### Core Engine

- `src/thesidia_hybrid_adaptive.py` -- Monolithic orchestrator with hybrid routing
- Sophia Memory System (7-layer gnostic map)
- Gnostic Blade Protocol (`::EXPOSURE::`, `::ETYMOLOGICAL INCISION::`, `::TRANSMISSION::`)
- Cognitive framework for storing/reusing information threads across queries
- Quality metrics tracker (`depth`, `pattern_recognition`, `truth_seeking`, `overall`)
- Personality system via `thesidia_modelfile.py` (14 voice personalities, 9 personas)

### Research

- `src/deep_research_engine.py` -- Single-source web search (DuckDuckGo only)
- `src/synthesis/data_synthesizer.py` -- Evidence-to-prose synthesis
- `src/synthesis/truth_engine.py` -- Claim verification

### Platform Integration

- Flask server with streaming SSE
- KIM messaging system
- Social platform (Katanx) with feed, bot generation, AI quality scoring
