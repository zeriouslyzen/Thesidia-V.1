# Remote API Setup Guide

**Quick guide to switch Thesidia frontend to use a remote API (your Mac/M4 server)**

---

## Quick Setup

### Option 1: Environment Variable (Recommended)

**1. Create `.env` file in `webapp/` directory**:
```bash
cd webapp
echo "API_ENDPOINT=https://api.thesidia.com/api/thesidia" > .env
echo "STATUS_ENDPOINT=https://api.thesidia.com/api/status" >> .env
```

**2. Update `app.js` to read from environment** (for Vercel):
- Vercel supports environment variables
- Set in Vercel dashboard: Settings → Environment Variables

---

### Option 2: Direct Edit (Simple)

**Edit `webapp/app.js`**:
```javascript
// Change line 5 from:
this.apiEndpoint = '/api/thesidia';

// To:
this.apiEndpoint = 'https://api.thesidia.com/api/thesidia';
// Or: 'https://abc123.ngrok.io/api/thesidia' (for ngrok)
```

---

### Option 3: Use api-config.js (Flexible)

**1. Uncomment in `index.html`**:
```html
<script src="api-config.js"></script>
```

**2. Edit `api-config.js`**:
```javascript
const USE_REMOTE_API = true;  // Enable remote API
const REMOTE_API_URL = 'https://api.thesidia.com/api/thesidia';  // Your API URL
```

---

## Testing

**1. Start API on your Mac/M4 server**:
```bash
cd webapp
python3 server.py  # Runs on localhost:5000
```

**2. Expose to internet** (choose one):

**ngrok** (easiest):
```bash
ngrok http 5000
# Get URL: https://abc123.ngrok.io
```

**Cloudflare Tunnel** (free, permanent):
```bash
cloudflared tunnel --url http://localhost:5000
```

**3. Update frontend**:
- Use the URL from step 2
- Deploy to Vercel
- Test!

---

## Production Setup (M4 Server)

**1. Set up API on M4 server** (see `docs/HYBRID_DEPLOYMENT_GUIDE.md`)

**2. Configure DNS**:
- Add A record: `api.thesidia.com → Your M4 Server IP`

**3. Update frontend**:
```javascript
this.apiEndpoint = 'https://api.thesidia.com/api/thesidia';
```

**4. Deploy to Vercel**:
- Frontend calls your M4 server API
- Full Thesidia functionality works!

---

## CORS Setup

**If API is on different domain, enable CORS in `webapp/server.py`**:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://thesidia.com", "https://www.thesidia.com"])
```

---

## Quick Commands

**Start API on Mac**:
```bash
cd "/Users/deshonjackson/thesidia ice/webapp"
python3 server.py
```

**Expose with ngrok**:
```bash
ngrok http 5000
```

**Test API**:
```bash
curl http://localhost:5000/api/status
curl https://your-ngrok-url.ngrok.io/api/status
```

---

## Summary

**For Testing**:
- Use ngrok to expose local API
- Update frontend to use ngrok URL
- Deploy to Vercel

**For Production**:
- Set up API on M4 server
- Use `api.thesidia.com` subdomain
- Update frontend to use subdomain
- Deploy to Vercel

**Result**: Frontend on Vercel (fast), API on your server (full functionality)!

