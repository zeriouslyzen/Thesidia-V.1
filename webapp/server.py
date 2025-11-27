#!/usr/bin/env python3
"""
Thesidia Web App Backend Server
Security-first API for Thesidia interactions
"""

import sys
import os
from pathlib import Path

# Ensure os is available for environment variables

# Add project root and src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
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
import json
from datetime import datetime
import importlib

# Ollama import - optional for Vercel deployment
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

# For Vercel: serve from public/ if it exists, otherwise current directory
static_dir = Path(__file__).parent.parent / 'public'
if static_dir.exists():
    app = Flask(__name__, static_folder=str(static_dir), static_url_path='')
else:
    app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for security

# Security headers middleware
from webapp.config.security import is_security_headers_enabled, is_https_required

@app.after_request
def add_security_headers(response):
    """Add security headers to responses"""
    if is_security_headers_enabled():
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        if is_https_required():
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy - allow unsafe-inline for now (until we add nonces to all scripts)
        # TODO: Add nonces to all inline scripts in HTML files
        csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'"
        response.headers['Content-Security-Policy'] = csp
    
    return response

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
    return send_from_directory('.', 'contexts.html')

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

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files with no-cache headers"""
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

@app.route('/api/status', methods=['GET'])
def status():
    """Get system status"""
    global thesidia_ready, ollama_status
    
    # Recheck status
    ollama_status = check_ollama()
    if ollama_status and not thesidia_ready:
        init_thesidia()
    
    features = {
        'deep_research': thesidia.deep_research_engine is not None if thesidia else False,
        'web_search': thesidia.web_search is not None if thesidia else False,
        'model_routing': thesidia.capabilities.model_router is not None if thesidia else False,
    }
    
    return jsonify({
        'ollama_status': ollama_status,
        'thesidia_ready': thesidia_ready,
        'model': thesidia.model if thesidia else None,
        'features': features,
        'timestamp': datetime.now().isoformat()
    })

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
    try:
        from webapp.middleware.security import sanitize_request_data
        request_data = request.get_json()
        if request_data is None:
            return jsonify({'error': 'Invalid JSON in request body'}), 400
        data = sanitize_request_data(request_data)
        raw_message = data.get('message', '').strip()
    except Exception as e:
        print(f"Error sanitizing request data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Invalid request data'}), 400
    
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
    
    # CRITICAL FIX #2: Normalize query BEFORE passing to ThesidiaHybridAdaptive
    # This ensures typo fixes and routing detection work correctly
    def normalize_query(text):
        """Normalize query with typo fixes"""
        text_normalized = text.lower()
        typo_fixes = {
            'gneneis': 'genesis', 'genisis': 'genesis', 'genises': 'genesis', 'genensis': 'genesis',
            'decrpted': 'decrypted', 'decrpt': 'decrypt', 'dycrpted': 'decrypted', 'dycrypt': 'decrypt',
            'bible': 'bible', 'bibel': 'bible'
        }
        for typo, correct in typo_fixes.items():
            text_normalized = text_normalized.replace(typo, correct)
        return text_normalized
    
    def detect_forensic_routing(text):
        """Detect if query needs forensic analysis BEFORE passing to model"""
        normalized = normalize_query(text)
        needs_forensic = any(term in normalized for term in [
            "genesis", "bible", "scripture", "torah", "quran", "veda", "ancient", "religion", "abrahamic", "origins", "canon", "canonization",
            "decode", "decoded", "decrypt", "decrypted", "dycrpted", "dycrypt", "expose", "hidden",
            "what are", "what are X really", "really about", "characters", "what's really", "true origins", "real origins"
        ])
        return needs_forensic
    
    # Normalize the message
    normalized_message = normalize_query(raw_message)
    needs_forensic = detect_forensic_routing(raw_message)
    
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
        
        # CRITICAL FIX: Normalize and detect routing BEFORE processing
        def normalize_query(text):
            """Normalize query with typo fixes"""
            text_normalized = text.lower()
            typo_fixes = {
                'gneneis': 'genesis', 'genisis': 'genesis', 'genises': 'genesis', 'genensis': 'genesis',
                'decrpted': 'decrypted', 'decrpt': 'decrypt', 'dycrpted': 'decrypted', 'dycrypt': 'decrypt',
                'bible': 'bible', 'bibel': 'bible'
            }
            for typo, correct in typo_fixes.items():
                text_normalized = text_normalized.replace(typo, correct)
            return text_normalized
        
        def detect_forensic_routing(text):
            """Detect if query needs forensic analysis"""
            normalized = normalize_query(text)
            needs_forensic = any(term in normalized for term in [
                "genesis", "bible", "scripture", "torah", "quran", "veda", "ancient", "religion", "abrahamic", "origins", "canon", "canonization",
                "decode", "decoded", "decrypt", "decrypted", "dycrpted", "dycrypt", "expose", "hidden",
                "what are", "what are X really", "really about", "characters", "what's really", "true origins", "real origins"
            ])
            return needs_forensic
        
        print(f"🔍 RAW USER INPUT (streaming): '{message}'", flush=True)
        normalized_message = normalize_query(message)
        needs_forensic = detect_forensic_routing(message)
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
    
    # Initialize quality scorer with Thesidia AI if available
    quality_scorer = AIQualityScorer(base_dir=project_root, thesidia=thesidia if thesidia_ready else None)
    
    # Initialize bot detector with AI
    from webapp.social.bot_detector import BotDetector
    bot_detector = BotDetector(base_dir=project_root, thesidia=thesidia if thesidia_ready else None)
    
    # Initialize moderation manager with AI-powered components
    moderation_manager = ModerationManager(
        base_dir=project_root,
        quality_scorer=quality_scorer,
        bot_detector=bot_detector
    )
    
    # Initialize AI content insights and recommendations
    content_insights = AIContentInsights(base_dir=project_root, thesidia=thesidia if thesidia_ready else None)
    ai_recommendations = AIRecommendations(base_dir=project_root, thesidia=thesidia if thesidia_ready else None)
except ImportError as e:
    print(f"Warning: Social media features not available: {e}")
    post_manager = None
    feed_manager = None
    social_graph = None
    interaction_manager = None
    moderation_manager = None
    quality_scorer = None
    content_insights = None

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get posts with optional filters"""
    if not post_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    try:
        if user_id:
            # Get posts by user
            posts = post_manager.get_posts_by_user(user_id, limit, offset)
        else:
            # Get all posts by date
            posts = post_manager.get_posts_by_date(limit, offset)
        
        # Add interactions to each post
        if interaction_manager:
            for post in posts:
                interactions = interaction_manager.get_interactions(post['id'])
                post['interactions'] = interactions
        
        return jsonify({'posts': posts, 'count': len(posts)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['POST'])
def create_post():
    """Create a new post"""
    if not post_manager or not moderation_manager or not feed_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    # Import validation utilities
    from webapp.utils.validation import (
        validate_user_id, validate_session_id, validate_post_content,
        validate_media, validate_tags, validate_visibility
    )
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    content = data.get('content', '')
    media = data.get('media', [])
    tags = data.get('tags', [])
    visibility = data.get('visibility', 'public')
    
    # Validate inputs
    if user_id:
        is_valid, error = validate_user_id(user_id)
        if not is_valid:
            return jsonify({'error': error}), 400
    
    if session_id:
        is_valid, error = validate_session_id(session_id)
        if not is_valid:
            return jsonify({'error': error}), 400
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    is_valid, error = validate_post_content(content)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    is_valid, error = validate_media(media)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    is_valid, error = validate_tags(tags)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    is_valid, error = validate_visibility(visibility)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        # Create post
        post = post_manager.create_post(
            author_id=user_id,
            content=content,
            media=media,
            tags=tags,
            visibility=visibility
        )
        
        # Moderate post (AI-powered)
        moderation_result = moderation_manager.moderate_post(post['id'])
        
        # Track user interests from post creation (AI-powered)
        if interest_tracker:
            try:
                interest_tracker.track_topic(
                    query=f"Created post: {post.get('content', '')[:200]}",
                    response=post.get('content', '')[:500]
                )
            except Exception:
                pass  # Fail silently
        
        # Invalidate feed cache
        feed_manager.invalidate_cache(user_id)
        
        return jsonify(post)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get posts with optional filters"""
    if not post_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    try:
        if user_id:
            # Get posts by user
            posts = post_manager.get_posts_by_user(user_id, limit, offset)
        else:
            # Get all posts by date
            posts = post_manager.get_posts_by_date(limit, offset)
        
        # Add interactions to each post
        if interaction_manager:
            for post in posts:
                interactions = interaction_manager.get_interactions(post['id'])
                post['interactions'] = interactions
        
        return jsonify({'posts': posts, 'count': len(posts)})
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
    
    # Import validation utilities
    from webapp.utils.validation import (
        validate_user_id, validate_session_id, validate_feed_type,
        validate_pagination
    )
    
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    feed_type = request.args.get('type', 'chronological')
    limit = request.args.get('limit', 20)
    offset = request.args.get('offset', 0)
    
    # Validate inputs
    if user_id:
        is_valid, error = validate_user_id(user_id)
        if not is_valid:
            return jsonify({'error': error}), 400
    
    if session_id:
        is_valid, error = validate_session_id(session_id)
        if not is_valid:
            return jsonify({'error': error}), 400
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    is_valid, error, limit_num, offset_num = validate_pagination(limit, offset, max_limit=100)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    is_valid, error = validate_feed_type(feed_type)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        # Get feed
        posts = feed_manager.get_feed(user_id, feed_type, limit_num, offset_num)
        
        # Add interactions to each post
        for post in posts:
            interactions = interaction_manager.get_interactions(post['id'])
            post['interactions'] = interactions
        
        return jsonify({
            'items': posts,
            'has_more': len(posts) == limit_num,
            'page': offset_num // limit_num if limit_num > 0 else 0,
            'limit': limit_num
        })
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/posts/<post_id>/like', methods=['POST'])
def like_post(post_id):
    """Like or unlike a post"""
    if not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    # Import validation utilities
    from webapp.utils.validation import (
        validate_user_id, validate_session_id, validate_post_id
    )
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    
    # Validate inputs
    is_valid, error = validate_post_id(post_id)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    if user_id:
        is_valid, error = validate_user_id(user_id)
        if not is_valid:
            return jsonify({'error': error}), 400
    
    if session_id:
        is_valid, error = validate_session_id(session_id)
        if not is_valid:
            return jsonify({'error': error}), 400
    
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
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/posts/<post_id>/comment', methods=['POST'])
def comment_post(post_id):
    """Comment on a post"""
    if not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    # Import validation utilities
    from webapp.utils.validation import (
        validate_user_id, validate_session_id, validate_post_id,
        validate_comment_content
    )
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    session_id = data.get('session_id') or request.args.get('session_id')
    content = data.get('content', '')
    
    # Validate inputs
    is_valid, error = validate_post_id(post_id)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    if user_id:
        is_valid, error = validate_user_id(user_id)
        if not is_valid:
            return jsonify({'error': error}), 400
    
    if session_id:
        is_valid, error = validate_session_id(session_id)
        if not is_valid:
            return jsonify({'error': error}), 400
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    is_valid, error = validate_comment_content(content)
    if not is_valid:
        return jsonify({'error': error}), 400
    
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

@app.route('/api/posts/<post_id>/repost', methods=['POST'])
def repost_post(post_id):
    """Repost or unrepost a post"""
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
        
        reposted = interaction_manager.repost(post_id, user_id)
        interactions = interaction_manager.get_interactions(post_id)
        
        return jsonify({
            'reposted': reposted,
            'interactions': interactions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    """Get comments for a post"""
    if not interaction_manager:
        return jsonify({'error': 'Social features not available'}), 503
    
    try:
        interactions = interaction_manager.get_interactions(post_id)
        comments = interactions.get('comments_list', [])
        
        return jsonify({
            'comments': comments,
            'count': len(comments)
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

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get AI-powered content recommendations"""
    if not ai_recommendations:
        return jsonify({'error': 'AI recommendations not available'}), 503
    
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    limit = int(request.args.get('limit', 10))
    
    if not user_id and not session_id:
        return jsonify({'error': 'user_id or session_id required'}), 400
    
    try:
        # Get user data
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recommendations
        recommended_posts = ai_recommendations.recommend_posts(user_id, limit)
        suggested_topics = ai_recommendations.suggest_content_topics(user_id)
        
        return jsonify({
            'recommended_posts': recommended_posts,
            'suggested_topics': suggested_topics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/suggest-hashtags', methods=['POST'])
def suggest_hashtags():
    """Get AI-powered hashtag suggestions for post content"""
    if not content_insights:
        return jsonify({'error': 'AI insights not available'}), 503
    
    data = request.get_json() or {}
    content = data.get('content', '')
    partial = data.get('partial', '')
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    try:
        # Create a temporary post object for suggestions
        temp_post = {'content': content, 'tags': []}
        suggestions = content_insights.suggest_related_topics(temp_post)
        
        # Filter suggestions based on partial match
        if partial:
            suggestions = [s for s in suggestions if s.lower().startswith(partial.lower())]
        
        return jsonify({'suggestions': suggestions[:5]})
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
        positions = astronomical_engine.calculate_all_calendars()
        return jsonify(positions)
    except Exception as e:
        print(f"Error in astronomical_current: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

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

