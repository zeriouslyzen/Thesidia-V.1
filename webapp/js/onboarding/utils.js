/**
 * Onboarding Utilities
 * Helper functions for the onboarding system
 */

export class OnboardingUtils {
    /**
     * Check if onboarding is enabled
     */
    static isEnabled() {
        // Check URL param first
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('onboarding') === 'false') {
            return false;
        }
        
        // Check localStorage
        const stored = localStorage.getItem('onboarding_enabled');
        if (stored !== null) {
            return stored === 'true';
        }
        
        // Default: enabled in dev mode
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1';
    }
    
    /**
     * Set onboarding enabled state
     */
    static setEnabled(enabled) {
        localStorage.setItem('onboarding_enabled', enabled.toString());
    }
    
    /**
     * Get onboarding progress
     */
    static getProgress() {
        try {
            const progress = localStorage.getItem('onboarding_progress');
            return progress ? JSON.parse(progress) : {};
        } catch {
            return {};
        }
    }
    
    /**
     * Update onboarding progress
     */
    static updateProgress(key, value) {
        const progress = this.getProgress();
        progress[key] = value;
        localStorage.setItem('onboarding_progress', JSON.stringify(progress));
    }
    
    /**
     * Check if tutorial is completed
     */
    static isTutorialCompleted(tutorialId) {
        const completed = localStorage.getItem('tutorials_completed');
        if (!completed) return false;
        try {
            const completedList = JSON.parse(completed);
            return Array.isArray(completedList) && completedList.includes(tutorialId);
        } catch {
            return false;
        }
    }
    
    /**
     * Mark tutorial as completed
     */
    static markTutorialCompleted(tutorialId) {
        const completed = localStorage.getItem('tutorials_completed');
        let completedList = [];
        if (completed) {
            try {
                completedList = JSON.parse(completed);
            } catch {}
        }
        if (!completedList.includes(tutorialId)) {
            completedList.push(tutorialId);
            localStorage.setItem('tutorials_completed', JSON.stringify(completedList));
        }
    }
    
    /**
     * Get current user ID
     */
    static getCurrentUserId() {
        return localStorage.getItem('thesidia_user_id') || 
               sessionStorage.getItem('thesidia_user_id');
    }
    
    /**
     * Check if viewing own profile
     */
    static isOwnProfile(profileUserId) {
        const currentUserId = this.getCurrentUserId();
        return currentUserId && profileUserId === currentUserId;
    }
    
    /**
     * Get profile customization settings
     */
    static getProfileCustomization() {
        try {
            const custom = localStorage.getItem('profile_customization');
            return custom ? JSON.parse(custom) : {};
        } catch {
            return {};
        }
    }
    
    /**
     * Save profile customization settings
     */
    static saveProfileCustomization(settings) {
        localStorage.setItem('profile_customization', JSON.stringify(settings));
    }
    
    /**
     * Safe error handler - prevents onboarding from breaking app
     */
    static safeExecute(fn, fallback = null) {
        try {
            return fn();
        } catch (error) {
            console.warn('[Onboarding] Error:', error);
            return fallback;
        }
    }
    
    /**
     * Wait for element to appear in DOM
     */
    static waitForElement(selector, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const element = document.querySelector(selector);
            if (element) {
                resolve(element);
                return;
            }
            
            const observer = new MutationObserver((mutations, obs) => {
                const element = document.querySelector(selector);
                if (element) {
                    obs.disconnect();
                    resolve(element);
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            setTimeout(() => {
                observer.disconnect();
                reject(new Error(`Element ${selector} not found within ${timeout}ms`));
            }, timeout);
        });
    }
    
    /**
     * Get page identifier
     */
    static getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('profile')) return 'profile';
        if (path.includes('stream')) return 'stream';
        if (path.includes('search') || path.includes('explore')) return 'explore';
        if (path.includes('kim')) return 'kim';
        if (path === '/' || path.includes('landing')) return 'landing';
        return 'unknown';
    }
}

