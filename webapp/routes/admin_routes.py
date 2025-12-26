"""
Admin Routes Blueprint - Command Center API

Handles admin dashboard and system control endpoints:
- /api/metrics - System metrics
- /api/admin/user - User profiler
- /api/neural/* - Neural/MLX model control
- Admin pages
"""

import random
import time
import psutil
from flask import jsonify, request, send_from_directory
from datetime import datetime
from webapp.routes import admin_bp
from logger_setup import server_logger


# Lazy references (set by main server)
mlx_inference = None
user_memory_manager = None
START_TIME = time.time()


def set_admin_dependencies(mlx, user_manager, start_time):
    """Set dependencies from main server"""
    global mlx_inference, user_memory_manager, START_TIME
    mlx_inference = mlx
    user_memory_manager = user_manager
    START_TIME = start_time


@admin_bp.route('/metrics', methods=['GET'])
def metrics():
    """System metrics for Admin Dashboard"""
    try:
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        
        # Count active sessions
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
                'inference_engine': 'MLX' if mlx_inference and mlx_inference.is_available() else 'Ollama'
            }
        })
    except Exception as e:
        server_logger.error(f"Metrics error: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/user', methods=['GET'])
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
    if user_memory_manager and query in user_memory_manager.user_cache:
        data = user_memory_manager.get_user_data(user_id=query)
        # Decorate with stats for UI demo
        data['risk_score'] = random.randint(0, 100)
        data['sentiment'] = random.choice(['Positive', 'Neutral', 'Negative', 'Agitated'])
        data['connections'] = random.randint(0, 500)
        data['device'] = 'Unknown Device'
        return jsonify(data)
    
    return jsonify({'error': 'User not found'}), 404


# Neural Control Center API
@admin_bp.route('/neural/status', methods=['GET'])
def neural_status():
    """Returns real-time MLX neural engine status"""
    try:
        mem = psutil.virtual_memory()
        
        status = {
            'active_model': mlx_inference.current_model if mlx_inference else 'None',
            'loaded_models': list(mlx_inference.loaded_models.keys()) if mlx_inference else [],
            'available_models': mlx_inference.list_models() if mlx_inference else [],
            'mlx_available': mlx_inference.is_available() if mlx_inference else False,
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


@admin_bp.route('/neural/load', methods=['POST'])
def neural_load_model():
    """Load a specific MLX model"""
    if not mlx_inference:
        return jsonify({'error': 'MLX inference not available'}), 503
        
    data = request.get_json()
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({'error': 'model parameter required'}), 400
    
    success = mlx_inference.load_model(model_name)
    if success:
        return jsonify({'status': 'loaded', 'model': model_name})
    else:
        return jsonify({'error': 'Failed to load model'}), 500


@admin_bp.route('/neural/unload', methods=['POST'])
def neural_unload_model():
    """Unload a specific MLX model to free memory"""
    if not mlx_inference:
        return jsonify({'error': 'MLX inference not available'}), 503
        
    data = request.get_json()
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({'error': 'model parameter required'}), 400
    
    success = mlx_inference.unload_model(model_name)
    if success:
        return jsonify({'status': 'unloaded', 'model': model_name})
    else:
        return jsonify({'error': 'Model not loaded'}), 404


# Admin pages (these need url_prefix removed to work at root)
# Note: These should be moved to pages_bp in production
