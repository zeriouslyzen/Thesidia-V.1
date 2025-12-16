# Thesidia Routing Decision Tree

## Overview
This document defines the complete decision tree for how Thesidia routes queries through different processing paths. Every query goes through these checkpoints in order.

## Decision Tree Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERY RECEIVED                      │
└───────────────────────┬───────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  CHECKPOINT 1: Simple Greeting?│
        └───────────────┬───────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
           YES                     NO
            │                       │
            ▼                       ▼
    ┌───────────────┐      ┌──────────────────────┐
    │ FAST GREETING │      │ CHECKPOINT 2:        │
    │ PATH          │      │ Conversational?     │
    │ - Skip memory │      └──────────┬───────────┘
    │ - Skip research│                │
    │ - Skip forensic│        ┌───────┴───────┐
    │ - Direct LLM   │       YES              NO
    │ - Return       │        │                │
    └───────┬───────┘        ▼                ▼
            │        ┌──────────────┐  ┌──────────────────┐
            │        │ CONVERSATIONAL│  │ CHECKPOINT 3:    │
            │        │ PATH          │  │ Fast Mode?       │
            │        │ - Skip research│ └────────┬─────────┘
            │        │ - Skip forensic│          │
            │        │ - Direct LLM  │   ┌──────┴──────┐
            │        │ - Return       │  YES           NO
            │        └───────┬────────┘   │              │
            │                │            ▼              ▼
            │                │    ┌──────────────┐ ┌──────────────────┐
            │                │    │ FAST MODE    │ │ CHECKPOINT 4:    │
            │                │    │ - Skip deep  │ │ Deep Research?   │
            │                │    │   research   │ └────────┬─────────┘
            │                │    │ - Regular    │          │
            │                │    │   search    │   ┌──────┴──────┐
            │                │    │   only      │  YES            NO
            │                │    │ - Direct LLM│   │              │
            │                │    └──────┬──────┘   ▼              ▼
            │                │           │    ┌──────────────┐ ┌──────────────┐
            │                │           │    │ DEEP RESEARCH│ │ REGULAR PATH │
            │                │           │    │ PATH          │ │ - Check      │
            │                │           │    │ - Forensic    │ │   research   │
            │                │           │    │   analysis    │ │ - Web search │
            │                │           │    │ - Multiple    │ │   (if needed)│
            │                │           │    │   sources     │ │ - Direct LLM │
            │                │           │    │ - Synthesis   │ │ - Return     │
            │                │           │    └──────┬───────┘ └──────┬───────┘
            │                │           │            │                 │
            └────────────────┴───────────┴────────────┴─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   RETURN RESPONSE│
                    └─────────────────┘
```

## Checkpoint Definitions

### CHECKPOINT 1: Simple Greeting Detection
**Location**: `src/thesidia_hybrid_adaptive.py:process()` (line ~3512)

**Patterns**:
- `^(hi|hello|hey|greetings)[\s,]*$`
- `^(hi|hello|hey|greetings)[\s,]+(there|you|how are you)[\s,]*$`
- Word count <= 4

**Action if TRUE**:
- Skip memory retrieval
- Skip forensic analysis
- Skip research
- Use cached greeting prompt
- Direct LLM call with minimal context
- Return immediately

**Action if FALSE**: Continue to Checkpoint 2

---

### CHECKPOINT 2: Conversational Query Detection
**Location**: `src/thesidia_hybrid_adaptive.py:process()` (line ~3814)

**Patterns**:
- `what.*?your favorite` (e.g., "what's your favorite movie?")
- `what.*?you think about`
- `^i'?m thinking about`
- `^tell me a random`
- `^what.*?you like`
- `^do you like`
- `^are you.*\?$`
- `^how are you`
- `^what.*?up\??$`

**Action if TRUE**:
- Skip ALL research (no `_needs_research()` call)
- Skip forensic analysis
- Skip deep research routing
- Direct LLM call with conversational context
- Return immediately

**Action if FALSE**: Continue to Checkpoint 3

---

### CHECKPOINT 3: Fast Mode Check
**Location**: `src/thesidia_hybrid_adaptive.py:process()` (line ~3775)

**Parameter**: `fast_mode: bool` (from UI toggle)

