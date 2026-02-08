# Thesidia AI Routing Logic Documentation

**Generated**: 2026-01-15  
**Audit Scope**: All routing decisions, query classification, and configuration points

---

## Executive Summary

The Thesidia AI system uses a multi-stage routing system to classify queries and route them to appropriate processing paths. Routing decisions are made based on query patterns, keywords, and user preferences. The system supports fast mode (quick responses) and deep research mode (comprehensive analysis).

---

## 1. Routing Decision Tree

```
User Query
  ↓
Input Sanitization
  ↓
Simple Greeting Detection
  ├─ Yes → Fast Greeting Path (1-3s)
  └─ No → Continue
  ↓
Conversational Query Detection
  ├─ Yes → Conversational Path (skip research)
  └─ No → Continue
  ↓
Forensic Routing Detection
  ├─ Yes → Forensic/Deep Research Path
  └─ No → Continue
  ↓
Fast Mode Check
  ├─ Yes → Skip Research, Direct Response
  └─ No → Research Decision
      ├─ Needs Research → Research Path
      └─ No Research → Direct Response
```

---

## 2. Query Classification

### 2.1 Simple Greeting Detection

**Location**: `src/thesidia_hybrid_adaptive.py` (lines 3840-3844, 3863-4006)

**Patterns**:
```python
greeting_only_patterns = [
    r'^(hi|hello|hey|greetings|hi+)+[\s,]*$', 
    r'^(hi|hello|hey|greetings)[\s,]+(there|you|how are you)[\s,]*$'
]
is_simple_greeting = any(re.match(pattern, text_stripped, re.IGNORECASE) for pattern in greeting_only_patterns) and len(text_stripped.split()) <= 4
```

**Criteria**:
- Matches greeting pattern
- Word count <= 4

**Routing**: Fast greeting path (bypasses all heavy processing)

**Processing**:
- Minimal memory check
- Cached prompt
- Direct model call (50-100 tokens)
- Fast post-processing

**Timing**: 1-3 seconds

---

### 2.2 Conversational Query Detection

**Location**: `src/thesidia_hybrid_adaptive.py` (lines 4062-4074)

**Patterns**:
```python
conversational_patterns = [
    r'what.*?your favorite',  # "what's your favorite movie?"
    r'what.*?you think about',  # "what do you think about X?"
    r'^i\'?m thinking about',  # "I'm thinking about pizza"
    r'^tell me a random',  # "tell me a random fact"
    r'^what.*?you like',  # "what do you like?"
    r'^do you like',  # "do you like X?"
    r'^are you.*\?$',  # "are you X?" (simple yes/no)
    r'^how are you',  # "how are you?"
    r'^what.*?up\??$',  # "what's up?"
]
```

**Criteria**:
- Matches any conversational pattern

**Routing**: Conversational path (skips research, direct response)

**Processing**:
- No web search
- No synthesis
- Direct model call
- Standard post-processing

**Timing**: 5-15 seconds

---

### 2.3 Forensic Routing Detection

**Location**: `src/support/query_utils.py` (lines 49-111)

**Function**: `detect_forensic_routing(text, comprehensive=False)`

**Basic Keywords** (always checked):
- Religious: genesis, bible, scripture, torah, quran, veda, ancient, religion
- Decode: decode, decoded, decrypt, decrypted, expose, hidden
- Truth-seeking: "what are", "what are x really", "really about", "true origins"

**Extended Keywords** (if comprehensive=True):
- Health: health, medicine, pharmaceutical, drug, treatment, cure
- Finance: bank, finance, money, currency, bitcoin, economy, federal reserve
- Law: law, legal, court, judge, lawyer, legislation, constitution
- Power: power, systematic transformation, redaction, deeper, secrets

**Criteria**:
- Any keyword found in normalized query

**Routing**: Forensic/Deep Research Path (always routes, no length check)

**Processing**:
- Deep research with forensic analysis
- Multi-source synthesis
- Gnostic map updates
- Extended exploration

**Timing**: 40-103 seconds

---

### 2.4 Deep Research Request Detection

**Location**: `src/thesidia_hybrid_adaptive.py` (lines 4846-4895)

**Function**: `_is_deep_research_request(text)`

**Indicators**:
```python
deep_research_indicators = [
    "deep research:", "research deeply:", "comprehensive research:",
    "research comprehensively:", "deep analysis:", "analyze deeply:",
    "what was done to", "who profits from", "who benefits from",
    "arrange the evidence", "show me the pattern", "what pattern emerges"
]
```

