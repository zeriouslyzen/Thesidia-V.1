# Quick Start Guide

## First Time Setup

1. **Create virtual environment** (if not already done):
```bash
cd "/Users/deshonjackson/thesidia ice"
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors ollama requests beautifulsoup4 lxml
```

2. **Start the server**:
```bash
# Option 1: Use the start script
./start_server.sh

# Option 2: Manual start
source venv/bin/activate
cd webapp
python3 server.py
```

## Access the Interfaces

Once the server is running, visit:
- **Main Chat**: http://localhost:5000/
- **Knowledge Base**: http://localhost:5000/knowledge_base.html
- **Metrics Dashboard**: http://localhost:5000/metrics_dashboard.html

## Troubleshooting

**If you get "ModuleNotFoundError: No module named 'flask'":**
- Make sure you've activated the virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

**If Ollama is not running:**
- Start Ollama: `ollama serve`
- Make sure the model is available: `ollama list`

## Dependencies

All required packages are in `requirements.txt`:
- flask
- flask-cors
- ollama
- requests
- beautifulsoup4
- lxml

