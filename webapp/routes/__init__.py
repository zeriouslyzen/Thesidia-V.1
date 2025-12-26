"""
Webapp Routes Package - Modular Flask Blueprints

This package contains modular route blueprints split from the monolithic server.py.
Each blueprint handles a specific domain of functionality:

- pages: Static page serving (landing, stream, profile, etc.)
- market: Market data API (crypto, stocks)
- events: Algorithmic Growth Engine event tracking
- ai: Thesidia AI API endpoints
- social: Social media features (posts, feed, interactions)
- settings: User settings and preferences
- admin: Admin dashboard and control panel
- astronomical: Astronomical pattern API

Usage:
    from webapp.routes import register_blueprints
    register_blueprints(app)
"""

from flask import Blueprint

# Create blueprints
pages_bp = Blueprint('pages', __name__)
market_bp = Blueprint('market', __name__, url_prefix='/api/market')
events_bp = Blueprint('events', __name__, url_prefix='/api/events')
ai_bp = Blueprint('ai', __name__, url_prefix='/api')
social_bp = Blueprint('social', __name__, url_prefix='/api')
settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')
admin_bp = Blueprint('admin', __name__, url_prefix='/api')
astronomical_bp = Blueprint('astronomical', __name__, url_prefix='/api/astronomical')

# Import route modules to register routes with blueprints
# Note: These imports must come AFTER blueprint creation
from webapp.routes import pages_routes  # noqa: F401, E402
from webapp.routes import market_routes  # noqa: F401, E402
from webapp.routes import events_routes  # noqa: F401, E402
from webapp.routes import astronomical_routes  # noqa: F401, E402
from webapp.routes import admin_routes  # noqa: F401, E402
from webapp.routes import settings_routes  # noqa: F401, E402


def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(pages_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(astronomical_bp)


