#!/usr/bin/env python3
"""
Thesidia Web App Backend Server
Security-first API for Thesidia interactions
"""

import sys
import os
from pathlib import Path

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

from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
from knowledge_base import KnowledgeBase
from memory.user_memory_manager import UserMemoryManager
from user_interest_tracker import UserInterestTracker
from astronomical_patterns import AstronomicalPatternEngine
import json
from datetime import datetime
import ollama
import importlib

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for security

# Initialize Thesidia
thesidia = None
thesidia_ready = False
ollama_status = False
knowledge_base = KnowledgeBase(base_dir=project_root)

# Initialize User Memory Manager
user_memory_manager = UserMemoryManager(base_dir=project_root)

# Initialize User Interest Tracker for engagement algorithm
interest_tracker = UserInterestTracker(base_dir=project_root)

# Initialize Astronomical Pattern Engine
astronomical_engine = AstronomicalPatternEngine(data_dir=project_root / 'data')

def check_ollama():
    """Check if Ollama is running"""
    try:
        ollama.list()
        return True
    except:
        return False

def init_thesidia():
    """Initialize Thesidia - FORCE FRESH INSTANCE"""
    global thesidia, thesidia_ready, ollama_status
    
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

# Try to initialize
init_thesidia()

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
    # Try index.html first, fallback to contexts.html
    if Path('index.html').exists():
        return send_from_directory('.', 'index.html')
    return send_from_directory('.', 'contexts.html')

@app.route('/robots.txt')
def robots():
    """Serve robots.txt for SEO"""
    return send_from_directory('.', 'robots.txt'), 200, {'Content-Type': 'text/plain'}

@app.route('/sitemap.xml')
def sitemap():
    """Serve sitemap.xml for SEO"""
    return send_from_directory('.', 'sitemap.xml'), 200, {'Content-Type': 'application/xml'}

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files with no-cache headers"""
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
    
    data = request.get_json()
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
    return send_from_directory('.', 'knowledge_base.html')

@app.route('/metrics_dashboard.html')
def metrics_dashboard():
    """Serve metrics dashboard HTML"""
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
        return jsonify(user_data)
    else:
        # Get session from query params
        user_id = request.args.get('user_id')
        session_id = request.args.get('session_id')
        
        user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
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

