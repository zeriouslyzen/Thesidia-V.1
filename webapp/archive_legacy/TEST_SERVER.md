# Server Status Check

## ✅ Fixed Issues

1. **Dependencies**: All required packages installed
   - flask ✅
   - flask-cors ✅
   - ollama ✅
   - chromadb ✅
   - requests ✅
   - beautifulsoup4 ✅
   - lxml ✅

2. **Imports**: All imports working
   - ThesidiaHybridAdaptive ✅
   - Flask ✅
   - All dependencies ✅

3. **Port Handling**: Server now finds free port automatically
   - Checks ports 5000-5009
   - Uses first available port
   - Prints port number on startup

## To Start Server

```bash
cd webapp
source venv/bin/activate
python3 server.py
```

Server will start on first available port (5000-5009) and print the URL.

## Note About Port 5000

On macOS, port 5000 is often used by AirPlay Receiver. The server now automatically finds an available port.

To disable AirPlay Receiver:
- System Preferences → General → AirDrop & Handoff
- Turn off AirPlay Receiver

Or just use the port the server finds automatically.

