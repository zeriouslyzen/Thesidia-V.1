#!/usr/bin/env python3
"""
KIM (Killer Instant Messaging) - Standalone Server
Encrypted DM & Chat Room Side-Project
"""

import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import secrets
import sys
import base64
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import KIM storage
from webapp.kim.storage import KIMStorage

# Try to import Katanx auth components (optional, for integration)
try:
    from webapp.middleware.user_auth import require_user_data
    from src.memory.user_manager import UserManager
    KATANX_AUTH_AVAILABLE = True
except ImportError:
    KATANX_AUTH_AVAILABLE = False
    print("Warning: Katanx auth components not available, using standalone mode")

# Initialize Flask
app = Flask(__name__, static_folder=None)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize storage
storage = KIMStorage()


# In-memory storage for active sessions
# users[kim_user_id] = { 'public_key': str, 'nickname': str, 'katanx_user_id': str, 'sid': str, 'status': str }
connected_users = {}
# Track SocketIO session IDs to user IDs
session_to_user = {} 

# --- KIM-Specific Routes ---

@app.route('/')
def index():
    return send_from_directory('.', 'kim.html')

@app.route('/kim-sidebar.html')
def kim_sidebar():
    return send_from_directory('.', 'kim-sidebar.html')

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/app.js')
def send_app_js():
    return send_from_directory('.', 'app.js')

@app.route('/navigation.js')
def send_navigation_js():
    return send_from_directory('.', 'navigation.js')

@app.route('/styles.css')
def send_styles_css():
    return send_from_directory('.', 'styles.css'), 200, {'Content-Type': 'text/css'}

@app.route('/manifest.json')
def send_manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/service-worker.js')
def send_service_worker():
    return send_from_directory('.', 'service-worker.js'), 200, {'Content-Type': 'application/javascript'}

# --- API Endpoints for Key Exchange ---

