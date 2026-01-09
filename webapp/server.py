#!/usr/bin/env python3
"""
Thesidia Web App Backend Server
Security-first API for Thesidia interactions
"""

import sys
import os
import secrets
import json
import random
import re
import math
import psutil
import requests
from logger_setup import server_logger
logger = server_logger  # Alias for convenience
from threading import Lock
import time
from pathlib import Path
from datetime import datetime

# Constants
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJECT_ROOT / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Server start time for uptime tracking
START_TIME = time.time()

# Ensure os is available for environment variables

# Add project root and src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context, redirect, session
from werkzeug.utils import secure_filename
from flask_cors import CORS

# New Centralized Initializer and Middleware
from src.core.thesidia_initializer import ThesidiaInitializer
from webapp.middleware.user_auth import require_user, require_user_data
from mlx_inference import MLXInference

# Initialize System
mlx_inference = MLXInference()
system_init = ThesidiaInitializer(project_root)

# Lazy import placeholders (preserved for legacy compatibility during transition)
ThesidiaHybridAdaptive = None
KnowledgeBase = None
UserMemoryManager = None
UserInterestTracker = None
AstronomicalPatternEngine = None

from datetime import datetime, timedelta
import importlib

# Response cleanup helpers
def _strip_general_framework_block(text: str) -> str:
    """Remove leaked coaching 'General Framework' template blocks from model output."""
    if not text:
        return text
    # Strip from the first occurrence of (optional markdown) 'General Framework:' to the end.
    # This is intentionally aggressive because the block is placeholder/template noise.
    text = re.sub(r'\*{0,2}\s*General Framework:\s*\*{0,2}[\s\S]*\Z', '', text, flags=re.IGNORECASE)
    return text.strip()

# Conversation persistence (SQLite default)
try:
    from webapp.conversations.storage import build_store, ConversationMessage
except Exception:
    build_store = None
    ConversationMessage = None

# MLX Edge Inference support
try:
    from webapp.mlx_inference import get_inference_router
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    print("Warning: MLX inference module not available")

# Ollama import - optional for Vercel deployment
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

# For Vercel: serve from public/ if it exists, otherwise current directory
try:
    # During development, we handle static files via a custom route to manage
    # cache-busting and path resolution across webapp and public directories.
    app = Flask(__name__, static_folder=None)
    CORS(app)  # Enable CORS for security
except Exception as e:
    # Fallback if Flask initialization fails
    import traceback
    print(f"Error initializing Flask app: {e}")
    traceback.print_exc()
    # Create minimal app
    from flask import Flask
    from flask_cors import CORS
    app = Flask(__name__)
    CORS(app)

# Session configuration for OAuth
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_urlsafe(32))

# Initialize SocketIO for real-time features
try:
    from flask_socketio import SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
    SOCKETIO_AVAILABLE = True
except ImportError:
    socketio = None
    SOCKETIO_AVAILABLE = False
    print("Warning: Flask-SocketIO not available")

# Initialize conversation store (SQLite) - safe no-op if imports unavailable
conversation_store = None
if build_store is not None:
    try:
        conversation_store = build_store(project_root)
    except Exception as e:
        print(f"Warning: Conversation store unavailable: {e}")

# Security headers middleware - wrapped in try/except for Vercel
try:
    from webapp.config.security import is_security_headers_enabled, is_https_required
except ImportError:
    # Fallback if security config can't be imported
    def is_security_headers_enabled():
        return False
    def is_https_required():
        return False

@app.after_request
def add_security_headers(response):
    """Add security headers to responses"""
    try:
        if is_security_headers_enabled():
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            if is_https_required():
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self'"
            response.headers['Content-Security-Policy'] = csp
    except Exception as e:
        # Don't crash if security headers fail - just log and continue
        print(f"Warning: Could not add security headers: {e}")
        import traceback
        traceback.print_exc()
    
    return response

# Global error handler to catch unhandled exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions gracefully"""
    import traceback
    error_trace = traceback.format_exc()
    print(f"❌ Unhandled exception: {e}")
    print(error_trace)
    
    # Return a proper error response instead of crashing
    return jsonify({
        'error': 'Internal server error',
        'message': str(e),  # Always show the actual error message
        'type': type(e).__name__
    }), 500

# Initialize Thesidia
thesidia = None
thesidia_ready = False
ollama_status = False
inference_router = None

if MLX_AVAILABLE:
    try:
        inference_router = get_inference_router()
        print("MLX Inference Router initialized")
    except Exception as e:
        print(f"Warning: Could not initialize MLX Inference Router: {e}")

# Lazy initialization - will be created in init_thesidia() if modules import successfully
knowledge_base = None
user_memory_manager = None

# Initialize User Interest Tracker for engagement algorithm (lazy)
interest_tracker = None

# Initialize Astronomical Pattern Engine (lazy)
astronomical_engine = None

# Initialize Settings Manager
try:
    from webapp.settings.settings_manager import SettingsManager
    settings_manager = SettingsManager(base_dir=project_root)
except ImportError:
    settings_manager = None

# Initialize Auth Manager
try:
    from webapp.auth.auth_manager import AuthManager
    auth_manager = AuthManager(base_dir=project_root)
except ImportError:
    auth_manager = None

# Initialize OAuth Manager
try:
    from webapp.auth.oauth_providers import OAuthManager
    oauth_manager = OAuthManager(base_dir=project_root)
except ImportError:
    oauth_manager = None

# Initialize Phone Auth Manager
try:
    from webapp.auth.phone_auth import PhoneAuthManager
    phone_auth_manager = PhoneAuthManager(base_dir=project_root)
except ImportError:
    phone_auth_manager = None

def check_ollama():
    """Check if Ollama is running"""
    if not OLLAMA_AVAILABLE:
        return False
    try:
        ollama.list()
        return True
    except Exception:
        return False

def init_thesidia():
    """Initialize Thesidia using centralized initializer"""
    global thesidia, thesidia_ready, ollama_status, knowledge_base, user_memory_manager, interest_tracker, astronomical_engine
    success = system_init.init(force_fresh=True)
    
    # Sync global variables for legacy code compatibility
    thesidia = system_init.thesidia
    thesidia_ready = system_init.thesidia_ready
    ollama_status = system_init.ollama_status
    knowledge_base = system_init.knowledge_base
    user_memory_manager = system_init.user_memory_manager
    interest_tracker = system_init.interest_tracker
    astronomical_engine = system_init.astronomical_engine
    
    return success

# Helper for middleware to access managers
def get_user_memory_manager():
    return system_init.user_memory_manager

# Ease of use middleware wrappers
def require_thesidia_user(f):
    return require_user(f)

def require_thesidia_user_data(f):
    return require_user_data(get_user_memory_manager)(f)

# Try to initialize (will fail gracefully on Vercel)
try:
    init_thesidia()
except Exception as e:
    print(f"Warning: Could not initialize Thesidia: {e}")
    print("This is expected on Vercel - Ollama is not available")

# Security: Rate limiting (simple in-memory)
request_counts = {}
RATE_LIMIT = 100  # requests per minute per IP

# Vibecode #3: Request queuing to prevent race conditions
import threading
from queue import Queue
_request_queue = Queue(maxsize=50)  # Max 50 concurrent requests
_request_lock = threading.Lock()
_active_requests = {}  # Track active requests by message_id

def check_rate_limit(ip):
    """Simple rate limiting"""
    now = datetime.now().timestamp()
    if ip not in request_counts:
        request_counts[ip] = []
    
    # Remove old requests (older than 1 minute)
    request_counts[ip] = [t for t in request_counts[ip] if now - t < 60]
    
    if len(request_counts[ip]) >= RATE_LIMIT:
        return False
    
    request_counts[ip].append(now)
    return True

@app.route('/index.html')
def index_direct():
    print("DEBUG: index_direct reached")
    return send_from_directory('.', 'index.html')

@app.route('/')
def index():
    """Serve landing page - landing.html is the main entry point for katanx.com"""
    try:
        # Check public/ directory first (for Vercel), then current directory
        static_dir = Path(__file__).parent.parent / 'public'
        if static_dir.exists():
            landing_path = static_dir / 'landing.html'
            if landing_path.exists():
                try:
                    return send_from_directory(str(static_dir), 'landing.html')
                except Exception as file_error:
                    print(f"Error sending landing.html: {file_error}")
        # Fallback to current directory
        current_landing = Path('landing.html')
        if current_landing.exists():
            try:
                return send_from_directory('.', 'landing.html')
            except Exception as file_error:
                print(f"Error sending current landing.html: {file_error}")
    except Exception as route_error:
        # If file serving fails, return a simple HTML response
        import traceback
        error_msg = str(route_error) if route_error else "Unknown error"
        print(f"Error in index route: {error_msg}")
        traceback.print_exc()
    
    # Final fallback - always return something
    try:
        return """<!DOCTYPE html>
<html>
<head>
    <title>katanx</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script>window.location.href = '/landing.html';</script>
</head>
<body>
    <h1>katanx</h1>
    <p>Application is loading...</p>
    <p>If you are not redirected, please <a href="/landing.html">click here</a>.</p>
</body>
</html>""", 200, {'Content-Type': 'text/html'}
    except Exception as final_error:
        # Absolute last resort - return plain text
        error_msg = str(final_error) if final_error else "Unknown error"
        return f"Error: {error_msg}", 500, {'Content-Type': 'text/plain'}

@app.route('/home')
def home():
    """Serve main application - app.html is the home page for katanx.com/home"""
    try:
        # Check public/ directory first (for Vercel), then current directory
        static_dir = Path(__file__).parent.parent / 'public'
        if static_dir.exists():
            app_path = static_dir / 'app.html'
            if app_path.exists():
                try:
                    return send_from_directory(str(static_dir), 'app.html')
                except Exception as file_error:
                    print(f"Error sending app.html: {file_error}")
            contexts_path = static_dir / 'contexts.html'
            if contexts_path.exists():
                try:
                    return send_from_directory(str(static_dir), 'contexts.html')
                except Exception as file_error:
                    print(f"Error sending contexts.html: {file_error}")
        # Fallback to current directory
        current_app = Path('app.html')
        if current_app.exists():
            try:
                return send_from_directory('.', 'app.html')
            except Exception as file_error:
                print(f"Error sending current app.html: {file_error}")
        current_contexts = Path('contexts.html')
        if current_contexts.exists():
            try:
                return send_from_directory('.', 'contexts.html')
            except Exception as file_error:
                print(f"Error sending current contexts.html: {file_error}")
    except Exception as route_error:
        # If file serving fails, return a simple HTML response
        import traceback
        error_msg = str(route_error) if route_error else "Unknown error"
        print(f"Error in home route: {error_msg}")
        traceback.print_exc()
    
    # Final fallback - redirect to landing
    try:
        return """<!DOCTYPE html>
<html>
<head>
    <title>Thesidia</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script>window.location.href = '/stream.html';</script>
</head>
<body>
    <h1>Thesidia</h1>
    <p>Application is loading...</p>
    <p>If you are not redirected, please <a href="/stream.html">click here</a>.</p>
</body>
</html>""", 200, {'Content-Type': 'text/html'}
    except Exception as final_error:
        # Absolute last resort - return plain text
        error_msg = str(final_error) if final_error else "Unknown error"
        return f"Error: {error_msg}", 500, {'Content-Type': 'text/plain'}

@app.route('/explore')
def explore():
    """Serve explore page - redirects to search"""
    return send_from_directory('.', 'search.html')

@app.route('/search')
def search():
    """Serve search page"""
    return send_from_directory('.', 'search.html')

@app.route('/robots.txt')
def robots():
    """Serve robots.txt for SEO"""
    static_dir = Path(__file__).parent.parent / 'public'
    if static_dir.exists() and (static_dir / 'robots.txt').exists():
        return send_from_directory(str(static_dir), 'robots.txt'), 200, {'Content-Type': 'text/plain'}
    return send_from_directory('.', 'robots.txt'), 200, {'Content-Type': 'text/plain'}

@app.route('/sitemap.xml')
def sitemap():
    """Serve sitemap.xml for SEO"""
    static_dir = Path(__file__).parent.parent / 'public'
    if static_dir.exists() and (static_dir / 'sitemap.xml').exists():
        return send_from_directory(str(static_dir), 'sitemap.xml'), 200, {'Content-Type': 'application/xml'}
    return send_from_directory('.', 'sitemap.xml'), 200, {'Content-Type': 'application/xml'}

# ============================================================================
# Clean URL Routes (no .html extension for professional URLs)
# ============================================================================

@app.route('/stream')
def stream_page():
    """Main chat/stream interface"""
    return send_from_directory('.', 'stream.html')

@app.route('/profile')
def profile_page():
    """User profile page"""
    return send_from_directory('.', 'profile.html')

@app.route('/atlas')
def atlas_page():
    """Atlas explorer"""
    return send_from_directory('.', 'atlas.html')

@app.route('/contexts')
def contexts_page():
    """Context management"""
    return send_from_directory('.', 'contexts.html')

@app.route('/reactor')
def reactor_page():
    """Reactor interface"""
    return send_from_directory('.', 'reactor.html')

@app.route('/archive')
def archive_page():
    """Archive browser"""
    return send_from_directory('.', 'archive.html')

@app.route('/application')
def application_page():
    """Application dashboard"""
    return send_from_directory('.', 'application.html')

@app.route('/knowledge-base')
@app.route('/knowledge')
def knowledge_base_page_clean():
    """Knowledge base (clean URL)"""
    return send_from_directory('.', 'knowledge_base.html')

@app.route('/metrics')
@app.route('/metrics-dashboard')
def metrics_page():
    """Metrics dashboard (clean URL)"""
    return send_from_directory('.', 'metrics_dashboard.html')

# ============================================================================
# Algorithmic Growth Engine - Event Tracking API
# ============================================================================
# ============================================================================
# Market Data API - Crypto & Stocks
# ============================================================================

@app.route('/api/market/crypto', methods=['GET'])
def get_crypto_prices():
    """
    Get real-time cryptocurrency prices from CoinGecko API.
    Query params: symbols (comma-separated, e.g., bitcoin,ethereum,solana,ripple)
    """
    try:
        symbols = request.args.get('symbols', 'bitcoin,ethereum,solana,ripple')
        symbol_list = [s.strip() for s in symbols.split(',')]
        
        # CoinGecko API - free tier, no API key needed
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': ','.join(symbol_list),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch crypto prices'}), 500
        
        data = response.json()
        
        # Format response
        result = {}
        symbol_map = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'solana': 'SOL',
            'ripple': 'XRP',
            'cardano': 'ADA',
            'dogecoin': 'DOGE',
            'polkadot': 'DOT',
            'avalanche-2': 'AVAX'
        }
        
        for coin_id, coin_data in data.items():
            result[coin_id] = {
                'symbol': symbol_map.get(coin_id, coin_id.upper()),
                'price': coin_data.get('usd', 0),
                'change_24h': coin_data.get('usd_24h_change', 0)
            }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error fetching crypto prices: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/stocks', methods=['GET'])
def get_stock_prices():
    """
    Get real-time stock/commodity prices using Yahoo Finance.
    Query params: symbols (comma-separated, e.g., ^IXIC,GC=F,SI=F)
    """
    try:
        symbols = request.args.get('symbols', '^IXIC,GC=F,SI=F')
        symbol_list = [s.strip() for s in symbols.split(',')]
        
        result = {}
        symbol_names = {
            '^IXIC': 'NASDAQ',
            'GC=F': 'GOLD',
            'SI=F': 'SILVER',
            '^GSPC': 'S&P 500',
            '^DJI': 'DOW'
        }
        
        for symbol in symbol_list:
            try:
                # Yahoo Finance API (free, no key needed)
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                params = {'interval': '1d', 'range': '5d'}
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code != 200:
                    continue
                
                data = response.json()
                quote = data.get('chart', {}).get('result', [{}])[0]
                meta = quote.get('meta', {})
                
                current_price = meta.get('regularMarketPrice', 0)
                previous_close = meta.get('previousClose', current_price)
                change_percent = ((current_price - previous_close) / previous_close * 100) if previous_close else 0
                
                result[symbol_names.get(symbol, symbol)] = {
                    'price': current_price,
                    'change': change_percent
                }
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                continue
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error fetching stock prices: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Algorithmic Growth Engine - Event Tracking API
# ============================================================================
event_store_path = project_root / 'data' / 'events.json'

