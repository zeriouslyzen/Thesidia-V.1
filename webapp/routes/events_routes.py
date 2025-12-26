"""
Events Routes Blueprint - Algorithmic Growth Engine

Handles event tracking API for user interactions:
- POST /api/events - Ingest user interaction events
- GET /api/events/stats - Get event tracking statistics
"""

import json
from flask import jsonify, request
from datetime import datetime
from pathlib import Path
from webapp.routes import events_bp


# Event store path
PROJECT_ROOT = Path(__file__).parent.parent.parent
EVENT_STORE_PATH = PROJECT_ROOT / 'data' / 'events.json'

# Valid action types for events
VALID_ACTION_TYPES = {
    'view', 'click', 'like', 'unlike', 'share', 'save', 'bookmark',
    'comment', 'reply', 'scroll', 'dwell', 'hover', 'expand',
    'play', 'pause', 'complete', 'skip', 'hide', 'report'
}


@events_bp.route('', methods=['POST'])
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
        
        # Validate and process events
        processed = []
        for event in events:
            # Basic validation
            if not event.get('content_id') or not event.get('action_type'):
                continue
            if event.get('action_type') not in VALID_ACTION_TYPES:
                continue
            
            # Add server timestamp
            event['server_timestamp'] = datetime.now().isoformat()
            processed.append(event)
        
        # Store events (try Supabase first, fall back to local JSON)
        stored_count = 0
        try:
            from webapp.conversations.supabase_storage import SupabaseConversationStore
            supabase_store = SupabaseConversationStore()
            if supabase_store.client:
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
                EVENT_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
                
                # Load existing events
                existing = []
                if EVENT_STORE_PATH.exists():
                    with open(EVENT_STORE_PATH, 'r') as f:
                        existing = json.load(f)
                
                # Append new events (keep last 10000)
                existing.extend(processed)
                existing = existing[-10000:]
                
                # Save
                with open(EVENT_STORE_PATH, 'w') as f:
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


@events_bp.route('/stats', methods=['GET'])
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
        if EVENT_STORE_PATH.exists():
            with open(EVENT_STORE_PATH, 'r') as f:
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
