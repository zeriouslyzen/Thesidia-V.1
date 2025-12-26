"""
AI Routes Blueprint - Thesidia Core API

Handles Thesidia AI interaction endpoints. This module requires special handling
due to tight coupling with the Thesidia instance and streaming responses.

Endpoints to migrate:
- /api/thesidia - Main AI interaction (streaming SSE)
- /api/status - System status
- /api/conversations/* - Conversation persistence
- /api/eval/* - Evaluation endpoints

Note: Full migration pending due to:
- Global Thesidia instance
- SSE streaming responses
- Complex request queuing
- Rate limiting integration
"""

from flask import jsonify, request
from webapp.routes import ai_bp


# Lazy references (set by main server)
thesidia = None
thesidia_ready = False
conversation_store = None


def set_ai_dependencies(thesidia_instance, ready_status, conv_store):
    """Set dependencies from main server"""
    global thesidia, thesidia_ready, conversation_store
    thesidia = thesidia_instance
    thesidia_ready = ready_status
    conversation_store = conv_store


# Placeholder routes - full implementation remains in server.py for now
# The Thesidia API requires streaming and complex state management

@ai_bp.route('/ai/health', methods=['GET'])
def ai_health():
    """Health check for AI API module"""
    return jsonify({
        'status': 'ok',
        'module': 'ai',
        'thesidia_ready': thesidia_ready,
        'thesidia_available': thesidia is not None,
        'conversation_store': conversation_store is not None,
        'note': 'Full routes remain in server.py pending incremental migration'
    })
