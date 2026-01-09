/**
 * Onboarding Manager
 * Core orchestrator for contextual onboarding pop-ups and tutorials
 */

import { OnboardingUtils } from './utils.js';
import { TutorialRegistry } from './tutorials.js';

export class OnboardingManager {
    constructor() {
        this.isInitialized = false;
        this.activeTutorial = null;
        this.tutorialRegistry = new TutorialRegistry();
        this.eventListeners = [];
        
        // Touch gesture tracking
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        this.swipeThreshold = 50; // Match existing app pattern
    }
    
    /**
     * Initialize the onboarding manager
     */
    init() {
        if (!OnboardingUtils.isEnabled()) {
            console.log('[Onboarding] Disabled - skipping initialization');
            return;
        }
        
        if (this.isInitialized) {
            console.warn('[Onboarding] Already initialized');
            return;
        }
        
        try {
            this.setupEventListeners();
            this.checkForTutorials();
            this.isInitialized = true;
            console.log('[Onboarding] Initialized successfully');
        } catch (error) {
            console.error('[Onboarding] Initialization error:', error);
            // Don't break the app - just log the error
        }
    }
    
    /**
     * Setup event listeners for contextual triggers
     */
    setupEventListeners() {
        // Listen for page changes
        window.addEventListener('popstate', () => {
            setTimeout(() => this.checkForTutorials(), 100);
        });
        
        // Listen for navigation events
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (link && link.href) {
                setTimeout(() => this.checkForTutorials(), 500);
            }
        });
        
        // Listen for profile page load
        if (OnboardingUtils.getCurrentPage() === 'profile') {
            setTimeout(() => this.checkProfileTutorial(), 1000);
        }
    }
    
    /**
     * Check if any tutorials should be triggered
     */
    checkForTutorials() {
        const page = OnboardingUtils.getCurrentPage();
        const progress = OnboardingUtils.getProgress();
        
        // First visit check
        if (!progress.firstVisitCompleted) {
            this.showWelcomeTutorial();
            return;
        }
        
        // Page-specific tutorials
        switch (page) {
            case 'profile':
                this.checkProfileTutorial();
                break;
            case 'stream':
                this.checkStreamTutorial();
                break;
            case 'explore':
                this.checkExploreTutorial();
                break;
            case 'kim':
                this.checkKimTutorial();
                break;
        }
    }
    
    /**
     * Show welcome tutorial (first visit)
     */
    showWelcomeTutorial() {
        if (OnboardingUtils.isTutorialCompleted('welcome')) {
            return;
        }
        
        const tutorial = this.tutorialRegistry.get('welcome');
        if (tutorial) {
            this.showTutorial(tutorial);
        }
    }
    
    /**
     * Check and show profile setup tutorial
     */
    checkProfileTutorial() {
        if (OnboardingUtils.isTutorialCompleted('profile-setup')) {
            return;
        }
        
        // Check if profile is incomplete
        const userId = OnboardingUtils.getCurrentUserId();
        if (!userId) return;
        
        // Wait for profile elements to load
        OnboardingUtils.waitForElement('.profile-page, .profile-info', 3000)
            .then(() => {
                const tutorial = this.tutorialRegistry.get('profile-setup');
                if (tutorial) {
                    this.showTutorial(tutorial);
                }
            })
            .catch(() => {
                // Element not found - that's okay
            });
    }
    
    /**
     * Check and show stream navigation tutorial
     */
    checkStreamTutorial() {
        if (OnboardingUtils.isTutorialCompleted('stream-navigation')) {
            return;
        }
        
        const progress = OnboardingUtils.getProgress();
        if (!progress.firstVisitCompleted) return;
        
        setTimeout(() => {
            const tutorial = this.tutorialRegistry.get('stream-navigation');
            if (tutorial) {
                this.showTutorial(tutorial);
            }
        }, 2000);
    }
    
    /**
     * Check and show explore tutorial
     */
    checkExploreTutorial() {
        if (OnboardingUtils.isTutorialCompleted('explore')) {
            return;
        }
        
        const progress = OnboardingUtils.getProgress();
        if (!progress.firstVisitCompleted) return;
        
        setTimeout(() => {
            const tutorial = this.tutorialRegistry.get('explore');
            if (tutorial) {
                this.showTutorial(tutorial);
            }
        }, 2000);
    }
    
    /**
     * Check and show KIM chat tutorial
     */
    checkKimTutorial() {
        if (OnboardingUtils.isTutorialCompleted('kim-chat')) {
            return;
        }
        
        const progress = OnboardingUtils.getProgress();
        if (!progress.firstVisitCompleted) return;
        
        setTimeout(() => {
            const tutorial = this.tutorialRegistry.get('kim-chat');
            if (tutorial) {
                this.showTutorial(tutorial);
            }
        }, 2000);
    }
    
    /**
     * Show a tutorial
     */
    showTutorial(tutorial) {
        if (this.activeTutorial) {
            this.closeTutorial();
        }
        
        this.activeTutorial = tutorial;
        this.renderTutorial(tutorial);
    }
    
    /**
     * Render tutorial UI (Mobile-first with bottom sheet)
     */
    renderTutorial(tutorial) {
        // Remove any existing tutorial overlays
        const existing = document.querySelector('.onboarding-overlay');
        if (existing) {
            existing.remove();
        }
        
        // Determine if this should be full-screen (welcome) or bottom sheet
        const isFullScreen = tutorial.id === 'welcome';
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'onboarding-overlay';
        if (isFullScreen) {
            overlay.classList.add('onboarding-fullscreen');
        } else {
            overlay.classList.add('onboarding-bottom-sheet');
        }
        overlay.setAttribute('data-tutorial-id', tutorial.id);
        
        // Add swipe handle for bottom sheets
        if (!isFullScreen) {
            const handle = document.createElement('div');
            handle.className = 'onboarding-swipe-handle';
            overlay.appendChild(handle);
        }
        
        // Create content container
        const container = document.createElement('div');
        container.className = isFullScreen ? 'onboarding-fullscreen-content' : 'onboarding-bottom-sheet-content';
        
        // Title
        const title = document.createElement('h3');
        title.className = 'onboarding-title';
        title.textContent = tutorial.title;
        container.appendChild(title);
        
        // Content
        const content = document.createElement('div');
        content.className = 'onboarding-content';
        if (typeof tutorial.content === 'string') {
            content.innerHTML = tutorial.content;
        } else if (Array.isArray(tutorial.content)) {
            tutorial.content.forEach(item => {
                const p = document.createElement('p');
                p.textContent = item;
                content.appendChild(p);
            });
        }
        container.appendChild(content);
        
        // Actions
        const actions = document.createElement('div');
        actions.className = 'onboarding-actions';
        
        // Skip button (if skippable)
        if (tutorial.skippable !== false) {
            const skipBtn = document.createElement('button');
            skipBtn.className = 'onboarding-btn-secondary';
            skipBtn.textContent = tutorial.skipText || 'Skip';
            skipBtn.addEventListener('touchend', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.skipTutorial(tutorial.id);
            });
            skipBtn.addEventListener('click', () => this.skipTutorial(tutorial.id));
            actions.appendChild(skipBtn);
        }
        
        // Next/Close button
        const nextBtn = document.createElement('button');
        nextBtn.className = 'onboarding-btn-primary';
        nextBtn.textContent = tutorial.nextText || 'Got it';
        nextBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.completeTutorial(tutorial.id);
        });
        nextBtn.addEventListener('click', () => this.completeTutorial(tutorial.id));
        actions.appendChild(nextBtn);
        
        container.appendChild(actions);
        overlay.appendChild(container);
        
        // Position relative to target if specified (for tooltip-style)
        if (tutorial.target && !isFullScreen) {
            this.positionBottomSheet(overlay, tutorial.target);
        }
        
        document.body.appendChild(overlay);
        
        // Setup touch gestures
        this.setupTouchGestures(overlay, tutorial);
        
        // Animate in
        setTimeout(() => {
            overlay.classList.add('active');
        }, 10);
    }
    
    /**
     * Setup touch gestures for mobile
     */
    setupTouchGestures(overlay, tutorial) {
        const container = overlay.querySelector('.onboarding-bottom-sheet-content, .onboarding-fullscreen-content');
        if (!container) return;
        
        // Touch start - Match app pattern
        container.addEventListener('touchstart', (e) => {
            // Don't interfere with scrollable content
            const scrollable = container.querySelector('.onboarding-content');
            if (scrollable && scrollable.scrollHeight > scrollable.clientHeight) {
                // Allow scrolling if content is scrollable
                const scrollTop = scrollable.scrollTop;
                const scrollHeight = scrollable.scrollHeight;
                const clientHeight = scrollable.clientHeight;
                
                // If at top, allow swipe down to dismiss
                if (scrollTop === 0) {
                    this.touchStartX = e.touches[0].clientX;
                    this.touchStartY = e.touches[0].clientY;
                }
                // If at bottom, also allow swipe
                else if (scrollTop + clientHeight >= scrollHeight - 5) {
                    this.touchStartX = e.touches[0].clientX;
                    this.touchStartY = e.touches[0].clientY;
                }
            } else {
                // No scrollable content, always allow swipe
                this.touchStartX = e.touches[0].clientX;
                this.touchStartY = e.touches[0].clientY;
            }
        }, { passive: true });
        
        // Touch move - allow dragging
        let currentY = 0;
        container.addEventListener('touchmove', (e) => {
            if (!this.touchStartY) return;
            
            const touchY = e.touches[0].clientY;
            const deltaY = touchY - this.touchStartY;
            
            // Only allow downward drag for bottom sheets
            if (overlay.classList.contains('onboarding-bottom-sheet') && deltaY > 0) {
                currentY = deltaY;
                container.style.transform = `translateY(${deltaY}px)`;
                // Add opacity fade as drags down
                const opacity = Math.max(0, 1 - (deltaY / 300));
                overlay.style.opacity = opacity;
            }
        }, { passive: true });
        
        // Touch end - detect swipe
        container.addEventListener('touchend', (e) => {
            if (!this.touchStartY) return;
            
            this.touchEndX = e.changedTouches[0].clientX;
            this.touchEndY = e.changedTouches[0].clientY;
            
            const deltaX = this.touchEndX - this.touchStartX;
            const deltaY = this.touchEndY - this.touchStartY;
            const absDeltaX = Math.abs(deltaX);
            const absDeltaY = Math.abs(deltaY);
            
            // Reset transform
            container.style.transform = '';
            overlay.style.opacity = '';
            
            // Swipe down to dismiss (bottom sheet) - Match app swipe threshold (50px)
            if (overlay.classList.contains('onboarding-bottom-sheet')) {
                if (deltaY > this.swipeThreshold && absDeltaY > absDeltaX) {
                    // Swipe down - dismiss (match app pattern)
                    this.skipTutorial(tutorial.id);
                    return;
                }
            }
            
            // Swipe up to dismiss (full-screen) - less common but useful
            if (overlay.classList.contains('onboarding-fullscreen')) {
                if (deltaY < -this.swipeThreshold && absDeltaY > absDeltaX) {
                    this.skipTutorial(tutorial.id);
                    return;
                }
            }
            
            // Swipe left/right for navigation (future: multi-step tutorials)
            if (absDeltaX > this.swipeThreshold && absDeltaX > absDeltaY) {
                // Could add swipe navigation here for multi-step tutorials
            }
            
            // Reset
            this.touchStartX = 0;
            this.touchStartY = 0;
        }, { passive: true });
        
        // Tap outside overlay to dismiss
        overlay.addEventListener('touchend', (e) => {
            if (e.target === overlay) {
                this.skipTutorial(tutorial.id);
            }
        }, { passive: true });
    }
    
    /**
     * Position bottom sheet relative to target element
     */
    positionBottomSheet(overlay, selector) {
        const target = document.querySelector(selector);
        if (!target) return;
        
        const rect = target.getBoundingClientRect();
        const container = overlay.querySelector('.onboarding-bottom-sheet-content');
        if (!container) return;
        
        // Position above target if space, otherwise below
        const spaceAbove = rect.top;
        const spaceBelow = window.innerHeight - rect.bottom;
        
        if (spaceAbove > 200) {
            // Position above
            container.style.bottom = `${window.innerHeight - rect.top + 20}px`;
        } else {
            // Position below (default bottom sheet behavior)
            container.style.bottom = '20px';
        }
    }
    
    
    /**
     * Complete tutorial
     */
    completeTutorial(tutorialId) {
        OnboardingUtils.markTutorialCompleted(tutorialId);
        
        // Update progress
        if (tutorialId === 'welcome') {
            OnboardingUtils.updateProgress('firstVisitCompleted', true);
        }
        
        this.closeTutorial();
    }
    
    /**
     * Skip tutorial
     */
    skipTutorial(tutorialId) {
        OnboardingUtils.markTutorialCompleted(tutorialId);
        this.closeTutorial();
    }
    
    /**
     * Close current tutorial (with mobile animation)
     */
    closeTutorial() {
        const overlay = document.querySelector('.onboarding-overlay');
        if (overlay) {
            overlay.classList.remove('active');
            
            // Animate out based on type
            const container = overlay.querySelector('.onboarding-bottom-sheet-content, .onboarding-fullscreen-content');
            if (container && overlay.classList.contains('onboarding-bottom-sheet')) {
                container.style.transform = 'translateY(100%)';
            }
            
            setTimeout(() => {
                overlay.remove();
            }, 300);
        }
        this.activeTutorial = null;
    }
    
    /**
     * Cleanup
     */
    destroy() {
        this.eventListeners.forEach(({ element, event, handler }) => {
            element.removeEventListener(event, handler);
        });
        this.eventListeners = [];
        this.closeTutorial();
        this.isInitialized = false;
    }
}