**Criteria**:
- Query starts with explicit research prefix, OR
- Contains directive pattern requesting research

**Routing**: Deep Research Path

**Processing**:
- Iterative multi-source research
- Evidence arrangement
- Comprehensive synthesis

**Timing**: 40-103 seconds

---

### 2.5 Mind-Body Query Detection

**Location**: `src/thesidia_hybrid_adaptive.py` (lines 4107-4109)

**Keywords**:
```python
mind_body_keywords = [
    "meditation", "chi gong", "qigong", "yoga", "breathing", 
    "mind-body", "mind body", "pranayama", "tai chi", "taichi"
]
```

**Criteria**:
- Any keyword found in query

**Routing**: Deep Research Path (needs mechanism depth)

**Processing**:
- Deep research with mechanism focus
- Extended exploration

**Timing**: 40-103 seconds

---

### 2.6 Deep Indicator Detection

**Location**: `src/thesidia_hybrid_adaptive.py` (lines 4111-4121)

**Indicators**:
```python
deep_indicators = [
    "true origins", "real origins", "what's really", "what are", "what are X really",
    "deeper", "darker", "secrets", "uncover", "reveal", "full deep dive", "deep dive",
    "comprehensive", "extensive", "really", "actually", "truth", "real", "true",
    "origins", "history", "power structures", "patterns", "connections", "what happened",
    "ufo", "ufos", "military", "evidence", "proof", "pyramids", "ancient", "egypt",
    "mechanisms", "how does", "how it works", "explain the", "what are the mechanisms",
    "decode", "decoded", "decrypt", "decrypted", "dycrpted", "dycrypt", "hack", "hacking", "matrix", "reality"
]
```

**Criteria**:
- Any indicator found in query

**Routing**: Deep Research Path (if not fast mode)

**Processing**:
- Deep research
- Extended exploration

**Timing**: 40-103 seconds

---

## 3. Routing Decision Logic

### 3.1 Fast Mode Routing

**Location**: `src/thesidia_hybrid_adaptive.py` (lines 4151-4154)

**Logic**:
```python
if fast_mode:
    # Fast mode: Only route to deep if explicitly requested
    if deep_research_query:
        should_route_to_deep = True
```

**Behavior**:
- Skips research by default
- Only routes to deep research if explicitly requested
- Direct response path

**Timing**: 5-15 seconds

---

### 3.2 Deep Mode Routing

**Location**: `src/thesidia_hybrid_adaptive.py` (lines 4155-4164)

**Logic**:
```python
else:
    # Deep mode: Full routing logic
    if deep_research_query:
        should_route_to_deep = True
    elif is_mind_body_query:
        should_route_to_deep = True
    elif has_deep_indicator:
        should_route_to_deep = True
    elif needs_forensic_analysis:  # ALWAYS route - no length check
        should_route_to_deep = True
```

**Behavior**:
- Routes to deep research if any condition met
- Forensic analysis always routes (no exceptions)
- Comprehensive routing logic

**Timing**: 40-103 seconds

---

### 3.3 Research Requirement Detection

**Location**: `src/thesidia_hybrid_adaptive.py` (lines 4721-4780)

**Function**: `_needs_research(text)`

**Exclusions**:
```python
simple_patterns = [
    r'^what is \d+\s*[\+\-\*/]\s*\d+',  # Math: "what is 2+2"
    r'^what is \d+$',  # Simple numbers only
    r'^how are you$',  # Greetings
    r'^hey$',  # Casual greetings
    r'^hi$',  # Greetings
    r'^hello$',  # Greetings
]
```

**Logic**:
- Excludes simple patterns
- Uses LLM-based classification (not keyword matching)
- Considers user interests and technical domain

**Routing**: Research Path (if needed)

**Processing**:
- Web search
- Synthesis
- Standard response

**Timing**: 20-42 seconds (fast mode) or 30-90 seconds (deep mode)

---

## 4. Configuration Points

### 4.1 Fast Mode Setting

**Location**: `webapp/app.js` (line 1320), `webapp/server.py` (line 978)

**Default**: `true`

**Effect**:
- Skips research by default
- 30-second timeout
- Quick responses

**User Control**: UI toggle (if available)

---

### 4.2 Research Depth

**Location**: `webapp/app.js` (line 1321), `webapp/server.py` (line 979)

