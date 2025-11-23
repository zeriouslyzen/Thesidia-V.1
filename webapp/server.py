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
    """Serve main HTML file"""
    return send_from_directory('.', 'index.html')

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
    """Serve static files"""
    return send_from_directory('.', path)

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
    message = data.get('message', '').strip()
    show_thinking = data.get('show_thinking', False)
    stream = data.get('stream', True)  # Default to streaming
    
    # Security: Validate input
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    if len(message) > 10000:
        return jsonify({'error': 'Message too long'}), 400
    
    # Security: Basic sanitization
    message = message.replace('<', '').replace('>', '')
    
    # If streaming requested, use SSE
    if stream:
        return Response(
            stream_with_context(_stream_thesidia_response(message, show_thinking)),
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
        
        # Process with Thesidia
        print(f"🔪 SERVER: Processing message: {message[:100]}...")
        print(f"🔪 SERVER: Thesidia instance: {thesidia}")
        print(f"🔪 SERVER: Has _handle_deep_research: {hasattr(thesidia, '_handle_deep_research')}")
        response = thesidia.process(message)
        print(f"🔪 SERVER: Response length: {len(response)}, has transmission: {'::TRANSMISSION:' in response}")
        
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

def _stream_thesidia_response(message, show_thinking):
    """Stream Thesidia response with progress updates"""
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
        
        # Phase 2: Classification
        is_directive = thesidia._is_directive(message)
        is_deep_research = thesidia._is_deep_research_request(message)
        
        yield send_event('progress', {
            'phase': 'classification',
            'message': f'Classifying: {"Deep Research" if is_deep_research else "Directive" if is_directive else "Question"}',
            'progress': 10
        })
        
        # Phase 3: Web search (if needed) - Show real progress
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
            # Note: Actual search happens in process(), we just show progress
        
        # Phase 4: Synthesis - Show real progress
        yield send_event('progress', {
            'phase': 'synthesis',
            'message': 'Synthesizing information and patterns...',
            'progress': 30
        })
        yield send_event('thinking', {
            'step': 'synthesis',
            'message': 'Cross-referencing sources and identifying patterns',
            'progress': 30
        })
        
        # Phase 5: Processing - Show real progress
        yield send_event('progress', {
            'phase': 'processing',
            'message': 'Generating response...',
            'progress': 40
        })
        yield send_event('thinking', {
            'step': 'generation',
            'message': 'Arranging evidence for pattern recognition',
            'progress': 40
        })
        
        # Process with Thesidia - ACTUAL STREAMING from Ollama
        print(f"🔪 SERVER: Processing message: {message[:100]}...")
        
        # Try to use real streaming from Ollama
        try:
            # Build prompt
            enhanced_prompt = thesidia.get_enhanced_prompt(query=message)
            full_prompt = f"{enhanced_prompt}\n\nUser: {message}\n\nThesidia:"
            
            # Stream directly from Ollama
            yield send_event('progress', {
                'phase': 'streaming',
                'message': 'Streaming response in real-time...',
                'progress': 50
            })
            
            accumulated_response = ""
            token_count = 0
            
            # Use Ollama streaming API
            stream_response = ollama.chat(
                model=thesidia.model,
                messages=[{"role": "user", "content": full_prompt}],
                options={
                    "temperature": 0.9,
                    "num_predict": 12000
                },
                stream=True  # Enable streaming
            )
            
            for chunk in stream_response:
                if 'message' in chunk and 'content' in chunk['message']:
                    token = chunk['message']['content']
                    accumulated_response += token
                    token_count += 1
                    
                    # Stream token immediately
                    yield send_event('chunk', {
                        'text': token,
                        'progress': 50 + min(40, (token_count / 12000) * 40),
                        'thinking': f'Generated {token_count} tokens...' if token_count % 50 == 0 else None
                    })
                    
                    # Show thinking every 50 tokens
                    if show_thinking and token_count % 50 == 0:
                        yield send_event('thinking', {
                            'step': 'generating',
                            'message': f'Generated {token_count} tokens, continuing...',
                            'progress': token_count
                        })
            
            response = accumulated_response.strip()
            
        except Exception as e:
            # Fallback: Use regular process (non-streaming)
            print(f"⚠️ Streaming failed, using fallback: {e}")
            response = thesidia.process(message)
            
            # Stream response in chunks as fallback
            yield send_event('progress', {
                'phase': 'streaming',
                'message': 'Streaming response...',
                'progress': 90
            })
            
            chunk_size = 50
            for i in range(0, len(response), chunk_size):
                chunk = response[i:i + chunk_size]
                yield send_event('chunk', {
                    'text': chunk,
                    'progress': 90 + (i / len(response)) * 10
                })
        
        # Phase 7: Complete
        yield send_event('complete', {
            'phase': 'complete',
            'message': 'Response complete',
            'progress': 100,
            'total_length': len(response)
        })
        
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
    print(f"Starting server on http://127.0.0.1:{port}")
    app.run(
        host='127.0.0.1',
        port=port,
        debug=False  # Disable debug in production
    )

