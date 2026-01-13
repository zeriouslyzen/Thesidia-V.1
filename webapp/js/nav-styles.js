/**
 * KATANX // Nav Styles Module (Hardened)
 * Dynamic navigation style switching with localStorage persistence
 * 
 * @version 2.0.0
 * @description Production-hardened with error handling, performance optimizations,
 *              debouncing, and graceful degradation.
 */

(function () {
    'use strict';

    // ============================================
    // CONFIGURATION
    // ============================================

    /** @type {string[]} Valid navigation style identifiers */
    const NAV_STYLES = Object.freeze(['unified', 'bottom-tab', 'floating-hud', 'contextual']);

    /** @type {string} localStorage key for persisting nav style */
    const STORAGE_KEY = 'nav_style';

    /** @type {string} Default style if none saved or invalid */
    const DEFAULT_STYLE = 'unified';

    /** @type {number} Debounce delay in ms to prevent rapid switching */
    const DEBOUNCE_MS = 150;

    /** @type {boolean} Enable debug logging */
    const DEBUG = false;

    // ============================================
    // STATE
    // ============================================

    /** @type {string|null} Currently applied style */
    let currentStyle = null;

    /** @type {number|null} Debounce timer ID */
    let debounceTimer = null;

    /** @type {boolean} Whether module has initialized */
    let isInitialized = false;

    // ============================================
    // UTILITIES
    // ============================================

    /**
     * Safe console logging (only in debug mode)
     * @param {...any} args - Arguments to log
     */
    function log(...args) {
        if (DEBUG) {
            console.log('[NavStyles]', ...args);
        }
    }

    /**
     * Safe console error logging (always enabled)
     * @param {...any} args - Arguments to log
     */
    function logError(...args) {
        console.error('[NavStyles Error]', ...args);
    }

    /**
     * Safe localStorage getter with error handling
     * @param {string} key - Storage key
     * @returns {string|null} Stored value or null
     */
    function safeGetStorage(key) {
        try {
            return localStorage.getItem(key);
        } catch (e) {
            logError('Failed to read localStorage:', e.message);
            return null;
        }
    }

    /**
     * Safe localStorage setter with error handling
     * @param {string} key - Storage key
     * @param {string} value - Value to store
     * @returns {boolean} Whether save succeeded
     */
    function safeSetStorage(key, value) {
        try {
            localStorage.setItem(key, value);
            return true;
        } catch (e) {
            logError('Failed to write localStorage:', e.message);
            return false;
        }
    }

    /**
     * Validate a style string
     * @param {string} style - Style to validate
     * @returns {string} Valid style or default
     */
    function validateStyle(style) {
        if (typeof style !== 'string') {
            return DEFAULT_STYLE;
        }
        const normalized = style.toLowerCase().trim();
        return NAV_STYLES.includes(normalized) ? normalized : DEFAULT_STYLE;
    }

    /**
     * Debounce function execution
     * @param {Function} fn - Function to debounce
     * @param {number} delay - Delay in ms
     * @returns {Function} Debounced function
     */
    function debounce(fn, delay) {
        return function (...args) {
            if (debounceTimer) {
                clearTimeout(debounceTimer);
            }
            debounceTimer = setTimeout(() => {
                debounceTimer = null;
                fn.apply(this, args);
            }, delay);
        };
    }

    // ============================================
    // CORE FUNCTIONS
    // ============================================

    /**
     * Get current nav style from localStorage
     * @returns {string} Current valid style
     */
    function getNavStyle() {
        const saved = safeGetStorage(STORAGE_KEY);
        return validateStyle(saved);
    }

    /**
     * Apply nav style to the document (debounced)
     * @param {string} style - Style to apply
     * @param {boolean} [immediate=false] - Skip debounce
     */
    function applyNavStyle(style, immediate = false) {
        const validStyle = validateStyle(style);

        // Skip if same style already applied (performance)
        if (validStyle === currentStyle && !immediate) {
            log('Style already applied, skipping:', validStyle);
            return;
        }

        const doApply = () => {
            try {
                // Update internal state
                currentStyle = validStyle;

                // Set data attribute on body (CSS will handle visibility)
                if (document.body) {
                    document.body.setAttribute('data-nav-style', validStyle);
                }

                // Save to localStorage
                safeSetStorage(STORAGE_KEY, validStyle);

                // Update dropdown if it exists
                const select = document.getElementById('navStyleSelect');
                if (select && select.value !== validStyle) {
                    select.value = validStyle;
                }

                // Inject/remove dynamic elements based on style
                injectNavElements(validStyle);

                log('Applied style:', validStyle);

                // Dispatch custom event for other modules to react
                window.dispatchEvent(new CustomEvent('katanx:navstyle', {
                    detail: { style: validStyle }
                }));

            } catch (e) {
                logError('Failed to apply style:', e.message);
                // Fallback: at least try to set the body attribute
                try {
                    document.body?.setAttribute('data-nav-style', DEFAULT_STYLE);
                } catch (fallbackError) {
                    // Silently fail - nothing more we can do
                }
            }
        };

        if (immediate) {
            doApply();
        } else {
            debounce(doApply, DEBOUNCE_MS)();
        }
    }

    /**
     * Inject navigation elements for specific styles
     * @param {string} style - Style requiring injection
     */
    function injectNavElements(style) {
        try {
            // Use requestAnimationFrame for smoother DOM updates
            requestAnimationFrame(() => {
                // Clean up existing injected elements
                const existingBottomNav = document.getElementById('dynamicBottomNav');
                const existingFloatingHud = document.getElementById('dynamicFloatingHud');

                // Remove with fade-out animation hint
                if (existingBottomNav) {
                    existingBottomNav.style.opacity = '0';
                    setTimeout(() => existingBottomNav.remove(), 150);
                }
                if (existingFloatingHud) {
                    existingFloatingHud.style.opacity = '0';
                    setTimeout(() => existingFloatingHud.remove(), 150);
                }

                // Get current active section for highlighting
                const activeNav = document.querySelector('.nav-item.active');
                const currentSection = activeNav?.dataset?.section || 'stream';

                // Wait for cleanup, then inject new elements
                setTimeout(() => {
                    if (style === 'bottom-tab') {
                        injectBottomTabBar(currentSection);
                    } else if (style === 'floating-hud') {
                        injectFloatingHud(currentSection);
                    }
                }, 160);
            });
        } catch (e) {
            logError('Failed to inject nav elements:', e.message);
        }
    }

    /**
     * Create bottom tab bar navigation with GPU acceleration
     * @param {string} activeSection - Currently active section
     */
    function injectBottomTabBar(activeSection) {
        // Check if already exists (prevent duplicates)
        if (document.getElementById('dynamicBottomNav')) {
            return;
        }

        const bottomNav = document.createElement('nav');
        bottomNav.id = 'dynamicBottomNav';
        bottomNav.className = 'dynamic-bottom-nav';
        bottomNav.setAttribute('role', 'navigation');
        bottomNav.setAttribute('aria-label', 'Main navigation');

        // Start invisible for fade-in
        bottomNav.style.opacity = '0';

        bottomNav.innerHTML = `
            <button class="bottom-nav-item${activeSection === 'home' ? ' active' : ''}" data-section="home" aria-label="Home">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                    <polyline points="9 22 9 12 15 12 15 22"/>
                </svg>
                <span>home</span>
            </button>
            <button class="bottom-nav-item${activeSection === 'stream' ? ' active' : ''}" data-section="stream" aria-label="Stream">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <line x1="3" y1="12" x2="21" y2="12"/>
                    <line x1="3" y1="6" x2="21" y2="6"/>
                    <line x1="3" y1="18" x2="21" y2="18"/>
                </svg>
                <span>stream</span>
            </button>
            <button class="bottom-nav-item${activeSection === 'kx-cuts' ? ' active' : ''}" data-section="kx-cuts" aria-label="KX Cuts">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <circle cx="12" cy="12" r="10"/>
                    <polygon points="10 8 16 12 10 16 10 8"/>
                </svg>
                <span>cuts</span>
            </button>
            <button class="bottom-nav-item${activeSection === 'circles' ? ' active' : ''}" data-section="circles" aria-label="Forums">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
                <span>forums</span>
            </button>
        `;

        // Event delegation for better performance (single listener)
        bottomNav.addEventListener('click', handleNavClick, { passive: true });

        document.body.appendChild(bottomNav);

        // Fade in with GPU-accelerated animation
        requestAnimationFrame(() => {
            bottomNav.style.transition = 'opacity 0.2s ease-out';
            bottomNav.style.opacity = '1';
        });
    }

    /**
     * Create floating HUD pill navigation with GPU acceleration
     * @param {string} activeSection - Currently active section
     */
    function injectFloatingHud(activeSection) {
        // Check if already exists (prevent duplicates)
        if (document.getElementById('dynamicFloatingHud')) {
            return;
        }

        const floatingHud = document.createElement('nav');
        floatingHud.id = 'dynamicFloatingHud';
        floatingHud.className = 'dynamic-floating-hud';
        floatingHud.setAttribute('role', 'navigation');
        floatingHud.setAttribute('aria-label', 'Main navigation');

        // Start invisible for fade-in
        floatingHud.style.opacity = '0';

        floatingHud.innerHTML = `
            <button class="hud-nav-item${activeSection === 'home' ? ' active' : ''}" data-section="home">home</button>
            <button class="hud-nav-item${activeSection === 'stream' ? ' active' : ''}" data-section="stream">stream</button>
            <button class="hud-nav-item${activeSection === 'kx-cuts' ? ' active' : ''}" data-section="kx-cuts">cuts</button>
            <button class="hud-nav-item${activeSection === 'circles' ? ' active' : ''}" data-section="circles">forums</button>
        `;

        // Event delegation for better performance
        floatingHud.addEventListener('click', handleNavClick, { passive: true });

        document.body.appendChild(floatingHud);

        // Fade in with GPU-accelerated animation
        requestAnimationFrame(() => {
            floatingHud.style.transition = 'opacity 0.2s ease-out';
            floatingHud.style.opacity = '1';
        });
    }

    /**
     * Unified click handler using event delegation
     * @param {Event} e - Click event
     */
    function handleNavClick(e) {
        const btn = e.target.closest('[data-section]');
        if (!btn) return;

        const section = btn.dataset.section;
        if (!section) return;

        // Navigate
        navigateToSection(section);

        // Update active states in the clicked nav
        const nav = btn.closest('nav');
        if (nav) {
            nav.querySelectorAll('[data-section]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }
    }

    /**
     * Navigate to a section (integrate with existing carousel navigation)
     * @param {string} section - Section identifier
     */
    function navigateToSection(section) {
        try {
            // Try to use existing navigation system
            const navItem = document.querySelector(`.advanced-nav .nav-item[data-section="${section}"]`);
            if (navItem) {
                navItem.click();
                return;
            }

            // Fallback: dispatch custom event for other modules
            window.dispatchEvent(new CustomEvent('katanx:navigate', {
                detail: { section },
                bubbles: true
            }));
        } catch (e) {
            logError('Navigation failed:', e.message);
        }
    }

    /**
     * Sync active state when navigation happens elsewhere
     */
    function syncActiveState() {
        const activeNav = document.querySelector('.advanced-nav .nav-item.active');
        const activeSection = activeNav?.dataset?.section;

        if (!activeSection) return;

        // Sync bottom nav
        const bottomNav = document.getElementById('dynamicBottomNav');
        if (bottomNav) {
            bottomNav.querySelectorAll('[data-section]').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.section === activeSection);
            });
        }

        // Sync floating HUD
        const floatingHud = document.getElementById('dynamicFloatingHud');
        if (floatingHud) {
            floatingHud.querySelectorAll('[data-section]').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.section === activeSection);
            });
        }
    }

    // ============================================
    // INITIALIZATION
    // ============================================

    /**
     * Initialize nav styles system
     */
    function init() {
        if (isInitialized) {
            log('Already initialized, skipping');
            return;
        }

        try {
            // Apply saved style immediately (skip debounce for initial load)
            const savedStyle = getNavStyle();
            applyNavStyle(savedStyle, true);

            // Setup select dropdown handler
            const select = document.getElementById('navStyleSelect');
            if (select) {
                select.value = savedStyle;
                select.addEventListener('change', (e) => {
                    applyNavStyle(e.target.value);
                });
            }

            // Listen for navigation changes from other modules
            window.addEventListener('katanx:navigate', () => {
                // Small delay to let the navigation complete
                setTimeout(syncActiveState, 100);
            });

            // Listen for carousel section changes
            document.addEventListener('click', (e) => {
                if (e.target.closest('.advanced-nav .nav-item')) {
                    setTimeout(syncActiveState, 100);
                }
            });

            isInitialized = true;
            log('Initialized successfully');

        } catch (e) {
            logError('Initialization failed:', e.message);
            // Try to at least set a default state
            try {
                document.body?.setAttribute('data-nav-style', DEFAULT_STYLE);
            } catch (fallbackError) {
                // Nothing more we can do
            }
        }
    }

    // ============================================
    // BOOTSTRAP
    // ============================================

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // DOM already ready, init immediately
        init();
    }

    // ============================================
    // PUBLIC API
    // ============================================

    /**
     * Public API exposed on window.NavStyles
     * @namespace
     */
    window.NavStyles = Object.freeze({
        /**
         * Apply a navigation style
         * @param {string} style - Style to apply
         */
        apply: applyNavStyle,

        /**
         * Get current navigation style
         * @returns {string} Current style
         */
        get: getNavStyle,

        /**
         * Available style options
         * @type {string[]}
         */
        styles: NAV_STYLES,

        /**
         * Force sync active states
         */
        sync: syncActiveState,

        /**
         * Module version
         * @type {string}
         */
        version: '2.0.0'
    });

})();
