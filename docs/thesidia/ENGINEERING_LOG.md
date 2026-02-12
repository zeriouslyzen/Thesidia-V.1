# Thesidia Engineering Log

A reasoning journal documenting how and why each major decision was made during the v1-v3 development arc. Written from the perspective of the engineering process, not the marketing narrative.

---

## Session 1: Initial Assessment

**Problem presented:** "Something is off about how Thesidia is answering."

**First observation:** The codebase is a 5,800-line monolith (`thesidia_hybrid_adaptive.py`) with deeply nested control flow. The `process()` method contains routing logic, research orchestration, personality injection, synthesis, and response formatting all interleaved. There is no clear separation between "decide what to do" and "do it."

**Second observation:** A `fast_mode` boolean controlled almost everything. When true (which was most of the time), it:
- Downgraded the model
- Set a 20-30 second hard timeout
- Skipped research entirely for many query types
- Simplified the synthesis prompt

The result: most user queries got a degraded experience, and "Auto" mode was functionally identical to "don't try very hard."

**Decision:** Replace the `fast_mode` boolean with an explicit mode system. Four modes -- auto, research, conversational, stream -- each with defined behavior contracts. No more hidden degradation.

---

## Session 2: The Modelfile Discovery

**Problem:** Responses had inconsistent personality. Sometimes formal, sometimes casual, sometimes leaking system prompt artifacts.

**Discovery:** `src/thesidia_modelfile.py` contains 14 voice personalities and 9 personas, adapted from a Grok-like architecture. This personality system was always active but fighting with the research synthesis prompts. When the LLM received conflicting instructions ("be a casual friend" + "perform forensic analysis"), the output was incoherent.

**Decision:** Separate conversational mode entirely from research mode. In conversational mode, the personality module drives the response. In research mode, the personality is suppressed in favor of structured analytical prompting. This is how Grok handles it -- the personality layer activates for chat, but Deep Search mode is a completely different pipeline.

---

## Session 3: The Timeout Problem

**Symptom:** Users kept seeing "Processing timed out (fast mode limited to 30s)."

**Root cause:** The timeout was implemented as a `ThreadPoolExecutor` with a 30-second `future.result(timeout=30)`. This was applied to ALL queries in auto mode, including ones that legitimately needed web search. A search taking 3 seconds + LLM synthesis taking 28 seconds = timeout.

**The deeper issue:** The timeout existed because the original developer wanted a "fast" experience, but 30 seconds is an arbitrary number that doesn't correspond to any actual processing stage. Perplexity takes 5-15 seconds for a research query. Grok takes 15-60 seconds for DeepSearch. The timeout should be per-mode, not global.

**Decision:**
- Auto mode: 120-second timeout (enough for search + synthesis)
- Research mode: no timeout (let it run)
- Conversational: inherently fast (no search), no timeout needed
- The old 30s timeout was the single biggest usability bug in the system

---

## Session 4: The Search Engine Gap

**Analysis method:** Cross-examined Thesidia's architecture against publicly available information about Perplexity and Grok's search infrastructure.

**Findings:**
- Perplexity runs its own search index (Vespa.ai + Qdrant), executes multi-stage RAG, and uses RL-trained tool-use agents for query decomposition
- Grok uses xAI's own search infrastructure with real-time X (Twitter) integration
- Thesidia was using a single `WebSearchEngine` class that called SearXNG serially with 5-result limits

**Gap analysis:**
| Capability | Perplexity | Grok | Thesidia (v1) |
|-----------|-----------|------|--------------|
| Parallel search | Yes (custom index) | Yes (proprietary) | No (serial, single source) |
| Source diversity | 5+ engines | Proprietary + X | 1 engine (SearXNG) |
| Query classification | ML-based | ML-based | Regex + LLM (slow) |
| Result reranking | Learned ranker | Learned ranker | None |
| Search latency | <2s | <3s | 5-10s |

**Decision:** Build a multi-source parallel search layer from scratch. Four engines (Brave, DuckDuckGo, SearXNG, Wikipedia) queried simultaneously via `ThreadPoolExecutor`. Rule-based classifier (zero LLM latency). Deduplication and reranking with domain caps and relevance scoring.

**Result:** Search latency dropped from 5-10s to 2.6s. Source count went from 2-3 to 8-10 per query. Source diversity improved dramatically (multiple domains instead of all from one engine).

---

## Session 5: DuckDuckGo Redirect Bug

**Symptom:** During benchmarking, quick search returned an average of 1.0 results despite DuckDuckGo returning 10 raw results.

**Investigation:** The HTML scraper was extracting URLs from DuckDuckGo results, but the URLs were all `duckduckgo.com/l/?uddg=...` redirect links. The reranker saw 10 results all from `duckduckgo.com` domain and capped them to 1 (max 2 per domain).

