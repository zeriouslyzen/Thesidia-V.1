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
from pathlib import Path

# Ensure os is available for environment variables

# Add project root and src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context, redirect, session
from werkzeug.utils import secure_filename
from flask_cors import CORS
# Force fresh import - clear any cached modules
import sys
if 'thesidia_hybrid_adaptive' in sys.modules:
    del sys.modules['thesidia_hybrid_adaptive']
if 'knowledge_base' in sys.modules:
    del sys.modules['knowledge_base']

# Lazy imports - only import when needed to avoid Vercel deployment issues
# These will be imported inside functions that need them
ThesidiaHybridAdaptive = None
KnowledgeBase = None
UserMemoryManager = None
UserInterestTracker = None
AstronomicalPatternEngine = None

def _lazy_import_modules():
    """Lazy import modules - only when actually needed"""
    global ThesidiaHybridAdaptive, KnowledgeBase, UserMemoryManager, UserInterestTracker, AstronomicalPatternEngine
    
    if ThesidiaHybridAdaptive is None:
        try:
            from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
            from knowledge_base import KnowledgeBase
            from memory.user_memory_manager import UserMemoryManager
            from user_interest_tracker import UserInterestTracker
            from astronomical_patterns import AstronomicalPatternEngine
        except ImportError as e:
            # For Vercel: modules that require ollama will fail to import
            print(f"Warning: Could not import Thesidia modules: {e}")
            print("This is expected on Vercel - Ollama is not available")
            return False
    return True
from datetime import datetime, timedelta
import importlib

# Ollama import - optional for Vercel deployment
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

# For Vercel: serve from public/ if it exists, otherwise current directory
try:
    static_dir = Path(__file__).parent.parent / 'public'
    if static_dir.exists():
        app = Flask(__name__, static_folder=str(static_dir), static_url_path='')
    else:
        app = Flask(__name__, static_folder='.', static_url_path='')
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
        'message': str(e) if os.getenv('VERCEL') else 'An error occurred',
        'type': type(e).__name__
    }), 500

# Initialize Thesidia
thesidia = None
thesidia_ready = False
ollama_status = False

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
    except:
        return False

def init_thesidia():
    """Initialize Thesidia - FORCE FRESH INSTANCE"""
    global thesidia, thesidia_ready, ollama_status, knowledge_base, user_memory_manager, interest_tracker, astronomical_engine
    
    # Try to import modules first
    if not _lazy_import_modules():
        ollama_status = False
        thesidia_ready = False
        return False
    
    # Check if Ollama is available first
    if not OLLAMA_AVAILABLE:
        ollama_status = False
        return False
    
    # Initialize knowledge base and other managers
    if knowledge_base is None:
        knowledge_base = KnowledgeBase(base_dir=project_root)
    if user_memory_manager is None:
        user_memory_manager = UserMemoryManager(base_dir=project_root)
    if interest_tracker is None:
        interest_tracker = UserInterestTracker(base_dir=project_root)
    if astronomical_engine is None:
        astronomical_engine = AstronomicalPatternEngine(data_dir=project_root / 'data')
    
    # Force reload module to ensure latest code
    import thesidia_hybrid_adaptive
    importlib.reload(thesidia_hybrid_adaptive)
    ThesidiaHybridAdaptive = thesidia_hybrid_adaptive.ThesidiaHybridAdaptive
    
    ollama_status = check_ollama()
    if not ollama_status:
        return False
    
    try:
        # Create fresh instance with reloaded class
        thesidia = ThesidiaHybridAdaptive(model="clean-mistral:latest")  # Changed from oracle-agent (has hardcoded Oracle identity)
        thesidia.load_state()
        thesidia_ready = True
        
        # Verify the instance has the updated method
        if hasattr(thesidia, '_handle_deep_research'):
            import inspect
            method_source = ''.join(inspect.getsourcelines(thesidia._handle_deep_research)[0])
            has_nuclear = 'NUCLEAR OPTION' in method_source
            print(f"🔪 SERVER INIT: Thesidia instance created. Has NUCLEAR stripping: {has_nuclear}")
        
        return True
    except Exception as e:
        print(f"Error initializing Thesidia: {e}")
        import traceback
        traceback.print_exc()
        thesidia_ready = False
        return False

# Try to initialize (will fail gracefully on Vercel)
try:
    init_thesidia()
except Exception as e:
    print(f"Warning: Could not initialize Thesidia: {e}")
    print("This is expected on Vercel - Ollama is not available")
    thesidia_ready = False
    ollama_status = False

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

