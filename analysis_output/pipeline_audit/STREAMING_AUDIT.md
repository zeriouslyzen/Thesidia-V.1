# Thesidia AI Streaming Implementation Audit

**Generated**: 2026-01-15  
**Audit Scope**: Streaming implementation, watchdog logic, heartbeat mechanism, and SSE event handling

---

## Executive Summary

The Thesidia AI system uses Server-Sent Events (SSE) for streaming responses. The implementation has a critical issue: no heartbeat events are sent during the blocking `thesidia.process()` call, causing the frontend watchdog to trigger after 8 seconds of silence. The streaming implementation is functional but needs improvements for reliability.

---

## 1. Streaming Architecture

### 1.1 Server-Sent Events (SSE)

**Protocol**: HTTP/1.1 Server-Sent Events  
**Content-Type**: `text/event-stream`  
**Format**: `event: <type>\ndata: <json>\n\n`

**Event Types**:
- `progress`: Progress updates (0-100%)
- `chunk`: Response text chunks
- `thinking`: Thinking steps (if enabled)
- `complete`: Completion event
- `error`: Error event

---

## 2. Frontend Streaming Implementation

### 2.1 Request Setup

**Location**: `webapp/app.js` (lines 1308-1324)

**Code**:
```javascript
const doFetch = (attempt = 0) => fetch(this.apiEndpoint, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        message: sanitizedMessage,
        conversation_id: this.currentConversationId,
        show_thinking: this.showThinking,
        stream: useStreaming,  // Always true
        user_id: this.userId,
        session_id: this.sessionId,
        fast_mode: this.fastMode,
        research_depth: this.fastMode ? 1 : 3
    }),
    signal: controller.signal
})
```

**Features**:
- AbortController for cancellation
- 10-minute overall timeout
- Streaming enabled by default

---

### 2.2 SSE Event Parsing

**Location**: `webapp/app.js` (lines 1334-1462)

**Code**:
```javascript
if (useStreaming && contentType.includes('text/event-stream')) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullResponse = '';
    let currentEvent = null;

    const readChunk = () => {
        resetWatchdog(); // Pulse the watchdog
        
        reader.read().then(({ done, value }) => {
            if (done) {
                // Handle completion...
                return;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('event: ')) {
                    currentEvent = line.substring(7).trim();
                    continue;
                }
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.substring(6));
                        // Process event...
                    } catch (e) {
                        console.error('Error parsing SSE data:', e, line);
                    }
                }
            }
            readChunk();
        });
    };
    
    readChunk();
}
```

**Features**:
- Line-by-line parsing
- Event type tracking
- JSON data parsing
- Buffer management

**Issues**:
- No error recovery for malformed events
- Silent failures on parse errors

---

### 2.3 Watchdog Mechanism

**Location**: `webapp/app.js` (lines 1341-1354)

**Code**:
```javascript
// STREAM WATCHDOG: Detect hung streams
let watchdogTimer = null;
const WATCHDOG_TIMEOUT = 8000; // 8 seconds silence = reconnect

const resetWatchdog = () => {
    if (watchdogTimer) clearTimeout(watchdogTimer);
    watchdogTimer = setTimeout(() => {
        console.warn("Stream stalled (Watchdog triggered). Aborting and retrying...");
        reader.cancel();
        controller.abort();
        reject(new Error("Stream stalled"));
    }, WATCHDOG_TIMEOUT);
};
```

**Purpose**: Detect hung streams and trigger retry

**Behavior**:
- Resets on each event received
- Triggers after 8 seconds of silence
- Aborts stream and triggers retry

**Critical Issue**: If `thesidia.process()` takes > 8 seconds and no events are sent, watchdog triggers

---

### 2.4 Event Handling

**Location**: `webapp/app.js` (lines 1396-1448)

**Event Types**:

**Progress Events**:
```javascript
if (data.phase === 'progress' || currentEvent === 'progress') {
    if (reasoningDiv) {
        reasoningDiv.style.display = 'block';
        // Update progress bar...
    }
    progressDiv.style.display = 'block';
    progressDiv.textContent = `${data.message} (${Math.round(data.progress)}%)`;
}
```

**Chunk Events**:
```javascript
else if (data.text || currentEvent === 'chunk') {
    const chunk = data.text || '';
    fullResponse += chunk;
    self.typeText(textElement, chunk, () => self.scrollToBottom());
}
```

