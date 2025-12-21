from functools import wraps
from flask import request, jsonify
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def require_user(f):
    """
    Decorator to ensure user_id or session_id is provided in the request.
    Extracts IDs from JSON body or query parameters and injects them into the function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = None
        session_id = None
        
        # 1. Try to extract from JSON body
        if request.is_json:
            try:
                data = request.get_json() or {}
                user_id = data.get('user_id')
                session_id = data.get('session_id')
            except Exception:
                pass
        
        # 2. Fallback to query parameters
        if not user_id:
            user_id = request.args.get('user_id')
        if not session_id:
            session_id = request.args.get('session_id')
            
        # 3. Validation
        if not user_id and not session_id:
            return jsonify({"error": "user_id or session_id required"}), 400
            
        # 4. Inject into function arguments
        kwargs['user_id'] = user_id
        kwargs['session_id'] = session_id
        
        return f(*args, **kwargs)
    return decorated_function

def require_user_data(user_memory_manager_provider):
    """
    Decorator that also fetches user_data from the memory manager.
    Takes a provider function that returns the user_memory_manager instance.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract IDs first
            user_id = None
            session_id = None
            
            if request.is_json:
                try:
                    data = request.get_json() or {}
                    user_id = data.get('user_id')
                    session_id = data.get('session_id')
                except Exception:
                    pass
            
            if not user_id:
                user_id = request.args.get('user_id')
            if not session_id:
                session_id = request.args.get('session_id')
                
            if not user_id and not session_id:
                return jsonify({"error": "user_id or session_id required"}), 400
            
            # Fetch user data
            try:
                user_memory_manager = user_memory_manager_provider()
                if not user_memory_manager:
                    return jsonify({"error": "User memory manager unavailable"}), 503
                    
                user_data = user_memory_manager.get_user_data(user_id=user_id, session_id=session_id)
                kwargs['user_data'] = user_data
                kwargs['user_id'] = user_data.get('user_id')
                kwargs['session_id'] = user_data.get('session_id')
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": f"Failed to fetch user data: {str(e)}"}), 500
                
        return decorated_function
    return decorator
