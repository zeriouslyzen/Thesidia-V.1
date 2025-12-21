# Troubleshooting Blank Screen

## Quick Fix Steps

1. **Check if server is running**:
   ```bash
   cd "/Users/deshonjackson/thesidia ice/webapp"
   source ../venv/bin/activate
   python3 server.py
   ```
   Should see: `Starting server on http://127.0.0.1:5000`

2. **Open browser console** (F12 or Cmd+Option+I):
   - Look for red error messages
   - Check if files are loading (Network tab)

3. **Test the diagnostic page**:
   Visit: http://localhost:5000/test.html
   This will show what's working

4. **Check browser console for errors**:
   - Open Developer Tools (F12)
   - Go to Console tab
   - Look for any red errors
   - Share the error message if you see one

## Common Issues

### Server Not Running
**Symptom**: Blank screen, can't connect
**Fix**: Start server (see step 1 above)

### JavaScript Error
**Symptom**: Console shows errors
**Fix**: Check error message - I've added error handling to prevent crashes

### Files Not Loading
**Symptom**: Network tab shows 404 errors
**Fix**: Make sure you're in the `webapp` directory when starting server

### Ollama Not Running
**Symptom**: Status shows offline
**Fix**: Start Ollama: `ollama serve`

## What I Fixed

1. ✅ Fixed HTML typo (extra "f" character)
2. ✅ Added error handling to prevent JavaScript crashes
3. ✅ Added null checks for DOM elements
4. ✅ Added console logging for debugging
5. ✅ Created test.html diagnostic page

## Next Steps

1. Start the server
2. Open http://localhost:5000/
3. Open browser console (F12)
4. Check for any error messages
5. If still blank, visit http://localhost:5000/test.html for diagnostics

