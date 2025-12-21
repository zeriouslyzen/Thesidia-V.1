# Bug Fix: "hi" Not Working

## Problem
When sending "hi" or any message, the server returned:
```
"ThesidiaHybridAdaptive.process() got an unexpected keyword argument 'input_text'"
```

## Root Cause
The `process()` method signature changed, but the server code was still using the old calling convention.

**Old (incorrect) way**:
```python
response = thesidia.process(input_text=message, user_id=user_id, ...)
```

**New (correct) way**:
```python
result = thesidia.process(
    input_data=message,
    context={
        "user_id": user_id,
        "session_id": session_id,
        "format_mode": format_mode,
        "research_depth": research_depth,
        "fast_mode": fast_mode
    }
)
response = result.get("output", "") if isinstance(result, dict) else str(result)
```

## Files Fixed
1. `webapp/server.py` - Fixed 2 locations (non-streaming and streaming)
2. `api/api_server.py` - Fixed 2 locations (non-streaming and streaming)

## Solution
The `process()` method now:
- Takes `input_data` (string) and `context` (dict) as parameters
- Returns a dictionary with `{"output": ..., "agent_id": ..., "status": ..., "metadata": ...}`
- We extract `result["output"]` to get the actual response string

## Next Steps
**Restart the server** to apply the fix:
```bash
./start_server.sh
```

Or manually:
```bash
pkill -f "python.*server.py"
cd webapp
python3 server.py
```

## Testing
After restarting, test with:
```bash
curl -X POST http://localhost:5002/api/thesidia \
  -H "Content-Type: application/json" \
  -d '{"message":"hi","stream":false}'
```

Should now return a proper response instead of an error.