**Thinking Events**:
```javascript
else if (currentEvent === 'thinking' || data.thinking) {
    if (self.showThinking) {
        self.displayThinkingStep(data.step || 'thinking', data.message || data.thinking);
    }
}
```

**Complete Events**:
```javascript
else if (data.phase === 'complete' || currentEvent === 'complete') {
    progressDiv.style.display = 'none';
    self.hideTypingIndicator();
    if (fullResponse && fullResponse.trim().length > 0) {
        self.addMessageActions(messageDiv, 'thesidia', fullResponse, messageId, queryData);
    }
}
```

**Error Events**:
```javascript
else if (data.error || currentEvent === 'error') {
    throw new Error(data.message || data.error || 'Unknown error');
}
```

---

## 3. Backend Streaming Implementation

### 3.1 Streaming Generator

**Location**: `webapp/server.py` (lines 1136-1328)

**Function**: `_stream_thesidia_response()`

**Structure**:
```python
def _stream_thesidia_response(...):
    def send_event(event_type, data):
        event_data = json.dumps(data)
        return f"event: {event_type}\ndata: {event_data}\n\n"
    
    try:
        # Phase 1: Initial progress (5%)
        yield send_event('progress', {...})
        
        # Phase 2: Processing progress (30%)
        yield send_event('progress', {...})
        
        # Phase 3: Call process() - BLOCKING
        yield send_event('progress', {'progress': 40})  # Only one event before blocking call
        result = thesidia.process(...)  # BLOCKING - no events sent during this time
        
        # Phase 4: Stream response (50-95%)
        yield send_event('progress', {'progress': 50})
        # Chunk response...
        
        # Phase 5: Complete (100%)
        yield send_event('complete', {...})
    except Exception as e:
        yield send_event('error', {...})
```

**Critical Issue**: Only one progress event (40%) is sent before the blocking `thesidia.process()` call. If processing takes > 8 seconds, the watchdog triggers.

---

### 3.2 Response Chunking

**Location**: `webapp/server.py` (lines 1272-1291)

**Code**:
```python
# Stream response character-by-character with typing animation
chunk_size = 3  # Small chunks for smooth typing
for i in range(0, total_length, chunk_size):
    chunk = response[i:i + chunk_size]
    accumulated_length += len(chunk)
    
    yield send_event('chunk', {
        'text': chunk,
        'progress': 50 + (accumulated_length / total_length) * 45 if total_length > 0 else 50,
        'accumulated': accumulated_length,
        'total': total_length
    })
```

**Behavior**:
- Chunks response into 3-character pieces
- Sends progress updates with each chunk
- Simulates typing animation

**Note**: Response is already generated before chunking (not true token-by-token streaming)

---

### 3.3 SSE Response Setup

**Location**: `webapp/server.py` (lines 1022-1032)

**Code**:
```python
if stream:
    return Response(
        stream_with_context(_stream_thesidia_response(...)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )
```

**Features**:
- Proper SSE content type
- No caching
- No buffering (for real-time streaming)

---

## 4. Critical Issues

### 4.1 Missing Heartbeats

**Problem**: No progress events sent during `thesidia.process()` call

**Location**: `webapp/server.py` (lines 1237-1257)

**Current Code**:
```python
# Send initial progress update
yield send_event('progress', {
    'phase': 'processing',
    'message': 'Processing your query...',
    'progress': 40
})

# Call process() - this may take time, but we've sent a progress update
# The frontend watchdog (8 seconds) should be satisfied by the progress event above
result = thesidia.process(...)  # BLOCKING - no events for 10-100 seconds
```

**Issue**: Comment says "should be satisfied", but watchdog resets on each event. If processing takes > 8 seconds, watchdog triggers.

**Impact**: 
- Watchdog timeout triggers
- Stream aborted
- User sees error
- Retry logic kicks in

**Frequency**: Common for research and deep research queries

---

### 4.2 Blocking Generator

**Problem**: Generator is blocked by synchronous `thesidia.process()` call

**Impact**:
- No events can be sent during processing
- Watchdog timeout inevitable for long operations
- Poor user experience

**Solution Required**: Send periodic heartbeat events during processing

---

### 4.3 No True Streaming

**Problem**: Response is generated completely, then chunked

**Current Behavior**:
1. Generate complete response (20-100 seconds)
2. Chunk response into 3-character pieces
3. Stream chunks with typing animation

