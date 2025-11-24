# Hybrid Deployment Guide: Vercel Frontend + Local/Server API

**Best Solution**: Frontend on Vercel (fast CDN), Backend on your Mac/M4 server (runs Ollama)

---

## Overview

**Architecture**:
```
User → Vercel (Frontend) → Your Mac/M4 Server (API with Ollama) → Response
```

**Benefits**:
- ✅ Frontend on Vercel (fast, global CDN)
- ✅ Backend on your Mac/M4 (runs Ollama, full functionality)
- ✅ Use your domain (thesidia.com) for frontend
- ✅ API can be on subdomain (api.thesidia.com) or same domain
- ✅ Free frontend hosting (Vercel)
- ✅ Full Thesidia functionality (Ollama on your server)

---

## Option 1: API on Your Mac (Local Development/Testing)

### Setup

**1. Start Thesidia API Server**:

```bash
cd "/Users/deshonjackson/thesidia ice/webapp"
python3 server.py
```

**2. Expose to Internet** (choose one):

**Option A: ngrok** (easiest for testing):
```bash
# Install ngrok
brew install ngrok

# Start Thesidia server (in one terminal)
cd "/Users/deshonjackson/thesidia ice/webapp"
python3 server.py  # Runs on localhost:5000

# Expose to internet (in another terminal)
ngrok http 5000
```

**Result**: Get a public URL like `https://abc123.ngrok.io`

**Option B: Cloudflare Tunnel** (free, permanent):
```bash
# Install cloudflared
brew install cloudflared

# Create tunnel
cloudflared tunnel --url http://localhost:5000
```

**Option C: LocalTunnel** (free):
```bash
npm install -g localtunnel
lt --port 5000
```

**3. Update Frontend API Endpoint**:

In `webapp/app.js`, update the API endpoint:
```javascript
// Change from:
const apiEndpoint = '/api/thesidia';

// To:
const apiEndpoint = 'https://your-ngrok-url.ngrok.io/api/thesidia';
// Or: 'https://api.thesidia.com/api/thesidia' (if using subdomain)
```

**4. Deploy Frontend to Vercel**:
- Frontend will call your Mac's API
- Full Thesidia functionality works

---

## Option 2: API on M4 Server (Production)

### Setup

**1. Set Up M4 Server**:

```bash
# SSH into your M4 server
ssh user@your-m4-server-ip

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip nginx certbot

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull clean-mistral:latest

# Clone Thesidia
cd /var/www
git clone https://github.com/zeriouslyzen/Thesidia-V.1.git thesidia
cd thesidia

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r webapp/requirements.txt
pip install gunicorn
```

**2. Configure Nginx** (reverse proxy):

Create `/etc/nginx/sites-available/thesidia-api`:
```nginx
server {
    listen 80;
    server_name api.thesidia.com;  # Or thesidia.com/api

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

**3. Enable Site**:
```bash
ln -s /etc/nginx/sites-available/thesidia-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

**4. Set Up SSL**:
```bash
certbot --nginx -d api.thesidia.com
```

**5. Run Thesidia as Service**:

Create `/etc/systemd/system/thesidia-api.service`:
```ini
[Unit]
Description=Thesidia API Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/thesidia/webapp
Environment="PATH=/var/www/thesidia/venv/bin"
ExecStart=/var/www/thesidia/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    server:app

[Install]
WantedBy=multi-user.target
```

**6. Start Service**:
```bash
systemctl daemon-reload
systemctl enable thesidia-api
systemctl start thesidia-api
systemctl status thesidia-api
```

**7. Update DNS**:

In Namecheap, add A record:
```
Type: A
Host: api
Value: [Your M4 Server IP]
TTL: Automatic
```

**8. Update Frontend**:

In `webapp/app.js`:
```javascript
const apiEndpoint = 'https://api.thesidia.com/api/thesidia';
```

---

## Option 3: API on Same Domain (thesidia.com/api)

### Setup

**1. Point thesidia.com to Your M4 Server**:
- Add A record in Namecheap: `thesidia.com → Your M4 Server IP`

**2. Configure Nginx** (serve both frontend and API):

```nginx
server {
    listen 80;
    server_name thesidia.com www.thesidia.com;

    # Frontend (static files from Vercel or serve locally)
    location / {
        # Option A: Proxy to Vercel
        proxy_pass https://your-vercel-deployment.vercel.app;
        
        # Option B: Serve static files directly
        # root /var/www/thesidia/webapp;
        # try_files $uri $uri/ /index.html;
    }

    # API endpoints
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

**3. Update Frontend**:

In `webapp/app.js`:
```javascript
const apiEndpoint = '/api/thesidia';  // Same domain, relative path
```

---

## Recommended: Option 2 (API Subdomain)

**Best for Production**:
- Frontend: `thesidia.com` (Vercel)
- API: `api.thesidia.com` (Your M4 Server)

**Benefits**:
- ✅ Clean separation
- ✅ Easy to scale
- ✅ Can move API later without affecting frontend
- ✅ CORS handled properly

---

## CORS Configuration

**If API is on different domain, enable CORS**:

In `webapp/server.py`, add:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://thesidia.com", "https://www.thesidia.com"])

# Or allow all (for testing):
# CORS(app)
```

---

## Security Considerations

**1. Rate Limiting** (already in server.py):
- ✅ Already implemented
- Adjust if needed

**2. API Authentication** (optional):
```python
# Add API key authentication
API_KEY = os.environ.get('THESIDIA_API_KEY')

@app.before_request
def check_api_key():
    if request.path.startswith('/api'):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
```

**3. Firewall**:
```bash
# Only allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp  # SSH
ufw enable
```

---

## Testing

**1. Test API Locally**:
```bash
curl http://localhost:5000/api/status
```

**2. Test API from Internet**:
```bash
curl https://api.thesidia.com/api/status
```

**3. Test Frontend**:
- Deploy to Vercel
- Frontend calls API
- Full functionality works

---

## Cost Comparison

**Hybrid Approach**:
- Frontend (Vercel): **$0** (free tier)
- API (Your Mac): **$0** (you already have it)
- API (M4 Server): **$12-24/month** (VPS)

**vs Full Cloud**:
- Railway: $5-20/month
- Render: $7-25/month

**Savings**: Use your existing Mac for free, or M4 server for same cost as cloud

---

## Quick Start: Mac API + Vercel Frontend

**1. Start API on Mac**:
```bash
cd "/Users/deshonjackson/thesidia ice/webapp"
python3 server.py  # Runs on localhost:5000
```

**2. Expose with ngrok**:
```bash
ngrok http 5000
# Get URL: https://abc123.ngrok.io
```

**3. Update Frontend**:
```javascript
// In webapp/app.js
const apiEndpoint = 'https://abc123.ngrok.io/api/thesidia';
```

**4. Deploy Frontend to Vercel**:
- Push to GitHub
- Vercel auto-deploys
- Frontend calls your Mac's API

**5. Test**:
- Visit Vercel URL
- Chat with Thesidia
- Full functionality works!

---

## Next Steps

1. **Choose option** (Mac for testing, M4 server for production)
2. **Set up API** (follow steps above)
3. **Update frontend** (change API endpoint)
4. **Deploy frontend** (Vercel)
5. **Test** (verify everything works)

---

## Summary

**Best Solution**: 
- ✅ Frontend on Vercel (thesidia.com)
- ✅ API on your Mac (testing) or M4 server (production)
- ✅ Full Thesidia functionality
- ✅ Use your domain
- ✅ Free or low cost

**This is the perfect hybrid approach!**

