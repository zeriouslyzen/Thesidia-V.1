#!/usr/bin/env python3
"""
Vercel-compatible Flask entrypoint for Thesidia

IMPORTANT: Thesidia requires Ollama running locally, which won't work on Vercel's serverless functions.
This wrapper allows Vercel to find the Flask app, but Thesidia functionality will be limited.

For full functionality, deploy to a platform that supports persistent services (Railway, Render, Fly.io, etc.)
"""

import os
import sys
from pathlib import Path

# Set VERCEL environment variable so webapp/server.py knows it's running on Vercel
os.environ['VERCEL'] = '1'

# Add project root and src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'webapp'))

# Import the Flask app from webapp/server.py
app = None

try:
    # Try direct import first (simpler for Vercel)
    from webapp.server import app as flask_app
    app = flask_app
    print("✅ Successfully imported Flask app from webapp.server")
except Exception as import_error:
    # Fallback: try dynamic import
    try:
        import importlib.util
        server_path = project_root / 'webapp' / 'server.py'
        if server_path.exists():
            spec = importlib.util.spec_from_file_location("webapp_server", server_path)
            server_module = importlib.util.module_from_spec(spec)
            sys.modules['webapp_server'] = server_module
            spec.loader.exec_module(server_module)
            app = server_module.app
            print("✅ Successfully loaded Flask app via dynamic import")
        else:
            raise ImportError(f"server.py not found at {server_path}")
    except Exception as dynamic_error:
        # Final fallback: Create minimal Flask app
        import traceback
        error_msg_import = str(import_error) if 'import_error' in locals() else "Unknown import error"
        error_msg_dynamic = str(dynamic_error) if 'dynamic_error' in locals() else "Unknown dynamic error"
        print(f"❌ Failed to import Flask app")
        print(f"   Direct import error: {error_msg_import}")
        print(f"   Dynamic import error: {error_msg_dynamic}")
        traceback.print_exc()
        
        from flask import Flask, jsonify
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def fallback(path):
            return jsonify({
                'error': 'Server initialization failed',
                'message': 'Thesidia requires Ollama running locally',
                'recommendation': 'Deploy to Railway, Render, Fly.io, or similar platform that supports persistent services',
                'import_error': error_msg_import,
                'dynamic_error': error_msg_dynamic
            }), 503
        
        print("⚠️  Created fallback Flask app")

# Ensure app is defined
if app is None:
    raise RuntimeError("Flask app could not be initialized")

# Export app for Vercel
# Vercel automatically wraps Flask apps - just export 'app'
# The app variable must be named 'app' for Vercel to detect it

