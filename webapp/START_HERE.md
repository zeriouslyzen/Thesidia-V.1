# ⚠️ IMPORTANT: You Need to Start the Server

## The Problem

**Opening the HTML file directly in the browser won't work!**

The app needs a server running because:
- JavaScript makes API calls to `/api/thesidia` and `/api/status`
- These API endpoints only work when the Flask server is running
- Opening `file:///path/to/index.html` won't have access to the server

## The Solution

**You MUST start the server first:**

```bash
cd "/Users/deshonjackson/thesidia ice/webapp"
source ../venv/bin/activate
python3 server.py
```

Then you'll see:
```
Starting server on http://127.0.0.1:5000
```

## Then Open in Browser

**Don't open the file directly!** Instead:

1. Start the server (see above)
2. Open your browser
3. Go to: **http://localhost:5000/**

That's it! The server must be running for the app to work.

## Quick Start Script

Or use the start script:
```bash
cd "/Users/deshonjackson/thesidia ice"
./start_server.sh
```

Then visit: http://localhost:5000/

