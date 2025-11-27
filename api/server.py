#!/usr/bin/env python3
"""
Vercel-compatible Flask entrypoint for Thesidia

IMPORTANT: Thesidia requires Ollama running locally, which won't work on Vercel's serverless functions.
This wrapper allows Vercel to find the Flask app, but Thesidia functionality will be limited.

For full functionality, deploy to a platform that supports persistent services (Railway, Render, Fly.io, etc.)
"""

import sys
from pathlib import Path

# Add project root and src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'webapp'))

# Import the Flask app from webapp/server.py
try:
    # Try relative import first (for Vercel)
    import importlib.util
    server_path = project_root / 'webapp' / 'server.py'
    if server_path.exists():
        spec = importlib.util.spec_from_file_location("server", server_path)
        server_module = importlib.util.module_from_spec(spec)
        sys.modules['server'] = server_module
        spec.loader.exec_module(server_module)
        app = server_module.app
    else:
        # Fallback: try direct import
        from webapp.server import app
except (ImportError, Exception) as e:
    # Fallback: Create minimal Flask app if import fails
    from flask import Flask, jsonify
    from flask_cors import CORS
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/')
    def index():
        return jsonify({
            'error': 'Thesidia requires Ollama running locally',
            'message': 'This deployment platform does not support local Ollama instances',
            'recommendation': 'Deploy to Railway, Render, Fly.io, or similar platform that supports persistent services',
            'import_error': str(e) if e else None
        }), 503
    
    @app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    def api_fallback(path):
        return jsonify({
            'error': 'Ollama not available',
            'message': 'Thesidia requires Ollama running locally. Vercel serverless functions cannot run Ollama.',
            'recommendation': 'Use a platform that supports persistent services like Railway, Render, or Fly.io',
            'note': 'For full functionality, deploy the API to Railway and configure the frontend to use that API endpoint'
        }), 503

# Export app for Vercel
# Vercel expects the Flask app to be available as 'app'
__all__ = ['app']

