# Thesidia Deployment Options

## Architecture Overview

Thesidia can be deployed in multiple ways depending on your needs:

1. **Hybrid (Recommended)**: Frontend on Vercel + API on Railway
2. **Self-Hosted API**: Run your own API server
3. **Full Local**: Everything runs locally

---

## Option 1: Hybrid Deployment (Recommended)

### Frontend on Vercel
- ✅ Fast, global CDN
- ✅ Free tier available
- ✅ Automatic deployments
- ❌ Can't run Ollama (serverless)

### API on Railway/Render/Fly.io
- ✅ Can run Ollama
- ✅ Persistent services
- ✅ Full Thesidia functionality

### Setup

1. **Deploy API to Railway:**
   ```bash
   # Railway will auto-detect and use api/Procfile
   # Set environment variables:
   CORS_ORIGINS=https://your-vercel-app.vercel.app
   PORT=5000  # Railway sets this automatically
   ```

2. **Deploy Frontend to Vercel:**
   - Connect your GitHub repo
   - Vercel will auto-deploy
   - Update `public/api-config.js` with your API URL:
   ```javascript
   window.API_CONFIG = {
       API_ENDPOINT: 'https://your-api.railway.app/api/thesidia',
       STATUS_ENDPOINT: 'https://your-api.railway.app/api/status'
   };
   ```

3. **Users can:**
   - Use the hosted API (your Railway instance)
   - Or deploy their own API instance
   - Or run locally

---

## Option 2: Self-Hosted API

Users can run their own API server:

### Quick Start

```bash
# Clone the repo
git clone https://github.com/yourusername/thesidia.git
cd thesidia

# Install dependencies
pip install -r api/requirements.txt

# Install Ollama (if not already installed)
# See: https://ollama.ai

# Run the API server
python api_server.py
```

### With Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Install Python dependencies
COPY api/requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run API server
CMD ["python", "api_server.py"]
```

### Environment Variables

```bash
PORT=5000                    # API server port
CORS_ORIGINS=*               # Allowed CORS origins (comma-separated)
API_KEY=your-secret-key      # Optional: API key for authentication
```

---

## Option 3: Full Local Development

Run everything locally:

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start API server
python api_server.py

# Terminal 3: Start frontend
cd webapp
python server.py
```

---

## API Configuration

### Frontend Configuration (`public/api-config.js`)

```javascript
window.API_CONFIG = {
    // Use your Railway API
    API_ENDPOINT: 'https://your-api.railway.app/api/thesidia',
    STATUS_ENDPOINT: 'https://your-api.railway.app/api/status',
    
    // Or use local API
    // API_ENDPOINT: 'http://localhost:5000/api/thesidia',
    // STATUS_ENDPOINT: 'http://localhost:5000/api/status',
    
    // Optional: API key
    API_KEY: 'your-api-key-here'
};
```

### API Endpoints

- `POST /api/thesidia` - Process query (returns full response)
- `POST /api/thesidia/stream` - Process query (streaming response)
- `GET /api/status` - Get system status
- `GET /health` - Health check

### API Request Format

```json
{
    "query": "Your question here",
    "user_id": "optional-user-id",
    "session_id": "optional-session-id",
    "format": "natural" | "structured",
    "research_depth": 1 | 2 | 3
}
```

### API Response Format

```json
{
    "response": "Thesidia's response",
    "timestamp": "2025-01-26T10:00:00Z"
}
```

---

## Railway Deployment (API Server)

1. **Create new Railway project**
2. **Connect GitHub repo**
3. **Set root directory to project root**
4. **Railway will detect `api/Procfile`**
5. **Set environment variables:**
   - `CORS_ORIGINS`: Your Vercel frontend URL
   - `API_KEY`: (Optional) For authentication

Railway will automatically:
- Install dependencies from `api/requirements.txt`
- Run `gunicorn` using the Procfile
- Expose the API on a public URL

---

## Vercel Deployment (Frontend Only)

1. **Connect GitHub repo to Vercel**
2. **Vercel will auto-detect and deploy**
3. **Update `public/api-config.js`** with your API URL
4. **Redeploy**

The frontend will:
- Serve static files (HTML, CSS, JS)
- Make API calls to your Railway API
- Work without Ollama (since API is separate)

---

## User Self-Hosting Guide

Users can deploy their own API:

### Option A: Railway (Easiest)
1. Fork the repo
2. Connect to Railway
3. Set environment variables
4. Deploy

### Option B: Render
1. Fork the repo
2. Create new Web Service on Render
3. Set build command: `pip install -r api/requirements.txt`
4. Set start command: `gunicorn api_server:app`
5. Deploy

### Option C: Fly.io
1. Fork the repo
2. Install Fly CLI
3. Run `fly launch`
4. Deploy

### Option D: Local
1. Clone repo
2. Install Ollama
3. Run `python api_server.py`
4. Update frontend `api-config.js` to point to `http://localhost:5000`

---

## Benefits of This Architecture

1. **Scalability**: Frontend and API scale independently
2. **Cost**: Frontend on free Vercel tier, API only when needed
3. **Flexibility**: Users can use hosted API or self-host
4. **Learning**: Users can see how to deploy and self-host
5. **Performance**: Frontend served from CDN, API close to Ollama

---

## Next Steps

1. Deploy API to Railway
2. Deploy frontend to Vercel
3. Update `api-config.js` with API URL
4. Test end-to-end
5. Share with users!

