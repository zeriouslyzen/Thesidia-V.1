# Deep Research Fix Summary

**Date**: 2026-01-16  
**Issue**: Deep research queries timing out due to short watchdog timeout  
**Status**: ✅ Fixed

---

## Problem

Deep research queries like "what are the origins of the pegasus horse" were:
1. ✅ Routing correctly to deep research
2. ❌ Timing out after 8 seconds (watchdog timeout)
3. ❌ User seeing "Stream stalled" errors

**Root Cause**: Frontend watchdog timeout (8 seconds) was too short for deep research, which takes 40-103 seconds.

---

## Fixes Applied

### 1. Frontend Watchdog Timeout (`webapp/app.js`)

**Change**: Increased timeout for deep research queries from 8 seconds to 2 minutes (120 seconds)

**Detection**: Automatically detects deep queries by:
- Checking if `fast_mode` is false, OR
- Checking if query contains deep indicators: "origins", "history", "deep", "comprehensive", etc.

**Code**:
```javascript
const isDeepQuery = !this.fastMode || 
    sanitizedMessage.toLowerCase().match(/\b(origins?|history|deep|comprehensive|forensic|decode|uncover|reveal|secrets?)\b/);
const WATCHDOG_TIMEOUT = isDeepQuery ? 120000 : 8000; // 2 minutes for deep, 8 seconds for fast
```

### 2. Backend Progress Messages (`webapp/server.py`)

**Change**: Added detection of deep indicators and sends informative progress message

**Code**:
```python
# Check for deep indicators (for watchdog timeout adjustment)
deep_indicators = [
    "origins", "history", "power structures", "patterns", "connections", 
    "true origins", "real origins", "what's really", "what are", "deeper", 
    "secrets", "uncover", "reveal", "comprehensive", "extensive"
]
text_lower = message.lower()
has_deep_indicator = any(indicator in text_lower for indicator in deep_indicators)

# Send informative message before deep research
if needs_forensic or has_deep_indicator:
    yield send_event('progress', {
        'phase': 'deep_research',
        'message': 'Starting deep research analysis... This may take 30-90 seconds.',
        'progress': 40
    })
```

### 3. Conversational Query Detection (`src/thesidia_hybrid_adaptive.py`)

**Change**: Added patterns for "what can you do" queries to prevent them from triggering research

**Added Patterns**:
- `r'what.*?can you do'` - "what can you do?" / "what else can you do?"
- `r'what.*?you do\??$'` - "what do you do?" / "what else do you do?"
- `r'what.*?your capabilities'` - "what are your capabilities?"
- `r'what.*?you.*?good at'` - "what are you good at?"

### 4. Read Message Function Fix (`webapp/app.js`)

**Change**: Improved error handling for `readMessage` function

**Code**:
```javascript
if (self && typeof self.readMessage === 'function') {
    try {
        self.readMessage(content, messageId, readBtn);
    } catch (error) {
        console.error('Error calling readMessage:', error);
        alert(`Error: ${error.message}. Please check console for details.`);
    }
}
```

---

## Test Results

### Before Fix
- Deep research queries: ❌ Timeout after 8 seconds
- Conversational queries: ❌ "what else can you do" stalling

### After Fix
- Deep research queries: ✅ 2-minute timeout allows full processing
- Conversational queries: ✅ "what else can you do" detected and fast
- Read button: ✅ Better error handling

---

## Files Modified

1. `webapp/app.js` - Watchdog timeout adjustment and readMessage fix
2. `webapp/server.py` - Deep indicator detection and progress messages
3. `src/thesidia_hybrid_adaptive.py` - Conversational pattern updates

---

## Next Steps

1. ✅ Deep research now works without timeout
2. ✅ Conversational queries are faster
3. ⚠️ Consider adding periodic heartbeat events during deep research (future optimization)
4. ⚠️ Consider true token-by-token streaming for better UX (future enhancement)

---

**Status**: ✅ Fixed and tested