**Action if TRUE (Fast Mode)**:
- Only route to deep research if explicitly requested (`_is_deep_research_request()`)
- Skip automatic forensic analysis
- Skip mind-body routing
- Skip deep indicator routing
- Regular search only (if `_needs_research()` returns True)

**Action if FALSE (Deep Mode)**:
- Continue to Checkpoint 4

---

### CHECKPOINT 4: Deep Research Routing
**Location**: `src/thesidia_hybrid_adaptive.py:process()` (line ~3771)

**Conditions (ANY of these trigger deep research)**:
1. Explicit deep research request (`_is_deep_research_request()`)
2. Mind-body query (meditation, chi gong, yoga, breathing)
3. Deep indicators present ("true origins", "real", "secrets", "uncover", etc.)
4. Forensic analysis needed (`detect_forensic_routing()`)

**Action if TRUE**:
- Route to `_handle_deep_research()`
- Full forensic analysis
- Multiple source synthesis
- Return deep research result

**Action if FALSE**: Continue to Regular Path

---

### Regular Path (Default)
**Location**: `src/thesidia_hybrid_adaptive.py:process()` (line ~3846)

**Steps**:
1. Check if research needed (`_needs_research()`)
   - This method checks conversational patterns FIRST (before LLM call)
   - If conversational pattern matched, return False immediately
   - Otherwise, may call LLM for classification
2. If research needed:
   - Parallel processing (web search + LLM thinking)
   - Or sequential web search
3. Build enhanced prompt
4. Direct LLM call with context
5. Return response

---

## Research Decision Logic (`_needs_research()`)

**Location**: `src/thesidia_hybrid_adaptive.py:_needs_research()` (line ~4286)

**Order of Checks**:
1. **Simple patterns** (return False immediately):
   - Math: `^what is \d+\s*[\+\-\*/]\s*\d+`
   - Numbers: `^what is \d+$`
   - Greetings: `how are you`, `hey`, `hi`, `hello`

2. **Conversational patterns** (return False immediately, NO LLM CALL):
   - All patterns from Checkpoint 2
   - This prevents slow LLM calls for conversational queries

3. **Deep indicators** (return True immediately):
   - "true origins", "real origins", "what's really", etc.
   - Forces research without LLM call

4. **User interests** (return True if match):
   - If query matches user's top interests

5. **Technical domain** (return True if match):
   - If technical domain detected

6. **LLM classification** (only if none of above matched):
   - Call LLM to classify if research needed
   - This is the slow path - avoided for conversational queries

---

## Fast Mode vs Deep Mode Behavior

### Fast Mode (`fast_mode=True`)
- **Greetings**: Fast path (Checkpoint 1)
- **Conversational**: Conversational path (Checkpoint 2)
- **Regular queries**: Regular path with research only if needed
- **Deep research**: ONLY if explicitly requested

### Deep Mode (`fast_mode=False`)
- **Greetings**: Fast path (Checkpoint 1)
- **Conversational**: Conversational path (Checkpoint 2)
- **Regular queries**: Regular path with research
- **Deep research**: Automatic if any deep indicator/forensic need detected

---

## Consistency Guarantees

1. **Conversational queries NEVER trigger**:
   - Deep research
   - Forensic analysis
   - Web research
   - Heavy processing

2. **Simple greetings NEVER trigger**:
   - Memory retrieval (unless user/session ID present)
   - Forensic analysis
   - Research
   - Heavy prompt building

3. **Fast mode NEVER triggers**:
   - Automatic deep research (only explicit requests)
   - Automatic forensic analysis

4. **All paths are mutually exclusive**:
   - Once a path is taken, no other path is executed
   - Early returns prevent fall-through

---

## Debugging Checkpoints

Each checkpoint logs its decision:
- `🔍 PROCESS: Using FAST greeting path`
- `🔍 PROCESS: Conversational query detected - skipping research`
- `🔍 PROCESS: needs_forensic_analysis={bool}, has_deep_indicator={bool}`
- `🔪 ROUTING: Deep research query detected`
- `🔍 _needs_research: Conversational pattern matched - skipping research`

---

## Future Engineering Considerations

1. **Caching**: Greeting prompts are cached to avoid rebuilding
2. **Performance**: Conversational pattern matching happens BEFORE LLM calls
3. **Extensibility**: New patterns can be added to conversational_patterns list
4. **Traceability**: All routing decisions are logged for debugging
