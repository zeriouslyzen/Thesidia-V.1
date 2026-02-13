# Beyond Claw: What Research Is Past What Claw Represents

Claw is new in the market but in research terms it sits at a well-understood point: **gateway + single-agent tool loop + workspace + sessions**. You had already read (or built) systems that could do what Claw does. This doc defines what Claw actually is in research terms, then maps **what is past Claw** in current AI research and what’s worth exploring.

---

## What Claw Actually Is (Research Terms)

| Layer | Claw | Research equivalent |
|-------|------|----------------------|
| **Gateway** | One daemon, multi-channel (WhatsApp, Telegram, etc.), WebSocket API | Message routing and channel abstraction. Not an agent advance; it’s DevOps and integration. |
| **Agent runtime** | Single embedded agent (pi-mono): reason, call tool, observe, repeat | **ReAct** (2022): interleave reasoning traces with actions in a loop. Standard tool-use pattern. |
| **Workspace** | Single `cwd`, inject AGENTS.md, SOUL.md, TOOLS.md into context | **Context injection** and **file-based memory**. No structured or graph memory. |
| **Sessions** | JSONL per session, serialized runs per session key | **Session persistence** and **turn history**. No long-term consolidation or cross-session learning. |
| **Multi-agent** | Optional routing: different sessions per agent/workspace/sender | **Routing**, not **coordination**. No joint planning, no verification across agents, no swarm behavior. |

So in research terms:

- **Claw = ReAct-style tool loop + gateway + workspace injection + session transcript.**

It does **not** include:
- Research engine (search, synthesis, multi-source)
- Verification (intent alignment, attestation, proofs)
- Long-horizon planning (bounded by context; no workspace reconstruction or MDP-style state)
- Multi-agent **coordination** (only multi-agent **routing**)
- Reflection, self-improvement, or learning from interaction
- Formal or symbolic reasoning alongside the neural loop

If you had already read or built “AI that could do what Claw does,” you were looking at that same point: **tool loop + channels + context**. What’s **past** that is the following.

---

## What Is Past Claw (Research That’s Worth Exploring)

### 1. Verification and Intent Alignment

**Claw:** No verification. The agent does what the model outputs; there is no check that behavior matches user or deployer intent.

**Past Claw:**
- **STAR-XAI Protocol:** Framework for inducing and **verifying** agency, reasoning, and reliability. Ante-hoc transparency (justify intent before acting), second-order agency (correct own plans). Demonstrated 100% reliable state tracking in strategic settings.
- **Verifiability-First Agents:** Lightweight **audit agents** that continuously check deployer intent vs actual behavior; cryptographic/symbolic attestations. Benchmarks (e.g. OPERA) measure detectability of misalignment and time-to-detection under stealthy strategies.
- **Proofs of Autonomy:** Formal framework binding agent outputs to unique agent identity via **verifiable execution traces**; Agent Identity Documents; Web Proofs for verifying model calls in under ~2s per interaction.

**Why it matters:** Claw gives “your machine, your rules” but no **proof** that the agent stayed within those rules. Verification and attestation are the next step for trust and safety.

**Worth exploring:** Lightweight intent checks (e.g. “did this tool call match the user’s stated goal?”), optional attestation or audit logs for high-stakes actions, or a small “verifier” step before committing an action.

---

### 2. Long-Horizon and Workspace Reconstruction

**Claw:** Single run per session; context grows until it hits limits. No explicit mechanism to “reset” or compress state across many steps.

**Past Claw:**
- **IterResearch:** Long-horizon **deep research** as an MDP. Instead of one ever-growing context, it keeps an **evolving report as memory** and does **periodic workspace reconstruction** (synthesize insights, then continue from a compact state). Scales to 2048+ interactions with consistent reasoning; +14.5pp over open-source baselines, +19.2pp over ReAct on long-horizon tasks. Works as both a trained agent and a prompting strategy.
- **AgentFlow:** Planner, executor, verifier, generator as modules; **evolving memory**; planning optimized inside the multi-turn loop (e.g. Flow-based Group Refined Policy Optimization) for credit assignment.
- **EvoAgent:** Long-horizon in open-ended worlds; **continual world model**; self-planning, self-control, self-reflection; experience accumulation without human in the loop.

