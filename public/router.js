/**
 * Katanx // Client-Side Router
 * Lightweight routing for page transitions and active states
 */

class Router {
    constructor() {
        this.routes = {
            '/': 'contexts',
            '/contexts.html': 'contexts',
            '/stream.html': 'stream',
            '/atlas.html': 'atlas',
            '/reactor.html': 'reactor',
            '/application.html': 'application',
            '/archive.html': 'archive',
            '/metrics_dashboard.html': 'metrics',
            '/thread.html': 'thread'
        };
        
        // Also handle thread.html as a base route
        if (window.location.pathname === '/thread.html') {
            this.routes[window.location.pathname] = 'thread';
        }
        
        // Dynamic route patterns
        this.routePatterns = [
            { pattern: /^\/thread\/([^\/]+)$/, handler: 'thread', param: 'threadId' },
            { pattern: /^\/circles\/([^\/]+)\/([^\/]+)$/, handler: 'thread', params: ['category', 'threadId'] }
        ];
        
        this.init();
    }
    
    /**
     * Match dynamic route patterns
     */
    matchRoute(path) {
        // Check exact routes first
        if (this.routes[path]) {
            return { handler: this.routes[path], params: {} };
        }
        
        // Check pattern routes
        for (const route of this.routePatterns) {
            const match = path.match(route.pattern);
            if (match) {
                const params = {};
                if (route.param) {
                    params[route.param] = match[1];
                } else if (route.params) {
                    route.params.forEach((param, index) => {
                        params[param] = match[index + 1];
                    });
                }
                return { handler: route.handler, params };
            }
        }
        
        return null;
    }
    
    /**
     * Initialize router
     */
    init() {
        // Set active page on load
        this.setActivePage();
        
        // Handle navigation clicks
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href]');
            if (link && link.href.startsWith(window.location.origin)) {
                const href = new URL(link.href).pathname;
                if (this.routes[href]) {
                    // Update state before navigation
                    if (window.State) {
                        window.State.setCurrentPage(this.routes[href]);
                    }
                }
            }
        });
        
        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            this.setActivePage();
        });
    }
    
    /**
     * Set active page based on current URL
     */
    setActivePage() {
        const path = window.location.pathname;
        const match = this.matchRoute(path);
        
        if (match) {
            // Store route params for use by page components
            window.currentRouteParams = match.params;
            
            // Update state
            if (window.State) {
                window.State.setCurrentPage(match.handler);
            }
            
            // Update navigation active states
            this.updateNavActiveStates(match.handler);
            
            // Initialize thread page if needed
            if (match.handler === 'thread' && window.ThreadDetailPage) {
                const threadId = match.params.threadId || match.params.id;
                if (threadId) {
                    window.ThreadDetailPage.loadThread(threadId);
                }
            }
        } else {
            const page = this.routes[path] || this.routes['/'];
            
            // Update state
            if (window.State) {
                window.State.setCurrentPage(page);
            }
            
            // Update navigation active states
            this.updateNavActiveStates(page);
        }
    }
    
    /**
     * Update navigation active states
     */
    updateNavActiveStates(activePage) {
        // Update global nav
        const navItems = document.querySelectorAll('.nav-item, .sidebar-nav-item');
        navItems.forEach(item => {
            const page = item.dataset.page || item.getAttribute('href')?.replace(/\.html$/, '').replace(/^\//, '');
            if (page === activePage || (page === 'contexts' && activePage === 'contexts')) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
    
    /**
     * Navigate to a page
     */
    navigate(path, options = {}) {
        const match = this.matchRoute(path);
        const page = match ? match.handler : this.routes[path];
        
        if (page && window.State) {
            window.State.setCurrentPage(page);
        }
        
        if (options.replace) {
            window.history.replaceState({}, '', path);
        } else {
            window.history.pushState({}, '', path);
        }
        
        this.setActivePage();
    }
    
    /**
     * Get current route
     */
    getCurrentRoute() {
        const path = window.location.pathname;
        const match = this.matchRoute(path);
        if (match) {
            return { handler: match.handler, params: match.params };
        }
        return { handler: this.routes[path] || this.routes['/'], params: {} };
    }
    
    /**
     * Navigate to thread detail page
     */
    navigateToThread(threadId, category = null) {
        if (!threadId) return;
        
        // Navigate to thread.html with thread ID in URL
        // Use hash for now to work with existing setup
        const currentPath = window.location.pathname;
        
        if (currentPath.includes('thread.html') || currentPath.startsWith('/thread/')) {
            // Already on thread page, just update and load
            let path;
            if (category) {
                path = `/circles/${category}/${threadId}`;
            } else {
                path = `/thread/${threadId}`;
            }
            window.history.pushState({}, '', path);
            if (window.ThreadDetailPage) {
                window.ThreadDetailPage.loadThread(threadId);
            }
        } else {
            // Navigate to thread.html with hash
            window.location.href = `/thread.html#${threadId}`;
        }
    }
    
    /**
     * Get query parameters
     */
    getQueryParams() {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        for (const [key, value] of params.entries()) {
            result[key] = value;
        }
        return result;
    }
}

// Create global instance
window.Router = new Router();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Router;
}

