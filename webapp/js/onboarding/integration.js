/**
 * Onboarding Integration Layer
 * Lightweight integration with existing app
 * Safe to include - won't break app if onboarding is disabled
 */

import { OnboardingUtils } from './utils.js';
import { OnboardingManager } from './onboarding-manager.js';
import { ProfileCustomization } from './profile-customization.js';

// Global instance (for debugging)
window.onboardingManager = null;
window.profileCustomization = null;

/**
 * Initialize onboarding system
 * Safe to call - catches all errors
 */
function initOnboarding() {
    // Check if onboarding is enabled
    if (!OnboardingUtils.isEnabled()) {
        console.log('[Onboarding] Disabled - not initializing');
        return;
    }
    
    // Check if already initialized
    if (window.onboardingManager) {
        console.log('[Onboarding] Already initialized');
        return;
    }
    
    try {
        // Initialize onboarding manager
        window.onboardingManager = new OnboardingManager();
        window.onboardingManager.init();
        
        // Initialize profile customization
        window.profileCustomization = new ProfileCustomization();
        window.profileCustomization.init();
        
        console.log('[Onboarding] System initialized successfully');
    } catch (error) {
        console.error('[Onboarding] Initialization error:', error);
        // Don't break the app - just log the error
        window.onboardingManager = null;
        window.profileCustomization = null;
    }
}

/**
 * Cleanup onboarding system
 */
function cleanupOnboarding() {
    try {
        if (window.onboardingManager) {
            window.onboardingManager.destroy();
            window.onboardingManager = null;
        }
        window.profileCustomization = null;
    } catch (error) {
        console.error('[Onboarding] Cleanup error:', error);
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initOnboarding);
} else {
    // DOM already loaded
    initOnboarding();
}

// Cleanup on page unload
window.addEventListener('beforeunload', cleanupOnboarding);

// Export for manual initialization if needed
export { initOnboarding, cleanupOnboarding };

