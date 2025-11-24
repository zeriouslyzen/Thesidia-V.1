# M4 Mac Setup Guide - Thesidia API

**Perfect for M4 Mac**: Run Thesidia API on your M4 Mac, frontend on Vercel

---

## Why M4 Mac is Perfect

**M4 Mac Advantages**:
- ✅ **Neural Engine**: Optimized for AI/ML workloads (Ollama runs great)
- ✅ **Powerful CPU**: Handles Ollama + Flask easily
- ✅ **Always On**: Can run 24/7 (or when you need it)
- ✅ **Free**: You already have it
- ✅ **Fast**: M4 is excellent for LLM inference

---

## Quick Setup (5 Minutes)

### Step 1: Start Thesidia API on M4 Mac

```bash
cd "/Users/deshonjackson/thesidia ice/webapp"
python3 server.py
```

**Should see**:
```
Starting server on http://127.0.0.1:5000
```

**Test locally**:
```bash
curl http://localhost:5000/api/status
```

---

### Step 2: Expose to Internet

**Option A: ngrok** (Easiest, 30 seconds):

```bash
# Install ngrok (if not installed)
brew install ngrok

# In a new terminal, expose your API
ngrok http 5000
```

**You'll get**:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

---

**Option B: Cloudflare Tunnel** (Free, Permanent):

```bash
# Install cloudflared
brew install cloudflared

# Create tunnel (one-time setup)
cloudflared tunnel login
cloudflared tunnel create thesidia-api

# Run tunnel
cloudflared tunnel --url http://localhost:5000
```

**You'll get a permanent URL** like `https://thesidia-api.trycloudflare.com`

---

**Option C: Use Your Domain** (Best for Production):

If you have `thesidia.com` and can set up port forwarding:

1. **Set up port forwarding** on your router:
   - Port 5000 → Your M4 Mac's local IP
   - Or use a different port (8080, 3000, etc.)

2. **Point DNS** (in Namecheap):
   ```
   Type: A
   Host: api
   Value: [Your Public IP]
   ```

3. **Use subdomain**: `api.thesidia.com`

---

### Step 3: Update Frontend

**Edit `webapp/app.js`**:

```javascript
// Change line 5 from:
this.apiEndpoint = '/api/thesidia';

// To your ngrok/cloudflare URL:
this.apiEndpoint = 'https://abc123.ngrok.io/api/thesidia';
// Or: 'https://api.thesidia.com/api/thesidia' (if using domain)
```

---

### Step 4: Enable CORS (If API is on Different Domain)

**Edit `webapp/server.py`**:

Make sure CORS is enabled:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins for testing
# Or specific: CORS(app, origins=["https://thesidia.com"])
```

---

### Step 5: Deploy Frontend to Vercel

```bash
git add webapp/app.js webapp/server.py
git commit -m "Configure M4 Mac API endpoint"
git push  # Vercel auto-deploys
```

---

## Keep API Running (Background)

### Option 1: Terminal (Simple)

**Keep terminal open**:
- Just leave `python3 server.py` running
- Use `Cmd+T` for new tabs if needed

---

### Option 2: Background Process (Better)

**Run in background**:
```bash
cd "/Users/deshonjackson/thesidia ice/webapp"
nohup python3 server.py > /tmp/thesidia-api.log 2>&1 &
```

**Check if running**:
```bash
ps aux | grep "python3 server.py"
```

**Stop**:
```bash
pkill -f "python3 server.py"
```

---

### Option 3: Launch Agent (Best - Auto Start)

**Create `~/Library/LaunchAgents/com.thesidia.api.plist`**:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thesidia.api</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/deshonjackson/thesidia ice/webapp/server.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/deshonjackson/thesidia ice/webapp</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/thesidia-api.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/thesidia-api.error.log</string>
</dict>
</plist>
```

**Load it**:
```bash
launchctl load ~/Library/LaunchAgents/com.thesidia.api.plist
```

**Start/Stop**:
```bash
launchctl start com.thesidia.api
launchctl stop com.thesidia.api
```

**Auto-starts on boot!**

---

## Keep ngrok Running (Background)

**Option 1: Background**:
```bash
nohup ngrok http 5000 > /tmp/ngrok.log 2>&1 &
```

**Option 2: Launch Agent** (auto-start):

Create `~/Library/LaunchAgents/com.ngrok.thesidia.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ngrok.thesidia</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/ngrok</string>
        <string>http</string>
        <string>5000</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/ngrok.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ngrok.error.log</string>
</dict>
</plist>
```

