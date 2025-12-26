"""
Social Routes Blueprint - Social Media API

Handles social media feature endpoints. This is the largest route module
and requires careful migration due to dependencies on:
- post_manager
- feed_manager
- social_graph
- interaction_manager
- moderation_manager
- quality_scorer

Endpoints to migrate (~40):
- Posts: create, get, delete, like, validate, reference
- Feed: get_feed, stream_section, kx_cuts, home, circles
- Interactions: follow, comment, vote, award
- Profile: get_user_profile, block, mute
- Forums: threads, comments, replies

Note: Full migration pending due to tight state coupling.
"""

from flask import jsonify, request
from webapp.routes import social_bp


# Lazy references (set by main server)
post_manager = None
feed_manager = None
social_graph = None
interaction_manager = None


def set_social_dependencies(post_mgr, feed_mgr, graph, interaction_mgr):
    """Set dependencies from main server"""
    global post_manager, feed_manager, social_graph, interaction_manager
    post_manager = post_mgr
    feed_manager = feed_mgr
    social_graph = graph
    interaction_manager = interaction_mgr


# Placeholder routes - full implementation remains in server.py for now
# These will be migrated incrementally as dependencies are decoupled

@social_bp.route('/social/health', methods=['GET'])
def social_health():
    """Health check for social API module"""
    return jsonify({
        'status': 'ok',
        'module': 'social',
        'post_manager': post_manager is not None,
        'feed_manager': feed_manager is not None,
        'social_graph': social_graph is not None,
        'note': 'Full routes remain in server.py pending incremental migration'
    })