@app.route('/api/register', methods=['POST'])
def register_user():
    """Register a user's session and public key, optionally linked to Katanx account."""
    try:
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
        if KATANX_AUTH_AVAILABLE and katanx_token:
            try:
                # In a real implementation, verify the token with Katanx auth
                # For now, we'll accept the katanx_user_id if provided
                if katanx_user_id:
                    # Could fetch user profile from Katanx here
                    pass
            except Exception as e:
                print(f"Katanx auth verification failed: {e}")
                # Continue with standalone registration
        
        # Store in database
        storage.register_kim_user(
            kim_user_id=kim_user_id,
            public_key=public_key_str,
            nickname=nickname,
            katanx_user_id=katanx_user_id,
            display_name=display_name,
            avatar_url=avatar_url
        )
        
        # Store in memory for active session
        connected_users[kim_user_id] = {
            'public_key': public_key_str,
            'nickname': nickname,
            'katanx_user_id': katanx_user_id,
            'display_name': display_name,
            'avatar_url': avatar_url,
            'status': 'online',
            'last_seen': datetime.now().isoformat()
        }
        
        print(f"User registered: {nickname} ({kim_user_id})" + (f" [Katanx: {katanx_user_id}]" if katanx_user_id else ""))
        return jsonify({
            'userId': kim_user_id,
            'status': 'registered',
            'katanxLinked': bool(katanx_user_id)
        })
    except Exception as e:
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get list of active users to chat with."""
    try:
        users_list = []
        for uid, u in connected_users.items():
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
        print(f"Get users error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kim/messages/<room_id>', methods=['GET'])
def get_messages(room_id):
    """Get message history for a room with pagination."""
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        messages = storage.get_messages(room_id, limit, offset)
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
        print(f"Get messages error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kim/messages/<message_id>/read', methods=['POST'])
def mark_message_read(message_id):
    """Mark a message as read"""
    try:
        data = request.get_json() or {}
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        storage.mark_message_read(message_id, user_id)
        
        # Broadcast read receipt
        socketio.emit('read_receipt', {
            'messageId': message_id,
            'userId': user_id,
            'readAt': datetime.now().isoformat()
        }, broadcast=True)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Mark read error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kim/messages/<message_id>/read', methods=['GET'])
def get_read_receipts(message_id):
    """Get read receipts for a message"""
    try:
        receipts = storage.get_read_receipts(message_id)
        return jsonify({'receipts': receipts})
    except Exception as e:
        print(f"Get read receipts error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kim/messages/<message_id>/reactions', methods=['GET'])
def get_message_reactions(message_id):
    """Get reactions for a message"""
    try:
        reactions = storage.get_reactions(message_id)
        return jsonify({'reactions': reactions})
    except Exception as e:
        print(f"Get reactions error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kim/messages/<message_id>/reactions', methods=['POST'])
def add_message_reaction(message_id):
    """Add a reaction to a message"""
    try:
        data = request.get_json() or {}
        user_id = data.get('userId')
        reaction_type = data.get('reactionType')
        
        if not user_id or not reaction_type:
            return jsonify({'error': 'User ID and reaction type required'}), 400
        
        storage.add_reaction(message_id, user_id, reaction_type)
        
        # Broadcast reaction
        socketio.emit('reaction_added', {
            'messageId': message_id,
            'userId': user_id,
            'reactionType': reaction_type
        }, broadcast=True)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Add reaction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kim/upload', methods=['POST'])
def upload_file():
    """Upload and encrypt a file for KIM messaging"""
    try:
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
        
        # Store encrypted file (in production, encrypt client-side before upload)
        # For now, we'll store the file and return metadata
        # The actual encryption should happen client-side before upload
        uploads_dir = project_root / 'data' / 'kim' / 'uploads'
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(datetime.now().timestamp() * 1000)
        unique_filename = f"{user_id}_{timestamp}_{filename}"
        file_path = uploads_dir / unique_filename
        
        # Save file (in production, this would be encrypted)
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
        print(f"File upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/kim/files/<filename>', methods=['GET'])
def serve_kim_file(filename):
    """Serve KIM uploaded files"""
    try:
        uploads_dir = project_root / 'data' / 'kim' / 'uploads'
        file_path = uploads_dir / secure_filename(filename)
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # In production, decrypt file before serving
        # For now, serve directly
        return send_from_directory(str(uploads_dir), secure_filename(filename))
    except Exception as e:
        print(f"File serve error: {e}")
        return jsonify({'error': str(e)}), 500

# --- SocketIO Events ---

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    # Update user status to offline
    user_id = session_to_user.get(request.sid)
    if user_id and user_id in connected_users:
        connected_users[user_id]['status'] = 'offline'
        connected_users[user_id]['last_seen'] = datetime.now().isoformat()
        storage.update_user_status(user_id, 'offline')
        # Broadcast presence update
        emit('presence_update', {
            'userId': user_id,
            'status': 'offline',
            'lastSeen': connected_users[user_id]['last_seen']
        }, broadcast=True)
    session_to_user.pop(request.sid, None)

@socketio.on('presence_update')
def handle_presence_update(data):
    """Handle user presence status updates"""
    user_id = data.get('userId')
    status = data.get('status', 'online')
    status_message = data.get('statusMessage')
    
    if user_id in connected_users:
        connected_users[user_id]['status'] = status
        if status_message:
            connected_users[user_id]['status_message'] = status_message
        connected_users[user_id]['last_seen'] = datetime.now().isoformat()
        storage.update_user_status(user_id, status, status_message)
        
        # Broadcast to all users
        emit('presence_update', {
            'userId': user_id,
            'status': status,
            'statusMessage': status_message,
            'lastSeen': connected_users[user_id]['last_seen']
        }, broadcast=True)

@socketio.on('heartbeat')
def handle_heartbeat(data):
    """Handle heartbeat/ping from client to maintain presence"""
    user_id = data.get('userId')
    if user_id and user_id in connected_users:
        connected_users[user_id]['last_seen'] = datetime.now().isoformat()
        session_to_user[request.sid] = user_id
        # Update status if it was away/busy but user is active
        if connected_users[user_id]['status'] in ['away', 'busy']:
            # Don't auto-change to online, let user control it
            pass

@socketio.on('typing_start')
def handle_typing_start(data):
    """Handle typing start event"""
    room = data.get('room')
    user_id = data.get('userId')
    if room and user_id:
        # Broadcast to all users in room except sender
        emit('typing_indicator', {
            'userId': user_id,
            'room': room,
            'typing': True
        }, room=room, include_self=False)

@socketio.on('typing_stop')
def handle_typing_stop(data):
    """Handle typing stop event"""
    room = data.get('room')
    user_id = data.get('userId')
    if room and user_id:
        # Broadcast to all users in room except sender
        emit('typing_indicator', {
            'userId': user_id,
            'room': room,
            'typing': False
        }, room=room, include_self=False)

@socketio.on('join')
def on_join(data):
    """Join a chat room (dm or public)."""
    room = data['room']
    join_room(room)
    print(f"User joined room: {room}")
    emit('status', {'msg': f'Joined room {room}'}, room=room)

@socketio.on('encrypted_message')
def handle_encrypted_message(data):
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
    
    print(f"Relaying encrypted message in {room} (ID: {message_id})")
    
    # Store message in database
    storage.store_message(
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
    emit('new_encrypted_message', data, room=room)

@socketio.on('message_edit')
def handle_message_edit(data):
    """Handle message edit event"""
    message_id = data.get('messageId')
    user_id = data.get('userId')
    new_content = data.get('newContent')
    
    if not message_id or not user_id:
        return
    
    # In a full implementation, we'd update the database
    # For now, we'll just broadcast the edit
    emit('message_edited', {
        'messageId': message_id,
        'userId': user_id,
        'newContent': new_content,
        'editedAt': datetime.now().isoformat()
    }, broadcast=True)


if __name__ == '__main__':
    print("KIM Secure Server starting on port 5001...")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
