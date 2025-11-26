/**
 * THESIDIA // State Management
 * Client-side state management with localStorage persistence
 */

class State {
    constructor() {
        this.state = {
            user: {
                user_id: null,
                session_id: null,
                preferences: {}
            },
            navigation: {
                currentPage: null,
                activeNavItem: null
            },
            cache: {
                stream: { data: null, timestamp: null },
                atlas: { data: null, timestamp: null },
                reactor: { data: null, timestamp: null },
                application: { data: null, timestamp: null },
                metrics: { data: null, timestamp: null }
            },
            interactions: []
        };
        
        this.load();
        this.initUserSession();
    }
    
    /**
     * Initialize user session
     */
    async initUserSession() {
        if (!this.state.user.user_id) {
            try {
                const response = await fetch('/api/user/session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.state.user.user_id = data.user_id;
                    this.state.user.session_id = data.session_id;
                    this.save();
                }
            } catch (error) {
                console.error('Failed to initialize session:', error);
            }
        }
    }
    
    /**
     * Get user ID
     */
    getUserId() {
        return this.state.user.user_id;
    }
    
    /**
     * Get session ID
     */
    getSessionId() {
        return this.state.user.session_id;
    }
    
    /**
     * Set current page
     */
    setCurrentPage(page) {
        this.state.navigation.currentPage = page;
        this.state.navigation.activeNavItem = page;
        this.save();
    }
    
    /**
     * Get current page
     */
    getCurrentPage() {
        return this.state.navigation.currentPage;
    }
    
    /**
     * Cache data for a page
     */
    cacheData(page, data, ttl = 300000) { // 5 minutes default
        this.state.cache[page] = {
            data: data,
            timestamp: Date.now(),
            ttl: ttl
        };
        this.save();
    }
    
    /**
     * Get cached data
     */
    getCachedData(page) {
        const cached = this.state.cache[page];
        if (!cached || !cached.data) return null;
        
        const age = Date.now() - cached.timestamp;
        if (age > (cached.ttl || 300000)) {
            // Cache expired
            this.state.cache[page] = { data: null, timestamp: null };
            this.save();
            return null;
        }
        
        return cached.data;
    }
    
    /**
     * Track user interaction
     */
    trackInteraction(type, itemId, action = 'view') {
        const interaction = {
            type: type,
            item_id: itemId,
            action: action,
            timestamp: new Date().toISOString()
        };
        
        this.state.interactions.push(interaction);
        
        // Keep only last 100 interactions
        if (this.state.interactions.length > 100) {
            this.state.interactions = this.state.interactions.slice(-100);
        }
        
        this.save();
        
        // Send to server
        this.sendInteraction(interaction);
    }
    
    /**
     * Send interaction to server
     */
    async sendInteraction(interaction) {
        try {
            await fetch('/api/stream/interact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    item_id: interaction.item_id,
                    type: interaction.action,
                    user_id: this.getUserId(),
                    session_id: this.getSessionId()
                })
            });
        } catch (error) {
            console.error('Failed to send interaction:', error);
        }
    }
    
    /**
     * Set user preference
     */
    setPreference(key, value) {
        this.state.user.preferences[key] = value;
        this.save();
    }
    
    /**
     * Get user preference
     */
    getPreference(key, defaultValue = null) {
        return this.state.user.preferences[key] || defaultValue;
    }
    
    /**
     * Save state to localStorage
     */
    save() {
        try {
            localStorage.setItem('thesidia_state', JSON.stringify(this.state));
        } catch (error) {
            console.error('Failed to save state:', error);
        }
    }
    
    /**
     * Load state from localStorage
     */
    load() {
        try {
            const saved = localStorage.getItem('thesidia_state');
            if (saved) {
                const parsed = JSON.parse(saved);
                // Merge with defaults
                this.state = { ...this.state, ...parsed };
            }
        } catch (error) {
            console.error('Failed to load state:', error);
        }
    }
    
    /**
     * Clear all state
     */
    clear() {
        this.state = {
            user: {
                user_id: null,
                session_id: null,
                preferences: {}
            },
            navigation: {
                currentPage: null,
                activeNavItem: null
            },
            cache: {
                stream: { data: null, timestamp: null },
                atlas: { data: null, timestamp: null },
                reactor: { data: null, timestamp: null },
                application: { data: null, timestamp: null },
                metrics: { data: null, timestamp: null }
            },
            interactions: []
        };
        localStorage.removeItem('thesidia_state');
    }
}

// Create global instance
window.State = new State();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = State;
}

