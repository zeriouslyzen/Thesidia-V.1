# Testing Refactored Code

## Quick Test

The refactoring is complete and all imports work. To test in browser:

### Option 1: Use Test Page (Recommended)

1. **Open in browser**: `http://localhost:5002/test_refactoring.html`
2. Click "Run All Tests" button
3. Verify all tests pass (green checkmarks)

### Option 2: Manual Testing

1. **Test Status**: `http://localhost:5002/api/status`
   - Should return JSON with `thesidia_ready: true/false`

2. **Test Query Normalization (typo fix)**:
   - Send POST to `/api/thesidia` with `{"message": "genensis", "stream": false}`
   - Should normalize "genensis" → "genesis" and route correctly
   - Check server logs for: `🔍 NORMALIZED: 'genesis'`

3. **Test Forensic Routing**:
   - Send POST to `/api/thesidia` with `{"message": "what is genesis really about", "stream": false}`
   - Should detect forensic query and route to deep research
   - Check server logs for: `🔍 NEEDS FORENSIC: True`

4. **Test Streaming**:
   - Send POST to `/api/thesidia` with `{"message": "hello", "stream": true}`
   - Should return Server-Sent Events (SSE) stream
   - Check server logs for streaming messages

### Option 3: Restart Server (If Needed)

If the server doesn't auto-reload changes:

```bash
# Kill existing server
kill 20075

# Restart server
cd webapp
python3 server.py
```

Then test again.

## What to Verify

✅ **Query Normalization**:
- Typo "genensis" → normalized to "genesis"
- Typo "dycrpted" → normalized to "decrypted"
- Server logs show normalized queries

✅ **Forensic Routing**:
- Queries with "genesis", "bible", "decode" trigger forensic analysis
- Server logs show `NEEDS FORENSIC: True`
- Responses include forensic analysis format

✅ **Profile Loading**:
- `/api/posts?user_id=...` returns posts with author profiles
- `/api/feed?user_id=...` returns feed with author profiles
- Missing profiles fall back to default gracefully

✅ **No Errors**:
- No import errors in server logs
- No 500 errors from endpoints
- All endpoints return valid JSON

## Expected Server Log Output

When testing, you should see:
```
🔍 RAW USER INPUT: 'genensis'
🔍 NORMALIZED: 'genesis'
🔍 NEEDS FORENSIC: True
```

This confirms the refactored code is working!