**Fix:** Parse the `uddg` query parameter from the redirect URL to extract the actual destination URL. This is a known DuckDuckGo behavior -- they wrap all outbound links in their own redirect for tracking.

**Lesson:** Always test the full pipeline end-to-end, not just individual components. The scraper "worked" (returned 10 results), the reranker "worked" (correctly capped domains), but the composition was broken.

---

## Session 6: Wikipedia 403 Errors

**Symptom:** Wikipedia API returning 403 Forbidden during benchmark.

**Root cause:** The Wikipedia REST API requires a descriptive User-Agent header. The default `python-requests` header gets blocked. This is documented in Wikipedia's API usage policy but easy to miss.

**Fix:** Added `ThesidiaResearchEngine/2.0 (research project; contact@thesidia.dev)` as User-Agent. Resolved immediately.

**Lesson:** Free APIs have soft requirements that aren't enforced by HTTP status codes until they are. Always set proper User-Agent headers.

---

## Session 7: The Frontend Disconnect

**Problem:** The v1 UI had no idea what the backend was doing. A search could take 30 seconds and the user saw... nothing. Or a blinking cursor. Or a static "Analyzing query..." text that never changed.

**Root cause:** The SSE streaming sent `progress` events with static messages like "Processing your query..." and "Responding..." -- but these were written at the server layer before `process()` was called. They didn't reflect actual backend activity.

**Decision for v3:**
1. SSE `progress` events now carry the actual phase name and percentage
2. New `sources` SSE event transmits real URLs/titles/snippets after search completes
3. Frontend routing status bar shows this data in real-time
4. Triangle grid animation state advances with progress: searching -> ranking -> synthesizing
5. On first text chunk arriving, routing status fades and grid returns to idle

**This is what Perplexity does right.** When you ask Perplexity something, you see "Searching 5 sources..." with actual domain names appearing. Then "Reading reuters.com..." Then the response streams. The user sees the work happening. Thesidia now has this same feedback loop.

---

## Session 8: CSS Isolation Decision

**Problem:** The chat interface was styled by `styles.css`, a 11,000+ line file that also styled landing pages, profile pages, settings pages, KIM messaging, and social feeds. Any change to the chat broke something else. The chat used indigo accent (`#6366f1`) while the brand uses gold (`#ffd700`).

**Decision:** Complete CSS isolation. New files scoped under `#thesidia-app` and `#thesidia-mini`. The `all: initial` reset on the root container ensures zero inheritance from site styles. The chat could now be redesigned without touching any other page.

**Trade-off:** Some duplication of basic reset styles. Accepted because the isolation guarantee is worth more than DRY CSS across unrelated page contexts.

---

## Session 9: Triangle Grid vs Generic Animations

**Requirement:** "We need our own beast -- like Grok's square grid but ours."

**Options considered:**
1. Canvas-based particle system -- rejected (too heavy, not CSS-animatable, accessibility concerns)
2. Lottie/After Effects export -- rejected (external dependency, not inline-controllable)
3. WebGL shader -- rejected (overkill, not progressive, breaks on many mobile browsers)
4. Inline SVG with CSS keyframes -- selected (lightweight, progressive, fully controllable from JS state machine, accessible)

**Implementation:** Tessellated triangle mesh (12x8, ~96 triangles) generated programmatically. Each vertex gets an animation delay calculated from its distance to the center point, creating a wave propagation effect. State transitions happen by adding/removing CSS classes on the `#thesidia-app` root, which cascades to all SVG elements via descendant selectors.

**Performance budget:** ~50 SVG elements animated via `fill` and `stroke` transitions. No JavaScript animation loop. GPU-compositable. Measured < 2ms per frame on M1.

---

## Unresolved Issues (Honest Assessment)

1. **Conversational mode leaks.** The "hows it going" test showed emoji, crypto mentions, and coaching artifacts. The personality module needs hard guardrails against emitting: emojis, unrequested topic suggestions, system prompt fragments, and research methodology hints.

2. **Ollama model quality ceiling.** The local LLM (clean-mistral) is not competitive with GPT-4, Claude, or even Grok's base model for synthesis quality. The search infrastructure can find great sources, but the synthesis step is bottlenecked by model capability. This is the fundamental trade-off of local-only operation.

3. **Single-threaded synthesis.** `process()` is synchronous. While search is parallel, the synthesis LLM call blocks the thread. For a production system, this needs to be async with proper request queuing.

4. **No persistent search cache.** Every identical query re-executes the full search. A TTL-based cache (even 5 minutes) would eliminate redundant searches during iterative research sessions.