**Values**:
- Fast mode: 1 (quick search)
- Deep mode: 3 (comprehensive search)

**Effect**:
- Number of search queries
- Synthesis depth
- Response length

**User Control**: UI selection (if available)

---

### 4.3 Format Mode

**Location**: `webapp/server.py` (line 977)

**Values**:
- `'natural'`: Natural prose (default)
- `'structured'`: Forensic format (::EXPOSURE::)

**Effect**:
- Response format
- Post-processing behavior

**User Control**: UI selection (if available)

---

### 4.4 Task Type

**Location**: `webapp/server.py` (line 991)

**Values**:
- `'conversation'`: Default
- `'gnostic_blade'`: Forensic analysis (auto-set if forensic routing detected)

**Effect**:
- Processing path
- Model selection
- Response style

**User Control**: Auto-detected

---

## 5. Routing Priority

**Priority Order** (highest to lowest):

1. **Simple Greeting**: Always routes to fast greeting path (bypasses all other checks)
2. **Conversational Query**: Always skips research (even in deep mode)
3. **Forensic Routing**: Always routes to deep research (no exceptions)
4. **Explicit Deep Research**: Routes to deep research if requested
5. **Mind-Body Query**: Routes to deep research (needs mechanism depth)
6. **Deep Indicators**: Routes to deep research (if not fast mode)
7. **Research Requirement**: Routes to research path (if needed and not fast mode)
8. **Default**: Direct response path

---

## 6. Routing Examples

### Example 1: Simple Greeting
**Query**: "hi"
**Routing**: Simple Greeting → Fast Path
**Processing**: Cached prompt, 50-100 tokens, minimal processing
**Time**: 1-3 seconds

### Example 2: Conversational
**Query**: "what's your favorite movie?"
**Routing**: Conversational → Skip Research
**Processing**: Direct model call, no research
**Time**: 5-15 seconds

### Example 3: Forensic (Health)
**Query**: "what are the health effects of X?"
**Routing**: Forensic → Deep Research
**Processing**: Multi-source research, forensic analysis, gnostic map update
**Time**: 40-103 seconds

### Example 4: Fast Mode Research
**Query**: "tell me about quantum physics"
**Routing**: Fast Mode → Skip Research (unless explicitly requested)
**Processing**: Direct model call, no research
**Time**: 5-15 seconds

### Example 5: Deep Mode Research
**Query**: "tell me about quantum physics"
**Routing**: Deep Mode → Research (if needed)
**Processing**: Web search, synthesis, comprehensive response
**Time**: 30-90 seconds

---

## 7. Routing Configuration

### 7.1 Query Normalization

**Location**: `src/support/query_utils.py` (lines 12-46)

**Function**: `normalize_query(text)`

**Operations**:
- Lowercase conversion
- Typo fixes (genensis→genesis, dycrpted→decrypted)

**Purpose**: Ensure routing works despite typos

---

### 7.2 Forensic Routing Configuration

**Location**: `src/support/query_utils.py` (lines 49-111)

**Parameters**:
- `comprehensive`: If True, includes extended keywords (health, finance, law)

**Usage**:
- Basic detection: `detect_forensic_routing(text, comprehensive=False)`
- Comprehensive detection: `detect_forensic_routing(text, comprehensive=True)`

**Default**: Comprehensive detection used in main processing

---

## 8. Recommendations

### 8.1 Routing Improvements

1. **Explicit Mode Selection**: Allow users to explicitly request deep research mode
2. **Routing Transparency**: Show users which path their query took
3. **Routing Overrides**: Allow users to override automatic routing
4. **Routing History**: Track routing decisions for analysis

### 8.2 Configuration Enhancements

1. **Per-User Preferences**: Store user preferences for fast/deep mode
2. **Smart Defaults**: Learn user preferences over time
3. **Mode Suggestions**: Suggest appropriate mode based on query complexity

---

## 9. Conclusion

The Thesidia AI routing system is comprehensive and handles a wide variety of query types. The multi-stage decision tree ensures appropriate processing for each query type, with clear priorities and fallback mechanisms.

**Strengths**:
- Comprehensive routing logic
- Multiple detection mechanisms
- Clear priority order
- Graceful fallbacks

**Weaknesses**:
- Complex decision tree (may be hard to debug)
- No routing transparency for users
- Limited user control over routing

**Priority Improvements**:
1. Add routing transparency (show users which path was taken)
2. Simplify routing logic where possible
3. Add user controls for routing overrides
