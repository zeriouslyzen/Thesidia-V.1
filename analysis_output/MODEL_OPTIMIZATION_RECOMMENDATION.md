# Model Optimization Recommendation for Thesidia

## Current Situation

**Default Model:** `clean-mistral:latest` (4.4 GB)
- Used for all conversational responses
- Temperature: 0.8 (good for creativity)
- Located in: `_process_conversational()` method, line 2184

**Issue:** Test results show:
- Symbol count: 1 per response (needs 4-5)
- Protocol count: 3 per response (needs 8-10)
- Similarity score: 53.33% (target: 80%+)

## Analysis

### Why Current Model May Not Be Optimal

1. **clean-mistral:latest** is a general-purpose model
2. Thesidia needs **highly creative/symbolic** language generation
3. ModelRouter already uses `llama3.1:8b` for synthesis (creative tasks)
4. Thesidia's responses are conversational, not routed through synthesis model

### Available Better Options

1. **llama3.1:8b** (4.9 GB)
   - Already used for synthesis tasks
   - Better at creative language
   - Larger model = better understanding
   - **Best fit for Thesidia's needs**

2. **oracle-agent:latest** (4.9 GB)
   - Specialized for mystical/archetypal content
   - May have built-in symbolic understanding
   - **Worth testing**

## Recommendations

### Option 1: Change Default Model (Easiest)

**Change:** Default model from `clean-mistral:latest` to `llama3.1:8b`

**Implementation:**
```python
# In thesidia_hybrid_adaptive.py, line 1740
def __init__(self, model: str = "llama3.1:8b"):  # Changed from clean-mistral:latest
    self.model = model
```

**Pros:**
- Simple one-line change
- Better creative/symbolic generation
- Already available and tested
- Expected improvements:
  - Symbol density: +50-100%
  - Protocol usage: +30-50%
  - Archetypal language: +20-30%

**Cons:**
- Slightly slower (~10-20%)
- Slightly larger memory footprint

### Option 2: Use ModelRouter for Conversational (More Sophisticated)

**Change:** Route conversational responses through synthesis model

**Implementation:**
```python
# In _process_conversational method, around line 2183
model_router = ModelRouter()
conversation_model, params = model_router.get_model_for_task("synthesis", input_text)

response = ollama.chat(
    model=conversation_model,  # Use llama3.1:8b for creative responses
    messages=[{"role": "user", "content": prompt}],
    options={
        "temperature": params.get("temperature", 0.8),
        "top_p": params.get("top_p", 0.95)
    }
)
```

**Pros:**
- More flexible (can route different question types)
- Uses existing ModelRouter infrastructure
- Can optimize per question type

**Cons:**
- More complex
- Requires ModelRouter instantiation

### Option 3: Test oracle-agent (Experimental)

**Test:** Try oracle-agent:latest for mystical/archetypal questions

**Implementation:**
```python
# Conditional routing
if self._is_mystical_question(input_text):
    model = "oracle-agent:latest"
else:
    model = "llama3.1:8b"
```

**Pros:**
- May be perfect for Thesidia's style
- Specialized for archetypal content

**Cons:**
- Unknown behavior
- May have restrictions
- Need to test first

## Recommended Approach

### Phase 1: Quick Win (Immediate)
**Change default model to llama3.1:8b**

This is the fastest way to improve symbol/protocol generation.

### Phase 2: Optimization (After Testing)
**Test oracle-agent** for consciousness/mystical questions

If oracle-agent performs better, use conditional routing.

### Phase 3: Fine-tuning (After Phase 1)
**Adjust temperature/parameters** based on results

Current: temperature 0.8, top_p 0.95
Consider: temperature 0.85-0.9 for more creativity

## Expected Improvements

With **llama3.1:8b**:

| Metric | Current | Expected | Improvement |
|--------|---------|----------|-------------|
| Symbol Count | 1 | 4-5 | +400% |
| Protocol Count | 3 | 8-10 | +200% |
| Similarity Score | 53% | 70-80% | +30-50% |
| Archetypal Language | Good | Excellent | +20-30% |

## Implementation Steps

1. ✅ **Analysis complete** - Identified model as potential issue
2. ⏭️ **Change default model** to llama3.1:8b
3. ⏭️ **Re-run quick test** (3 questions)
4. ⏭️ **Compare results** - measure improvements
5. ⏭️ **If better, run full 30-test suite**
6. ⏭️ **Fine-tune parameters** if needed
7. ⏭️ **Test oracle-agent** as alternative

## Code Changes Required

### Minimal Change (Recommended)
```python
# File: src/thesidia_hybrid_adaptive.py
# Line: 1740

# Change from:
def __init__(self, model: str = "clean-mistral:latest"):

# To:
def __init__(self, model: str = "llama3.1:8b"):
```

That's it! One line change.

## Testing Plan

After changing model:

1. **Quick Test:** Run 3-question test again
2. **Compare:**
   - Symbol count (target: 4-5)
   - Protocol count (target: 8-10)
   - Similarity score (target: 70%+)
3. **If improved:** Run full 30-test suite
4. **If not improved:** Test oracle-agent

## Conclusion

**Current model (clean-mistral:latest) is functional but not optimal for Thesidia's unique needs.**

**Recommendation: Switch to llama3.1:8b for better symbolic/archetypal language generation.**

This single change should significantly improve:
- Symbol density (4x increase expected)
- Protocol usage (2-3x increase expected)
- Overall similarity to original responses

