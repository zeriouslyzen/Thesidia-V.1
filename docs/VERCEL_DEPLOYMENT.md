# Vercel Deployment Guide

**Status**: ⚠️ **LIMITED FUNCTIONALITY** - Thesidia requires Ollama running locally

---

## Critical Limitation

**Thesidia requires Ollama to run locally**, which **will NOT work on Vercel's serverless functions**.

Vercel uses serverless functions that:
- ❌ Cannot run persistent services like Ollama
- ❌ Have limited execution time (max 60 seconds)
- ❌ Cannot maintain state between requests
- ❌ Cannot run background processes

**Result**: Thesidia will not function on Vercel.

---

## Alternative Deployment Platforms

For full Thesidia functionality, deploy to platforms that support persistent services:

### Recommended Platforms:

1. **Railway** (https://railway.app)
   - ✅ Supports persistent services
   - ✅ Can run Ollama
   - ✅ Easy deployment
   - ✅ Free tier available

2. **Render** (https://render.com)
   - ✅ Supports persistent services
   - ✅ Can run Ollama
   - ✅ Free tier available
   - ✅ Good for Flask apps

3. **Fly.io** (https://fly.io)
   - ✅ Supports persistent services
   - ✅ Can run Ollama
   - ✅ Global edge deployment
   - ✅ Free tier available

4. **DigitalOcean App Platform**
   - ✅ Supports persistent services
   - ✅ Can run Ollama
   - ✅ Good Flask support

5. **AWS/GCP/Azure**
   - ✅ Full control
   - ✅ Can run Ollama
   - ⚠️ More complex setup

---

## Current Vercel Configuration

The repository now includes:
- ✅ `vercel.json` - Vercel configuration
- ✅ `api/server.py` - Vercel-compatible Flask entrypoint
- ✅ Routes configured for API and static files

**However**, this will only work for:
- ✅ Static file serving (HTML, CSS, JS)
- ❌ Thesidia API endpoints (requires Ollama)

---

## What Will Work on Vercel

### ✅ Will Work:
- Static frontend files (HTML, CSS, JavaScript)
- Basic Flask app structure
- API endpoint routing

### ❌ Will NOT Work:
- Thesidia processing (requires Ollama)
- Web search functionality
- Deep research functionality
- Any LLM-based features

---

## Recommended Deployment Strategy

### Option 1: Hybrid Deployment (Recommended)

**Frontend on Vercel, Backend on Railway/Render**:

1. **Deploy frontend to Vercel**:
   - Static files (HTML, CSS, JS)
   - Fast CDN delivery
   - Free hosting

2. **Deploy backend to Railway/Render**:
   - Flask API with Ollama
   - Full Thesidia functionality
   - Persistent service

3. **Update frontend API endpoint**:
   ```javascript
   // In webapp/app.js
   const apiEndpoint = 'https://your-backend.railway.app/api/thesidia';
   ```

### Option 2: Full Deployment on Railway/Render

**Deploy everything to one platform**:
- Frontend + Backend together
- Ollama running as service
- Full functionality
- Single deployment

---

## Vercel Configuration Files

### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/server.py"
    },
    {
      "src": "/(.*)",
      "dest": "webapp/$1"
    }
  ]
}
```

### `api/server.py`
- Wrapper that imports Flask app from `webapp/server.py`
- Handles Ollama unavailability gracefully
- Returns error messages explaining limitation

---

## Next Steps

1. **For Vercel**: Use only for frontend, deploy backend elsewhere
2. **For Full Functionality**: Deploy to Railway/Render/Fly.io
3. **For Testing**: Keep using localhost with Ollama

---

## Railway Deployment (Recommended)

### Quick Start:

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Initialize**:
   ```bash
   railway init
   ```

4. **Add Ollama Service**:
   - Railway supports Docker containers
   - Can run Ollama in separate service
   - Connect services together

5. **Deploy**:
   ```bash
   railway up
   ```

---

## Conclusion

**Vercel is NOT suitable for Thesidia** due to Ollama requirement.

**Recommended**: Deploy to Railway, Render, or Fly.io for full functionality.

**Alternative**: Use Vercel for frontend only, deploy backend to Railway/Render.