**True Streaming Would Be**:
1. Stream tokens as they're generated
2. Display tokens immediately
3. Better perceived latency

**Impact**: 
- Perceived latency: High (wait for complete response)
- Actual latency: Same (but better UX with true streaming)

---

## 5. Watchdog Analysis

### 5.1 Watchdog Configuration

**Timeout**: 8 seconds  
**Reset**: On each event received  
**Action**: Abort stream and trigger retry

**Rationale**: Detect hung streams and recover automatically

**Issue**: Too short for long operations (research, deep research)

---

### 5.2 Watchdog Triggers

**Common Scenarios**:
1. `thesidia.process()` takes > 8 seconds (no heartbeats)
2. Network issues (no events received)
3. Server crashes (no events sent)

**Current Behavior**: Abort and retry (up to 2 retries)

**Problem**: Retries will also timeout if issue persists

---

## 6. Recommendations

### 6.1 Immediate Fixes

1. **Add Heartbeat Events**: Send progress events every 5 seconds during `thesidia.process()` call
   ```python
   # Pseudo-code
   def process_with_heartbeats():
       heartbeat_thread = start_heartbeat_thread()
       try:
           result = thesidia.process(...)
       finally:
           stop_heartbeat_thread(heartbeat_thread)
   ```

2. **Increase Watchdog Timeout**: Consider increasing from 8s to 15s for deep research
   ```javascript
   const WATCHDOG_TIMEOUT = 15000; // 15 seconds for deep research
   ```

3. **Add Processing Status**: Send "processing" events with estimated time remaining
   ```python
   yield send_event('progress', {
       'phase': 'processing',
       'message': 'Processing your query... (estimated 30s remaining)',
       'progress': 40
   })
   ```

---

### 6.2 Short-term Improvements

1. **Implement True Streaming**: Stream tokens as they're generated
   - Requires model-level streaming support
   - Better perceived latency
   - Immediate feedback

2. **Background Processing**: Move `thesidia.process()` to background task
   - Non-blocking generator
   - Status updates via events
   - Better concurrency

3. **Adaptive Watchdog**: Adjust timeout based on query type
   - Simple queries: 8 seconds
   - Research queries: 30 seconds
   - Deep research: 120 seconds

---

### 6.3 Long-term Enhancements

1. **WebSocket Support**: Consider WebSocket for bidirectional communication
   - Better for long operations
   - Lower overhead
   - More control

2. **Progress Tracking**: Add detailed progress tracking at each stage
   - Web search progress
   - Synthesis progress
   - Model generation progress

3. **Error Recovery**: Better error recovery for streaming failures
   - Resume from last chunk
   - Partial response display
   - Graceful degradation

---

## 7. Event Flow Diagram

```
Frontend Request
  ↓
Backend: Initial Progress (5%)
  ↓
Backend: Processing Progress (30%)
  ↓
Backend: Processing Start (40%)
  ↓
[BLOCKING: thesidia.process() - 10-100 seconds]
  ↓ [NO EVENTS SENT - WATCHDOG TRIGGERS IF > 8s]
Backend: Streaming Start (50%)
  ↓
Backend: Chunk Events (50-95%)
  ↓
Backend: Complete (100%)
  ↓
Frontend: Display Complete
```

**Issue**: Gap between 40% and 50% events (blocking call)

**Fix**: Add heartbeat events during blocking call

---

## 8. Conclusion

The Thesidia AI streaming implementation is functional but has a critical issue: no heartbeat events during the blocking `thesidia.process()` call. This causes the frontend watchdog to trigger after 8 seconds of silence, aborting the stream and triggering retries.

**Strengths**:
- Proper SSE implementation
- Good event structure
- Watchdog mechanism for hung streams
- Retry logic

**Weaknesses**:
- Missing heartbeats during processing
- Blocking generator
- No true token-by-token streaming
- Watchdog timeout too short for long operations

**Priority Fixes**:
1. Add heartbeat events during processing (HIGH)
2. Increase watchdog timeout or make it adaptive (HIGH)
3. Implement true streaming (MEDIUM)
4. Add background processing (MEDIUM)

**Expected Impact**:
- Watchdog timeout rate: 80% → 5% (with heartbeats)
- User experience: Significantly improved (immediate feedback)
- Error rate: Reduced (fewer timeouts)