@app.route('/')
def index():
    """Serve main HTML file - index.html is the main entry point"""
    try:
        # Check public/ directory first (for Vercel), then current directory
        static_dir = Path(__file__).parent.parent / 'public'
        if static_dir.exists():
            index_path = static_dir / 'index.html'
            if index_path.exists():
                return send_from_directory(str(static_dir), 'index.html')
            contexts_path = static_dir / 'contexts.html'
            if contexts_path.exists():
                return send_from_directory(str(static_dir), 'contexts.html')
        # Fallback to current directory
        if Path('index.html').exists():
            return send_from_directory('.', 'index.html')
        if Path('contexts.html').exists():
            return send_from_directory('.', 'contexts.html')
    except Exception as e:
        # If file serving fails, return a simple HTML response
        import traceback
        print(f"Error serving index file: {e}")
        traceback.print_exc()
        # Return a minimal HTML page
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Thesidia</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>Thesidia</h1>
    <p>Application is loading...</p>
    <script>window.location.href = '/stream.html';</script>
</body>
</html>""", 200, {'Content-Type': 'text/html'}
    
    # Final fallback if nothing works
    return """<!DOCTYPE html>
<html>
<head>
    <title>Thesidia</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>Thesidia</h1>
    <p>Please navigate to <a href="/stream.html">/stream.html</a></p>
