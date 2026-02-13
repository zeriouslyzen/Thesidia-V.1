# OpenClaw Research and Thesi Agent Design

Research on OpenClaw (2026) and how it informs upgrading Thesidia versus introducing a separate agentic agent ("Thesi"). No mix: Thesidia stays research/synthesis; Thesi is agentic-only.

---

## OpenClaw: What It Is (As of February 2026)

**Origin:** Weekend project by Peter Steinberger (Austria), November 2025. Evolved from "Clawd" (renamed after Anthropic request) to "Moltbot" to **OpenClaw**. MIT-licensed, 188k+ GitHub stars, 380+ contributors.

**Positioning:** Self-hosted gateway that connects chat apps (WhatsApp, Telegram, Discord, Slack, iMessage, WebChat, Twitch, Google Chat) to an AI agent that runs on your machine. "Your assistant. Your machine. Your rules."

**Tech:** TypeScript/Node 22+. Single long-lived Gateway process owns all channel connections. Clients and nodes connect over WebSocket (default `127.0.0.1:18789`). Protocol: JSON over WS with `connect` handshake, then request/response and server-push events.

### Architecture (Relevant to Us)

| Layer | OpenClaw | Purpose |
|-------|----------|---------|
| **Gateway** | One daemon per host | Holds provider connections (Baileys for WhatsApp, grammY for Telegram, etc.), typed WS API, validation, events: `agent`, `chat`, `presence`, `health`, `heartbeat`, `cron` |
| **Agent Runtime** | Derived from pi-mono | Single embedded coding agent: tool use, sessions, memory. Not a research pipeline. |
| **Agent Loop** | Intake -> context -> model -> tools -> stream -> persist | One serialized run per session; lifecycle + tool + assistant events streamed |
| **Workspace** | Single `cwd` per agent | Only working directory for tools. User-editable files injected into context: `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `BOOTSTRAP.md`, `IDENTITY.md`, `USER.md` |
| **Skills** | Bundled + `~/.openclaw/skills` + `<workspace>/skills` | Loaded and injected into env/prompt; can be gated by config |
| **Sessions** | JSONL per session under `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl` | Stable session ID; runs serialized per session key (and optionally global lane) |
| **Multi-Agent Routing** | Isolated sessions per agent/workspace/sender | Multiple agents can be configured; routing by session key |

### Agent Loop (Detail)

1. **Entry:** `agent` RPC validates params, resolves session, persists metadata, returns `{ runId, acceptedAt }` immediately.
2. **Run:** `agentCommand` resolves model, loads skills snapshot, calls `runEmbeddedPiAgent` (pi-agent-core). Runs are serialized per session; timeout enforced (default 600s); aborts on timeout or AbortSignal.
3. **Streaming:** Pi events mapped to OpenClaw streams: tool events -> `stream: "tool"`, assistant deltas -> `stream: "assistant"`, lifecycle -> `stream: "lifecycle"` (phase: start/end/error).
4. **Queue modes:** `steer` (inject user message mid-run, skip remaining tool calls), `followup`/`collect` (hold until turn ends). Block streaming can send completed assistant blocks on `text_end` or `message_end`.
5. **Hooks:** Internal (e.g. `agent:bootstrap`, command hooks) and plugin (e.g. `before_agent_start`, `after_tool_call`, `session_start`, `gateway_start`). Used to inject context, override system prompt, or observe tool calls.

### Built-in Tools and Security

- Core tools: read/exec/edit/write and related system tools; `apply_patch` optional and gated.
- `TOOLS.md` in workspace is guidance for how the user wants tools used, not a tool allowlist.
- Security: 34+ security-related commits; machine-checkable formal models; prompt injection called out as unsolved. Strong recommendation: allowlists (`allowFrom`), mention rules in groups.

### What OpenClaw Is Not

- Not a research engine. No web search, no synthesis from multiple sources, no Gnostic Blade.
- Not multi-step research decomposition. It is a coding/assistant agent with a tool loop.
- Not local-LLM-only by default; it supports Anthropic, OpenAI, etc. (self-hosted means you run the Gateway and choose providers).

---

## Lessons for Thesidia (Upgrade Path)

These are applicable if we want to make Thesidia itself "more agentic" without building a second agent.

| Lesson | Application to Thesidia |
|--------|-------------------------|
| **Workspace injection** | Thesidia has no single workspace. We could define a research workspace (e.g. `data/thesidia_workspace/`) with `AGENTS.md` (operating instructions), `SOUL.md` (persona/boundaries), and inject them into the synthesis system prompt. Improves consistency and user control. |
| **Session persistence** | We have conversation history and cognitive framework findings, but not a single JSONL transcript per "session" that can be replayed or compacted. Adding session IDs and JSONL transcripts would enable session pruning, compaction, and clearer multi-turn context. |
| **Streaming lifecycle** | We already stream chunks and progress. OpenClaw's `lifecycle` (start/end/error) and tool events could map to our SSE: e.g. `phase: "search"`, `phase: "synthesis"`, `phase: "streaming"`, plus explicit `lifecycle: end`. Improves client-side state machine. |
| **Hook points** | We have no plugin/hook system. Adding `before_research`, `after_synthesis`, `before_tool_call` (if we add tools) would allow extensions without forking the monolith. |
| **Tool abstraction** | Thesidia today has no tool loop. Search is internal. If we ever expose "run search," "scrape URL," "save to notebook" as tools, a permissioned tool layer (OpenClaw-style) would keep control explicit. |
| **Single responsibility** | OpenClaw separates Gateway (channels, routing, sessions) from Agent Runtime (loop, tools, model). Thesidia mixes HTTP, SSE, routing, search, synthesis, and streaming in one process. A clear split would improve testability and future multi-channel support. |

**Verdict:** Thesidia can adopt workspace injection, session transcripts, lifecycle events, and hooks without becoming a full agentic loop. That keeps her "research-only, simple" while improving observability and extensibility.

---

## What We Already Have (Agents Module)

The codebase already has an agent abstraction that is underused:

**`src/agents/base_agent.py`**
- Abstract `BaseAgent` with `process(input_data, context) -> Dict`, `get_capabilities() -> List[str]`.
- Provides `get_memory_context()`, `store_memory()`, `call_model()`, `update_status()`, `register_event_handler()`, `emit_event()`, `get_info()`.
- Uses `ModelClient` and `MemoryManager` (injected or default).

**`src/agents/agent_registry.py`**
- `AgentRegistry`: register by instance or by class (with capabilities).
- `create_agent(class_name, agent_id, **kwargs)`, `get_agent(agent_id)`, `find_agents_by_capability()`, `find_agents_by_capabilities()`, `list_all_agents()`, `unregister_agent()`, `get_stats()`.
- Capability index for discovery.

**`src/agents/agent_interface.py`**
- `AgentInterface` (Protocol): `agent_id`, `capabilities`, `status`, `process()`, `get_capabilities()`, `get_info()`.
- `MessageProtocol`: `create_message()`, `create_response()` for agent-to-agent messages.

**Current use:** `ThesidiaHybridAdaptive(BaseAgent)` subclasses `BaseAgent` and implements `process()` and `get_capabilities()`. The registry is not used in the main request path; the Flask server instantiates a single Thesidia and calls `process()` directly. So we have the interface and registry ready for a second agent, but no second agent and no tool loop.

---

## Thesi: Agentic-Only Agent (Design)

**Goal:** A separate agent, nickname "Thesi," that is agentic only: reason -> choose tool -> execute -> stream -> repeat. No research pipeline mixing. Thesidia remains the research/synthesis engine; Thesi is the one that uses tools, workspace, and a persistent loop.

**Principles:**
- Simple first: minimal loop, one channel (e.g. WebChat or KIM), few tools.
- Reuse existing infra: `BaseAgent`, `AgentRegistry`, `ModelClient`, `MemoryManager`.
- No duplication of Thesidia's search/synthesis: Thesi can *invoke* Thesidia as a tool ("run research on X") if we want, but the loop and identity are Thesi's.

### Proposed Architecture

```
User message (WebChat / KIM / future WhatsApp)
        |
        v
