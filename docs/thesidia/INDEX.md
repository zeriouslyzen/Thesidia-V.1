# Thesidia -- Documentation Index

**Subsystem**: Deep Research Engine & Conversational AI  
**Platform**: Katanx  
**Maintainer**: Jack Danger  
**Last Updated**: 2026-02-12  

---

## Documents

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System topology, data flow diagrams, component map, module responsibilities |
| [CHANGELOG.md](CHANGELOG.md) | Version history from v1 through v3 -- every structural change logged |
| [ENGINEERING_LOG.md](ENGINEERING_LOG.md) | Reasoning journal -- why decisions were made, what failed, what was learned |
| [V4_ROADMAP.md](V4_ROADMAP.md) | Next-generation plan with prioritized gaps, proposed solutions, and effort estimates |
| [COMPETITIVE_ANALYSIS.md](COMPETITIVE_ANALYSIS.md) | Raw honest assessment of Thesidia vs Perplexity, Grok, ChatGPT Search, Gemini Deep Research |
| [OPENCLAW_RESEARCH_AND_THESI_AGENT.md](OPENCLAW_RESEARCH_AND_THESI_AGENT.md) | OpenClaw (2026) research, lessons for Thesidia, and Thesi as a separate agentic-only agent |
| [CURRENT_FIRST_AGENTIC_STACK.md](CURRENT_FIRST_AGENTIC_STACK.md) | Unified stack (all features + currentness layer): as_of, freshness, stale/supersede; solves outdated material |
| [AI_STACK_ADVANCES_AND_DIRECTION.md](AI_STACK_ADVANCES_AND_DIRECTION.md) | What actually advanced (algorithms) vs hype; map of your early work to today; concrete direction |
| [BEYOND_CLAW_RESEARCH_DIRECTION.md](BEYOND_CLAW_RESEARCH_DIRECTION.md) | What Claw is in research terms; what research is past Claw (verification, long-horizon, multi-agent, reflection); what to explore |

---

## Quick Reference

### What Thesidia Is

Thesidia is a hybrid research-and-conversational AI engine. It is not a wrapper around a single LLM API. It is a multi-stage pipeline that:

1. **Classifies** incoming queries (greeting, factual, forensic, conversational, deep research)
2. **Searches** the open web in parallel across multiple engines (Brave, DuckDuckGo, SearXNG, Wikipedia)
3. **Deduplicates and reranks** results by relevance, source trust, and freshness
4. **Synthesizes** a response by feeding real search evidence into a local LLM (Ollama) with structured prompting
5. **Streams** the response token-by-token with real-time routing status updates
6. **Optionally runs client-side** via WebLLM for offline/edge inference

### Where Thesidia Lives in the Codebase

```
src/
  thesidia_hybrid_adaptive.py    -- core orchestrator (process(), routing, synthesis)
  search/                        -- v2 multi-source search layer
    multi_search.py              -- parallel fan-out to Brave/DDG/SearXNG/Wikipedia
    query_classifier.py          -- rule-based query routing (no LLM call)
    reranker.py                  -- dedup, domain cap, relevance scoring
    brave_search.py              -- Brave Web Search API wrapper
    wikipedia_search.py          -- Wikipedia REST API wrapper
  deep_research_engine.py        -- legacy deep research (still used for scraping)
  synthesis/
    data_synthesizer.py          -- evidence-to-prose synthesis engine
    truth_engine.py              -- claim verification
  thesidia_modelfile.py          -- personality presets (14 voices, 9 personas)
  quality_metrics_tracker.py     -- response quality tracking

webapp/
  server.py                      -- Flask API, SSE streaming, route handlers
  index.html / app.html          -- v3 chat interface
  app.js                         -- frontend logic (message rendering, SSE, routing status)
  edge_inference.js              -- WebLLM client-side inference
  css/
    tokens.css                   -- design tokens (palette, typography, spacing)
    thesidia-chat.css            -- chat UI (scoped #thesidia-app)
    thesidia-mini.css            -- mini-chat widget (scoped #thesidia-mini)
  js/
    thesidia-animations.js       -- triangle grid + gear SVG animations
    thesidia-mini.js             -- floating mini-chat widget
```

### Modes

| Mode | Behavior |
|------|----------|
| `auto` | Classifies query, routes to conversational or research automatically |
| `research` | Forces deep multi-source search, no timeout, full synthesis |
| `conversational` | Personality-driven response, no web search, fast |
| `stream` | Post/content analysis mode for social platform integration |

### Current Search Engine Status

| Engine | Status | Notes |
|--------|--------|-------|
| DuckDuckGo | Active | HTML scraping, always available, no API key |
| Brave Search | Inactive | Requires `BRAVE_API_KEY` env var |
| SearXNG | Inactive | Requires local instance at `localhost:8080` |
| Wikipedia | Active | REST API, free, factual baseline |
