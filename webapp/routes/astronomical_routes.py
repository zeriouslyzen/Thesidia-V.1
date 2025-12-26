"""
Astronomical Routes Blueprint - Temporal Pattern API

Handles astronomical and calendar pattern endpoints:
- /api/astronomical/current - Current positions
- /api/astronomical/correlations - Historical correlations
- /api/astronomical/patterns - Recurring patterns
- /api/astronomical/predict - Future predictions
"""

from flask import jsonify, request
from datetime import datetime
from webapp.routes import astronomical_bp


# Lazy reference to astronomical engine (will be set by main server)
astronomical_engine = None


def set_astronomical_engine(engine):
    """Set the astronomical engine reference from main server"""
    global astronomical_engine
    astronomical_engine = engine


@astronomical_bp.route('/current', methods=['GET'])
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
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@astronomical_bp.route('/correlations', methods=['GET'])
def astronomical_correlations():
    """Find historical events with similar calendar positions"""
    try:
        if not astronomical_engine:
            return jsonify({'error': 'Astronomical engine not available'}), 503
            
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


@astronomical_bp.route('/patterns', methods=['GET'])
def astronomical_patterns_api():
    """Get detected recurring temporal patterns"""
    try:
        if not astronomical_engine:
            return jsonify({'error': 'Astronomical engine not available'}), 503
            
        patterns = astronomical_engine.detect_recurring_patterns()
        return jsonify({
            'patterns': patterns,
            'count': len(patterns),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in astronomical_patterns: {e}")
        return jsonify({'error': str(e)}), 500


@astronomical_bp.route('/predict', methods=['GET'])
def astronomical_predict():
    """Predict future calendar positions"""
    try:
        if not astronomical_engine:
            return jsonify({'error': 'Astronomical engine not available'}), 503
            
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
