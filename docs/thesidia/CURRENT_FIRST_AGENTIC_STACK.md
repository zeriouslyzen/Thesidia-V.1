# Current-First Agentic Stack

Unified design: all the things (research executor, Claw-style channel, dual mode, Thesi as front door, skills) plus a **currentness layer** that OpenClaw does not address. Claw's focus is on tools and channels over **existing** material (files, code, chat). Ours is **agentic + research that stays current** and explicitly handles outdated material.

---

## The Gap Claw Doesn't Solve

| OpenClaw | Problem |
|----------|--------|
| Workspace = files on disk | No notion of "when was this true." A saved finding from last month can be stale; Claw doesn't track or warn. |
| Sessions = transcript | Transcript is timeless. No "as of" date on answers, no "this may be outdated" flag. |
| Tools = read/write/exec | Tools operate on static artifacts. No built-in "refresh this," "re-verify this," or "newer sources contradict this." |
| No research engine | No search, no synthesis, no source dates. So no way to prioritize fresh sources or deprecate old ones. |

**Impact:** Users get an agent that can do things everywhere (WhatsApp, Telegram, etc.) but has no guarantee that the **information** it uses or surfaces is current. We can own the opposite: **agentic + current-first.**

---

## Currentness Layer (What We Add)

### 1. Every Finding Has an "As Of"

- **Stored findings** (cognitive framework, notebook, saved answers) carry: `as_of: ISO8601`, `source_urls: [...]`, optional `source_dates: [...]`.
- **Display:** "As of 2026-02-12" or "Last verified: 2 hours ago" in UI and in agent replies.
- **API:** Research responses include `as_of` and optional `freshness_hint` ("recent" | "mixed" | "older").

### 2. Freshness-Aware Search and Synthesis

- **Search:** Already have Brave `freshness` (pd/pw/pm). Extend: default to "prefer recent" (e.g. `pw` or `pm`) for research mode; optional "any time" for historical queries.
- **Reranker:** Already score by freshness. Add: hard filter option "only include results from last N days" for time-sensitive queries.
- **Synthesis prompt:** Inject: "Prefer recent sources. If you cite older material, note that it may be outdated."
- **Output:** Synthesis includes a one-line footer when appropriate: "Based on sources from [date range]. Re-run research to refresh."

### 3. Stale Detection and Warnings

- **When surfacing a saved finding:** Compare `as_of` to now. If older than threshold (e.g. 7 days for news, 90 days for reference), show: "This was true as of [date]. It may be outdated; consider re-running research."
- **Optional:** Background job that re-runs high-value research (e.g. saved "what's happening in Brazil") on a schedule and replaces or versions the finding.
- **Notebook / workspace:** Entries show "as of" and a "Refresh" action that triggers new research and optionally supersedes.

### 4. Debunk / Supersede

- **When new research contradicts a stored finding:** Store both; mark the old one `superseded_by: finding_id` or `superseded_at: ...`. UI: "You had this; newer research suggests: [summary]."
- **Tool (for Thesi):** `check_freshness(finding_id)` → re-run research on same query, compare; return "current" | "stale" | "superseded" with optional delta.
- **Research executor:** When delivering a scheduled digest, compare to previous run; if material changed significantly, highlight "Updated since last run."

This layer is **independent of** Claw-style gateway/tools; it sits under both Thesidia and Thesi and makes "current" a first-class property.

---

## Unified Stack: All the Things + Currentness

Single coherent system that does:

1. **Research (current-first)** — Thesidia: search with freshness defaults, synthesis with "as of," stored findings with dates.
2. **Agentic loop** — Thesi (or Thesidia agentic mode): tools (read_file, write_file, thesidia_research, schedule, etc.), workspace, sessions.
3. **Claw-style channel** — One gateway: messages from Telegram/KIM/WebChat → router → Thesidia or Thesi; replies streamed back.
4. **Research executor** — Thesi (or cron + Thesidia): "Run research on X every Monday"; deliver with "as of" and "updated since last time."
5. **Skills** — Shared tool pack: thesidia_research (with freshness params), save_to_notebook (with as_of), check_freshness, summarize_url (with extract date).
6. **Temporal workspace** — Notebook and saved findings are versioned by time; "what we knew as of 2026-02-01" vs "what we know now"; refresh and supersede as above.

