# Streaming and Greeting Flow (How the System Actually Works)

## Request path (streaming)

1. **Client (app.js)**  
   POST `/api/thesidia` with `message`, `stream: true`, `user_id`, `session_id`, `fast_mode`, `research_depth`.  
   Expects SSE: `event: progress` (with `data: { progress, message }`) and `event: chunk` (with `data: { text }`).  
   **Watchdog:** If no *chunk* (or other data that triggers a `read()`) arrives within `WATCHDOG_TIMEOUT` (60s fast / 180s deep), client aborts and rejects with "Stream stalled". When the stream ends, if `fullResponse` is still empty, client throws "Empty streaming response".

2. **Server (server.py)**  
   For `stream=true`, returns `Response(stream_with_context(_stream_thesidia_response(...)), mimetype='text/event-stream')`.

3. **_stream_thesidia_response (generator)**  
   - **Classification (UX only):**  
     `is_simple_greeting = (text in ['hi','hello','hey'] or len(words) <= 2)`.  
     Used only to choose which progress messages to send.  
   - **Yields:** A few progress events (5%, 30%, 40%).  
   - **Then:** `result = thesidia.process(message, context)` — **blocking**.  
     No further `yield` until `process()` returns.  
   - **Then:** Yields progress 50%, then chunk events (sliced full response), then `complete`.  
   So the client gets a short burst of progress, then **silence for the entire duration of `thesidia.process()`**. If that takes >60s, the client watchdog fires and the stream is aborted; when the connection dies, the client has no body text → "Empty streaming response".

4. **thesidia.process() (wrapper in thesidia_hybrid_adaptive.py)**  
   - **Fast-mode heuristic:**  
     `is_simple_greeting = (text in ("hi","hello","hey") or len(words) <= 3)`.  
     If True, `effective_fast_mode = False` (no 30s timeout).  
   - Calls `_process_original(...)` (same for greeting vs non-greeting; only timeout is skipped for “greeting”).

5. **_process_original (actual pipeline)**  
   - **Greeting check (fast path):**  
     `greeting_only_patterns` = regexes:  
     - `^(hi|hello|hey|greetings|hi+)+[\s,]*$`  
     - `^(hi|hello|hey|greetings)[\s,]+(there|you|how are you)[\s,]*$`  
     and `len(words) <= 4`.  
     `is_simple_greeting = any(re.match(...)) and len <= 4`.  
   - If `is_simple_greeting`: takes **fast path** (cached greeting prompt, single model call, no research).  
   - If not: full pipeline (memory, forensic check, research, synthesis, model call) — can take 60+ seconds.

## Why "whats good thesidia" stalls

- **Server stream:** `is_simple_greeting` = False (3 words, not in ['hi','hello','hey'] and not len<=2). So we only send a few progress events, then block on `process()`.
- **process() wrapper:** Treats it as “greeting” for timeout only (len <= 3 → no 30s timeout).
- **_process_original:** "whats good thesidia" does **not** match `greeting_only_patterns` (doesn’t start with hi/hello/hey/greetings). So `is_simple_greeting` = False → **full pipeline** runs → 60+ seconds → stream yields nothing until then → client watchdog fires → "Stream stalled" / "Empty streaming response".

So the stall is not a bug in the watchdog; it’s that the **only** place that actually short-circuits to a fast reply is `_process_original`’s regex, and "whats good thesidia" doesn’t match it.

## Fix (aligned with how the system works)

- **Option A (recommended):** In `_process_original`, broaden what counts as a greeting so short casual openers take the fast path:  
  - Either extend `greeting_only_patterns` to include things like "whats good", "what's good", "how you doing", "how are you", "sup", "yo", or  
  - Add a fallback: if `len(words) <= 4` and the query is clearly conversational (e.g. no question words like "why"/"when"/"where" or no deep indicators), treat as greeting and use the fast path.  
  Then "whats good thesidia" returns in a few seconds, the generator yields chunks before 60s, and the client never hits the watchdog.

- **Option B:** In `_stream_thesidia_response`, treat more inputs as “simple greeting” for UX (e.g. len<=3 or “whats good” etc.) so we at least show “Responding…” — but the **real** fix is still in `_process_original`, otherwise we still block for 60+ seconds and the client will stall.

- **Option C:** Don’t block the generator on `process()`. Run `process()` in a thread/executor and periodically yield "still working" progress events (e.g. every 15s) until `process()` returns, then yield chunks. That would prevent the watchdog from firing but is a bigger change; aligning the greeting definition (Option A) is smaller and matches the existing fast path.

## Summary

| Layer                    | Who decides “greeting”? | "whats good thesidia" |
|--------------------------|-------------------------|------------------------|
| app.js                   | N/A (watchdog only)     | —                      |
| _stream_thesidia_response| UX only, len<=2 or hi/hello/hey | **No** (3 words) |
| process() wrapper        | Timeout only, len<=3    | Yes (no timeout)       |
| _process_original        | Fast path, regex + len<=4 | **No** (regex)      |

So the **only** place that actually sends a quick reply is `_process_original`’s greeting branch. Align that with the wrapper (and optionally with the stream UX) so short casual openers like "whats good thesidia" use the fast path end-to-end.