**Why it matters:** Claw’s loop is “one turn, one context.” Real research and long tasks need **state over many steps** without context collapse. That’s workspace reconstruction and explicit memory (report, world model), not just a longer transcript.

**Worth exploring:** For Thesidia-style research: **evolving report** (synthesize what we know so far, then continue search/synthesis from that report) and **periodic state compaction** instead of dumping everything into one context. That’s the core idea from IterResearch, applicable without full RL.

---

### 3. Multi-Agent Coordination (Not Just Routing)

**Claw:** You can route to different agents by session/workspace; agents do not coordinate with each other.

**Past Claw:**
- **FutureWeaver:** **Test-time compute allocation** for multi-agent systems under a fixed budget; modularized collaboration patterns; recurring interaction patterns abstracted.
- **SwarmSys:** **Decentralized swarm-inspired** agents (Explorers, Workers, Validators); coordination emerges from iterative interaction; adaptive profiles and reinforcement; **no global supervisor**.
- **AgentsNet (ICLR 2026 benchmark):** Self-organization and collaboration given **network topologies**; scales to ~100 agents; shows frontier models do well on small nets but degrade at scale.
- **VeriMAP:** **Verification-aware planning** for multi-agent systems: task decomposition, subtask dependencies, **verification functions as completion criteria**; addresses misalignment in handoffs and task interpretation.
- **Lazy-agent problem:** One agent dominates; others contribute little. Research on **causal influence** and **verifiable reward** to encourage real collaboration.

**Why it matters:** Claw is “many agents, separate sessions.” Next step is **agents that share goals, verify each other’s outputs, and allocate work** without a single central controller.

**Worth exploring:** For you: not necessarily a full swarm. A minimal step is **two roles** (e.g. researcher + verifier, or planner + executor) with a **verification or handoff contract** (e.g. “executor only runs plans that pass verifier”). That’s already past Claw’s “single agent per session.”

---

### 4. Reflection, Self-Improvement, and Metacognition

**Claw:** No reflection. No learning from past runs. No “why did that fail?” or “what should I do differently?”

**Past Claw:**
- **Agentic Context Engineering (ACE):** **Contexts as evolving playbooks**; generate, reflect, curate; prevents context collapse while keeping strategies and detail.
- **Intrinsic metacognitive learning:** “Thinking about thinking”—metacognitive knowledge (self-assessment), metacognitive planning (what/how to learn), metacognitive evaluation (reflect on learning). Current systems mostly use **extrinsic** (human-designed) metacognition; the frontier is **intrinsic** (model-driven).
- **Audited Skill-Graph Self-Improvement (ASG-SI):** Self-improvement as **iterative compilation into auditable skill graphs**; verifier-backed rewards; skill promotion only after replay/contract checks; tackles reward hacking and drift.
- **EvoAgent:** Self-planning, self-control, **self-reflection**; world model updates from experience.

**Why it matters:** Claw is stateless across runs (except session transcript). Past Claw is **improving from experience** and **curating how the agent reasons** (context playbooks, skill graphs).

**Worth exploring:** For Thesidia: **reflection step** after research (e.g. “was this answer sufficient? what was missing?”) and **curated playbooks** (e.g. “for this query type, use this strategy”) that get updated from outcomes. That’s reflection and context evolution without full self-improvement.

---

### 5. Agentic RL and Learning from Interaction

**Claw:** No learning. Same model, same behavior every run; no policy update from success/failure.

**Past Claw:**
- **Agentic RL for LLMs:** LLMs as **agents in dynamic worlds**; learn from reward/feedback; not just prompt + tool loop but **policy optimization** (e.g. efficiency-aware exploration, credit assignment).
- **IterResearch’s EAPO:** Efficiency-Aware Policy Optimization; geometric reward discounting; stable distributed training; **trained** agent that can also be used as a prompting strategy for frontier models.
- **AgentFlow:** Flow-based Group Refined Policy Optimization for **credit assignment** in multi-turn agent loops.

