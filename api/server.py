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
import_error_msg = "Not attempted"
dynamic_error_msg = "Not attempted"

try:
    # Try direct import first (simpler for Vercel)
    from webapp.server import app as flask_app
    app = flask_app
    print("✅ Successfully imported Flask app from webapp.server")
except Exception as import_err:
    # Capture error message immediately
    import_error_msg = str(import_err) if import_err else "Unknown import error"
    print(f"⚠️  Direct import failed: {import_error_msg}")
    
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
    except Exception as dynamic_err:
        # Capture error message immediately
        dynamic_error_msg = str(dynamic_err) if dynamic_err else "Unknown dynamic error"
        print(f"⚠️  Dynamic import failed: {dynamic_error_msg}")
        
        # Final fallback: Create minimal Flask app
        import traceback
        print(f"❌ Failed to import Flask app")
        print(f"   Direct import error: {import_error_msg}")
        print(f"   Dynamic import error: {dynamic_error_msg}")
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
                'import_error': import_error_msg,
                'dynamic_error': dynamic_error_msg
            }), 503
        
        print("⚠️  Created fallback Flask app")

# Ensure app is defined
if app is None:
    # Create absolute minimal app if everything failed
    from flask import Flask, jsonify
    from flask_cors import CORS
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def minimal_fallback(path):
        return jsonify({
            'error': 'Flask app initialization failed',
            'message': 'Unable to initialize Thesidia server',
            'import_error': import_error_msg,
            'dynamic_error': dynamic_error_msg
        }), 503

# Ensure the app has a global error handler that catches everything
# This will catch any exceptions that slip through
if not hasattr(app, '_thesidia_error_handler_added'):
    @app.errorhandler(Exception)
    def catch_all_errors(e):
        """Catch all exceptions and return a safe response"""
        import traceback
        error_msg = str(e) if e else "Unknown error"
        error_type = type(e).__name__ if e else "Unknown"
        print(f"❌ Exception caught by global handler: {error_msg}")
        print(f"   Type: {error_type}")
        traceback.print_exc()
        
        from flask import jsonify
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'type': error_type
        }), 500
    
    app._thesidia_error_handler_added = True

# Export app for Vercel
# Vercel automatically wraps Flask apps - just export 'app'
# The app variable must be named 'app' for Vercel to detect it