+-------------------+
| Thesi Gateway     |  (thin: auth, session resolve, route to Thesi)
| or existing Flask |
+--------+----------+
         |
         v
+-------------------+
| Thesi Agent       |  Subclass of BaseAgent; agent_id="thesi"
| - Workspace       |  data/thesi_workspace/ (AGENTS.md, SOUL.md, TOOLS.md)
| - Session         |  JSONL per sessionKey (e.g. user_id or thread_id)
| - Tool loop       |  reason -> tools -> execute -> stream
+--------+----------+
         |
         v
+-------------------+
| Tools (minimal)   |  read_file, write_file, run_shell (sandboxed), 
|                   |  optional: thesidia_research(query) -> call Thesidia.process()
+-------------------+
```

### Thesi Agent Loop (Minimal)

1. **Receive** user message; resolve session (load or create JSONL transcript).
2. **Assemble context:** workspace files (AGENTS.md, SOUL.md, TOOLS.md) + last N turns from session.
3. **Model call:** "Given context and tools, output either a final reply or a tool call (name + args)."
4. **If tool call:** execute tool (sandboxed), append result to transcript, go to 3 (re-reason with tool result).
5. **If final reply:** stream to user, append to session, persist transcript.
6. **Timeouts and limits:** max tool steps per turn (e.g. 5), total timeout (e.g. 120s).

### Tools (Phase 1)

| Tool | Description | Risk |
|------|-------------|------|
| `read_file` | Read from workspace or allowed paths | Path allowlist |
| `write_file` | Write to workspace only | No escape outside workspace |
| `run_shell` | Optional; subprocess with timeout and allowlist (e.g. `ls`, `python -c`) | High; gate by config or omit initially |
| `thesidia_research` | Optional; POST to Thesidia API or call `ThesidiaHybridAdaptive.process(mode="research")` | Low; read-only from Thesi's perspective |

Phase 2 could add: browse_url (sandboxed), send_message (to KIM), etc.

### Workspace (OpenClaw-Style)

- `data/thesi_workspace/`
  - `AGENTS.md` – operating instructions (when to use tools, when to answer directly).
  - `SOUL.md` – persona and boundaries (Thesi's tone, what it refuses).
  - `TOOLS.md` – user notes on how tools should be used (conventions, not allowlist).
- Injected into the first system prompt or every turn (with truncation if large).

### Registry and Routing

- Register Thesi: `registry.register_agent(thesi_agent)` or `registry.register_agent_class("thesi", ThesiAgent, ["agentic", "tools", "assistant"])`.
- Routing: by channel or by explicit mode. For example, Katanx could have "Thesidia" (research) and "Thesi" (agentic) as two entry points; the server chooses which agent to invoke by route or parameter, not by mixing both in one pipeline.

### What Thesi Does Not Do

- Does not run the Gnostic Blade protocol.
- Does not run multi-source search or synthesis (unless via a single `thesidia_research` tool).
- Does not replace Thesidia; it coexists. Thesidia = research and depth. Thesi = agency and tools.

---

## Summary Table

| Aspect | Thesidia (current / upgraded) | Thesi (proposed) |
|--------|-------------------------------|------------------|
| Role | Research, synthesis, forensic, conversational | Agentic: tools, workspace, multi-step |
| Loop | Classify -> search -> synthesize -> stream | Reason -> tool -> execute -> stream (repeat) |
| Tools | None (search internal) | read_file, write_file, optional run_shell, optional thesidia_research |
| Workspace | None (could add) | thesi_workspace with AGENTS.md, SOUL.md, TOOLS.md |
| Sessions | Cognitive framework + conversation history | JSONL per session, replayable |
| Channels | Web app (Flask) | Start with same Web app (e.g. /api/thesi); later Gateway-style if needed |
| OpenClaw ideas used | Workspace injection, lifecycle events, hooks (optional) | Full loop, workspace, session serialization, tool layer |

---

## References

- OpenClaw: https://openclaw.ai , https://github.com/openclaw/openclaw
- Docs: https://docs.openclaw.ai (Gateway Architecture, Agent Runtime, Agent Loop, System Prompt, Tools, Multi-Agent Routing)
- Introducing OpenClaw (blog): https://openclaw.ai/blog/introducing-openclaw
- Security: https://docs.openclaw.ai/gateway/security
- Internal: `docs/engineering/AGENT_FRAMEWORKS_AUDIT.md`, `docs/engineering/COMPREHENSIVE_INTEGRATION_PLAN.md`, `src/agents/` (base_agent, agent_registry, agent_interface)