</body>
</html>""", 200, {'Content-Type': 'text/html'}

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

@app.route('/api/status', methods=['GET'])
def status():
    """Get system status"""
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
            except:
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

@app.route('/api/thesidia', methods=['POST'])
def thesidia_api():
    """Main API endpoint for Thesidia interactions - with streaming support"""
    global thesidia_ready, ollama_status
    
    # Check status
    ollama_status = check_ollama()
    if not ollama_status:
        return jsonify({
            'error': 'Ollama is not running',
            'ollama_status': False
        }), 503
    
    if not thesidia_ready:
        if not init_thesidia():
            return jsonify({
                'error': 'Thesidia is not ready',
                'thesidia_ready': False
            }), 503
    
    # Security: Rate limiting
    client_ip = request.remote_addr
    if not check_rate_limit(client_ip):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    # Security: Validate request
    if not request.is_json:
        return jsonify({'error': 'Invalid content type'}), 400
    
    # Security: Input sanitization
    from webapp.middleware.security import sanitize_request_data
    data = sanitize_request_data(request.get_json())
    raw_message = data.get('message', '').strip()
    
    # CRITICAL FIX #1: Log RAW user input BEFORE any processing
    print(f"🔍 RAW USER INPUT: '{raw_message}'", flush=True)
    
    show_thinking = data.get('show_thinking', False)
    stream = data.get('stream', True)  # Default to streaming
    format_mode = data.get('format', 'natural')  # 'natural' or 'structured' - from UI selection
    research_depth = data.get('research_depth', 2)  # 1=Quick, 2=Deep, 3=Forensic - from UI slider
    
    # Get user session info
    user_id = data.get('user_id')
    session_id = data.get('session_id')
    
    # Security: Validate input
    if not raw_message:
        return jsonify({'error': 'Message is required'}), 400
    
    if len(raw_message) > 10000:
        return jsonify({'error': 'Message too long'}), 400
    
    # Normalize query and detect forensic routing (using shared utilities)
    from src.support.query_utils import normalize_query, detect_forensic_routing
    
    normalized_message = normalize_query(raw_message)
    needs_forensic = detect_forensic_routing(raw_message, comprehensive=False)
    
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
                                                         format_mode=format_mode, research_depth=research_depth)),
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
        response = thesidia.process(message, user_id=user_id, session_id=session_id, 
                                   format_mode=format_mode, research_depth=research_depth)
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
        
        return jsonify({
            'response': response,
            'thinking_steps': thinking_steps if show_thinking else [],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error processing request: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

def _stream_thesidia_response(message, show_thinking, user_id=None, session_id=None, format_mode='natural', research_depth=2):
    """Stream Thesidia response with progress updates - USES FULL THESIDIA PROCESS"""
    global thesidia
    
    def send_event(event_type, data):
        """Send SSE event"""
        event_data = json.dumps(data)
        return f"event: {event_type}\ndata: {event_data}\n\n"
    
    try:
        # Phase 1: Input received
        yield send_event('progress', {
            'phase': 'input_received',
            'message': 'Processing your query...',
            'progress': 5
        })
        
        # CRITICAL: Use thesidia.process() to get full routing, forensic analysis, deep research
        # This ensures all the logic we built actually runs
        
        # Normalize and detect routing BEFORE processing (using shared utilities)
        from src.support.query_utils import normalize_query, detect_forensic_routing
        
        print(f"🔍 RAW USER INPUT (streaming): '{message}'", flush=True)
        normalized_message = normalize_query(message)
        needs_forensic = detect_forensic_routing(message, comprehensive=False)
        print(f"🔍 NORMALIZED (streaming): '{normalized_message}'", flush=True)
        print(f"🔍 NEEDS FORENSIC (streaming): {needs_forensic}", flush=True)
        print(f"🔪 SERVER: Using full Thesidia process() for: {message[:100]}...", flush=True)
        
        # Check routing before processing (using normalized)
        is_gnostic = needs_forensic
        
        if is_gnostic:
            yield send_event('progress', {
                'phase': 'classification',
                'message': 'Detected forensic truth-seeking query - routing to deep research...',
                'progress': 10
            })
            yield send_event('thinking', {
                'step': 'routing',
                'message': 'Query requires forensic analysis (health/finance/law/religion)',
                'progress': 10
            })
        
        # Phase 2: Web search (if needed)
        if thesidia._needs_research(message) and thesidia.web_search:
            yield send_event('progress', {
                'phase': 'web_search',
                'message': 'Searching the web for sources...',
                'progress': 20
            })
            yield send_event('thinking', {
                'step': 'web_search',
                'message': 'Gathering information from multiple sources',
                'progress': 20
            })
        
        # Phase 3: Processing with Thesidia (includes routing, forensic analysis, synthesis)
        yield send_event('progress', {
            'phase': 'processing',
            'message': 'Processing with Thesidia (routing, forensic analysis, synthesis)...',
            'progress': 30
        })
        yield send_event('thinking', {
            'step': 'processing',
            'message': 'Using full Thesidia system: routing, deep research, forensic analysis',
            'progress': 30
        })
        
        # Phase 4: Prepare for streaming generation
        # We'll do research/routing first, then stream the final generation
        yield send_event('progress', {
            'phase': 'preparing',
            'message': 'Preparing response generation...',
            'progress': 40
        })
        
        # Get the full response using process() to ensure all routing/research happens
        # This is fast (research/routing), then we'll stream the final generation
        # For now, we'll use process() and then stream it, but in future we can optimize
        # by intercepting the final Ollama call
        
        # TEMPORARY: Use process() to get complete response, then stream it
        # TODO: Optimize to stream final generation directly from Ollama
        response = thesidia.process(message, user_id=user_id, session_id=session_id,
                                   format_mode=format_mode, research_depth=research_depth)
        
        # Phase 5: Stream the response token-by-token for optimal UX
        yield send_event('progress', {
            'phase': 'streaming',
            'message': 'Generating response...',
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
    try:
        if not user_memory_manager:
            # Fallback: create basic session without memory manager
            import secrets
            user_id = f"user_{secrets.token_hex(8)}"
            session_id = f"session_{secrets.token_hex(16)}"
            return jsonify({
                'user_id': user_id,
                'session_id': session_id,
                'created_at': datetime.now().isoformat()
            })
        
        if request.method == 'POST':
            # Create or get user session
            data = request.get_json() or {}
            user_id = data.get('user_id')
            session_id = data.get('session_id')
            
            user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
            # Convert Path objects to strings for JSON serialization
            if 'user_dir' in user_data and hasattr(user_data['user_dir'], '__str__'):
                user_data['user_dir'] = str(user_data['user_dir'])
            return jsonify(user_data)
        else:
            # Get session from query params
            user_id = request.args.get('user_id')
            session_id = request.args.get('session_id')
            
            user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
            # Convert Path objects to strings for JSON serialization
            if 'user_dir' in user_data and hasattr(user_data['user_dir'], '__str__'):
                user_data['user_dir'] = str(user_data['user_dir'])
            return jsonify(user_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Fallback: create basic session on error
        import secrets
        user_id = f"user_{secrets.token_hex(8)}"
        session_id = f"session_{secrets.token_hex(16)}"
        return jsonify({
            'user_id': user_id,
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'error': str(e)
        })

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
    if not settings_manager:
        return jsonify({'error': 'Settings manager not available'}), 503
    
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        # Get user data to find user_id
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        settings = settings_manager.get_settings(user_id)
        return jsonify(settings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/account', methods=['POST'])
def update_account_settings():
    """Update account settings"""
    if not settings_manager:
        return jsonify({'error': 'Settings manager not available'}), 503
    
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
def update_privacy_settings():
    """Update privacy settings"""
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
def update_notification_settings():
    """Update notification settings"""
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
def update_content_settings():
    """Update content settings"""
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
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
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
def delete_post(post_id):
    """Delete a post"""
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
def get_feed():
    """Get user feed"""
    if not feed_manager or not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    feed_type = request.args.get('type', 'chronological')  # chronological, quality, personalized
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        # Get feed
        posts = feed_manager.get_feed(user_id, feed_type, limit, offset)
        
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
        return jsonify({'error': str(e)}), 500

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
        
        # Generate mock cuts
        author_ids = [f"user_{i}" for i in range(10)]
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

@app.route('/api/sections/circles', methods=['GET'])
def get_circles_section():
    """Get circles forum threads"""
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    filter_type = request.args.get('filter', 'all')
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
        
        # Generate mock threads
        author_ids = [f"user_{i}" for i in range(10)]
        threads = generate_threads(count=limit-1, author_ids=author_ids, seed=456)  # -1 to make room for welcome thread
        
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
            'circle': 'General',
            'tags': ['welcome', 'guide', 'getting-started'],
            'author': {
                'user_id': 'user_0',
                'username': 'admin',
                'display_name': 'Admin',
                'avatar_url': ''
            }
        }
        threads.insert(0, welcome_thread)
        
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
        
        # Get available categories from CIRCLE_TOPICS
        from data.mock.mock_circles import CIRCLE_TOPICS
        categories = []
        for topic in CIRCLE_TOPICS:
            # Count threads in this category
            topic_threads = [t for t in threads if t.get('circle') == topic]
            categories.append({
                'id': topic,
                'name': topic.title(),
                'slug': topic,
                'thread_count': len(topic_threads),
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
                'circle': 'General',
                'tags': ['welcome', 'guide', 'getting-started']
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
                random.seed(hash(thread_id) % 1000)
                topic = random.choice(CIRCLE_TOPICS)
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
                    'circle': topic,
                    'tags': [topic]
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
            comments = _generate_mock_comments(thread_id, limit)
            
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
        
        # Random parent (some top-level, some replies)
        parent_id = None
        if i > 2 and random.random() > 0.4:
            parent_id = comments[random.randint(0, min(i-1, 5))]['id']
        
        upvotes = random.randint(0, 100)
        downvotes = random.randint(0, 20)
        
        comment = {
            'id': comment_id,
            'thread_id': thread_id,
            'parent_id': parent_id,
            'author': author,
            'content': f"This is a mock comment #{i+1}. It contains some thoughtful discussion about the topic.",
            'created_at': (datetime.now() - timedelta(hours=random.randint(0, 48))).isoformat(),
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
        vote_file.parent.mkdir(parents=True, exist_ok=True)
        with open(vote_file, 'w') as f:
            json.dump(votes, f, indent=2)
        
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
        vote_file.parent.mkdir(parents=True, exist_ok=True)
        
        if vote_file.exists():
            with open(vote_file, 'r') as f:
                data = json.load(f)
        else:
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
            vote_file.parent.mkdir(parents=True, exist_ok=True)
            with open(vote_file, 'w') as f:
                json.dump(data, f, indent=2)
        
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
        return jsonify(result)
    except Exception as e:
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
    
    # Use PORT from environment (Railway, Heroku, etc.) or find available port
    port = int(os.getenv('PORT', 0))
    if not port:
        port = find_free_port(5002)  # Use 5002 to match frontend
    
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
        print(f"Access from your phone: https://192.168.1.130:{port}")
        print("Note: You may need to accept the self-signed certificate warning on your phone")
        app.run(
            host='0.0.0.0',  # Bind to all interfaces for network access
            port=port,
            debug=False,  # Disable debug in production
            ssl_context=context
        )
    else:
        print(f"Starting server on http://0.0.0.0:{port}")
        print(f"Access from your phone: http://192.168.1.130:{port}")
        app.run(
            host='0.0.0.0',  # Bind to all interfaces for network access
            port=port,
            debug=False  # Disable debug in production
        )

# Catch-all route for static files - MUST be registered last so API routes match first
# Skip this route on Vercel (Vercel handles static files)
if not os.getenv('VERCEL'):
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files with no-cache headers"""
        try:
            # Check public/ directory first (for Vercel), then current directory
            static_dir = Path(__file__).parent.parent / 'public'
            if static_dir.exists() and (static_dir / path).exists():
                response = send_from_directory(str(static_dir), path)
            else:
                response = send_from_directory('.', path)
            # Add cache-busting headers for HTML, CSS, and JS files
            if path.endswith(('.html', '.css', '.js')):
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            return response
        except Exception as e:
            return jsonify({'error': 'File not found', 'path': path}), 404

