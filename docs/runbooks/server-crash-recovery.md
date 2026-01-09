# Runbook: Server Crash Recovery

## Symptoms
- Server not responding
- 502/503 errors
- Process not running

## Quick Check

```bash
# Check if server is running
ps aux | grep python | grep server

# Check port
lsof -i :5002
```

## Recovery Steps

### 1. Kill Stuck Processes
```bash
# Kill any orphaned processes
pkill -f "python.*server" || true
lsof -ti:5002 | xargs kill -9 2>/dev/null || true
```

### 2. Check Logs
```bash
# View recent errors
tail -100 webapp/logs/server.log
```

### 3. Restart Server
```bash
cd webapp
python3 server.py
```

### 4. Verify
- Open https://localhost:5002
- Check status endpoint: `/api/status`

## If Still Failing

1. **Check Ollama**: `ollama list` - is the model available?
2. **Check disk space**: `df -h`
3. **Check memory**: `top` or `htop`
4. **Check permissions**: Files should be readable

## Escalation

If none of the above works:
1. Save logs
2. Check for recent code changes
3. Try git stash / git checkout to revert
