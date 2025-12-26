"""
Settings Routes Blueprint - User Preferences API

Handles user settings endpoints:
- /api/settings - Get all settings
- /api/settings/account - Account settings
- /api/settings/security - Security/password
- /api/settings/privacy - Privacy settings
- /api/settings/notifications - Notification preferences
- /api/settings/content - Content preferences
"""

from flask import jsonify, request
from webapp.routes import settings_bp


# Lazy references (set by main server)
settings_manager = None
user_memory_manager = None
auth_manager = None


def set_settings_dependencies(settings_mgr, user_mgr, auth_mgr):
    """Set dependencies from main server"""
    global settings_manager, user_memory_manager, auth_manager
    settings_manager = settings_mgr
    user_memory_manager = user_mgr
    auth_manager = auth_mgr


# Default mock settings for demo mode
MOCK_SETTINGS = {
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


@settings_bp.route('', methods=['GET'])
def get_settings():
    """Get all user settings"""
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')
    
    # Return mock settings in demo mode
    if not settings_manager:
        return jsonify(MOCK_SETTINGS), 200
    
    try:
        settings = settings_manager.get_settings(user_id=user_id, session_id=session_id)
        return jsonify(settings or MOCK_SETTINGS), 200
    except Exception as e:
        return jsonify(MOCK_SETTINGS), 200  # Fallback to mock


@settings_bp.route('/account', methods=['POST'])
def update_account_settings():
    """Update account settings"""
    if not settings_manager:
        return jsonify({'error': 'Settings manager not available'}), 503
    
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
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


@settings_bp.route('/security', methods=['POST'])
def update_security_settings():
    """Update security settings (password change)"""
    if not settings_manager:
        return jsonify({'error': 'Settings manager not available'}), 503
        
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        # Handle password change if provided
        if data.get('current_password') and data.get('new_password') and auth_manager:
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
        
        success, error = settings_manager.update_settings_section(user_id, 'security', security_data)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'success': True, 'message': 'Security settings updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/privacy', methods=['POST'])
def update_privacy_settings():
    """Update privacy settings"""
    if not settings_manager:
        return jsonify({'error': 'Settings manager not available'}), 503
        
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
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


@settings_bp.route('/notifications', methods=['POST'])
def update_notification_settings():
    """Update notification settings"""
    if not settings_manager:
        return jsonify({'error': 'Settings manager not available'}), 503
        
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
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


@settings_bp.route('/content', methods=['POST'])
def update_content_settings():
    """Update content settings"""
    if not settings_manager:
        return jsonify({'error': 'Settings manager not available'}), 503
        
    data = request.get_json() or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
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