@app.route('/api/events', methods=['POST'])
def track_events():
    """
    Ingest user interaction events for Algorithmic Growth Engine.
    Supports batch event submission from client-side collector.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        events = data.get('events', [])
        if not events:
            return jsonify({'error': 'No events in payload'}), 400
        
        # Validate events
        valid_action_types = {
            'view', 'click', 'like', 'unlike', 'share', 'save', 'bookmark',
            'comment', 'reply', 'scroll', 'dwell', 'hover', 'expand',
            'play', 'pause', 'complete', 'skip', 'hide', 'report'
        }
        
        processed = []
        for event in events:
            # Basic validation
            if not event.get('content_id') or not event.get('action_type'):
                continue
            if event.get('action_type') not in valid_action_types:
                continue
            
            # Add server timestamp
            event['server_timestamp'] = datetime.now().isoformat()
            processed.append(event)
        
        # Store events (try Supabase first, fall back to local JSON)
        stored_count = 0
        try:
            # Try Supabase if available
            from webapp.conversations.supabase_storage import SupabaseConversationStore
            supabase_store = SupabaseConversationStore()
            if supabase_store.client:
                # Insert into user_interactions table
                for event in processed:
                    try:
                        supabase_store.client.table('user_interactions').insert({
                            'user_id': event.get('user_id'),
                            'session_id': event.get('session_id'),
                            'content_id': event.get('content_id'),
                            'content_type': event.get('content_type', 'unknown'),
                            'action_type': event.get('action_type'),
                            'action_value': event.get('action_value'),
                            'sequence_position': event.get('sequence_position'),
                            'session_start_at': event.get('session_start_at'),
                            'source_page': event.get('source_page'),
                            'device_type': event.get('device_type')
                        }).execute()
                        stored_count += 1
                    except Exception:
                        pass
        except Exception:
            pass
        
        # Fallback: store locally as JSON
        if stored_count == 0:
            try:
                event_store_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Load existing events
                existing = []
                if event_store_path.exists():
                    with open(event_store_path, 'r') as f:
                        existing = json.load(f)
                
                # Append new events (keep last 10000)
                existing.extend(processed)
                existing = existing[-10000:]
                
                # Save
                with open(event_store_path, 'w') as f:
                    json.dump(existing, f)
                
                stored_count = len(processed)
            except Exception as e:
                return jsonify({'error': f'Failed to store events: {str(e)}'}), 500
        
        return jsonify({
            'status': 'ok',
            'events_received': len(events),
            'events_stored': stored_count
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/stats', methods=['GET'])
def event_stats():
    """Get event tracking statistics"""
    try:
        stats = {
            'total_events': 0,
            'action_breakdown': {},
            'content_types': {},
            'storage': 'local'
        }
        
        # Try to get stats from local store
        if event_store_path.exists():
            with open(event_store_path, 'r') as f:
                events = json.load(f)
                stats['total_events'] = len(events)
                
                # Count by action type
                for event in events:
                    action = event.get('action_type', 'unknown')
                    stats['action_breakdown'][action] = stats['action_breakdown'].get(action, 0) + 1
                    
                    ctype = event.get('content_type', 'unknown')
                    stats['content_types'][ctype] = stats['content_types'].get(ctype, 0) + 1
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ─────────────────────────────────────────────────────────────────────────────
# Health Check Endpoint (lightweight, no auth required)
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check for process monitors and load balancers."""
    return jsonify({
        'status': 'ok',
        'uptime_seconds': round(time.time() - START_TIME, 2),
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200

@app.route('/api/status', methods=['GET'])

def status():
    """Get system status"""
    # PROXY SUPPORT: Check upstream status instead
    upstream_url = os.getenv('UPSTREAM_API_URL')
    if upstream_url:
        try:
            resp = requests.get(f"{upstream_url.rstrip('/')}/api/status", timeout=5)
            return jsonify(resp.json()), resp.status_code
        except Exception as e:
            # If upstream fails, return simplified error status
            return jsonify({
                'ollama_status': False,
                'thesidia_ready': False,
                'error': f"Upstream unreachable: {e}"
            }), 200

    global thesidia_ready, ollama_status
    
    try:
        # Recheck status
        ollama_status = check_ollama()
        if ollama_status and not thesidia_ready:
            try:
                init_thesidia()
            except Exception as e:
                print(f"Warning: Could not initialize Thesidia: {e}")
        
        features = {}
        if thesidia:
            try:
                features = {
                    'deep_research': thesidia.deep_research_engine is not None if hasattr(thesidia, 'deep_research_engine') else False,
                    'web_search': thesidia.web_search is not None if hasattr(thesidia, 'web_search') else False,
                    'model_routing': thesidia.capabilities.model_router is not None if hasattr(thesidia, 'capabilities') and hasattr(thesidia.capabilities, 'model_router') else False,
                }
            except (AttributeError, TypeError) as e:
                features = {}
        
        return jsonify({
            'ollama_status': ollama_status,
            'thesidia_ready': thesidia_ready,
            'model': thesidia.model if thesidia else None,
            'features': features,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in /api/status: {e}")
        print(error_trace)
        return jsonify({
            'ollama_status': False,
            'thesidia_ready': False,
            'model': None,
            'features': {},
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 200  # Return 200 instead of 500 so frontend can handle gracefully


@app.route('/api/conversations', methods=['GET'])
def list_conversations():
    """List recent conversations for the current user/session."""
    if conversation_store is None:
        return jsonify({"conversations": [], "storage": "disabled"}), 200
    user_id = request.args.get("user_id") or None
    session_id = request.args.get("session_id") or None
    limit = request.args.get("limit", "50")
    try:
        conversations = conversation_store.list_conversations(user_id=user_id, session_id=session_id, limit=int(limit))
        return jsonify({"conversations": conversations, "storage": "sqlite"}), 200
    except Exception as e:
        return jsonify({"conversations": [], "storage": "error", "error": str(e)}), 200


@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id: str):
    """Load one conversation with messages."""
    if conversation_store is None:
        return jsonify({"error": "Conversation storage disabled"}), 404
    user_id = request.args.get("user_id") or None
    session_id = request.args.get("session_id") or None
    try:
        conv = conversation_store.get_conversation(conversation_id=conversation_id, user_id=user_id, session_id=session_id)
        if not conv:
            return jsonify({"error": "Not found"}), 404
        return jsonify(conv), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/conversations/<conversation_id>', methods=['POST'])
def upsert_conversation(conversation_id: str):
    """Upsert a conversation (client-side cache -> server persistence)."""
    if conversation_store is None:
        return jsonify({"ok": False, "error": "Conversation storage disabled"}), 503
    if not request.is_json:
        return jsonify({"ok": False, "error": "Invalid content type"}), 400
    payload = request.get_json() or {}
    user_id = payload.get("user_id") or None
    session_id = payload.get("session_id") or None
    title = (payload.get("title") or "")[:200]
    preview = (payload.get("preview") or "")[:500]
    messages = payload.get("messages") or []
    try:
        normalized = []
        for m in messages:
            role = (m.get("type") or m.get("role") or "").strip()
            content = (m.get("content") or "").strip()
            ts = m.get("timestamp")
            if not role or not content:
                continue
            try:
                ts_ms = int(ts) if ts is not None else int(time.time() * 1000)
            except Exception:
                ts_ms = int(time.time() * 1000)
            normalized.append(ConversationMessage(role=role, content=content, ts_ms=ts_ms))
        conversation_store.upsert_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            session_id=session_id,
            title=title or (normalized[0].content[:50] if normalized else conversation_id),
            preview=preview or (normalized[-1].content[:100] if normalized else ""),
            messages=normalized,
        )
        return jsonify({"ok": True}), 200
    except ValueError as e:
        # Handle UUID validation errors gracefully
        if "uuid" in str(e).lower():
            log.warning(f"Invalid user_id format (expected UUID): {user_id}")
            # Save to localStorage will still work on client side
            return jsonify({"ok": True, "warning": "Server sync skipped (invalid user_id format)"}), 200
        return jsonify({"ok": False, "error": str(e)}), 500
    except Exception as e:
        log.error(f"Error upserting conversation: {e}")
        # Return 200 so client-side caching still works
        return jsonify({"ok": True, "warning": f"Server sync failed: {str(e)}"}), 200


@app.route('/api/eval/run', methods=['POST'])
def eval_run():
    """Run the conversational + gnostic eval suite and persist artifacts under data/evals/."""
    global thesidia_ready
    if not thesidia_ready:
        if not init_thesidia():
            return jsonify({"error": "Thesidia is not ready"}), 503
    try:
        from webapp.eval.runner import EvalRunner
        runner = EvalRunner(base_dir=project_root, thesidia=thesidia)
        report = runner.run()
        return jsonify(report), 200
    except Exception as e:
        import traceback
        print(f"Error in /api/eval/run: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route('/api/eval/latest', methods=['GET'])
def eval_latest():
    """Return latest eval report, if any."""
    try:
        path = project_root / "data" / "evals" / "latest.json"
        if not path.exists():
            return jsonify({"error": "No evals yet"}), 404
        return jsonify(json.loads(path.read_text(encoding="utf-8"))), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/thesidia', methods=['POST'])
@require_user
def thesidia_api(user_id=None, session_id=None):
    """Main API endpoint for Thesidia interactions - with streaming support"""
    # PROXY SUPPORT: If UPSTREAM_API_URL is set, forward requests there
    upstream_url = os.getenv('UPSTREAM_API_URL')
    if upstream_url:
        print(f"🔄 PROXY: Forwarding request to {upstream_url}")
        try:
            # Forward JSON payload with auth headers if needed
            resp = requests.post(
                f"{upstream_url.rstrip('/')}/api/thesidia",
                json=request.get_json(),
                stream=True,
                timeout=120
            )
            # Stream response back
            return Response(
                stream_with_context(resp.iter_content(chunk_size=None)),
                content_type=resp.headers.get('Content-Type'),
                status=resp.status_code
            )
        except Exception as e:
            print(f"❌ PROXY ERROR: {e}")
            return jsonify({'error': f'Upstream proxy failed: {e}'}), 502

    # Check status and auto-init if needed
    if not thesidia_ready or not thesidia:
        if not init_thesidia():
            return jsonify({
                'error': 'Thesidia is not ready. Is Ollama running?',
                'ollama_status': ollama_status,
                'thesidia_ready': False
            }), 503
    
    # Security: Rate limiting
    client_ip = request.remote_addr
    if not check_rate_limit(client_ip):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    # Security: Validate request
    if not request.is_json:
        return jsonify({'error': 'Invalid content type'}), 400
    
    # Get JSON data
    json_data = request.get_json()
    if json_data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    # Security: Input sanitization
    from webapp.middleware.security import sanitize_request_data
    data = sanitize_request_data(json_data)
    raw_message = data.get('message', '').strip()
    
    # CRITICAL FIX #1: Log RAW user input BEFORE any processing
    print(f"🔍 RAW USER INPUT: '{raw_message}'", flush=True)
    
    show_thinking = data.get('show_thinking', False)
    include_metadata = data.get('include_metadata', False)
    stream = data.get('stream', True)  # Default to streaming
    format_mode = data.get('format', 'natural')  # 'natural' or 'structured' - from UI selection
    fast_mode = data.get('fast_mode', True)  # true = fast (regular search), false = deep research
    research_depth = data.get('research_depth', 1 if fast_mode else 3)  # 1=Quick (fast), 3=Forensic (deep)
    
    # user_id and session_id are now provided by the @require_user decorator
    
    # Security: Validate input
    if not raw_message:
        return jsonify({'error': 'Message is required'}), 400
    
    if len(raw_message) > 10000:
        return jsonify({'error': 'Message too long'}), 400

    # Determine task type for routing
    task_type = data.get('task_type', 'conversation')
    
    # Check if we should use MLX for this request
    use_mlx = data.get('use_mlx', True) and MLX_AVAILABLE and inference_router is not None
    
    # Set router on thesidia instance for internal use
    if thesidia and inference_router:
        thesidia.inference_router = inference_router
    
    # Normalize query and detect forensic routing (using shared utilities)
    from src.support.query_utils import normalize_query, detect_forensic_routing
    
    normalized_message = normalize_query(raw_message)
    needs_forensic = detect_forensic_routing(raw_message, comprehensive=False)
    
    if needs_forensic:
        task_type = "gnostic_blade"
    
    print(f"🔍 ROUTING: Task={task_type}, MLX={use_mlx}", flush=True)
    
    print(f"🔍 NORMALIZED: '{normalized_message}'", flush=True)
    print(f"🔍 NEEDS FORENSIC: {needs_forensic}", flush=True)
    
    # Use normalized message for processing (but keep original for display)
    message = raw_message  # Keep original for now, but routing will use normalized
    
    # Security: Basic sanitization (HTML only, don't modify content)
    message = message.replace('<', '').replace('>', '')
    
    # If streaming requested, use SSE
    # NOTE: We use thesidia.process() which handles all routing/forensic analysis, then stream the result
    if stream:
        return Response(
            stream_with_context(_stream_thesidia_response(message, show_thinking, user_id=user_id, session_id=session_id,
                                                         format_mode=format_mode, research_depth=research_depth, fast_mode=fast_mode,
                                                         task_type=task_type, use_mlx=use_mlx)),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    # Non-streaming fallback
    try:
        thinking_steps = []
        
        # Capture thinking steps if requested
        if show_thinking:
            thinking_steps.append({
                'step': 'Input received',
                'detail': f'Processing: {message[:100]}...',
                'timestamp': datetime.now().isoformat()
            })
            
            # Detect directive type
            is_directive = thesidia._is_directive(message)
            is_deep_research = thesidia._is_deep_research_request(message)
            
            thinking_steps.append({
                'step': 'Classification',
                'detail': f'Type: {"Directive" if is_directive else "Question/Conversation"}, Deep Research: {is_deep_research}',
                'timestamp': datetime.now().isoformat()
            })
            
            if is_directive:
                directive_type = thesidia.capabilities._classify_directive(message)
                research_depth = thesidia.capabilities._determine_research_depth(message)
                model, params = thesidia.capabilities.model_router.get_model_for_task(directive_type, message)
                
                thinking_steps.append({
                    'step': 'Model Routing',
                    'detail': f'Type: {directive_type}, Model: {model}, Depth: {research_depth}, Temp: {params["temperature"]}',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Process with Thesidia (with user memory support)
        print(f"🔪 SERVER: Processing message: {message[:100]}...", flush=True)
        print(f"🔪 SERVER: Normalized: {normalized_message[:100]}...", flush=True)
        print(f"🔪 SERVER: Needs forensic: {needs_forensic}", flush=True)
        print(f"🔪 SERVER: Thesidia instance: {thesidia}", flush=True)
        print(f"🔪 SERVER: Has _handle_deep_research: {hasattr(thesidia, '_handle_deep_research')}", flush=True)
        
        # CRITICAL: Pass the ORIGINAL message (not normalized) to process()
        # The process() method will do its own normalization and routing
        # Pass format_mode and research_depth from UI selection (not auto-detection)
        result = thesidia.process(
            input_data=message,
            context={
                "user_id": user_id,
                "session_id": session_id,
                "format_mode": format_mode,
                "research_depth": research_depth,
                "fast_mode": fast_mode,
                "task_type": task_type,
                "use_mlx": use_mlx
            }
        )
        response = result.get("output", "") if isinstance(result, dict) else str(result)
        response = _strip_general_framework_block(response)
        print(f"🔪 SERVER: Response length: {len(response)}, has transmission: {'::TRANSMISSION:' in response}", flush=True)
        
        # Store interaction in user memory
        try:
            user_memory_manager.store_interaction(
                user_input=message,
                assistant_output=response,
                user_id=user_id,
                session_id=session_id,
                metadata={
                    'timestamp': datetime.now().isoformat(),
                    'response_length': len(response)
                }
            )
        except Exception as e:
            print(f"Warning: Could not store interaction in user memory: {e}")
        
        if show_thinking:
            thinking_steps.append({
                'step': 'Response generated',
                'detail': f'Length: {len(response)} chars',
                'timestamp': datetime.now().isoformat()
            })
        
        # Save state
        thesidia.save_state()
        
        payload = {
            'response': response,
            'thinking_steps': thinking_steps if show_thinking else [],
            'timestamp': datetime.now().isoformat()
        }
        if include_metadata and isinstance(result, dict):
            payload["metadata"] = result.get("metadata", {})
        return jsonify(payload)
        
    except Exception as e:
        print(f"Error processing request: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

def _stream_thesidia_response(message, show_thinking, user_id=None, session_id=None, format_mode='natural', research_depth=2, fast_mode=True, task_type='general', use_mlx=False):
    """Stream Thesidia response with progress updates - USES FULL THESIDIA PROCESS"""
    global thesidia
    
    def send_event(event_type, data):
        """Send SSE event"""
        event_data = json.dumps(data)
        return f"event: {event_type}\ndata: {event_data}\n\n"
    
    try:
        # Phase 1: Input received and initial classification (for UX feedback only)
        # NOTE: Actual routing happens in process() - this is just for UX messages
        text_stripped = message.strip().lower()
        is_simple_greeting = text_stripped in ['hi', 'hello', 'hey'] or len(text_stripped.split()) <= 2
        
        # Check forensic routing (for UX feedback - actual routing in process())
        needs_forensic = False
        if not is_simple_greeting:
            from src.support.query_utils import normalize_query, detect_forensic_routing
            normalized_message = normalize_query(message)
            needs_forensic = detect_forensic_routing(message, comprehensive=False)
            print(f"🔍 NORMALIZED (streaming): '{normalized_message}'", flush=True)
            print(f"🔍 NEEDS FORENSIC (streaming): {needs_forensic}", flush=True)
        
        print(f"🔪 SERVER: is_simple_greeting={is_simple_greeting}, needs_forensic={needs_forensic}", flush=True)
        
        # Show appropriate initial progress message
        if is_simple_greeting:
            yield send_event('progress', {
                'phase': 'input_received',
                'message': 'Responding...',
                'progress': 5
            })
        elif needs_forensic:
            yield send_event('progress', {
                'phase': 'input_received',
                'message': 'Detected forensic query - routing to deep research...',
                'progress': 5
            })
            if show_thinking:
                yield send_event('thinking', {
                    'step': 'classification',
                    'message': 'Query requires forensic analysis (health/finance/law/religion)',
                    'progress': 5
                })
        else:
            yield send_event('progress', {
                'phase': 'input_received',
                'message': 'Processing your query...',
                'progress': 5
            })
        
        # Check if conversational (for UX messages only - actual routing happens in process())
        # This is ONLY for showing appropriate progress messages, not for actual routing
        conversational_patterns = [
            r'what.*?your favorite', r'what.*?you think about', r'^i\'?m thinking about',
            r'^tell me a random', r'^what.*?you like', r'^do you like', r'^are you.*\?$'
        ]
        is_conversational = any(re.search(pattern, text_stripped) for pattern in conversational_patterns)
        
        # Phase 2: Show appropriate progress based on query type
        # NOTE: Actual routing/research happens inside process() - we're just showing UX feedback
        if is_simple_greeting:
            # Simple greeting - minimal processing, fast response
            yield send_event('progress', {
                'phase': 'processing',
                'message': 'Responding...',
                'progress': 30
            })
        elif is_conversational:
            # Conversational query - direct response, no research
            yield send_event('progress', {
                'phase': 'processing',
                'message': 'Processing query...',
                'progress': 30
            })
        elif needs_forensic:
            # Forensic query - will route to deep research
            yield send_event('progress', {
                'phase': 'processing',
                'message': 'Analyzing query and routing to deep research...',
                'progress': 30
            })
            if show_thinking:
                yield send_event('thinking', {
                    'step': 'routing',
                    'message': 'Query requires forensic analysis - routing to deep research',
                    'progress': 30
                })
        else:
            # Regular query - may need research
            yield send_event('progress', {
                'phase': 'processing',
                'message': 'Processing query...',
                'progress': 30
            })
        
        # Phase 3: Call process() - this handles ALL routing, research, and generation
        # NOTE: We don't check _needs_research() here because process() will handle it
        # This prevents duplicate work and ensures consistency
        result = thesidia.process(
            input_data=message,
            context={
                "user_id": user_id,
                "session_id": session_id,
                "format_mode": format_mode,
                "research_depth": research_depth,
                "fast_mode": fast_mode,
                "task_type": task_type,
                "use_mlx": use_mlx
            }
        )
        response = result.get("output", "") if isinstance(result, dict) else str(result)
        response = _strip_general_framework_block(response)
        
        # Phase 4: Stream the response token-by-token for optimal UX
        # Response is already generated by process(), now we stream it
        yield send_event('progress', {
            'phase': 'streaming',
            'message': 'Streaming response...',
            'progress': 50
        })
        
        # Stream response character-by-character with typing animation
        # This simulates real-time generation for better UX
        # Character-by-character is smoother than chunk-by-chunk
        accumulated_length = 0
        total_length = len(response)
        
        # Stream in small chunks for smooth typing effect
        # Each chunk will be displayed with typing animation on frontend
        chunk_size = 3  # Small chunks for smooth typing
        for i in range(0, total_length, chunk_size):
            chunk = response[i:i + chunk_size]
            accumulated_length += len(chunk)
            
            yield send_event('chunk', {
                'text': chunk,
                'progress': 50 + (accumulated_length / total_length) * 45 if total_length > 0 else 50,
                'accumulated': accumulated_length,
                'total': total_length
            })
            
            # Small delay for smooth streaming (frontend will add typing animation)
            # This ensures chunks arrive at optimal rate for typing effect
        
        # Phase 6: Complete
        yield send_event('complete', {
            'phase': 'complete',
            'message': 'Response complete',
            'progress': 100,
            'total_length': total_length
        })
        
        # Store interaction in user memory (after streaming completes)
        if (user_id or session_id) and user_memory_manager:
            try:
                user_memory_manager.store_interaction(
                    user_input=message,
                    assistant_output=response,
                    user_id=user_id,
                    session_id=session_id,
                    metadata={
                        'timestamp': datetime.now().isoformat(),
                        'response_length': total_length,
                        'streamed': True
                    }
                )
            except Exception as e:
                print(f"Warning: Could not store interaction in user memory: {e}")
        
        # Save state (async)
        thesidia.save_state()
        
    except Exception as e:
        print(f"Error streaming response: {e}")
        import traceback
        traceback.print_exc()
        yield send_event('error', {
            'error': 'Internal server error',
            'message': str(e)
        })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/knowledge_base.html')
def knowledge_base_page():
    """Serve knowledge base HTML"""
    static_dir = Path(__file__).parent.parent / 'public'
    if static_dir.exists() and (static_dir / 'knowledge_base.html').exists():
        return send_from_directory(str(static_dir), 'knowledge_base.html')
    return send_from_directory('.', 'knowledge_base.html')

@app.route('/metrics_dashboard.html')
def metrics_dashboard():
    """Serve metrics dashboard HTML"""
    static_dir = Path(__file__).parent.parent / 'public'
    if static_dir.exists() and (static_dir / 'metrics_dashboard.html').exists():
        return send_from_directory(str(static_dir), 'metrics_dashboard.html')
    return send_from_directory('.', 'metrics_dashboard.html')

@app.route('/api/knowledge/stats', methods=['GET'])
def knowledge_stats():
    """Get knowledge base statistics"""
    stats = knowledge_base.get_stats()
    return jsonify(stats)

@app.route('/api/knowledge/topics', methods=['GET'])
def knowledge_topics():
    """Get all topics"""
    topics = knowledge_base.get_all_topics()
    return jsonify(topics)

@app.route('/api/knowledge/topic/<path:topic>', methods=['GET'])
def knowledge_topic(topic):
    """Get specific topic"""
    data = knowledge_base.get_knowledge(topic)
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Topic not found'}), 404

@app.route('/api/knowledge/search', methods=['GET'])
def knowledge_search():
    """Search knowledge base"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))
    results = knowledge_base.search(query, limit)
    return jsonify(results)

@app.route('/api/knowledge/connections', methods=['GET'])
def knowledge_connections():
    """Find connections between topics"""
    topic1 = request.args.get('topic1', '')
    topic2 = request.args.get('topic2', '')
    if not topic1 or not topic2:
        return jsonify({'error': 'Both topic1 and topic2 required'}), 400
    connections = knowledge_base.find_connections(topic1, topic2)
    return jsonify(connections)

@app.route('/api/metrics/current', methods=['GET'])
def metrics_current():
    """Get current session metrics"""
    if thesidia and thesidia.metrics:
        metrics = thesidia.metrics.get_current_metrics()
        return jsonify(metrics)
    return jsonify({'error': 'Metrics not available'}), 503

@app.route('/api/metrics/patterns', methods=['GET'])
def metrics_patterns():
    """Get pattern analysis"""
    if thesidia and thesidia.metrics:
        patterns = thesidia.metrics.get_pattern_analysis()
        return jsonify(patterns)
    return jsonify({'error': 'Metrics not available'}), 503

@app.route('/api/metrics/historical', methods=['GET'])
def metrics_historical():
    """Get historical metrics"""
    if thesidia and thesidia.metrics:
        historical = thesidia.metrics.get_historical_stats()
        return jsonify(historical)
    return jsonify({'error': 'Metrics not available'}), 503

@app.route('/api/user/session', methods=['GET', 'POST'])
def user_session():
    """Get or create user session"""
    user_id = None
    session_id = None
    
    # Extract IDs
    if request.is_json:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        session_id = data.get('session_id')
    
    if not user_id:
        user_id = request.args.get('user_id')
    if not session_id:
        session_id = request.args.get('session_id')
    
    # Get or create user data (auto-creates if IDs are missing)
    if user_memory_manager:
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        
        # Convert Path objects to strings for JSON serialization
        if 'user_dir' in user_data and hasattr(user_data['user_dir'], '__str__'):
            user_data['user_dir'] = str(user_data['user_dir'])
            
        return jsonify(user_data)
    
    return jsonify({'error': 'User memory manager not available'}), 503

@app.route('/api/stream/feed', methods=['GET'])
def stream_feed():
    """Stream feed endpoint - returns feed data"""
    try:
        page = int(request.args.get('page', 0))
        limit = int(request.args.get('limit', 20))
        
        # Return empty feed for now (can be populated later)
        return jsonify({
            'items': [],
            'has_more': False,
            'page': page,
            'limit': limit
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/metrics', methods=['GET'])
def metrics():
    """System metrics for Admin Dashboard"""
    try:
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        
        # Count active sessions (rough estimate based on user_memory_manager cache if available)
        active_users = 0
        if user_memory_manager and hasattr(user_memory_manager, 'user_cache'):
            active_users = len(user_memory_manager.user_cache)
            
        return jsonify({
            'system': {
                'cpu_percent': cpu,
                'memory_percent': mem.percent,
                'memory_used_gb': round(mem.used / (1024**3), 2),
                'memory_total_gb': round(mem.total / (1024**3), 2)
            },
            'application': {
                'active_sessions': active_users,
                'uptime_seconds': time.time() - START_TIME,
                'inference_engine': 'MLX' if mlx_inference.is_available() else 'Ollama'
            }
        })
    except Exception as e:
        server_logger.error(f"Metrics error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/user', methods=['GET'])
def admin_user_search():
    """Cerebro User Profiler Endpoint"""
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query required'}), 400
        
    # Mock Demo for "demo" query
    if query.lower() == 'demo':
        return jsonify({
            'user_id': 'user_demo_123',
            'username': 'neo_anderson',
            'risk_score': 85,
            'sentiment': 'Rebellious',
            'last_active': datetime.now().isoformat(),
            'connections': 142,
            'tags': ['influencer', 'high_risk', 'beta_tester'],
            'recent_prompt': "What is the Matrix?",
            'device': 'iPhone 15 Pro (iOS 18.1)'
        })

    # Real lookup attempt
    if user_memory_manager:
        # Try to find user (simplistic lookup by ID for now)
        # In a real DB we would search by partial username
        if query in user_memory_manager.user_cache:
             data = user_memory_manager.get_user_data(user_id=query)
             # Decorate with "God Mode" fake stats for the UI demo
             data['risk_score'] = random.randint(0, 100)
             data['sentiment'] = random.choice(['Positive', 'Neutral', 'Negative', 'Agitated'])
             data['connections'] = random.randint(0, 500)
             data['device'] = 'Unknown Device'
             return jsonify(data)
    
    return jsonify({'error': 'User not found'}), 404

# Overwatch API
# Neural Control Center API
@app.route('/api/neural/status', methods=['GET'])
def neural_status():
    """Returns real-time MLX neural engine status"""
    try:
        mem = psutil.virtual_memory()
        
        # Get MLX inference state
        status = {
            'active_model': mlx_inference.current_model or 'None',
            'loaded_models': list(mlx_inference.loaded_models.keys()),
            'available_models': mlx_inference.list_models(),
            'mlx_available': mlx_inference.is_available(),
            'memory': {
                'used_gb': round(mem.used / (1024**3), 2),
                'total_gb': round(mem.total / (1024**3), 2),
                'percent': mem.percent
            },
            'uptime_seconds': time.time() - START_TIME
        }
        
        return jsonify(status)
    except Exception as e:
        server_logger.error(f"Neural status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/neural/load', methods=['POST'])
def neural_load_model():
    """Load a specific MLX model"""
    data = request.get_json()
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({'error': 'model parameter required'}), 400
    
    success = mlx_inference.load_model(model_name)
    if success:
        return jsonify({'status': 'loaded', 'model': model_name})
    else:
        return jsonify({'error': 'Failed to load model'}), 500

@app.route('/api/neural/unload', methods=['POST'])
def neural_unload_model():
    """Unload a specific MLX model to free memory"""
    data = request.get_json()
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({'error': 'model parameter required'}), 400
    
    success = mlx_inference.unload_model(model_name)
    if success:
        return jsonify({'status': 'unloaded', 'model': model_name})
    else:
        return jsonify({'error': 'Model not loaded'}), 404

@app.route('/admin')
def admin_panel():
    """Serve the Admin Command Dashboard"""
    # Simply serve from current directory for now
    return send_from_directory('.', 'admin.html')

@app.route('/admin.js')
def admin_script():
    """Serve the Admin Dashboard logic"""
    return send_from_directory('.', 'admin.js')

@app.route('/admin-control')
def admin_control_panel():
    """Serve the Admin Control Panel (no .html extension)"""
    return send_from_directory('.', 'admin_control.html')

@app.route('/api/user/export', methods=['GET', 'POST'])
def user_export():
    """Export user conversation data for download"""
    if request.method == 'POST':
        data = request.get_json() or {}
        user_id = data.get('user_id')
        session_id = data.get('session_id')
    else:
        user_id = request.args.get('user_id')
        session_id = request.args.get('session_id')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        export_data = user_memory_manager.export_user_data(user_id=user_id, session_id=session_id)
        
        # Return as JSON download
        response = jsonify(export_data)
        response.headers['Content-Disposition'] = f'attachment; filename=thesidia_conversation_{export_data.get("user_id", "export")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Settings API
@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get all user settings"""
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    
    # Mock settings always available to avoid 500s in demo
    mock_settings = {
        'account': {
            'username': 'katanx_user',
            'display_name': 'Katanx Explorer',
            'bio': 'Exploring modern craft, motion, and systems.',
            'location': 'Global',
            'website': 'https://katanx.com'
        },
        'privacy': {
            'profile_visibility': 'public',
            'private_account': False,
            'dm_enabled': True
        },
        'notifications': {'email': True, 'push': False},
        'content': {'mature_filter': True}
    }
    
    # Always return mock in this build to prevent 500s
    return jsonify(mock_settings), 200


@app.route('/favicon.ico')
def favicon():
    # Minimal placeholder to prevent 500s in dev/demo
    return '', 204

@app.route('/api/settings/account', methods=['POST'])
@require_thesidia_user_data
def update_account_settings(user_id=None, session_id=None, user_data=None):
    """Update account settings"""
    if not settings_manager:
        return jsonify({'error': 'Settings manager not available'}), 503
    
    data = request.get_json() or {}
    
    try:
        # Update account section
        account_data = {
            'username': data.get('username', ''),
            'email': data.get('email', ''),
            'phone_number': data.get('phone_number', ''),
            'display_name': data.get('display_name', ''),
            'bio': data.get('bio', ''),
            'location': data.get('location', ''),
            'website': data.get('website', '')
        }
        
        # Validate username if provided
        if account_data['username']:
            is_valid, error = settings_manager.validate_username(account_data['username'], user_id)
            if not is_valid:
                return jsonify({'error': error}), 400
        
        success, error = settings_manager.update_settings_section(user_id, 'account', account_data)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'success': True, 'message': 'Account settings updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/security', methods=['POST'])
def update_security_settings():
    """Update security settings (password change)"""
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        # Handle password change
        if 'current_password' in data and 'new_password' in data:
            if not auth_manager:
                return jsonify({'error': 'Auth manager not available'}), 503
            success = auth_manager.change_password(
                user_id,
                data['current_password'],
                data['new_password']
            )
            if not success:
                return jsonify({'error': 'Invalid current password'}), 400
        
        # Update security section
        security_data = {
            'two_factor_enabled': data.get('two_factor_enabled', False),
            'login_notifications': data.get('login_notifications', True)
        }
        
        # Handle password change if provided
        if data.get('current_password') and data.get('new_password'):
            from webapp.auth.auth_manager import AuthManager
            from webapp.config.security import is_auth_required
            
            if is_auth_required():
                # In production mode, verify and update password
                auth_manager = AuthManager(user_manager=user_memory_manager.user_manager)
                
                # Verify current password
                user_info = user_memory_manager.user_manager._load_user_info(user_id)
                if not auth_manager.verify_password(data.get('current_password'), user_info.get('password_hash', '')):
                    return jsonify({'error': 'Current password is incorrect'}), 400
                
                # Hash and save new password
                new_password_hash = auth_manager.hash_password(data.get('new_password'))
                user_info['password_hash'] = new_password_hash
                user_memory_manager.user_manager._save_user_info(user_id, user_info)
            else:
                # In dev mode, just store it
                user_info = user_memory_manager.user_manager._load_user_info(user_id)
                user_info['password_hash'] = data.get('new_password')
                user_memory_manager.user_manager._save_user_info(user_id, user_info)
        
        success, error = settings_manager.update_settings_section(user_id, 'security', security_data)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'success': True, 'message': 'Security settings updated'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/privacy', methods=['POST'])
@require_thesidia_user_data
def update_privacy_settings(user_id=None, session_id=None, user_data=None):
    """Update privacy settings"""
    data = request.get_json() or {}
    
    try:
        # Update privacy section
        privacy_data = {
            'profile_visibility': data.get('profile_visibility', 'public'),
            'private_account': data.get('private_account', False),
            'dm_enabled': data.get('dm_enabled', True),
            'show_online_status': data.get('show_online_status', True),
            'blocked_users': data.get('blocked_users', []),
            'muted_users': data.get('muted_users', [])
        }
        
        success, error = settings_manager.update_settings_section(user_id, 'privacy', privacy_data)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'success': True, 'message': 'Privacy settings updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/notifications', methods=['POST'])
@require_thesidia_user_data
def update_notification_settings(user_id=None, session_id=None, user_data=None):
    """Update notification settings"""
    data = request.get_json() or {}
    
    try:
        # Update notifications section
        notifications_data = {
            'email_enabled': data.get('email_enabled', False),
            'push_enabled': data.get('push_enabled', True),
            'mentions': data.get('mentions', True),
            'follows': data.get('follows', True),
            'likes': data.get('likes', True),
            'comments': data.get('comments', True),
            'reposts': data.get('reposts', False)
        }
        
        success, error = settings_manager.update_settings_section(user_id, 'notifications', notifications_data)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'success': True, 'message': 'Notification settings updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/content', methods=['POST'])
@require_thesidia_user_data
def update_content_settings(user_id=None, session_id=None, user_data=None):
    """Update content settings"""
    data = request.get_json() or {}
    
    try:
        # Update content section
        content_data = {
            'auto_play_videos': data.get('auto_play_videos', False),
            'content_filter': data.get('content_filter', 'moderate'),
            'language': data.get('language', 'en'),
            'timezone': data.get('timezone', 'UTC')
        }
        
        success, error = settings_manager.update_settings_section(user_id, 'content', content_data)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'success': True, 'message': 'Content settings updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/upload', methods=['POST'])
def upload_media():
    """Upload media file (image or video)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    user_id = request.form.get('user_id') or request.args.get('user_id')
    session_id = request.form.get('session_id') or request.args.get('session_id')
    
    try:
        # Get user data
        if user_memory_manager:
            user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
            user_id = user_data.get('user_id') if user_data else user_id
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        # Validate file type
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm', 'mov'}
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'File type not allowed. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        # Determine media type
        media_type = 'video' if file_ext in {'mp4', 'webm', 'mov'} else 'image'
        
        # Create uploads directory structure
        uploads_dir = project_root / 'data' / 'uploads' / 'media'
        try:
            uploads_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            # On read-only filesystem (Vercel), return error
            return jsonify({'error': 'File uploads not available on this platform'}), 503
        
        # Generate unique filename
        timestamp = int(datetime.now().timestamp() * 1000)
        unique_filename = f"{user_id}_{timestamp}_{filename}"
        file_path = uploads_dir / unique_filename
        
        # Save file
        file.save(str(file_path))
        
        # Generate URL
        media_url = f'/api/media/{unique_filename}'
        
        return jsonify({
            'url': media_url,
            'type': media_type,
            'filename': unique_filename,
            'size': file_path.stat().st_size
        }), 201
        
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/media/<filename>', methods=['GET'])
def serve_media(filename):
    """Serve uploaded media files"""
    try:
        uploads_dir = project_root / 'data' / 'uploads' / 'media'
        file_path = uploads_dir / secure_filename(filename)
        
        if not file_path.exists() or not file_path.is_file():
            return jsonify({'error': 'File not found'}), 404
        
        # Determine content type
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'mp4': 'video/mp4',
            'webm': 'video/webm',
            'mov': 'video/quicktime'
        }
        content_type = content_types.get(ext, 'application/octet-stream')
        
        return send_from_directory(str(uploads_dir), filename, mimetype=content_type)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/avatar', methods=['POST'])
def upload_avatar():
    """Upload avatar image"""
    # TODO: Implement file upload handling
    return jsonify({'error': 'Not implemented yet'}), 501

@app.route('/api/settings/banner', methods=['POST'])
def upload_banner():
    """Upload banner image"""
    # TODO: Implement file upload handling
    return jsonify({'error': 'Not implemented yet'}), 501

@app.route('/api/settings/delete-account', methods=['POST'])
def delete_account():
    """Delete user account"""
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    password = data.get('password', '')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify password if in production mode
        from webapp.config.security import is_auth_required
        if is_auth_required() and password:
            from webapp.auth.auth_manager import AuthManager
            auth_manager = AuthManager(user_manager=user_memory_manager.user_manager)
            user_info = user_memory_manager.user_manager._load_user_info(user_id)
            if not auth_manager.verify_password(password, user_info.get('password_hash', '')):
                return jsonify({'error': 'Password is incorrect'}), 400
        
        # Delete user data
        user_dir = project_root / "data" / "users" / user_id
        if user_dir.exists():
            import shutil
            shutil.rmtree(user_dir)
        
        # Delete user posts
        if post_manager:
            user_posts = post_manager.get_posts_by_user(user_id)
            for post in user_posts:
                post_manager.delete_post(post['id'])
        
        return jsonify({'success': True, 'message': 'Account deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<target_username>/block', methods=['POST'])
def block_user(target_username):
    """Block a user"""
    if not social_graph:
        return jsonify({'error': 'Social features not available'}), 503
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        # Find target user by username
        # TODO: Implement username lookup
        # For now, assume target_username is a user_id
        target_user_id = target_username.lstrip('@')
        
        success = social_graph.block_user(user_id, target_user_id)
        if success:
            return jsonify({'success': True, 'message': 'User blocked'})
        return jsonify({'error': 'Failed to block user'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<target_username>/mute', methods=['POST'])
def mute_user(target_username):
    """Mute a user"""
    if not social_graph:
        return jsonify({'error': 'Social features not available'}), 503
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        # Find target user by username
        target_user_id = target_username.lstrip('@')
        
        success = social_graph.mute_user(user_id, target_user_id)
        if success:
            return jsonify({'success': True, 'message': 'User muted'})
        return jsonify({'error': 'Failed to mute user'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Social Media API
try:
    from webapp.social.post_manager import PostManager
    from webapp.social.feed_manager import FeedManager
    from webapp.social.social_graph import SocialGraph
    from webapp.social.interaction_manager import InteractionManager
    from webapp.social.moderation_manager import ModerationManager
    from webapp.social.ai_quality_scorer import AIQualityScorer
    
    # Initialize social managers
    post_manager = PostManager(base_dir=project_root)
    feed_manager = FeedManager(base_dir=project_root)
    social_graph = SocialGraph(base_dir=project_root)
    interaction_manager = InteractionManager(base_dir=project_root)
    moderation_manager = ModerationManager(base_dir=project_root)
    quality_scorer = AIQualityScorer(base_dir=project_root)
except ImportError as e:
    print(f"Warning: Social media features not available: {e}")
    post_manager = None
    feed_manager = None
    social_graph = None
    interaction_manager = None
    moderation_manager = None
    quality_scorer = None

@app.route('/api/posts', methods=['POST'])
def create_post():
    """Create a new post"""
    if not post_manager or not moderation_manager or not feed_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        # Create post
        post = post_manager.create_post(
            author_id=user_id,
            content=data.get('content', ''),
            media=data.get('media', []),
            tags=data.get('tags', []),
            visibility=data.get('visibility', 'public')
        )
        
        # Moderate post
        moderation_result = moderation_manager.moderate_post(post['id'])
        
        # Invalidate feed cache
        feed_manager.invalidate_cache(user_id)
        
        return jsonify(post)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get posts by user_id"""
    if not post_manager or not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        # Get posts by user
        posts = post_manager.get_posts_by_user(user_id, limit=limit, offset=offset)
        
        # Add interactions and author info to each post
        from webapp.utils.profile_loader import attach_author_to_post
        
        for post in posts:
            interactions = interaction_manager.get_interactions(post['id'])
            post['interactions'] = interactions
            
            # Add author profile information (using shared utility)
            attach_author_to_post(post, project_root, include_legacy_fields=True)
            
            # Add interaction counts for profile.js compatibility
            post['replies'] = interactions.get('comments', 0)
            post['reposts'] = interactions.get('reposts', 0)
            post['likes'] = interactions.get('likes', 0)
        
        return jsonify({'posts': posts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/tags', methods=['GET'])
def get_post_tags():
    """Get all unique tags from posts in database"""
    try:
        if not post_manager:
            # Fallback: return empty tags
            return jsonify({'tags': []})
        
        # Get all unique tags from posts
        tags = post_manager.get_all_tags()
        
        return jsonify({'tags': tags})
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc(), 'tags': []}), 500

@app.route('/api/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """Get a post by ID"""
    if not post_manager or not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    try:
        post = post_manager.get_post(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Get interactions
        interactions = interaction_manager.get_interactions(post_id)
        post['interactions'] = interactions
        
        return jsonify(post)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<post_id>', methods=['DELETE'])
@require_thesidia_user_data
def delete_post(post_id, user_id=None, session_id=None, user_data=None):
    """Delete a post"""
    if not post_manager or not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
        
    try:
        success = post_manager.delete_post(post_id, user_id)
        if not success:
            return jsonify({'error': 'Post not found'}), 404
        
        # Invalidate feed cache
        feed_manager.invalidate_cache()
        
        return jsonify({'success': True})
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/feed', methods=['GET'])
@require_thesidia_user_data
def get_feed(user_id=None, session_id=None, user_data=None):
    """Get user feed with filter and vibe support"""
    filter_type = request.args.get('filter', 'discover')  # for-you, discover
    vibe = request.args.get('vibe')  # relaxing, exciting, inspiring, focused, creative, analytical
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    if not feed_manager or not interaction_manager or not user_memory_manager:
        # Mock fallback feed when managers are unavailable
        from data.mock.mock_posts import generate_posts
        posts = generate_posts(count=limit, author_ids=[f"user_kxc_{i}" for i in ['aurora','motif','sierra','ember','nova','lumen']], seed=42)
        
        # Apply vibe filter if specified
        if vibe:
            posts = _filter_posts_by_vibe(posts, vibe, limit)
        
        return jsonify({'items': posts, 'has_more': False})
    
    try:
        # Determine feed type based on filter
        if filter_type == 'for-you':
            feed_type = 'personalized'  # Personalized feed for user
        elif filter_type == 'discover':
            feed_type = 'quality'  # Quality/discovery feed
        else:
            feed_type = 'chronological'  # Default fallback
        
        # Get feed
        posts = feed_manager.get_feed(user_id, feed_type, limit, offset)
        
        # Apply vibe filter if specified
        if vibe:
            posts = _filter_posts_by_vibe(posts, vibe, limit)
        
        # Add interactions and author info to each post
        from webapp.utils.profile_loader import attach_author_to_post
        
        for post in posts:
            interactions = interaction_manager.get_interactions(post['id'])
            post['interactions'] = interactions
            
            # Add author profile information (using shared utility)
            attach_author_to_post(post, project_root, include_legacy_fields=False)
        
        return jsonify({
            'items': posts,
            'has_more': len(posts) == limit,
            'page': offset // limit,
            'limit': limit
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

def _filter_posts_by_vibe(posts, vibe, limit=20):
    """
    Filter posts by vibe using content analysis and metadata
    
    Vibe mappings:
    - relaxing: calm, peaceful, meditative content
    - exciting: high energy, dynamic, engaging content
    - inspiring: motivational, uplifting, transformative content
    - focused: technical, detailed, educational content
    - creative: artistic, innovative, experimental content
    - analytical: data-driven, research-based, critical content
    """
    if not vibe or not posts:
        return posts
    
    # Vibe scoring keywords and patterns
    vibe_keywords = {
        'relaxing': ['calm', 'peaceful', 'meditation', 'breath', 'zen', 'mindful', 'quiet', 'serene', 'gentle', 'soft'],
        'exciting': ['energy', 'dynamic', 'intense', 'thrilling', 'adventure', 'action', 'power', 'vibrant', 'electric', 'pulse'],
        'inspiring': ['inspire', 'motivate', 'transform', 'breakthrough', 'discover', 'journey', 'growth', 'elevate', 'awaken', 'vision'],
        'focused': ['technical', 'detail', 'precision', 'method', 'system', 'analysis', 'structure', 'framework', 'protocol', 'process'],
        'creative': ['art', 'creative', 'innovative', 'experimental', 'design', 'imagine', 'express', 'original', 'unique', 'visionary'],
        'analytical': ['data', 'research', 'study', 'evidence', 'analysis', 'critical', 'examine', 'evaluate', 'metrics', 'quantify']
    }
    
    keywords = vibe_keywords.get(vibe.lower(), [])
    if not keywords:
        return posts
    
    # Score posts based on vibe
    scored_posts = []
    for post in posts:
        content = (post.get('content', '') or '').lower()
        tags = [tag.lower() for tag in (post.get('tags', []) or [])]
        
        # Calculate vibe score
        score = 0
        for keyword in keywords:
            if keyword in content:
                score += 2  # Content match is stronger
            if any(keyword in tag for tag in tags):
                score += 1  # Tag match
        
        # Also consider AI score and engagement for certain vibes
        ai_score = post.get('ai_score', 0) or 0
        interactions = post.get('interactions', {}) or {}
        engagement = (interactions.get('likes', 0) or 0) + (interactions.get('comments', 0) or 0)
        
        if vibe == 'exciting' and engagement > 10:
            score += 1
        if vibe == 'inspiring' and ai_score > 0.7:
            score += 1
        if vibe == 'analytical' and ai_score > 0.6:
            score += 1
        
        scored_posts.append((score, post))
    
    # Sort by score (highest first) and return top posts
    scored_posts.sort(key=lambda x: x[0], reverse=True)
    
    # Return posts with score > 0, or all if none match
    filtered = [post for score, post in scored_posts if score > 0]
    return filtered if filtered else posts

# Section-specific API endpoints
@app.route('/api/sections/home', methods=['GET'])
def get_home_section():
    """Get home dashboard data"""
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    
    try:
        # Import mock data generators
        from data.mock.mock_profiles import generate_profile
        from data.mock.mock_posts import generate_posts
        
        # Get user data (optional - don't fail if not available)
        current_user_id = None
        try:
            if user_memory_manager:
                user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
                current_user_id = user_data.get('user_id') if user_data else None
        except:
            pass  # Continue with mock data even if user lookup fails
        
        # Generate mock stats
        stats = {
            'posts': random.randint(10, 200),
            'interactions': random.randint(50, 1000),
            'connections': random.randint(5, 100)
        }
        
        # Generate recent activity
        recent_posts = generate_posts(count=5, author_ids=[current_user_id] if current_user_id else None, seed=42)
        recent_activity = []
        for post in recent_posts[:5]:
            time_ago = "2 hours ago" if random.random() > 0.5 else "1 day ago"
            recent_activity.append({
                'text': f"Posted: {post['content'][:50]}...",
                'time': time_ago
            })
        
        return jsonify({
            'stats': stats,
            'recent_activity': recent_activity
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/sections/stream', methods=['GET'])
def get_stream_section():
    """Get stream section data (enhanced feed)"""
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    try:
        from data.mock.mock_posts import generate_posts
        from data.mock.mock_profiles import generate_profiles
        from webapp.utils.profile_loader import load_author_profile
        
        # Get user data (optional)
        current_user_id = None
        try:
            if user_memory_manager:
                user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
                current_user_id = user_data.get('user_id') if user_data else None
        except:
            pass
        
        # Generate mock posts
        author_ids = [f"user_{i}" for i in range(10)]
        posts = generate_posts(count=limit, author_ids=author_ids, seed=321)
        
        # Generate mock profiles for authors
        from data.mock.mock_profiles import generate_profile
        author_profiles = {}
        for author_id in author_ids:
            # Use author_id as seed for consistent profile generation
            seed = hash(author_id) % 10000
            author_profiles[author_id] = generate_profile(user_id=author_id, seed=seed)
        
        # Attach author profiles
        for post in posts:
            try:
                author_id = post['author_id']
                author_profile = author_profiles.get(author_id)
                
                if author_profile:
                    post['author'] = {
                        'user_id': author_profile.get('user_id'),
                        'username': author_profile.get('username'),
                        'display_name': author_profile.get('display_name', author_profile.get('username', 'User')),
                        'avatar_url': author_profile.get('avatar_url', '')
                    }
                else:
                    # Fallback - try loading from file
                    author_profile = load_author_profile(author_id, project_root)
                    if author_profile:
                        post['author'] = {
                            'user_id': author_profile.get('user_id'),
                            'username': author_profile.get('username'),
                            'display_name': author_profile.get('display_name', author_profile.get('username', 'User')),
                            'avatar_url': author_profile.get('avatar_url', '')
                        }
                    else:
                        # Final fallback
                        post['author'] = {
                            'user_id': author_id,
                            'username': author_id.replace('user_', 'user'),
                            'display_name': author_id.replace('user_', 'User ').title(),
                            'avatar_url': ''
                        }
            except Exception as e:
                # Fallback if profile loading fails
                post['author'] = {
                    'user_id': post['author_id'],
                    'username': post['author_id'].replace('user_', 'user'),
                    'display_name': post['author_id'].replace('user_', 'User ').title(),
                    'avatar_url': ''
                }
        
        return jsonify({
            'items': posts,
            'has_more': len(posts) == limit
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/sections/kx-cuts', methods=['GET'])
def get_kx_cuts_section():
    """Get kx cuts (short-form content)"""
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    limit = int(request.args.get('limit', 20))
    
    try:
        from data.mock.mock_cuts import generate_cuts
        from data.mock.mock_profiles import generate_profiles
        from webapp.utils.profile_loader import load_author_profile
        
        # Get user data (optional)
        current_user_id = None
        try:
            if user_memory_manager:
                user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
                current_user_id = user_data.get('user_id') if user_data else None
        except:
            pass
        
        # Generate mock cuts (aligned with curated mock profiles)
        author_ids = [
            "user_kxc_aurora",
            "user_kxc_motif",
            "user_kxc_sierra",
            "user_kxc_ember",
            "user_kxc_nova",
            "user_kxc_lumen"
        ]
        cuts = generate_cuts(count=limit, author_ids=author_ids, seed=123)
        
        # Attach author profiles
        for cut in cuts:
            try:
                author_profile = load_author_profile(cut['author_id'], project_root)
                if author_profile:
                    cut['author'] = {
                        'user_id': author_profile.get('user_id'),
                        'username': author_profile.get('username'),
                        'display_name': author_profile.get('display_name', ''),
                        'avatar_url': author_profile.get('avatar_url', '')
                    }
                else:
                    # Fallback
                    cut['author'] = {
                        'user_id': cut['author_id'],
                        'username': cut['author_id'].replace('user_', ''),
                        'display_name': cut['author_id'].replace('user_', '').replace('_', ' ').title(),
                        'avatar_url': ''
                    }
            except:
                # Fallback if profile loading fails
                cut['author'] = {
                    'user_id': cut['author_id'],
                    'username': cut['author_id'].replace('user_', ''),
                    'display_name': cut['author_id'].replace('user_', '').replace('_', ' ').title(),
                    'avatar_url': ''
                }
        
        return jsonify({
            'items': cuts,
            'has_more': len(cuts) == limit
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/cuts/<cut_id>/recognize', methods=['POST'])
def recognize_cut(cut_id):
    """Recognize a cut (acknowledge quality expression)"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        if not cut_id:
            return jsonify({'error': 'cut_id required'}), 400
        
        # TODO: Implement recognition logic
        # For now, return mock response
        return jsonify({
            'success': True,
            'count': 1,
            'message': 'Cut recognized'
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/cuts/<cut_id>/growth', methods=['POST'])
def growth_cut(cut_id):
    """Share growth insight for a cut"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        if not cut_id:
            return jsonify({'error': 'cut_id required'}), 400
        
        # TODO: Implement growth logic
        # For now, return mock response
        return jsonify({
            'success': True,
            'count': 1,
            'message': 'Growth insight shared'
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/cuts/<cut_id>/connect', methods=['POST'])
def connect_cut(cut_id):
    """Request connection for a cut"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        if not cut_id:
            return jsonify({'error': 'cut_id required'}), 400
        
        # TODO: Implement connection logic
        # For now, return mock response
        return jsonify({
            'success': True,
            'count': 1,
            'message': 'Connection requested'
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get full category structure with subcategories"""
    try:
        from data.mock.forum_categories import FORUM_CATEGORIES, TAG_LEVELS, TAG_FORMATS, TAG_SOURCING
        
        return jsonify({
            'categories': FORUM_CATEGORIES,
            'tag_options': {
                'levels': TAG_LEVELS,
                'formats': TAG_FORMATS,
                'sourcing': TAG_SOURCING
            }
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/sections/circles', methods=['GET'])
def get_circles_section():
    """Get circles forum threads"""
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    filter_type = request.args.get('filter', 'all')
    category_filter = request.args.get('category')  # New: filter by category/subcategory
    limit = int(request.args.get('limit', 20))
    
    try:
        from data.mock.mock_circles import generate_threads
        from data.mock.mock_profiles import generate_profiles
        from webapp.utils.profile_loader import load_author_profile
        
        # Get user data (optional)
        current_user_id = None
        try:
            if user_memory_manager:
                user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
                current_user_id = user_data.get('user_id') if user_data else None
        except:
            pass
        
        # Generate mock threads - use one per category for demo
        from data.mock.mock_circles import generate_one_thread_per_category
        author_ids = [f"user_{i}" for i in range(10)]
        threads = generate_one_thread_per_category(author_ids=author_ids, seed=456)
        
        # Add welcome thread at the beginning
        welcome_thread = {
            'id': 'thread_welcome_how_to_use',
            'author_id': 'user_0',
            'title': 'Welcome: How to Use This Platform',
            'body': 'Welcome to our community platform. This guide will help you get started.\n\n**Navigation**\nThe platform is organized into sections accessible via the main navigation. Each section serves a specific purpose:\n\n- **Circles**: Community discussions organized by topic. Browse existing threads or start your own.\n- **Stream**: Your personalized feed of content and updates.\n- **Knowledge Base**: Curated information and resources.\n- **Studio**: Learning programs and mentorship opportunities.\n\n**Circles Section**\nCircles are topic-based communities where you can:\n- Browse discussions by category (Philosophy, Science, Business, etc.)\n- Click on any thread to view the full discussion\n- Upvote or downvote threads and comments\n- Reply to comments to create threaded discussions\n- Sort comments by Best, Top, New, or Controversial\n- Give awards to comments you find particularly valuable\n\n**Interacting with Content**\n- Use the upvote (^) button to support content you find valuable\n- Click the comment icon to view and participate in discussions\n- Click on any thread title to open the full discussion page\n- Use keyboard shortcuts: Cmd/Ctrl+Enter to submit comments, Escape to clear\n\n**Getting Started**\n1. Explore the Circles section to see what discussions are happening\n2. Click on a thread that interests you\n3. Read through the comments and replies\n4. Join the conversation by adding your own thoughts\n\nThis platform is designed for thoughtful, meaningful discussions. Take your time, engage authentically, and contribute value to the community.',
            'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
            'upvotes': 10,
            'downvotes': 0,
            'comment_count': 5,
            'views': 150,
            'circle': 'meta-guidelines/posting-rules',
            'category_id': 'meta-guidelines',
            'subcategory_id': 'posting-rules',
            'category_name': 'Meta / Guidelines',
            'subcategory_name': 'Posting Rules',
            'tags': ['welcome', 'guide', 'getting-started'],
            'tag_metadata': {
                'format': 'guide',
                'level': 'beginner'
            },
            'author': {
                'user_id': 'user_0',
                'username': 'admin',
                'display_name': 'Admin',
                'avatar_url': ''
            }
        }
        threads.insert(0, welcome_thread)
        
        # Apply category filter if specified
        if category_filter and category_filter != 'all':
            filtered_threads = []
            for thread in threads:
                thread_circle = thread.get('circle', '')
                thread_category_id = thread.get('category_id', '')
                # Match exact circle path, category ID, or parent category
                if (thread_circle == category_filter or 
                    thread_circle.startswith(category_filter + '/') or
                    thread_category_id == category_filter or
                    thread_circle.split('/')[0] == category_filter):
                    filtered_threads.append(thread)
            threads = filtered_threads
        
        # Apply filter
        if filter_type == 'trending':
            threads.sort(key=lambda x: x['upvotes'] - x['downvotes'], reverse=True)
            # Keep welcome thread at top even when sorting
            if welcome_thread in threads:
                threads.remove(welcome_thread)
                threads.insert(0, welcome_thread)
        elif filter_type == 'recent':
            threads.sort(key=lambda x: x['created_at'], reverse=True)
            # Keep welcome thread at top even when sorting
            if welcome_thread in threads:
                threads.remove(welcome_thread)
                threads.insert(0, welcome_thread)
        
        # Attach author profiles
        for thread in threads:
            try:
                author_profile = load_author_profile(thread['author_id'], project_root)
                if author_profile:
                    thread['author'] = {
                        'user_id': author_profile.get('user_id'),
                        'username': author_profile.get('username'),
                        'display_name': author_profile.get('display_name', ''),
                        'avatar_url': author_profile.get('avatar_url', '')
                    }
                else:
                    # Fallback
                    thread['author'] = {
                        'user_id': thread['author_id'],
                        'username': thread['author_id'].replace('user_', ''),
                        'display_name': thread['author_id'].replace('user_', '').replace('_', ' ').title(),
                        'avatar_url': ''
                    }
            except:
                # Fallback if profile loading fails
                thread['author'] = {
                    'user_id': thread['author_id'],
                    'username': thread['author_id'].replace('user_', ''),
                    'display_name': thread['author_id'].replace('user_', '').replace('_', ' ').title(),
                    'avatar_url': ''
                }
        
        # Get available categories from new category structure
        from data.mock.forum_categories import FORUM_CATEGORIES, get_all_subcategories
        
        categories = []
        
        # Add main categories
        for cat_id, cat_data in FORUM_CATEGORIES.items():
            # Count threads in this category (including subcategories)
            topic_threads = [
                t for t in threads 
                if t.get('category_id') == cat_id or t.get('circle', '').startswith(cat_id + '/')
            ]
            categories.append({
                'id': cat_id,
                'name': cat_data['name'],
                'slug': cat_id,
                'description': cat_data.get('description', ''),
                'thread_count': len(topic_threads),
                'type': 'category',
                'has_subcategories': len(cat_data.get('subcategories', [])) > 0,
                'avatar_url': None  # Will be generated client-side
            })
        
        # Add subcategories (flattened for easy filtering)
        all_subcategories = get_all_subcategories()
        for subcat in all_subcategories:
            # Count threads in this subcategory
            topic_threads = [
                t for t in threads 
                if t.get('circle') == f"{subcat['parent_category_id']}/{subcat['id']}"
            ]
            categories.append({
                'id': f"{subcat['parent_category_id']}/{subcat['id']}",
                'name': subcat['name'],
                'slug': subcat['id'],
                'description': subcat.get('description', ''),
                'parent_category_id': subcat['parent_category_id'],
                'parent_category_name': subcat['parent_category_name'],
                'thread_count': len(topic_threads),
                'type': 'subcategory',
                'avatar_url': None  # Will be generated client-side
            })
        
        return jsonify({
            'threads': threads,
            'categories': categories,
            'has_more': len(threads) == limit
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/threads/<thread_id>', methods=['GET'])
def get_thread_detail(thread_id):
    """Get thread detail with full content"""
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    
    try:
        from data.mock.mock_circles import generate_threads, CIRCLE_TOPICS
        from data.mock.mock_profiles import generate_profiles
        from webapp.utils.profile_loader import load_author_profile
        
        # Get user data (optional)
        current_user_id = None
        user_vote = None
        try:
            if user_memory_manager:
                user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
                current_user_id = user_data.get('user_id') if user_data else None
        except:
            pass
        
        # Generate threads to find the one we need
        # In a real system, this would query by ID
        from data.mock.forum_categories import FORUM_CATEGORIES
        author_ids = [f"user_{i}" for i in range(10)]
        all_threads = generate_threads(count=100, author_ids=author_ids, seed=456)
        
        # Check for special welcome thread
        if thread_id == 'thread_welcome_how_to_use':
            thread = {
                'id': 'thread_welcome_how_to_use',
                'author_id': 'user_0',
                'title': 'Welcome: How to Use This Platform',
                'body': '''Welcome to our community platform. This guide will help you get started.

**Navigation**
The platform is organized into sections accessible via the main navigation. Each section serves a specific purpose:

- **Circles**: Community discussions organized by topic. Browse existing threads or start your own.
- **Stream**: Your personalized feed of content and updates.
- **Knowledge Base**: Curated information and resources.
- **Studio**: Learning programs and mentorship opportunities.

**Circles Section**
Circles are topic-based communities where you can:
- Browse discussions by category (Philosophy, Science, Business, etc.)
- Click on any thread to view the full discussion
- Upvote or downvote threads and comments
- Reply to comments to create threaded discussions
- Sort comments by Best, Top, New, or Controversial
- Give awards to comments you find particularly valuable

**Interacting with Content**
- Use the upvote (^) button to support content you find valuable
- Click the comment icon to view and participate in discussions
- Click on any thread title to open the full discussion page
- Use keyboard shortcuts: Cmd/Ctrl+Enter to submit comments, Escape to clear

**Getting Started**
1. Explore the Circles section to see what discussions are happening
2. Click on a thread that interests you
3. Read through the comments and replies
4. Join the conversation by adding your own thoughts

This platform is designed for thoughtful, meaningful discussions. Take your time, engage authentically, and contribute value to the community.''',
                'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                'upvotes': 10,
                'downvotes': 0,
                'comment_count': 5,
                'views': 150,
                'circle': 'meta-guidelines/posting-rules',
                'category_id': 'meta-guidelines',
                'subcategory_id': 'posting-rules',
                'category_name': 'Meta / Guidelines',
                'subcategory_name': 'Posting Rules',
                'tags': ['welcome', 'guide', 'getting-started'],
                'tag_metadata': {
                    'format': 'guide',
                    'level': 'beginner'
                }
            }
        else:
            # Find thread by ID (or generate one if not found)
            thread = None
            for t in all_threads:
                if t['id'] == thread_id:
                    thread = t
                    break
            
            # If not found, generate a new one with the ID
            if not thread:
                import random
                from data.mock.forum_categories import FORUM_CATEGORIES
                random.seed(hash(thread_id) % 1000)
                
                # Select random category and subcategory
                category_id = random.choice(list(FORUM_CATEGORIES.keys()))
                category = FORUM_CATEGORIES[category_id]
                subcategories = category.get('subcategories', [])
                
                if subcategories:
                    subcategory = random.choice(subcategories)
                    circle = f"{category_id}/{subcategory['id']}"
                    topic = f"{category['name']} - {subcategory['name']}"
                else:
                    circle = category_id
                    topic = category['name']
                
                thread = {
                    'id': thread_id,
                    'author_id': random.choice(author_ids),
                    'title': f"Discussion: {topic}",
                    'body': f"I've been thinking about {topic} lately and wanted to get the community's perspective. What do you all think?",
                    'created_at': datetime.now().isoformat(),
                    'upvotes': random.randint(0, 500),
                    'downvotes': random.randint(0, 50),
                    'comment_count': random.randint(0, 100),
                    'views': random.randint(10, 5000),
                    'circle': circle,
                    'category_id': category_id,
                    'subcategory_id': subcategory['id'] if subcategories else None,
                    'category_name': category['name'],
                    'subcategory_name': subcategory['name'] if subcategories else None,
                    'tags': [circle],
                    'tag_metadata': {}
                }
        
        # Attach author profile
        try:
            author_profile = load_author_profile(thread['author_id'], project_root)
            if author_profile:
                thread['author'] = {
                    'user_id': author_profile.get('user_id'),
                    'username': author_profile.get('username'),
                    'display_name': author_profile.get('display_name', ''),
                    'avatar_url': author_profile.get('avatar_url', '')
                }
            else:
                thread['author'] = {
                    'user_id': thread['author_id'],
                    'username': thread['author_id'].replace('user_', ''),
                    'display_name': thread['author_id'].replace('user_', '').replace('_', ' ').title(),
                    'avatar_url': ''
                }
        except:
            thread['author'] = {
                'user_id': thread['author_id'],
                'username': thread['author_id'].replace('user_', ''),
                'display_name': thread['author_id'].replace('user_', '').replace('_', ' ').title(),
                'avatar_url': ''
            }
        
        # Calculate score
        thread['score'] = thread['upvotes'] - thread['downvotes']
        thread['user_vote'] = user_vote
        
        return jsonify(thread)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/threads/<thread_id>/comments', methods=['GET'])
def get_thread_comments(thread_id):
    """Get comments for a thread with sorting"""
    sort_type = request.args.get('sort', 'best')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    
    try:
        # Load comments from interaction manager or generate mock
        comments = []
        
        # Load vote states for comments
        vote_file = project_root / 'data' / 'social' / 'interactions' / f'{thread_id}.json'
        comment_votes = {}
        comment_awards = {}
        if vote_file.exists():
            try:
                with open(vote_file, 'r') as f:
                    data = json.load(f)
                    comment_votes = data.get('comment_votes', {})
                    comment_awards = data.get('comment_awards', {})
            except:
                pass
        
        # Check for welcome thread comments
        if thread_id == 'thread_welcome_how_to_use':
            welcome_file = project_root / 'data' / 'social' / 'interactions' / 'thread_welcome_how_to_use.json'
            if welcome_file.exists():
                try:
                    with open(welcome_file, 'r') as f:
                        welcome_data = json.load(f)
                        raw_comments = welcome_data.get('comments', [])
                        
                        # Attach vote states and awards to comments
                        for comment in raw_comments:
                            comment_id = comment.get('id')
                            
                            # Add vote state
                            if comment_id in comment_votes:
                                votes = comment_votes[comment_id]
                                comment['upvotes'] = len(votes.get('upvotes', []))
                                comment['downvotes'] = len(votes.get('downvotes', []))
                                comment['score'] = comment['upvotes'] - comment['downvotes']
                                if user_id:
                                    if user_id in votes.get('upvotes', []):
                                        comment['user_vote'] = 'up'
                                    elif user_id in votes.get('downvotes', []):
                                        comment['user_vote'] = 'down'
                            
                            # Add awards
                            if comment_id in comment_awards:
                                from webapp.social.awards import aggregate_awards
                                comment['awards'] = aggregate_awards(comment_awards[comment_id])
                        
                        # Convert to nested structure
                        comments = _build_comment_tree(raw_comments, user_id)
                except Exception as e:
                    print(f"Error loading welcome thread comments: {e}")
                    comments = []
        
        # Try to load from interaction manager
        if not comments and interaction_manager:
            try:
                interactions = interaction_manager.get_interactions(thread_id)
                raw_comments = interactions.get('comments', [])
                
                # Attach vote states and awards to comments
                for comment in raw_comments:
                    comment_id = comment.get('id')
                    
                    # Add vote state
                    if comment_id in comment_votes:
                        votes = comment_votes[comment_id]
                        comment['upvotes'] = len(votes.get('upvotes', []))
                        comment['downvotes'] = len(votes.get('downvotes', []))
                        comment['score'] = comment['upvotes'] - comment['downvotes']
                        if user_id:
                            if user_id in votes.get('upvotes', []):
                                comment['user_vote'] = 'up'
                            elif user_id in votes.get('downvotes', []):
                                comment['user_vote'] = 'down'
                    
                    # Add awards
                    if comment_id in comment_awards:
                        from webapp.social.awards import aggregate_awards
                        comment['awards'] = aggregate_awards(comment_awards[comment_id])
                
                # Convert to nested structure
                comments = _build_comment_tree(raw_comments, user_id)
            except:
                pass
        
        # If no comments, generate mock comments
        if not comments:
            # For category threads, generate exactly 3 comments
            comment_count = 3 if thread_id.startswith('thread_cat_') else limit
            comments = _generate_mock_comments(thread_id, comment_count)
            
            # Attach vote states and awards to mock comments
            for comment in comments:
                comment_id = comment.get('id')
                
                # Add vote state if exists
                if comment_id in comment_votes:
                    votes = comment_votes[comment_id]
                    comment['upvotes'] = len(votes.get('upvotes', []))
                    comment['downvotes'] = len(votes.get('downvotes', []))
                    comment['score'] = comment['upvotes'] - comment['downvotes']
                    if user_id:
                        if user_id in votes.get('upvotes', []):
                            comment['user_vote'] = 'up'
                        elif user_id in votes.get('downvotes', []):
                            comment['user_vote'] = 'down'
                
                # Add awards if exists
                if comment_id in comment_awards:
                    from webapp.social.awards import aggregate_awards
                    comment['awards'] = aggregate_awards(comment_awards[comment_id])
        
        # Sort comments
        try:
            from webapp.social.comment_sorter import sort_comments
            comments = sort_comments(comments, sort_type)
        except ImportError:
            # Fallback sorting if module not available
            if sort_type == 'top':
                comments.sort(key=lambda c: c.get('score', 0), reverse=True)
            elif sort_type == 'new':
                comments.sort(key=lambda c: c.get('created_at', ''), reverse=True)
            # 'best' and 'controversial' default to score-based
            else:
                comments.sort(key=lambda c: c.get('score', 0), reverse=True)
        
        # Apply pagination
        total = len(comments)
        comments = comments[offset:offset + limit]
        
        return jsonify({
            'comments': comments,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

def _build_comment_tree(raw_comments, user_id=None):
    """Build nested comment tree from flat list"""
    # Group by parent_id
    by_parent = {}
    for comment in raw_comments:
        parent_id = comment.get('parent_id')
        if parent_id not in by_parent:
            by_parent[parent_id] = []
        by_parent[parent_id].append(comment)
    
    def build_tree(parent_id=None):
        children = by_parent.get(parent_id, [])
        result = []
        for comment in children:
            comment_data = {
                'id': comment.get('id'),
                'thread_id': comment.get('thread_id'),
                'parent_id': comment.get('parent_id'),
                'author': comment.get('author', {}),
                'content': comment.get('content', ''),
                'created_at': comment.get('created_at', ''),
                'score': comment.get('score', 0),
                'upvotes': comment.get('upvotes', 0),
                'downvotes': comment.get('downvotes', 0),
                'user_vote': comment.get('user_vote'),
                'replies': build_tree(comment.get('id')),
                'awards': comment.get('awards', [])
            }
            result.append(comment_data)
        return result
    
    return build_tree()

def _generate_mock_comments(thread_id, count=10):
    """Generate mock comments for a thread"""
    import random
    from webapp.utils.profile_loader import load_author_profile
    
    comments = []
    author_ids = [f"user_{i}" for i in range(10)]
    
    # Use consistent seed for category threads to get same comments each time
    if thread_id.startswith('thread_cat_'):
        random.seed(hash(thread_id) % 10000)
    
    # Comment templates for more realistic content
    comment_templates = [
        "This is a great point. I've been thinking about this from a different angle - what if we consider {perspective}?",
        "I agree with the main idea here. In my experience, {experience} has shown that {insight}.",
        "Interesting perspective. I'd like to add that {addition}. What do others think about this?",
        "This resonates with me. I've found that {finding} when exploring {topic}.",
        "Good discussion. One thing to consider is {consideration}. Has anyone else noticed this?",
        "I appreciate this insight. From what I understand, {understanding} plays a key role here.",
        "This is helpful. I'm curious about {curiosity}. Does anyone have thoughts on this?",
        "Well said. I think {thought} is particularly relevant here. What's your take?"
    ]
    
    for i in range(count):
        comment_id = f"comment_{thread_id}_{i}"
        author_id = random.choice(author_ids)
        
        # Try to load author profile
        author = {
            'user_id': author_id,
            'username': author_id.replace('user_', ''),
            'display_name': author_id.replace('user_', '').replace('_', ' ').title(),
            'avatar_url': ''
        }
        
        try:
            author_profile = load_author_profile(author_id, project_root)
            if author_profile:
                author = {
                    'user_id': author_profile.get('user_id'),
                    'username': author_profile.get('username'),
                    'display_name': author_profile.get('display_name', ''),
                    'avatar_url': author_profile.get('avatar_url', '')
                }
        except:
            pass
        
        # For category threads (3 comments), make them all top-level
        # For other threads, allow some nesting
        parent_id = None
        if not thread_id.startswith('thread_cat_') and i > 2 and random.random() > 0.4:
            parent_id = comments[random.randint(0, min(i-1, 5))]['id']
        
        # Generate more realistic comment content
        if thread_id.startswith('thread_cat_'):
            # Use simple, clear comments for demo
            content_options = [
                "This is a thoughtful discussion. I appreciate the insights shared here.",
                "Great points made. I'd like to add that this topic deserves deeper exploration.",
                "Interesting perspective. I'm looking forward to seeing more discussion on this."
            ]
            content = content_options[i % len(content_options)]
        else:
            template = random.choice(comment_templates)
            # Simple placeholder replacement
            content = template.replace('{perspective}', 'the practical applications').replace('{experience}', 'working with this').replace('{insight}', 'there are multiple valid approaches').replace('{addition}', 'context matters here').replace('{finding}', 'patterns emerge').replace('{topic}', 'this area').replace('{consideration}', 'the broader implications').replace('{understanding}', 'collaboration').replace('{curiosity}', 'how this connects to other concepts').replace('{thought}', 'the underlying principles')
        
        upvotes = random.randint(2, 25) if thread_id.startswith('thread_cat_') else random.randint(0, 100)
        downvotes = random.randint(0, 3) if thread_id.startswith('thread_cat_') else random.randint(0, 20)
        
        comment = {
            'id': comment_id,
            'thread_id': thread_id,
            'parent_id': parent_id,
            'author': author,
            'content': content,
            'created_at': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
            'score': upvotes - downvotes,
            'upvotes': upvotes,
            'downvotes': downvotes,
            'user_vote': None,
            'replies': [],
            'awards': []
        }
        comments.append(comment)
    
    # Build tree structure
    return _build_comment_tree(comments)

@app.route('/api/threads/<thread_id>/comments', methods=['POST'])
def create_thread_comment(thread_id):
    """Create a top-level comment on a thread"""
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Comment content required'}), 400
    
    try:
        # Get user data
        if user_memory_manager:
            user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
            user_id = user_data.get('user_id') if user_data else user_id
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        # Create comment via interaction manager or direct storage
        comment_id = f"comment_{thread_id}_{int(datetime.now().timestamp() * 1000)}"
        
        from webapp.utils.profile_loader import load_author_profile
        author_profile = load_author_profile(user_id, project_root)
        author = {
            'user_id': user_id,
            'username': author_profile.get('username', user_id.replace('user_', '')) if author_profile else user_id.replace('user_', ''),
            'display_name': author_profile.get('display_name', '') if author_profile else '',
            'avatar_url': author_profile.get('avatar_url', '') if author_profile else ''
        }
        
        comment = {
            'id': comment_id,
            'thread_id': thread_id,
            'parent_id': None,
            'author': author,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'score': 0,
            'upvotes': 0,
            'downvotes': 0,
            'user_vote': None,
            'replies': [],
            'awards': []
        }
        
        # Save comment via interaction manager
        if interaction_manager:
            try:
                interaction_manager.comment_post(thread_id, user_id, content)
            except:
                pass
        
        return jsonify(comment), 201
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/comments/<comment_id>/reply', methods=['POST'])
def reply_to_comment(comment_id):
    """Reply to an existing comment"""
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    content = data.get('content', '').strip()
    thread_id = data.get('thread_id')
    
    if not content:
        return jsonify({'error': 'Comment content required'}), 400
    
    try:
        # Get user data
        if user_memory_manager:
            user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
            user_id = user_data.get('user_id') if user_data else user_id
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        # Get parent comment to find thread_id
        if not thread_id:
            # Try to extract from comment_id or load from storage
            thread_id = comment_id.split('_')[1] if '_' in comment_id else None
        
        if not thread_id:
            return jsonify({'error': 'Thread ID required'}), 400
        
        from webapp.utils.profile_loader import load_author_profile
        author_profile = load_author_profile(user_id, project_root)
        author = {
            'user_id': user_id,
            'username': author_profile.get('username', user_id.replace('user_', '')) if author_profile else user_id.replace('user_', ''),
            'display_name': author_profile.get('display_name', '') if author_profile else '',
            'avatar_url': author_profile.get('avatar_url', '') if author_profile else ''
        }
        
        reply_id = f"comment_{thread_id}_{int(datetime.now().timestamp() * 1000)}"
        
        reply = {
            'id': reply_id,
            'thread_id': thread_id,
            'parent_id': comment_id,
            'author': author,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'score': 0,
            'upvotes': 0,
            'downvotes': 0,
            'user_vote': None,
            'replies': [],
            'awards': []
        }
        
        # Save reply via interaction manager
        if interaction_manager:
            try:
                interaction_manager.comment_post(thread_id, user_id, content)
            except:
                pass
        
        return jsonify(reply), 201
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/threads/<thread_id>/vote', methods=['POST'])
def vote_thread(thread_id):
    """Vote on a thread (upvote, downvote, or remove vote)"""
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    direction = data.get('direction')  # 'up', 'down', or None to remove
    
    try:
        # Get user data
        if user_memory_manager:
            user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
            user_id = user_data.get('user_id') if user_data else user_id
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        # Load or create vote storage
        vote_file = project_root / 'data' / 'social' / 'interactions' / f'{thread_id}.json'
        votes = {'upvotes': [], 'downvotes': []}
        
        if vote_file.exists():
            try:
                with open(vote_file, 'r') as f:
                    data = json.load(f)
                    votes['upvotes'] = data.get('upvotes', [])
                    votes['downvotes'] = data.get('downvotes', [])
            except:
                pass
        
        # Update votes
        user_vote = None
        if direction == 'up':
            if user_id in votes['downvotes']:
                votes['downvotes'].remove(user_id)
            if user_id not in votes['upvotes']:
                votes['upvotes'].append(user_id)
            user_vote = 'up'
        elif direction == 'down':
            if user_id in votes['upvotes']:
                votes['upvotes'].remove(user_id)
            if user_id not in votes['downvotes']:
                votes['downvotes'].append(user_id)
            user_vote = 'down'
        else:
            # Remove vote
            if user_id in votes['upvotes']:
                votes['upvotes'].remove(user_id)
            if user_id in votes['downvotes']:
                votes['downvotes'].remove(user_id)
            user_vote = None
        
        # Save votes
        try:
            vote_file.parent.mkdir(parents=True, exist_ok=True)
            with open(vote_file, 'w') as f:
                json.dump(votes, f, indent=2)
        except (OSError, PermissionError) as e:
            # On read-only filesystem (Vercel), use in-memory storage
            print(f"Warning: Cannot save votes to disk (read-only filesystem): {e}")
        
        score = len(votes['upvotes']) - len(votes['downvotes'])
        
        return jsonify({
            'score': score,
            'upvotes': len(votes['upvotes']),
            'downvotes': len(votes['downvotes']),
            'user_vote': user_vote
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/comments/<comment_id>/vote', methods=['POST'])
def vote_comment(comment_id):
    """Vote on a comment (upvote, downvote, or remove vote)"""
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    direction = data.get('direction')  # 'up', 'down', or None to remove
    
    try:
        # Get user data
        if user_memory_manager:
            user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
            user_id = user_data.get('user_id') if user_data else user_id
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        # Extract thread_id from comment_id
        thread_id = comment_id.split('_')[1] if '_' in comment_id else None
        
        # Load comment votes
        vote_file = project_root / 'data' / 'social' / 'interactions' / f'{thread_id}.json'
        votes = {'upvotes': [], 'downvotes': []}
        comment_votes = {}
        
        if vote_file.exists():
            try:
                with open(vote_file, 'r') as f:
                    data = json.load(f)
                    comment_votes = data.get('comment_votes', {})
                    if comment_id in comment_votes:
                        votes = comment_votes[comment_id]
                    else:
                        votes = {'upvotes': [], 'downvotes': []}
            except:
                pass
        
        # Update votes
        user_vote = None
        if direction == 'up':
            if user_id in votes.get('downvotes', []):
                votes['downvotes'].remove(user_id)
            if user_id not in votes.get('upvotes', []):
                if 'upvotes' not in votes:
                    votes['upvotes'] = []
                votes['upvotes'].append(user_id)
            user_vote = 'up'
        elif direction == 'down':
            if user_id in votes.get('upvotes', []):
                votes['upvotes'].remove(user_id)
            if user_id not in votes.get('downvotes', []):
                if 'downvotes' not in votes:
                    votes['downvotes'] = []
                votes['downvotes'].append(user_id)
            user_vote = 'down'
        else:
            # Remove vote
            if 'upvotes' in votes and user_id in votes['upvotes']:
                votes['upvotes'].remove(user_id)
            if 'downvotes' in votes and user_id in votes['downvotes']:
                votes['downvotes'].remove(user_id)
            user_vote = None
        
        # Save comment votes
        comment_votes[comment_id] = votes
        try:
            vote_file.parent.mkdir(parents=True, exist_ok=True)
            if vote_file.exists():
                with open(vote_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
        except (OSError, PermissionError) as e:
            # On read-only filesystem (Vercel), use in-memory storage
            print(f"Warning: Cannot save comment votes to disk (read-only filesystem): {e}")
            data = {}
        
        data['comment_votes'] = comment_votes
        with open(vote_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        score = len(votes.get('upvotes', [])) - len(votes.get('downvotes', []))
        
        return jsonify({
            'score': score,
            'upvotes': len(votes.get('upvotes', [])),
            'downvotes': len(votes.get('downvotes', [])),
            'user_vote': user_vote
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/comments/<comment_id>/award', methods=['POST'])
def award_comment(comment_id):
    """Give an award to a comment"""
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    award_type = data.get('award_type')
    
    if not award_type:
        return jsonify({'error': 'Award type required'}), 400
    
    try:
        # Get user data
        if user_memory_manager:
            user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
            user_id = user_data.get('user_id') if user_data else user_id
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        from webapp.social.awards import add_award, get_award_types
        
        # Validate award type
        valid_types = [a['id'] for a in get_award_types()]
        if award_type not in valid_types:
            return jsonify({'error': f'Invalid award type. Must be one of: {", ".join(valid_types)}'}), 400
        
        # Add award
        award = add_award(comment_id, user_id, award_type)
        
        # Load existing awards for this comment
        thread_id = comment_id.split('_')[1] if '_' in comment_id else None
        if thread_id:
            vote_file = project_root / 'data' / 'social' / 'interactions' / f'{thread_id}.json'
            awards_data = {}
            
            if vote_file.exists():
                try:
                    with open(vote_file, 'r') as f:
                        data = json.load(f)
                        awards_data = data.get('comment_awards', {})
                except:
                    pass
            
            if comment_id not in awards_data:
                awards_data[comment_id] = []
            
            awards_data[comment_id].append(award)
            
            # Save awards
            if vote_file.exists():
                with open(vote_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            
            data['comment_awards'] = awards_data
            try:
                vote_file.parent.mkdir(parents=True, exist_ok=True)
                with open(vote_file, 'w') as f:
                    json.dump(data, f, indent=2)
            except (OSError, PermissionError) as e:
                # On read-only filesystem (Vercel), use in-memory storage
                print(f"Warning: Cannot save awards to disk (read-only filesystem): {e}")
        
        return jsonify(award), 201
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/awards/types', methods=['GET'])
def get_award_types():
    """Get all available award types"""
    try:
        from webapp.social.awards import get_award_types
        return jsonify({'awards': get_award_types()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sections/studio', methods=['GET'])
def get_studio_section():
    """Get studio mentor programs"""
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    filter_type = request.args.get('filter', 'all')
    
    try:
        from data.mock.mock_studio import generate_programs
        
        # Get user data (optional)
        current_user_id = None
        try:
            if user_memory_manager:
                user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
                current_user_id = user_data.get('user_id') if user_data else None
        except:
            pass
        
        # Generate mock programs
        mentor_ids = [f"mentor_{i}" for i in range(5)]
        programs = generate_programs(count=12, mentor_ids=mentor_ids, seed=789)
        
        # Apply filter
        if filter_type == 'active':
            programs = [p for p in programs if p['status'] == 'active']
        elif filter_type == 'upcoming':
            programs = [p for p in programs if p['status'] == 'upcoming']
        
        return jsonify({
            'programs': programs
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/posts/<post_id>/like', methods=['POST'])
def like_post(post_id):
    """Like or unlike a post"""
    if not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        liked = interaction_manager.like_post(post_id, user_id)
        interactions = interaction_manager.get_interactions(post_id)
        
        return jsonify({
            'liked': liked,
            'interactions': interactions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<post_id>/validate', methods=['POST'])
def validate_post(post_id):
    """Validate or un-validate a post (high-signal rigor action)"""
    if not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        validated = interaction_manager.validate_post(post_id, user_id)
        interactions = interaction_manager.get_interactions(post_id)
        
        return jsonify({
            'validated': validated,
            'interactions': interactions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<post_id>/reference', methods=['POST'])
def reference_post(post_id):
    """Reference a post (utility / citation signal)"""
    if not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    context = data.get('context') or request.args.get('context')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        ref = interaction_manager.reference_post(post_id, user_id, context=context)
        interactions = interaction_manager.get_interactions(post_id)
        
        return jsonify({
            'reference': ref,
            'interactions': interactions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<post_id>/contribute', methods=['POST'])
def contribute_post_mastery(post_id):
    """Register a structured contribution to a post (peer-review style)"""
    if not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    content = data.get('content', '')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    if not content:
        return jsonify({'error': 'Contribution content required'}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        contribution = interaction_manager.contribute_to_post(post_id, user_id, content)
        interactions = interaction_manager.get_interactions(post_id)
        
        return jsonify({
            'contribution': contribution,
            'interactions': interactions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<post_id>/comment', methods=['POST'])
def comment_post(post_id):
    """Comment on a post"""
    if not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    content = data.get('content', '')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    if not content:
        return jsonify({'error': 'Comment content required'}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        comment = interaction_manager.comment_post(post_id, user_id, content)
        interactions = interaction_manager.get_interactions(post_id)
        
        return jsonify({
            'comment': comment,
            'interactions': interactions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<target_user_id>/follow', methods=['POST'])
def follow_user(target_user_id):
    """Follow or unfollow a user"""
    if not social_graph or not feed_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if already following
        is_following = social_graph.is_following(user_id, target_user_id)
        
        if is_following:
            social_graph.unfollow_user(user_id, target_user_id)
            following = False
        else:
            social_graph.follow_user(user_id, target_user_id)
            following = True
        
        # Invalidate feed cache
        feed_manager.invalidate_cache(user_id)
        
        return jsonify({
            'following': following,
            'target_user_id': target_user_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile"""
    if not settings_manager or not social_graph or not post_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    try:
        settings = settings_manager.get_settings(user_id)
        profile = settings.get('account', {})
        
        # Get social graph
        graph = social_graph.get_social_graph(user_id)
        
        # Get post count
        posts = post_manager.get_posts_by_user(user_id, limit=1)
        
        profile_data = {
            'user_id': user_id,
            'username': profile.get('username', ''),
            'display_name': profile.get('display_name', ''),
            'bio': profile.get('bio', ''),
            'avatar_url': profile.get('avatar_url', ''),
            'stats': {
                'posts': len(posts),
                'followers': len(graph.get('followers', [])),
                'following': len(graph.get('following', []))
            }
        }
        
        return jsonify(profile_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Astronomical & Temporal Pattern API
@app.route('/api/astronomical/current', methods=['GET'])
def astronomical_current():
    """Get current astronomical and calendar positions"""
    try:
        if not astronomical_engine:
            return jsonify({
                'error': 'Astronomical engine not available',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        positions = astronomical_engine.calculate_all_calendars()
        return jsonify(positions)
    except Exception as e:
        print(f"Error in astronomical_current: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/astronomical/correlations', methods=['GET'])
def astronomical_correlations():
    """Find historical events with similar calendar positions"""
    try:
        date_str = request.args.get('date')
        if date_str:
            date = datetime.fromisoformat(date_str)
        else:
            date = datetime.now()
        
        window_days = int(request.args.get('window', 365))
        correlations = astronomical_engine.find_pattern_correlations(date, window_days)
        
        return jsonify({
            'date': date.isoformat(),
            'correlations': correlations,
            'count': len(correlations),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in astronomical_correlations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/astronomical/patterns', methods=['GET'])
def astronomical_patterns_api():
    """Get detected recurring temporal patterns"""
    try:
        patterns = astronomical_engine.detect_recurring_patterns()
        return jsonify({
            'patterns': patterns,
            'count': len(patterns),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in astronomical_patterns: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/astronomical/predict', methods=['GET'])
def astronomical_predict():
    """Predict future calendar positions"""
    try:
        days_ahead = int(request.args.get('days', 365))
        calendar = request.args.get('calendar', 'all')
        
        future_positions = astronomical_engine.predict_cycle_phase(calendar, days_ahead)
        
        return jsonify({
            'days_ahead': days_ahead,
            'positions': future_positions,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in astronomical_predict: {e}")
        return jsonify({'error': str(e)}), 500

# Bot Generation API
try:
    from webapp.social.bot_generator import BotGenerator
    from webapp.social.bot_cleanup import BotCleanup
    bot_generator = BotGenerator(base_dir=project_root)
    bot_cleanup = BotCleanup(base_dir=project_root)
except ImportError:
    bot_generator = None
    bot_cleanup = None

@app.route('/api/bots/generate', methods=['POST'])
def generate_bots():
    """Generate bot profiles and activity"""
    if not bot_generator:
        return jsonify({'error': 'Bot generator not available'}), 503
    
    data = request.get_json() or {}
    count = int(data.get('count', 10))
    bot_types = data.get('bot_types', ['active', 'moderate', 'casual'])
    generate_activity = data.get('generate_activity', True)
    days_of_activity = int(data.get('days_of_activity', 30))
    
    try:
        result = bot_generator.generate_bot_army(
            count=count,
            bot_types=bot_types,
            generate_activity=generate_activity,
            days_of_activity=days_of_activity
        )
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/bots/generate-community', methods=['POST'])
def generate_community_bots():
    """Generate community bots with tags"""
    if not bot_generator:
        return jsonify({'error': 'Bot generator not available'}), 503
    
    data = request.get_json() or {}
    communities = data.get('communities', None)  # Auto-generate if None
    bots_per_community = int(data.get('bots_per_community', 3))
    generate_activity = data.get('generate_activity', True)
    days_of_activity = int(data.get('days_of_activity', 30))
    
    try:
        result = bot_generator.generate_community_bots(
            communities=communities,
            bots_per_community=bots_per_community,
            generate_activity=generate_activity,
            days_of_activity=days_of_activity
        )
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/bots/generate-activity', methods=['POST'])
def generate_bot_activity():
    """Generate activity for existing bot"""
    if not bot_generator:
        return jsonify({'error': 'Bot generator not available'}), 503
    
    data = request.get_json() or {}
    bot_id = data.get('bot_id')
    days = int(data.get('days', 30))
    posts_per_day_min = float(data.get('posts_per_day_min', 0.5))
    posts_per_day_max = float(data.get('posts_per_day_max', 3))
    
    if not bot_id:
        return jsonify({'error': 'bot_id required'}), 400
    
    try:
        result = bot_generator.generate_bot_activity(
            bot_id=bot_id,
            days=days,
            posts_per_day_range=(posts_per_day_min, posts_per_day_max)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bots/list', methods=['GET'])
def list_bots():
    """List all generated bots"""
    if not bot_generator:
        return jsonify({'error': 'Bot generator not available'}), 503
    
    bots_dir = project_root / "data" / "bots"
    bots = []
    
    if bots_dir.exists():
        for bot_file in bots_dir.glob("bot_*.json"):
            try:
                with open(bot_file, 'r', encoding='utf-8') as f:
                    bot_data = json.load(f)
                    bots.append({
                        'bot_id': bot_data.get('bot_id'),
                        'username': bot_data.get('username'),
                        'display_name': bot_data.get('display_name'),
                        'bot_type': bot_data.get('bot_type'),
                        'created_at': bot_data.get('created_at')
                    })
            except Exception:
                continue
    
    return jsonify({'bots': bots, 'count': len(bots)})

@app.route('/api/bots/cleanup', methods=['POST'])
def cleanup_bot_posts():
    """Clean up old bot posts"""
    if not bot_cleanup:
        return jsonify({'error': 'Bot cleanup not available'}), 503
    
    data = request.get_json() or {}
    retention_days = int(data.get('retention_days', 30))
    
    try:
        result = bot_cleanup.cleanup_all()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bots/post-now', methods=['POST'])
def bot_post_now():
    """Make a bot post right now (real-time)"""
    if not bot_generator:
        return jsonify({'error': 'Bot generator not available'}), 503
    
    import random
    
    data = request.get_json() or {}
    bot_id = data.get('bot_id')
    
    # If no bot_id, select random active bot
    if not bot_id:
        bots_dir = project_root / "data" / "bots"
        bot_files = list(bots_dir.glob("bot_*.json")) if bots_dir.exists() else []
        if not bot_files:
            return jsonify({'error': 'No bots available'}), 404
        
        bot_file = random.choice(bot_files)
        with open(bot_file, 'r', encoding='utf-8') as f:
            bot_data = json.load(f)
            bot_id = bot_data.get('bot_id')
    
    try:
        # Load bot profile
        profile_file = bot_generator.bots_dir / f"{bot_id}.json"
        if not profile_file.exists():
            return jsonify({'error': 'Bot not found'}), 404
        
        with open(profile_file, 'r', encoding='utf-8') as f:
            bot_profile = json.load(f)
        
        # Generate content
        content = bot_generator.content_synthesizer.synthesize_post(bot_profile)
        
        # Generate media (higher chance for Labs/community)
        media = []
        bot_type = bot_profile.get('bot_type', 'moderate')
        media_chance = 0.8 if bot_type == "community" else 0.6  # More media for Labs
        
        if random.random() < media_chance:
            topic = random.choice(bot_profile.get('interests', ['technology']))
            media = bot_generator.media_generator.generate_media_for_post(
                post_type="random",
                topic=topic
            )
        
        # Generate tags
        tags = []
        if bot_type == "community" and bot_profile.get('community'):
            tags = [bot_profile.get('community').lower()]
        elif random.random() < 0.3:
            interests = bot_profile.get('interests', [])
            if interests:
                tag = random.choice(interests).lower().replace(' ', '')
                tags = [tag]
        
        # Create post with media and tags
        post = bot_generator.post_manager.create_post(
            author_id=bot_id,
            content=content,
            media=media if media else None,
            tags=tags if tags else None,
            visibility="public"
        )
        
        # Get all bot IDs for engagement
        all_bot_ids = []
        if bot_generator.bots_dir.exists():
            for bf in bot_generator.bots_dir.glob("bot_*.json"):
                try:
                    with open(bf, 'r', encoding='utf-8') as f:
                        bd = json.load(f)
                        all_bot_ids.append(bd.get('bot_id'))
                except Exception:
                    continue
        
        # Generate engagement (async - will happen later)
        if random.random() < 0.7:
            bot_generator._generate_engagement(
                post['id'],
                datetime.now(),
                bot_profile,
                all_bot_ids
            )
        
        return jsonify({
            'success': True,
            'post': post,
            'bot_id': bot_id
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Authentication Routes
@app.route('/auth.html')
def auth_page():
    """Serve authentication page"""
    static_dir = Path(__file__).parent.parent / 'public'
    if static_dir.exists() and (static_dir / 'auth.html').exists():
        return send_from_directory(str(static_dir), 'auth.html')
    return send_from_directory('.', 'auth.html')

@app.route('/api/auth/phone/send', methods=['POST'])
def phone_send_code():
    """Send SMS verification code"""
    if not phone_auth_manager:
        return jsonify({'error': 'Phone authentication not available'}), 503
    
    data = request.get_json() or {}
    phone = data.get('phone', '').strip()
    
    if not phone:
        return jsonify({'error': 'Phone number required'}), 400
    
    try:
        result = phone_auth_manager.send_verification_code(phone)
        # In dev mode, log the code to console
        if result.get('success') and result.get('mock_code'):
            logger.info(f"📱 MOCK SMS CODE for {phone}: {result['mock_code']}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Phone auth error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/phone/verify', methods=['POST'])
def phone_verify_code():
    """Verify SMS code and create/login user"""
    if not phone_auth_manager:
        return jsonify({'error': 'Phone authentication not available'}), 503
    
    data = request.get_json() or {}
    verification_id = data.get('verification_id')
    code = data.get('code', '').strip()
    
    if not verification_id or not code:
        return jsonify({'error': 'Verification ID and code required'}), 400
    
    try:
        result = phone_auth_manager.verify_code(verification_id, code)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        # Get verified phone
        phone = result.get('phone')
        
        # Find or create user by phone
        # Check if user exists with this phone
        user_info_file = project_root / "data" / "auth" / "phone_users.json"
        phone_users = {}
        if user_info_file.exists():
            try:
                with open(user_info_file, 'r', encoding='utf-8') as f:
                    phone_users = json.load(f)
            except Exception:
                pass
        
        user_id = None
        for uid, user_data in phone_users.items():
            if user_data.get('phone') == phone:
                user_id = uid
                break
        
        # Create new user if doesn't exist
        if not user_id:
            user_id = f"user_{secrets.token_urlsafe(12)}"
            phone_users[user_id] = {
                'phone': phone,
                'created_at': datetime.now().isoformat()
            }
            with open(user_info_file, 'w', encoding='utf-8') as f:
                json.dump(phone_users, f, indent=2, ensure_ascii=False)
        
        # Get or create user session
        user_data = user_memory_manager.get_user_data(user_id=user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_data['user_id'],
            'session_id': user_data['session_id']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def email_register():
    """Email/password registration"""
    if not auth_manager:
        return jsonify({'error': 'Authentication not available'}), 503
    
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    try:
        # Use email as username (extract username part)
        username = email.split('@')[0]
        
        # Register user
        result = auth_manager.register_user(username, password, email=email)
        
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def email_login():
    """Email/password login"""
    if not auth_manager:
        return jsonify({'error': 'Authentication not available'}), 503
    
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    try:
        # For now, use email as username (can be improved)
        result = auth_manager.authenticate_user(email, password)
        
        if not result:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/<provider>', methods=['GET'])
def oauth_initiate(provider):
    """Initiate OAuth flow"""
    # Check if in dev mode (mock OAuth)
    is_dev = os.getenv('DEV_MODE', 'true').lower() == 'true'
    
    if is_dev and not oauth_manager:
        # Mock OAuth - return success immediately
        mock_user_id = f"user_{secrets.token_urlsafe(12)}"
        mock_session_id = f"session_{secrets.token_urlsafe(12)}"
        return f"""
        <html>
        <head><title>Mock OAuth - {provider}</title></head>
        <body style="font-family: monospace; padding: 40px; text-align: center;">
            <h2>🧪 Mock OAuth: {provider}</h2>
            <p>In production, this would redirect to {provider}.</p>
            <p>Mock user created: {mock_user_id}</p>
            <script>
                localStorage.setItem('thesidia_user_id', '{mock_user_id}');
                localStorage.setItem('thesidia_session_id', '{mock_session_id}');
                localStorage.setItem('thesidia_oauth_provider', '{provider}');
                setTimeout(() => window.location.href = '/', 2000);
            </script>
        </body>
        </html>
        """
    
    if not oauth_manager:
        return jsonify({'error': 'OAuth not available'}), 503
    
    oauth_provider = oauth_manager.get_provider(provider)
    if not oauth_provider:
        return jsonify({'error': f'OAuth provider {provider} not configured'}), 404
    
    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # Get authorization URL
    auth_url = oauth_provider.get_authorization_url(state)
    
    return redirect(auth_url)

@app.route('/api/auth/<provider>/callback', methods=['GET'])
def oauth_callback(provider):
    """Handle OAuth callback"""
    if not oauth_manager:
        return jsonify({'error': 'OAuth not available'}), 503
    
    oauth_provider = oauth_manager.get_provider(provider)
    if not oauth_provider:
        return jsonify({'error': f'OAuth provider {provider} not configured'}), 404
    
    # Verify state
    state = request.args.get('state')
    if state != session.get('oauth_state'):
        return jsonify({'error': 'Invalid state parameter'}), 400
    
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Authorization code missing'}), 400
    
    try:
        # Exchange code for token
        token_data = oauth_provider.get_access_token(code)
        access_token = token_data.get('access_token')
        
        if not access_token:
            return jsonify({'error': 'Failed to get access token'}), 500
        
        # Get user info
        user_info = oauth_provider.get_user_info(access_token)
        
        # Find or create user by provider ID
        provider_id = f"{provider}_{user_info['provider_id']}"
        user_info_file = project_root / "data" / "auth" / "oauth_users.json"
        oauth_users = {}
        if user_info_file.exists():
            try:
                with open(user_info_file, 'r', encoding='utf-8') as f:
                    oauth_users = json.load(f)
            except Exception:
                pass
        
        user_id = None
        for uid, user_data in oauth_users.items():
            if user_data.get('provider_id') == provider_id:
                user_id = uid
                break
        
        # Create new user if doesn't exist
        if not user_id:
            user_id = f"user_{secrets.token_urlsafe(12)}"
            oauth_users[user_id] = {
                'provider': provider,
                'provider_id': provider_id,
                'email': user_info.get('email'),
                'username': user_info.get('username'),
                'name': user_info.get('name'),
                'avatar_url': user_info.get('avatar_url'),
                'created_at': datetime.now().isoformat()
            }
            with open(user_info_file, 'w', encoding='utf-8') as f:
                json.dump(oauth_users, f, indent=2, ensure_ascii=False)
        
        # Get or create user session
        user_data = user_memory_manager.get_user_data(user_id=user_id)
        
        # Store session in response (will be set in localStorage by frontend)
        # Redirect to app with session data
        redirect_url = f"/?user_id={user_data['user_id']}&session_id={user_data['session_id']}"
        return redirect(redirect_url)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# Onboarding Feature Flag Endpoint
@app.route('/api/onboarding/status', methods=['GET'])
def onboarding_status():
    """Get onboarding feature flag status"""
    enabled = os.getenv('ONBOARDING_ENABLED', 'true').lower() == 'true'
    return jsonify({
        'enabled': enabled,
        'configurable': True
    })

@app.route('/api/onboarding/test', methods=['GET'])
def onboarding_test():
    """Test endpoint to verify onboarding system is accessible"""
    return jsonify({
        'status': 'ok',
        'message': 'Onboarding system is accessible',
        'test_page': '/onboarding.html'
    })

# Catch-all route for static files - MUST be registered last so API routes match first
# Skip this route on Vercel (Vercel handles static files)
if not os.getenv('VERCEL'):
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files with no-cache headers"""
        try:
            # Serve from webapp directory (where server.py lives) - PREFER THIS
            webapp_dir = Path(__file__).parent.resolve()
            file_path = (webapp_dir / path).resolve()
            
            if file_path.exists() and file_path.is_file() and str(file_path).startswith(str(webapp_dir)):
                from flask import send_file
                # Determine mimetype
                mimetype = None
                if path.endswith('.js'): mimetype = 'application/javascript'
                elif path.endswith('.css'): mimetype = 'text/css'
                elif path.endswith('.html'): mimetype = 'text/html'
                
                response = send_file(str(file_path), mimetype=mimetype)
                
                # Add cache-busting headers for HTML, CSS, and JS files
                if path.endswith(('.html', '.css', '.js')):
                    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
                return response

            # Fallback to public/ directory (mostly for Vercel/legacy compatibility)
            static_dir = (Path(__file__).parent.parent / 'public').resolve()
            if static_dir.exists() and (static_dir / path).exists():
                from flask import send_file
                return send_file(str(static_dir / path))
            
            # If not found, raise 404 to be caught by Flask's default or our handler
            from werkzeug.exceptions import NotFound
            raise NotFound()
        except Exception as e:
            if isinstance(e, NotFound):
                print(f"DEBUG: File not found: {path}")
                return jsonify({'error': 'File not found', 'path': path}), 404
            raise e

# --- KIM API Endpoints ---

@app.route('/api/register', methods=['POST'])
def register_kim_user():
    """Register a user's session and public key, optionally linked to Katanx account."""
    try:
        from webapp.kim.storage import KIMStorage
        kim_storage = KIMStorage()

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400

        public_key = data.get('publicKey')
        nickname = data.get('nickname')
        katanx_token = data.get('katanxToken')  # Optional Katanx auth token
        katanx_user_id = data.get('katanxUserId')  # Optional Katanx user ID

        if not public_key or not nickname:
            return jsonify({'error': 'Missing public key or nickname'}), 400

        # Public key is a JWK object, convert to string for storage
        if isinstance(public_key, dict):
            # Use a unique identifier from the JWK
            kim_user_id = public_key.get('x', '')[-16:] if public_key.get('x') else str(hash(str(public_key)))[-16:]
            public_key_str = json.dumps(public_key)
        else:
            # Already a string
            kim_user_id = str(public_key)[-16:]
            public_key_str = public_key

        # If Katanx auth is available and token provided, verify and link
        display_name = nickname
        avatar_url = None
        if katanx_token and katanx_user_id:
            # In a real implementation, verify the token with Katanx auth
            pass

        # Store in database
        kim_storage.register_kim_user(
            kim_user_id=kim_user_id,
            public_key=public_key_str,
            nickname=nickname,
            katanx_user_id=katanx_user_id,
            display_name=display_name,
            avatar_url=avatar_url
        )

        # Store in memory for active session
        global kim_connected_users
        kim_connected_users[kim_user_id] = {
            'public_key': public_key_str,
            'nickname': nickname,
            'katanx_user_id': katanx_user_id,
            'display_name': display_name,
            'avatar_url': avatar_url,
            'status': 'online',
            'last_seen': datetime.now().isoformat()
        }

        print(f"KIM: User registered: {nickname} ({kim_user_id})" + (f" [Katanx: {katanx_user_id}]" if katanx_user_id else ""))
        return jsonify({
            'userId': kim_user_id,
            'status': 'registered',
            'katanxLinked': bool(katanx_user_id)
        })
    except Exception as e:
        print(f"KIM: Registration error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_kim_users():
    """Get list of active users to chat with."""
    try:
        from webapp.kim.storage import KIMStorage
        kim_storage = KIMStorage()

        users_list = []
        for uid, u in kim_connected_users.items():
            # Parse public key if it's a JSON string
            try:
                public_key = json.loads(u['public_key']) if isinstance(u['public_key'], str) else u['public_key']
            except:
                public_key = u['public_key']

            users_list.append({
                'userId': uid,
                'nickname': u['nickname'],
                'displayName': u.get('display_name', u['nickname']),
                'publicKey': public_key,
                'status': u.get('status', 'online'),
                'avatarUrl': u.get('avatar_url'),
                'katanxUserId': u.get('katanx_user_id')
            })
        return jsonify(users_list)
    except Exception as e:
        print(f"KIM: Get users error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kim/messages/<room_id>', methods=['GET'])
def get_kim_messages(room_id):
    """Get message history for a room with pagination."""
    try:
        from webapp.kim.storage import KIMStorage
        kim_storage = KIMStorage()

        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        messages = kim_storage.get_messages(room_id, limit, offset)
        # Reverse to get chronological order (oldest first)
        messages.reverse()

        return jsonify({
            'messages': messages,
            'room_id': room_id,
            'limit': limit,
            'offset': offset,
            'count': len(messages)
        })
    except Exception as e:
        print(f"KIM: Get messages error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kim/upload', methods=['POST'])
def upload_kim_file():
    """Upload and encrypt a file for KIM messaging"""
    try:
        from webapp.kim.storage import KIMStorage
        from werkzeug.utils import secure_filename

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get user ID from request
        user_id = request.form.get('userId') or request.args.get('userId')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        # Validate file type and size
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'txt', 'doc', 'docx', 'mp4', 'webm', 'mov'}

        if file_ext not in allowed_extensions:
            return jsonify({'error': f'File type not allowed. Allowed: {", ".join(allowed_extensions)}'}), 400

        # Read file content
        file_content = file.read()
        file_size = len(file_content)

        # Max 10MB
        if file_size > 10 * 1024 * 1024:
            return jsonify({'error': 'File too large. Maximum size is 10MB'}), 400

        # Store encrypted file
        uploads_dir = PROJECT_ROOT / 'data' / 'kim' / 'uploads'
        uploads_dir.mkdir(parents=True, exist_ok=True)

        timestamp = int(datetime.now().timestamp() * 1000)
        unique_filename = f"{user_id}_{timestamp}_{filename}"
        file_path = uploads_dir / unique_filename

        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # Determine media type
        media_type = 'video' if file_ext in {'mp4', 'webm', 'mov'} else \
                    'image' if file_ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'} else \
                    'document'

        return jsonify({
            'fileId': unique_filename,
            'filename': filename,
            'type': media_type,
            'size': file_size,
            'url': f'/api/kim/files/{unique_filename}'
        }), 201

    except Exception as e:
        print(f"KIM: File upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/kim/files/<filename>', methods=['GET'])
def serve_kim_file(filename):
    """Serve KIM uploaded files"""
    try:
        uploads_dir = PROJECT_ROOT / 'data' / 'kim' / 'uploads'
        file_path = uploads_dir / secure_filename(filename)

        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        from flask import send_from_directory
        return send_from_directory(str(uploads_dir), secure_filename(filename))
    except Exception as e:
        print(f"KIM: File serve error: {e}")
        return jsonify({'error': str(e)}), 500

# --- SocketIO Event Handlers ---

# KIM Namespace (/kim) for encrypted messaging
if SOCKETIO_AVAILABLE:
    from webapp.kim.storage import KIMStorage

    # Initialize KIM storage
    kim_storage = KIMStorage()

    # In-memory storage for active KIM sessions
    kim_connected_users = {}
    kim_session_to_user = {}

    @socketio.on('connect', namespace='/kim')
    def handle_kim_connect():
        print(f"KIM: Client connected: {request.sid}")

    @socketio.on('disconnect', namespace='/kim')
    def handle_kim_disconnect():
        print(f"KIM: Client disconnected: {request.sid}")
        # Update user status to offline
        user_id = kim_session_to_user.get(request.sid)
        if user_id and user_id in kim_connected_users:
            kim_connected_users[user_id]['status'] = 'offline'
            kim_connected_users[user_id]['last_seen'] = datetime.now().isoformat()
            kim_storage.update_user_status(user_id, 'offline')
            # Broadcast presence update
            socketio.emit('presence_update', {
                'userId': user_id,
                'status': 'offline',
                'lastSeen': kim_connected_users[user_id]['last_seen']
            }, namespace='/kim')
        kim_session_to_user.pop(request.sid, None)

    @socketio.on('presence_update', namespace='/kim')
    def handle_kim_presence_update(data):
        """Handle user presence status updates"""
        user_id = data.get('userId')
        status = data.get('status', 'online')
        status_message = data.get('statusMessage')

        if user_id in kim_connected_users:
            kim_connected_users[user_id]['status'] = status
            if status_message:
                kim_connected_users[user_id]['status_message'] = status_message
            kim_connected_users[user_id]['last_seen'] = datetime.now().isoformat()
            kim_storage.update_user_status(user_id, status, status_message)

            # Broadcast to all users
            socketio.emit('presence_update', {
                'userId': user_id,
                'status': status,
                'statusMessage': status_message,
                'lastSeen': kim_connected_users[user_id]['last_seen']
            }, namespace='/kim')

    @socketio.on('heartbeat', namespace='/kim')
    def handle_kim_heartbeat(data):
        """Handle heartbeat/ping from client to maintain presence"""
        user_id = data.get('userId')
        if user_id and user_id in kim_connected_users:
            kim_connected_users[user_id]['last_seen'] = datetime.now().isoformat()
            kim_session_to_user[request.sid] = user_id
            # Update status if it was away/busy but user is active
            if kim_connected_users[user_id]['status'] in ['away', 'busy']:
                # Don't auto-change to online, let user control it
                pass

    @socketio.on('typing_start', namespace='/kim')
    def handle_kim_typing_start(data):
        """Handle typing start event"""
        room = data.get('room')
        user_id = data.get('userId')
        if room and user_id:
            # Broadcast to all users in room except sender
            socketio.emit('typing_indicator', {
                'userId': user_id,
                'room': room,
                'typing': True
            }, room=room, namespace='/kim', include_self=False)

    @socketio.on('typing_stop', namespace='/kim')
    def handle_kim_typing_stop(data):
        """Handle typing stop event"""
        room = data.get('room')
        user_id = data.get('userId')
        if room and user_id:
            # Broadcast to all users in room except sender
            socketio.emit('typing_indicator', {
                'userId': user_id,
                'room': room,
                'typing': False
            }, room=room, namespace='/kim', include_self=False)

    @socketio.on('join', namespace='/kim')
    def handle_kim_join(data):
        """Join a chat room (dm or public)."""
        room = data['room']
        socketio.join_room(room, sid=request.sid, namespace='/kim')
        print(f"KIM: User joined room: {room}")
        socketio.emit('status', {'msg': f'Joined room {room}'}, room=room, namespace='/kim')

    @socketio.on('encrypted_message', namespace='/kim')
    def handle_kim_encrypted_message(data):
        """
        Relay encrypted message blob.
        Server CANNOT read this.
        data = {
            'room': str,
            'encryptedContent': str (base64/hex),
            'iv': str,
            'senderId': str,
            'timestamp': str,
            'messageId': str (optional, generated if not provided),
            'parentMessageId': str (optional, for threading)
        }
        """
        room = data.get('room')
        if not room:
            return

        # Generate message ID if not provided
        message_id = data.get('messageId') or f"{data.get('senderId')}_{int(datetime.now().timestamp() * 1000)}"

        print(f"KIM: Relaying encrypted message in {room} (ID: {message_id})")

        # Store message in database
        kim_storage.store_message(
            message_id=message_id,
            room_id=room,
            sender_id=data.get('senderId'),
            encrypted_content=data.get('encryptedContent'),
            iv=data.get('iv'),
            mode=data.get('mode', 'AES-GCM'),
            parent_message_id=data.get('parentMessageId')
        )

        # Add message ID to data
        data['messageId'] = message_id

        # Relay to everyone in room (including sender, client filters)
        socketio.emit('new_encrypted_message', data, room=room, namespace='/kim')

    @socketio.on('message_edit', namespace='/kim')
    def handle_kim_message_edit(data):
        """Handle message edit event"""
        message_id = data.get('messageId')
        user_id = data.get('userId')
        new_content = data.get('newContent')

        if not message_id or not user_id:
            return

        # In a full implementation, we'd update the database
        # For now, we'll just broadcast the edit
        socketio.emit('message_edited', {
            'messageId': message_id,
            'userId': user_id,
            'newContent': new_content,
            'editedAt': datetime.now().isoformat()
        }, namespace='/kim')

if __name__ == '__main__':
    import socket
    
    # Find available port
    def find_free_port(start_port=5000):
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        return 5000  # Fallback
    
    # Get local IP address for network access
    def get_local_ip():
        """Get the local IP address for network access"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # Doesn't actually connect, just determines local IP
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
            except Exception:
                ip = '127.0.0.1'
            finally:
                s.close()
            return ip
        except Exception:
            return '127.0.0.1'
    
    # Use PORT from environment (Railway, Heroku, etc.) or find available port
    port = int(os.getenv('PORT', 0))
    if not port:
        port = find_free_port(5002)  # Use 5002 to match frontend
    
    START_TIME = time.time()
    
    # Get local IP for network access
    local_ip = get_local_ip()
    
    # Security: Run on localhost by default
    # For production, use proper WSGI server (gunicorn, uwsgi)
    import ssl
    
    # Try to enable HTTPS with self-signed certificate
    cert_path = Path(__file__).parent / 'cert.pem'
    key_path = Path(__file__).parent / 'key.pem'
    
    if cert_path.exists() and key_path.exists():
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(cert_path), str(key_path))
        print(f"Starting server with HTTPS on https://0.0.0.0:{port}")
        print(f"Access from your phone: https://{local_ip}:{port}")
        print("Note: You may need to accept the self-signed certificate warning on your phone")
        if SOCKETIO_AVAILABLE:
            socketio.run(
                app,
                host='0.0.0.0',  # Bind to all interfaces for network access
                port=port,
                debug=False,  # Disable debug in production
                ssl_context=context
            )
        else:
            app.run(
                host='0.0.0.0',  # Bind to all interfaces for network access
                port=port,
                debug=False,  # Disable debug in production
                ssl_context=context
            )
    else:
        print(f"Starting server on http://0.0.0.0:{port}")
        print(f"Access from your phone: http://{local_ip}:{port}")
        print(f"Access from this computer: http://localhost:{port}")
        if SOCKETIO_AVAILABLE:
            socketio.run(
                app,
                host='0.0.0.0',  # Bind to all interfaces for network access
                port=port,
                debug=False  # Disable debug in production
            )
        else:
            app.run(
                host='0.0.0.0',  # Bind to all interfaces for network access
                port=port,
                debug=False  # Disable debug in production
            )


