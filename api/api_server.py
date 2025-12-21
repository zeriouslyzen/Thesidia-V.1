#!/usr/bin/env python3
"""
Thesidia API Server - Standalone API for Thesidia
Can be deployed separately from the frontend (Railway, Render, Fly.io, etc.)

Usage:
    python api_server.py
    
Environment Variables:
    PORT: Port to bind to (default: 5000)
    CORS_ORIGINS: Comma-separated list of allowed origins (default: *)
    API_KEY: Optional API key for authentication
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'webapp'))

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json
from datetime import datetime

# New Centralized Initializer and Middleware
from src.core.thesidia_initializer import ThesidiaInitializer
from webapp.middleware.user_auth import require_user

# Initialize Flask app
app = Flask(__name__)

# CORS configuration
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
CORS(app, origins=cors_origins, supports_credentials=True)

# Initialize System
system_init = ThesidiaInitializer(project_root)

def init_thesidia():
    """Initialize Thesidia system"""
    global thesidia, thesidia_ready, knowledge_base, user_memory_manager, interest_tracker, astronomical_engine
    
    success = system_init.init(force_fresh=True)
    
    # Sync global variables
    thesidia = system_init.thesidia_instance
    thesidia_ready = system_init.thesidia_ready
    knowledge_base = system_init.knowledge_base
    user_memory_manager = system_init.user_memory_manager
    interest_tracker = system_init.interest_tracker
    astronomical_engine = system_init.astronomical_engine
    
    return success

# Initialize on startup
init_thesidia()

# API Key authentication (optional)
API_KEY = os.getenv('API_KEY', None)

def check_auth():
    """Check API key if configured"""
    if not API_KEY:
        return True  # No auth required
    
    provided_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    return provided_key == API_KEY

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'thesidia_ready': thesidia_ready,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/thesidia', methods=['POST'])
@require_user
def thesidia_api(user_id=None, session_id=None):
    """Main Thesidia API endpoint"""
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not thesidia_ready or not thesidia:
        # Try to re-init
        if not init_thesidia():
            return jsonify({
                'error': 'Thesidia not ready',
                'message': 'Ollama is not running or Thesidia failed to initialize'
            }), 503
    
    try:
        data = request.get_json() or {}
        # Support both 'query' and 'message' for compatibility
        query = data.get('query') or data.get('message', '')
        # user_id and session_id are provided by @require_user
        format_type = data.get('format', 'natural')
        research_depth = data.get('research_depth', 2)
        
        if not query:
            return jsonify({'error': 'query or message is required'}), 400
        
        # Process with Thesidia
        result = thesidia.process(
            input_data=query,
            context={
                "user_id": user_id,
                "session_id": session_id,
                "format_mode": format_type,
                "research_depth": research_depth
            }
        )
        response = result.get("output", "") if isinstance(result, dict) else str(result)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/thesidia/stream', methods=['POST'])
def thesidia_stream():
    """Streaming Thesidia API endpoint"""
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not thesidia_ready:
        return jsonify({
            'error': 'Thesidia not ready',
            'message': 'Ollama is not running or Thesidia failed to initialize'
        }), 503
    
    try:
        data = request.get_json() or {}
        # Support both 'query' and 'message' for compatibility
        query = data.get('query') or data.get('message', '')
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        format_type = data.get('format', 'natural')
        research_depth = data.get('research_depth', 2)
        
        if not query:
            return jsonify({'error': 'query or message is required'}), 400
        
        def generate():
            try:
                # Use streaming from Thesidia (if available)
                # For now, process and stream chunks manually
                result = thesidia.process(
                    input_data=query,
                    context={
                        "user_id": user_id,
                        "session_id": session_id,
                        "format_mode": format_type,
                        "research_depth": research_depth
                    }
                )
                response = result.get("output", "") if isinstance(result, dict) else str(result)
                # Stream response in chunks
                chunk_size = 50
                for i in range(0, len(response), chunk_size):
                    chunk = response[i:i+chunk_size]
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Get system status"""
    return jsonify({
        'thesidia_ready': thesidia_ready,
        'ollama_status': thesidia_ready,  # Simplified
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Starting Thesidia API Server on port {port}")
    print(f"📡 CORS origins: {cors_origins}")
    if API_KEY:
        print(f"🔑 API Key authentication enabled")
    else:
        print(f"⚠️  API Key authentication disabled (set API_KEY env var to enable)")
    
    app.run(host='0.0.0.0', port=port, debug=False)

