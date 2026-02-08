# Timeout Investigation Report

**Date**: 2026-01-16  
**Issue**: Queries timing out in fast mode (30-second limit)  
**Status**: Partially Fixed - Root cause identified, optimization implemented

---

## Executive Summary

Thesidia queries were timing out in fast mode, even for simple queries. Investigation revealed multiple performance bottlenecks:

1. **Heavy prompt building** - `get_enhanced_prompt(query=input_text)` runs multiple module analyses (CSI, health coach, cosmos, etc.) even in fast mode
2. **MLX routing** - Queries routing to MLX models which may be slower than Ollama
3. **Large system prompts** - Even with optimizations, prompts are still large

---

## Root Causes Identified

### 1. Prompt Building Overhead

**Location**: `src/thesidia_hybrid_adaptive.py:4204`

**Problem**: 
- `get_enhanced_prompt(query=input_text)` is called for ALL queries, even in fast mode
- This triggers multiple module analyses:
  - CSI Investigator (`analyze_query`)
  - Health Coach (`analyze_health_query`)
  - Cosmos Knowledge Base (`get_relevant_knowledge`)
  - Cosmos Pattern Analyzer (`analyze_cosmological_pattern`)
  - Scientific Simulator (`should_simulate`)
  - Reporter/Archaeologist/Psychologist modes
  - Etymology/Linguistic analysis
  - Meta-Awareness checks

**Impact**: 
- Each analysis adds processing time
- Large system prompts slow down LLM inference
- Even simple queries get full prompt treatment

**Fix Applied**:
```python
# FAST MODE: Skip query-specific modules to reduce prompt size and processing time
if fast_mode:
    # Use minimal prompt (skip CSI/health/cosmos analysis) for faster responses
    enhanced_base = self.get_enhanced_prompt(query=None)
else:
    # Deep mode: Full prompt with all modules
    enhanced_base = self.get_enhanced_prompt(query=input_text)
```

### 2. Model Routing to MLX

**Location**: Logs show routing to `mlx-community/Qwen2.5-1.5B-Instruct-4bit`

**Problem**:
- MLX models may be slower than Ollama for some queries
- First-time model loading adds overhead
- MLX inference may not be optimized for fast responses

**Status**: Needs investigation - MLX may be appropriate for some queries but not all

### 3. Fast Mode Timeout Configuration

**Location**: `src/thesidia_hybrid_adaptive.py:3723`

**Current**: 30-second timeout with error message saying "20s"

**Issue**: Error message is misleading (says 20s but timeout is 30s)

---

## Test Results

### Before Fix
- Simple "Hello": ~11 seconds ✅
- Complex query (consciousness): >30 seconds ❌ (timeout)

### After Fix
- Simple "Hello": ~5 seconds ✅ (improved)
- Complex query (consciousness): Still timing out ⚠️ (needs more work)

---

## Remaining Issues

1. **Complex queries still slow**: Even with prompt optimization, complex queries like "explain consciousness" still timeout
2. **MLX performance**: Need to verify if MLX is appropriate for fast mode
3. **LLM inference time**: The actual model inference may be the bottleneck, not just prompt building

---

## Recommendations

### Immediate Actions
1. ✅ **DONE**: Skip query-specific modules in fast mode
2. **TODO**: Increase fast mode timeout to 45-60 seconds for complex queries
3. **TODO**: Add option to force Ollama instead of MLX for fast mode
4. **TODO**: Cache enhanced prompts for common query patterns

### Long-term Optimizations
1. **Streaming LLM responses**: Don't wait for full response before starting to stream
2. **Progressive enhancement**: Start with minimal prompt, add modules only if needed
3. **Model selection**: Use faster models (smaller, quantized) for fast mode
4. **Parallel processing**: Run prompt building and model loading in parallel

---

## Code Changes Made

**File**: `src/thesidia_hybrid_adaptive.py`

**Change**: Modified `_process_original()` to skip query-specific modules in fast mode:

```python
# Line 4204-4210
# Get enhanced prompt from modelfile system (includes persona, voice, preset)
# FAST MODE: Skip query-specific modules to reduce prompt size and processing time
if fast_mode:
    # Use minimal prompt (skip CSI/health/cosmos analysis) for faster responses
    enhanced_base = self.get_enhanced_prompt(query=None)
else:
    # Deep mode: Full prompt with all modules
    enhanced_base = self.get_enhanced_prompt(query=input_text)
```

---

## Next Steps

1. Test with more queries to verify improvement
2. Monitor MLX vs Ollama performance
3. Consider increasing fast mode timeout
4. Implement additional optimizations as needed

---

## Performance Metrics

| Query Type | Before | After | Target |
|------------|--------|-------|--------|
| Simple greeting | 11s | 5s | <2s |
| Conversational | 23s | ? | <5s |
| Complex question | >30s (timeout) | >30s (timeout) | <15s |

---

**Investigation Status**: ✅ Root cause identified, partial fix applied  
**Next Action**: Continue optimization and testing
