# Quick Fixes for Thesidia Issues

## Issue 1: Multiple Server Processes

**Problem**: Multiple Python server processes running simultaneously, causing conflicts.

**Solution**: Updated `start_server.sh` to kill old processes before starting.

**To Apply**:
```bash
./start_server.sh
```

Or manually:
```bash
pkill -f "python.*server.py"
cd webapp
python3 server.py
```

## Issue 2: Model Availability Check

**Status**: ✅ Model `clean-mistral:latest` is available

**To Verify**:
```bash
ollama list | grep clean-mistral
```

**If Missing**:
```bash
ollama pull clean-mistral:latest
```

## Issue 3: Port Conflicts

**Current**: Server finds free port automatically (5000-5009)

**If Port Still in Use**:
```bash
# Find process using port
lsof -i :5002

# Kill it
kill -9 <PID>
```

## Issue 4: Server Not Responding

**Check**:
1. Is Ollama running?
   ```bash
   ollama list
   ```

2. Is server running?
   ```bash
   pgrep -fl "python.*server.py"
   ```

3. Check server logs:
   ```bash
   tail -f webapp/server.log
   ```

## Issue 5: Frontend Not Connecting

**Check**:
1. Open browser console (F12)
2. Check for CORS errors
3. Verify API endpoint: `/api/thesidia`
4. Check network tab for failed requests

**Common Fixes**:
- Clear browser cache
- Hard refresh (Cmd+Shift+R / Ctrl+Shift+R)
- Check server is running on correct port

## Issue 6: Streaming Not Working

**Symptoms**: Responses appear all at once instead of streaming

**Check**:
1. Server logs for SSE errors
2. Browser console for fetch errors
3. Network tab shows `text/event-stream` content type

**Fix**: Ensure `stream: true` in frontend request

## Testing Checklist

After applying fixes:

- [ ] Only one server process running
- [ ] Server starts without errors
- [ ] Ollama connection successful
- [ ] Model available
- [ ] Frontend loads correctly
- [ ] API responds to requests
- [ ] Streaming works
- [ ] No console errors

## Next Steps

See `THESIDIA_AUDIT_REPORT.md` for:
- Detailed architecture analysis
- UX issues
- Long-term improvements
- Refactoring recommendations



