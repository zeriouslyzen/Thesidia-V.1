# Thesidia v4 Roadmap

What v4 should be, based on everything learned building v1 through v3. Prioritized by impact, with honest effort estimates.

---

## Tier 1: Critical (Ship-blocking)

### 1.1 Conversational Mode Guardrails

**Problem:** Greetings like "how's it going" return emoji, unprompted topic suggestions, leaked coaching text ("Next checks: Check recent research on..."), and meta-commentary. This makes Thesidia look broken even when the research pipeline works perfectly.

**Solution:**
- Hard post-processing filter on conversational responses: strip emojis, strip lines starting with "Next checks:", "I can also:", "As an AI"
- Constrain conversational system prompt to 200 tokens max -- remove all research/analysis instructions
- Add response length cap for greetings (max 100 tokens for "hi"/"hello"/"hey")
- Test suite: 20 conversational prompts that must pass format validation

**Effort:** 1-2 days  
**Impact:** Eliminates the most visible user-facing bug

### 1.2 Gnostic Blade Protocol Rendering

**Problem:** Responses start with `::EXPOSURE::` as raw text. These protocol tags are meaningful structural markers but render as gibberish to users who don't know the format.

**Solution:**
- Frontend parser in `formatMessage()` that detects `::TAG::` patterns
- Render as styled section headers: gold accent bar, uppercase Inconsolata, subtle animation on appearance
- Map known tags: EXPOSURE (findings), ETYMOLOGICAL INCISION (word origin analysis), PATTERN RECOGNITION (connections), TRANSMISSION (conclusion/synthesis)
- Fallback: unknown tags render as muted headers

**Effort:** 1 day  
**Impact:** Transforms research responses from "weird text" to "professional structured analysis"

### 1.3 Search Cache (TTL-based)

**Problem:** Identical queries re-execute the full search pipeline. During iterative research ("tell me more about X"), the same sources get fetched repeatedly.

**Solution:**
- LRU cache on `MultiSearch.quick_search()` and `deep_search()` keyed on normalized query
- 5-minute TTL (fresh enough for most research sessions)
- Cache hit returns stored results instantly, skipping network entirely
- Display "[cached]" indicator in routing status when cache is used

**Effort:** 0.5 days  
**Impact:** Repeat queries go from 3s to <100ms. Follow-up questions feel instant.

---

## Tier 2: High Value

### 2.1 Model Upgrade Path

**Problem:** Ollama's `clean-mistral` is the synthesis bottleneck. The search finds excellent sources, but the model's ability to reason over them and produce structured output is limited compared to frontier models.

**Solution path:**
- Short-term: Switch to `mistral-nemo:12b` or `qwen2.5:7b` for synthesis (better instruction following)
- Medium-term: Try `deepseek-r1:8b` for research synthesis (strong reasoning, open weights)
- Long-term: Optional hybrid mode where synthesis can use a cloud API (OpenRouter, Together) for users who opt in, while keeping search and routing fully local
- Benchmark harness: compare 5 models on 20 research prompts, score by factual accuracy, citation quality, coherence, and protocol adherence

**Effort:** 2-3 days (benchmarking + integration)  
**Impact:** The single highest-leverage change for response quality

### 2.2 Brave API Activation

**Problem:** Brave Search returns 0 results because `BRAVE_API_KEY` is not set. This means all research runs on DuckDuckGo alone.

**Solution:**
- Set `BRAVE_API_KEY` in environment / `.env` file
- Brave free tier: 2,000 queries/month -- sufficient for development and light usage
- Brave returns structured JSON (no HTML scraping), higher quality snippets, and different result rankings than DuckDuckGo
- Cross-referencing Brave + DuckDuckGo results produces significantly more robust evidence

**Effort:** 10 minutes (env var) + monitoring  
**Impact:** Source diversity doubles overnight

### 2.3 Async Processing Pipeline

**Problem:** `process()` is synchronous. The Flask thread blocks during the entire search + synthesis cycle. Under concurrent load, requests queue behind each other.