**Note**: ngrok free tier gives you a new URL each time. For permanent URL, use Cloudflare Tunnel or your domain.

---

## Production Setup (Using Your Domain)

### Step 1: Get Your Public IP

```bash
curl ifconfig.me
# Or visit: https://whatismyipaddress.com
```

### Step 2: Set Up Port Forwarding

**On your router**:
1. Log into router admin (usually `192.168.1.1` or `192.168.0.1`)
2. Find "Port Forwarding" or "Virtual Server"
3. Add rule:
   - External Port: 80, 443, or 5000
   - Internal IP: Your M4 Mac's local IP (check in System Settings → Network)
   - Internal Port: 5000
   - Protocol: TCP

### Step 3: Point DNS

**In Namecheap**:
```
Type: A
Host: api
Value: [Your Public IP from Step 1]
TTL: Automatic
```

### Step 4: Set Up SSL (HTTPS)

**Use Cloudflare** (easiest):
1. Add `api.thesidia.com` to Cloudflare
2. Enable "Proxy" (orange cloud)
3. Cloudflare handles SSL automatically

**Or use Let's Encrypt** (on your Mac):
```bash
# Install certbot
brew install certbot

# Get certificate (if you have port forwarding)
certbot certonly --standalone -d api.thesidia.com
```

---

## M4 Mac Performance Tips

### Optimize Ollama for M4

**1. Use M4-optimized models**:
```bash
# Pull models optimized for Apple Silicon
ollama pull mistral:latest
ollama pull llama2:latest
```

**2. Set environment variables**:
```bash
# In ~/.zshrc or ~/.bash_profile
export OLLAMA_NUM_GPU=1  # Use Neural Engine
export OLLAMA_NUM_THREAD=8  # Adjust for M4
```

**3. Monitor performance**:
```bash
# Check CPU/GPU usage
top -o cpu

# Check Ollama performance
ollama ps
```

---

## Testing

### Test API Locally

```bash
# Test status endpoint
curl http://localhost:5000/api/status

# Test Thesidia endpoint
curl -X POST http://localhost:5000/api/thesidia \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Thesidia!"}'
```

### Test from Internet

```bash
# Replace with your ngrok/domain URL
curl https://abc123.ngrok.io/api/status
```

### Test Frontend

1. Deploy to Vercel
2. Visit your Vercel URL
3. Chat with Thesidia
4. Should work perfectly!

---

## Troubleshooting

### API Not Accessible

**Check firewall**:
```bash
# Allow incoming connections
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/bin/python3
```

**Check if port is in use**:
```bash
lsof -i :5000
```

**Change port** (if 5000 is busy):
```python
# In webapp/server.py, change:
app.run(host='127.0.0.1', port=5001)  # Use different port
```

---

### ngrok URL Changes

**Problem**: ngrok free tier gives new URL each time

**Solutions**:
1. **Use Cloudflare Tunnel** (permanent URL)
2. **Use your domain** (api.thesidia.com)
3. **ngrok paid plan** (static domain)

---

### CORS Errors

**If frontend can't call API**:

1. **Enable CORS in server.py**:
```python
from flask_cors import CORS
CORS(app)  # Allow all origins
```

2. **Check API URL** in frontend matches ngrok/domain URL

---

## Quick Commands Reference

```bash
# Start API
cd "/Users/deshonjackson/thesidia ice/webapp"
python3 server.py

# Expose with ngrok
ngrok http 5000

# Check if running
ps aux | grep "python3 server.py"

# Stop API
pkill -f "python3 server.py"

# View logs
tail -f /tmp/thesidia-api.log
```

---

## Summary

**Perfect Setup for M4 Mac**:

1. ✅ **API on M4 Mac** (runs Ollama, full functionality)
2. ✅ **Expose with ngrok/Cloudflare** (free, easy)
3. ✅ **Frontend on Vercel** (free, fast CDN)
4. ✅ **Use your domain** (thesidia.com for frontend, api.thesidia.com for API)

**Cost**: $0 (using your M4 Mac + free services)

**Performance**: Excellent (M4 Neural Engine optimizes Ollama)

**Result**: Full Thesidia functionality, fast frontend, zero cost!

---

## Next Steps

1. **Start API**: `python3 webapp/server.py`
2. **Expose**: `ngrok http 5000`
3. **Update frontend**: Change API endpoint in `app.js`
4. **Deploy**: Push to GitHub (Vercel auto-deploys)
5. **Test**: Visit Vercel URL, chat with Thesidia!

**You're all set!** 🚀

