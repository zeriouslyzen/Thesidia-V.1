# Development Server Setup

## Server Status

The development server is configured and running with network access enabled.

## Access Information

**Local Access (this computer):**
- URL: `http://localhost:5002`
- Status API: `http://localhost:5002/api/status`

**Network Access (from your phone or other devices):**
- URL: `http://192.168.1.130:5002`
- Status API: `http://192.168.1.130:5002/api/status`

## Starting the Server

The server is configured to:
1. Automatically detect available ports (starting from 5002)
2. Bind to all network interfaces (`0.0.0.0`) for network access
3. Dynamically detect and display your local IP address

**To start the server:**

```bash
cd "/Users/deshonjackson/thesidia ice"
source venv/bin/activate
cd webapp
python3 server.py
```

Or use the start script:
```bash
cd "/Users/deshonjackson/thesidia ice"
./start_server.sh
```

## Network Configuration

- **Host:** `0.0.0.0` (allows access from any network interface)
- **Port:** 5002 (or first available port 5002-5011)
- **IP Detection:** Automatically detects local IP address on startup

## Phone Access Requirements

1. **Same Wi-Fi Network:** Your phone must be on the same Wi-Fi network as your computer
2. **Firewall:** Ensure your Mac's firewall allows incoming connections on the server port
3. **IP Address:** Use the IP address shown when the server starts (currently: `192.168.1.130`)

## Firewall Configuration

If you can't access from your phone, you may need to allow the connection:

**macOS Firewall:**
1. System Settings → Network → Firewall
2. Click "Options" or "Firewall Options"
3. Ensure "Block all incoming connections" is OFF, or
4. Add Python to allowed applications

**Or allow the port via Terminal:**
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/bin/python3
```

## Verification

**Check server is running:**
```bash
curl http://localhost:5002/api/status
```

**Check network access:**
```bash
curl http://192.168.1.130:5002/api/status
```

**Check what port is listening:**
```bash
lsof -i -P | grep LISTEN | grep python
```

## Dependencies

All required dependencies are installed:
- Flask
- Flask-CORS
- Ollama (with models available)
- All other required packages

## Troubleshooting

**Server won't start:**
- Check if port is already in use: `lsof -i :5002`
- Try a different port by setting `PORT` environment variable

**Can't access from phone:**
- Verify both devices are on the same Wi-Fi network
- Check firewall settings
- Verify IP address hasn't changed (check server startup output)
- Try accessing from another device on the same network first

**Ollama not working:**
- Ensure Ollama is running: `ollama list`
- Check if models are available: `ollama list`

## Current Server Status

- ✅ Server running on port 5002
- ✅ Network access enabled (0.0.0.0)
- ✅ Local IP: 192.168.1.130
- ✅ Ollama available
- ✅ Dependencies installed
- ✅ API endpoints responding