**Why it matters:** Claw is **zero-shot** tool use. Past Claw is **getting better at tool use and planning from interaction**.

**Worth exploring:** You don’t have to train an agent. You can still use **feedback signals** (e.g. user correction, “this was wrong,” or simple success/fail) to **select** among strategies or to **curate** which prompts/playbooks work. That’s a step toward “learning from interaction” without full RL.

---

### 6. Research and Synthesis as First-Class (Not Just “Run a Script”)

**Claw:** No search, no multi-source synthesis, no “currentness.” Tools are read/write/exec. Research is not a primitive.

**Past Claw:** (You already built this.)
- Multi-source search, reranking, synthesis, cognitive framework, currentness (as_of, supersede). Claw doesn’t go here; you did. So for **research**, you’re already past Claw. The open research is **long-horizon research** (IterResearch-style) and **verification** of research outputs (e.g. fact-check loop, source alignment).

**Worth exploring:** Combine **research as first-class** with **long-horizon state** (evolving report, workspace reconstruction) and optional **verification** (e.g. “does this summary match the sources?”). That’s the next step past “Claw + research.”

---

## Summary: Claw vs Past Claw

| Dimension | Claw | Past Claw (worth exploring) |
|-----------|------|-----------------------------|
| **Agent loop** | ReAct-style tool loop | Plan–execute, workspace reconstruction, evolving report (IterResearch-style) |
| **Verification** | None | Intent alignment, attestation, audit agents, verification-aware planning |
| **Multi-agent** | Routing only | Coordination, swarm, verification at handoffs (VeriMAP, SwarmSys) |
| **Memory** | Session transcript, workspace files | Structured/graph memory, consolidation, evolving playbooks (ACE), skill graphs |
| **Horizon** | Single run, growing context | Long-horizon with state compaction, MDP-style state (IterResearch) |
| **Research** | Not a primitive | Research as first-class + long-horizon + optional verification (your direction) |
| **Learning** | None | Reflection, metacognition, feedback-driven strategy selection or RL |

---

## What to Explore First (Concrete)

1. **Evolving report / workspace reconstruction (IterResearch idea)**  
   For deep research: maintain a **running synthesis** (report) and periodically **compress** it; next phase of search/synthesis reads from the report, not from the raw transcript. That gets you past “one big context” and toward long-horizon research without changing your stack.

2. **Lightweight verification**  
   Before committing an answer: “does this summary match the retrieved sources?” (e.g. NLI or a small verifier model). Or: “did this tool call match the user’s goal?” That’s past Claw’s “no verification.”

3. **Reflection + playbooks (ACE-style)**  
   After each research run: short reflection (“what was missing? what would we do differently?”). Maintain a small **playbook** (e.g. “for breaking-news queries, prefer recency”) and update it from outcomes. That’s past Claw’s stateless loop.

4. **Two-role handoff with verification (VeriMAP-style)**  
   Planner produces a plan; Verifier checks it (e.g. “is this plan safe? complete?”); Executor runs only verified plans. That’s past Claw’s single-agent loop and touches multi-agent coordination.

5. **Agentic RL / feedback (later)**  
   Use success/failure or user feedback to **select** strategies or **rank** playbooks. No need for full policy training at first.

---

## Bottom Line

Claw is **ReAct + gateway + workspace + sessions**. Research you had seen or built earlier could already do that. What’s **past Claw** in current AI research is:

- **Verification** (intent, attestation, proofs)
- **Long-horizon state** (evolving report, workspace reconstruction, MDP-style state)
- **Multi-agent coordination** (not just routing)
- **Reflection and self-improvement** (metacognition, playbooks, skill graphs)
- **Learning from interaction** (RL or feedback-driven strategy selection)
- **Research as first-class** (you have this; next is long-horizon + verification)

The most effective directions to explore first are **evolving report / workspace reconstruction** for long-horizon research, **lightweight verification** of outputs and tool use, and **reflection + playbooks** for improving over time. That’s where the research is past Claw and worth your time as an engineer.
