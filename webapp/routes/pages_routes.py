"""
Page Routes Blueprint - Static Page Serving

Handles all static HTML page routes:
- Landing page (/)
- Home (/home)
- Stream, Profile, Atlas, Contexts, Reactor, Archive
- SEO files (robots.txt, sitemap.xml)
"""

from flask import send_from_directory
from pathlib import Path
from webapp.routes import pages_bp


# Get webapp directory for serving files
WEBAPP_DIR = Path(__file__).parent.parent
PUBLIC_DIR = WEBAPP_DIR.parent / 'public'


def _serve_file(filename, fallback_dir='.'):
    """Helper to serve files from public or webapp directory"""
    if PUBLIC_DIR.exists() and (PUBLIC_DIR / filename).exists():
        return send_from_directory(str(PUBLIC_DIR), filename)
    return send_from_directory(fallback_dir, filename)


@pages_bp.route('/index.html')
def index_direct():
    """Direct index.html access"""
    return send_from_directory('.', 'index.html')


@pages_bp.route('/')
def index():
    """Serve landing page - landing.html is the main entry point for katanx.com"""
    try:
        if PUBLIC_DIR.exists() and (PUBLIC_DIR / 'landing.html').exists():
            return send_from_directory(str(PUBLIC_DIR), 'landing.html')
        if Path('landing.html').exists():
            return send_from_directory('.', 'landing.html')
    except Exception as e:
        print(f"Error in index route: {e}")
    
    # Fallback redirect
    return """<!DOCTYPE html>
<html>
<head>
    <title>katanx</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script>window.location.href = '/landing.html';</script>
</head>
<body>
    <h1>katanx</h1>
    <p>Application is loading...</p>
    <p>If you are not redirected, please <a href="/landing.html">click here</a>.</p>
</body>
</html>""", 200, {'Content-Type': 'text/html'}


@pages_bp.route('/home')
def home():
    """Serve main application - app.html is the home page"""
    try:
        if PUBLIC_DIR.exists():
            for filename in ['app.html', 'contexts.html']:
                if (PUBLIC_DIR / filename).exists():
                    return send_from_directory(str(PUBLIC_DIR), filename)
        for filename in ['app.html', 'contexts.html']:
            if Path(filename).exists():
                return send_from_directory('.', filename)
    except Exception as e:
        print(f"Error in home route: {e}")
    
    # Fallback redirect
    return """<!DOCTYPE html>
<html>
<head>
    <title>Thesidia</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script>window.location.href = '/stream.html';</script>
</head>
<body>
    <h1>Thesidia</h1>
    <p>Application is loading...</p>
    <p>If you are not redirected, please <a href="/stream.html">click here</a>.</p>
</body>
</html>""", 200, {'Content-Type': 'text/html'}


# SEO files
@pages_bp.route('/robots.txt')
def robots():
    """Serve robots.txt for SEO"""
    return _serve_file('robots.txt')


@pages_bp.route('/sitemap.xml')
def sitemap():
    """Serve sitemap.xml for SEO"""
    return _serve_file('sitemap.xml')


# Clean URL Routes (no .html extension)
@pages_bp.route('/stream')
def stream_page():
    """Main chat/stream interface"""
    return send_from_directory('.', 'stream.html')


@pages_bp.route('/profile')
def profile_page():
    """User profile page"""
    return send_from_directory('.', 'profile.html')


@pages_bp.route('/atlas')
def atlas_page():
    """Atlas explorer"""
    return send_from_directory('.', 'atlas.html')


@pages_bp.route('/contexts')
def contexts_page():
    """Context management"""
    return send_from_directory('.', 'contexts.html')


@pages_bp.route('/reactor')
def reactor_page():
    """Reactor interface"""
    return send_from_directory('.', 'reactor.html')


@pages_bp.route('/archive')
def archive_page():
    """Archive browser"""
    return send_from_directory('.', 'archive.html')


@pages_bp.route('/application')
def application_page():
    """Application dashboard"""
    return send_from_directory('.', 'application.html')


@pages_bp.route('/knowledge-base')
@pages_bp.route('/knowledge')
def knowledge_base_page_clean():
    """Knowledge base (clean URL)"""
    return send_from_directory('.', 'knowledge_base.html')


@pages_bp.route('/metrics')
@pages_bp.route('/metrics-dashboard')
def metrics_page():
    """Metrics dashboard (clean URL)"""
    return send_from_directory('.', 'metrics_dashboard.html')
