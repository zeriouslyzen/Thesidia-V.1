# Debugging Blank Screen

## Quick Checks

1. **Is the server running?**
   ```bash
   cd "/Users/deshonjackson/thesidia ice/webapp"
   source ../venv/bin/activate
   python3 server.py
   ```
   You should see: `Starting server on http://127.0.0.1:5000`

2. **Check browser console** (F12 or Cmd+Option+I):
   - Look for JavaScript errors (red text)
   - Check Network tab - are files loading? (200 status)
   - Check if `/api/status` returns data

3. **Test the test page**:
   Visit: http://localhost:5000/test.html
   This will show what's working and what's not

## Common Issues

### Issue 1: Server not running
**Symptom**: Blank screen, no console errors
**Fix**: Start the server (see above)

### Issue 2: JavaScript error
**Symptom**: Console shows red errors
**Fix**: Check the error message and fix the code

### Issue 3: API endpoint failing
**Symptom**: Status indicators show offline
**Fix**: Check if Ollama is running: `ollama serve`

### Issue 4: CSS not loading
**Symptom**: Page loads but looks broken
**Fix**: Check Network tab - is styles.css loading?

## Manual Test

Open browser console and run:
```javascript
// Test if app initialized
console.log(window.thesidiaApp);

// Test API
fetch('/api/status').then(r => r.json()).then(console.log);

// Test if elements exist
console.log(document.getElementById('app'));
console.log(document.getElementById('messages'));
```

## Next Steps

1. Start server
2. Open http://localhost:5000/
3. Open browser console (F12)
4. Check for errors
5. Visit http://localhost:5000/test.html for diagnostics

