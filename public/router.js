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
            '/metrics_dashboard.html': 'metrics'
        };
        
        this.init();
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
        const page = this.routes[path] || this.routes['/'];
        
        // Update state
        if (window.State) {
            window.State.setCurrentPage(page);
        }
        
        // Update navigation active states
        this.updateNavActiveStates(page);
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
        const page = this.routes[path];
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
        return this.routes[path] || this.routes['/'];
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