**Solution:**
- Wrap `process()` in `asyncio.to_thread()` or use Celery/RQ for background processing
- SSE connection stays open, polling a result store
- Or: migrate to FastAPI (native async) and use `StreamingResponse`

**Effort:** 3-5 days (FastAPI migration is cleanest but largest)  
**Impact:** Enables concurrent users, production-grade scalability

---

## Tier 3: Differentiation

### 3.1 Follow-Up Intelligence

**Problem:** Each query is independent. "Tell me more about that" has no context about what "that" refers to.

**Solution:**
- Maintain a session-level context window (last 3 queries + their search results)
- When a follow-up is detected (pronouns, "more about", "expand on"), inject previous query context
- Cognitive framework already stores findings -- extend it to also store the conversation thread
- This is how Perplexity's "Ask follow-up" works and it is the primary retention mechanism

**Effort:** 2-3 days  
**Impact:** Transforms one-shot research into a research session. Major UX differentiator.

### 3.2 URL Scraping + Full-Text Analysis

**Problem:** Search results only contain snippets (100-200 chars). The LLM synthesizes from snippets, not full articles. Perplexity scrapes the top 5-10 URLs and feeds full text to the model.

**Solution:**
- After reranking, scrape top 5 URLs (already partially implemented in `MultiSearch.scrape_urls()`)
- Extract article text using `readability-lxml` or `trafilatura`
- Feed first 2,000 chars of each article into the synthesis prompt
- This dramatically improves synthesis quality because the model has real evidence, not just search snippets

**Effort:** 2 days  
**Impact:** Closes the biggest quality gap with Perplexity

### 3.3 NotebookLM-Style Data Playground

**Problem:** The Notebook panel exists but is passive. It shows sources and notes but doesn't let users interact with the data.

**Solution:**
- "Ask about this source" -- click a source card, ask a follow-up question scoped to that source
- "Compare sources" -- select 2-3 sources, get a synthesis of agreements/contradictions
- "Export" -- download research as structured markdown with citations
- Audio summary -- use Web Speech API to generate a podcast-style overview (NotebookLM's killer feature)
- Drag-and-drop source reordering for manual curation

**Effort:** 5-7 days  
**Impact:** Transforms Thesidia from "search tool" to "research workspace." This is the product vision.

### 3.4 Stream Mode Integration

**Problem:** Stream mode (social post fact-checking) exists but isn't surfaced in the UI. The Katanx social platform could show Thesidia analysis inline on posts.

**Solution:**
- Floating analysis badge on social feed posts ("Thesidia verified: 3 claims checked")
- Click to expand: see claim-by-claim verification with sources
- Real-time fact-checking on trending content
- This is unique -- no other platform has an AI research engine embedded in a social feed

**Effort:** 5-7 days  
**Impact:** Unique product differentiator that no competitor offers

---

## Tier 4: Long-Term Vision

### 4.1 Own Search Index

**Problem:** Dependence on third-party search engines means Thesidia's result quality is bounded by DuckDuckGo/Brave's index. Perplexity built its own index for a reason.

**Solution path:**
- Phase 1: Web crawler that indexes domains from previous research sessions (build a personal research index)
- Phase 2: Vector store (Qdrant or ChromaDB) for semantic retrieval over crawled content
- Phase 3: Hybrid retrieval (keyword + vector) for research queries

**Effort:** Weeks to months  
**Impact:** Removes the single biggest architectural dependency

### 4.2 Multi-Agent Research

**Problem:** Single-pass synthesis produces one perspective. Deep research benefits from multiple "angles" -- historical, economic, political, technical.

**Solution:**
- Decompose complex queries into sub-queries (one per angle)
- Run parallel search + synthesis for each sub-query
- Merge sub-syntheses into a final response with section headers
- This is essentially what Grok's "Think" mode does internally

**Effort:** 1-2 weeks  
**Impact:** Step-change in research depth for complex queries
