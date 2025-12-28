# Thesidia API - Quick Start

## Architecture

**Frontend (Vercel)** → **API Server (Railway)** → **Ollama (Local)**

This allows:
- ✅ Frontend on fast, free Vercel CDN
- ✅ API on Railway (can run Ollama)
- ✅ Users can self-host their own API
- ✅ Users can learn to go local

---

## Quick Setup

### 1. Deploy API to Railway

1. **Fork/clone this repo**
2. **Connect to Railway**
3. **Railway will auto-detect `api/Procfile`**
4. **Set environment variables:**
   - `CORS_ORIGINS`: `https://your-vercel-app.vercel.app`
   - `API_KEY`: (Optional) Your secret key
5. **Deploy!**

Railway will give you a URL like: `https://your-api.railway.app`

### 2. Deploy Frontend to Vercel

1. **Connect GitHub repo to Vercel**
2. **Vercel auto-deploys**
3. **Update `public/api-config.js`:**
   ```javascript
   window.API_CONFIG = {
       API_ENDPOINT: 'https://your-api.railway.app/api/thesidia',
       STATUS_ENDPOINT: 'https://your-api.railway.app/api/status',
       API_KEY: 'your-api-key'  // Optional
   };
   ```
4. **Redeploy**

### 3. Done!

Frontend on Vercel → API on Railway → Full Thesidia functionality!

---

## For Users: Self-Host Your Own API

### Option 1: Railway (Easiest)

1. Fork this repo
2. Connect to Railway
3. Set `CORS_ORIGINS` to your frontend URL
4. Deploy
5. Update your frontend `api-config.js` with the new URL

### Option 2: Local Development

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Install Python dependencies
pip install -r api/requirements.txt

# Run API server
python api_server.py

# Update frontend api-config.js:
# API_ENDPOINT: 'http://localhost:5000/api/thesidia'
```

### Option 3: Docker

```bash
# Build
docker build -t thesidia-api .

# Run
docker run -p 5000:5000 \
  -e CORS_ORIGINS="*" \
  -e API_KEY="your-key" \
  thesidia-api
```

---

## API Endpoints

- `POST /api/thesidia` - Process query
- `POST /api/thesidia/stream` - Stream response
- `GET /api/status` - Check status
- `GET /health` - Health check

See `docs/DEPLOYMENT_OPTIONS.md` for full details.

---

## Benefits

1. **Scalable**: Frontend and API scale independently
2. **Cost-effective**: Frontend free on Vercel, API only when needed
3. **Flexible**: Users can use hosted API or self-host
4. **Educational**: Users learn deployment and self-hosting
5. **Fast**: Frontend from CDN, API close to Ollama