### How It Fits Together

```
[Channel: Telegram / KIM / WebChat]
         |
         v
+----------------+  route by intent or explicit mode
| Router         |  "research X" -> Thesidia
|                |  "do Y" / "remind me" / tool use -> Thesi
+--------+-------+
         |
    +----+----+
    |         |
    v         v
+--------+  +--------+
|Thesidia|  | Thesi  |
|research|  | agentic|
|current |  | + tools|
+----+---+  +---+----+
     |           |
     |           | thesidia_research(freshness=...)
     |           | save_to_notebook(as_of=...)
     |           | check_freshness(id)
     v           v
+----------------------------------+
| Currentness layer                |
| - as_of on all findings          |
| - freshness in search/synthesis  |
| - stale warning / supersede       |
| - refresh / re-run               |
+----------------------------------+
```

### What Each Component Does

| Component | Role | Currentness |
|-----------|------|-------------|
| **Thesidia** | Research only: classify -> search (freshness-aware) -> synthesize -> stream. No tool loop. | All responses and stored findings have `as_of`; synthesis prefers recent sources; optional footer "re-run to refresh." |
| **Thesi** | Agentic: reason -> tools -> execute -> stream. Tools include `thesidia_research`, `save_to_notebook`, `check_freshness`, `schedule_research`. | When calling thesidia_research, passes freshness; when saving, stores as_of; when delivering scheduled research, compares to previous run. |
| **Router** | Single entry from channel; routes to Thesidia or Thesi by intent/mode. | N/A |
| **Skills / tools** | thesidia_research(query, freshness=...), save_to_notebook(..., as_of=...), check_freshness(finding_id), summarize_url(url) [with extracted date]. | Every tool that touches research or storage is aware of "as of" and optional refresh. |
| **Notebook / workspace** | User-visible saved findings and notes. | Every entry has as_of; "Refresh" re-runs research and can supersede; stale warning if old. |
| **Research executor** | Thesi (or cron) runs research on schedule; delivers digest. | Digest says "as of [date]"; if previous run exists, "Updated since [last date]" when relevant. |

---

## Implementation Order

1. **Currentness in research (Thesidia)**  
   - Add `as_of` and optional `source_dates` to API response and to cognitive framework stored findings.  
   - Default search freshness (e.g. `pw`) for research mode; synthesis prompt + footer.  
   - Small change, big signal: "We say when this was true."

2. **Stale warning in UI**  
   - When showing a saved finding or notebook entry, if `as_of` older than threshold, show banner: "As of [date]. May be outdated; re-run research to refresh."  
   - Optional "Refresh" button that re-triggers research and updates.

3. **Skills/tools with currentness**  
   - `thesidia_research(query, freshness=...)`  
   - `save_to_notebook(content, as_of=now(), source_urls=...)`  
   - `check_freshness(finding_id)`  
   - Then add agentic loop (Thesi or Thesidia agentic mode) that can call these.

4. **Thesi + research executor**  
   - Thesi as front door: route "research X" to Thesidia, "do Y" to Thesi.  
   - Tool: schedule_research(query, cron_or_interval, channel).  
   - On run: call Thesidia, store result with as_of, compare to previous, deliver with "Updated since…" if changed.

5. **Supersede and debunk**  
   - When re-running same query: compare new synthesis to stored finding; if materially different, mark old `superseded_by` and optionally notify.  
   - UI: "You had this; newer research suggests: …"

6. **Claw-style channel**  
   - One gateway process or Flask route: receive from Telegram/KIM/WebChat, route to Thesidia or Thesi, stream reply.  
   - Reuse same currentness semantics in replies (e.g. "As of …" in message).

---

## Why This Is More Impactful Than Claw Alone

- **Claw:** "Your assistant, your machine, your rules" over **existing** material (files, code, chat). No built-in notion of information age or truth over time.  
- **Us:** Same agentic and channel benefits, plus **research that is current by default** and **explicit handling of outdated material** (as_of, stale warning, refresh, supersede).  

So we're not "Claw + research"; we're **current-first agentic research**: one stack that does research executor, Claw-style channel, dual mode, Thesi as front door, and skills, and solves the problem Claw doesn't: **outdated material**.
