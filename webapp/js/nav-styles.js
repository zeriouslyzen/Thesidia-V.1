/**
 * KATANX // Nav Styles Module
 * Dynamic navigation style switching with localStorage persistence
 */

(function() {
    'use strict';

    const NAV_STYLES = ['unified', 'bottom-tab', 'floating-hud', 'contextual'];
    const STORAGE_KEY = 'nav_style';
    const DEFAULT_STYLE = 'unified';

    /**
     * Get current nav style from localStorage
     */
    function getNavStyle() {
        const saved = localStorage.getItem(STORAGE_KEY);
        return NAV_STYLES.includes(saved) ? saved : DEFAULT_STYLE;
    }

    /**
     * Apply nav style to the document
     */
    function applyNavStyle(style) {
        if (!NAV_STYLES.includes(style)) {
            style = DEFAULT_STYLE;
        }

        // Set data attribute on body
        document.body.setAttribute('data-nav-style', style);
        
        // Save to localStorage
        localStorage.setItem(STORAGE_KEY, style);

        // Update dropdown if it exists
        const select = document.getElementById('navStyleSelect');
        if (select && select.value !== style) {
            select.value = style;
        }

        // Inject/remove dynamic elements based on style
        injectNavElements(style);

        console.log('[NavStyles] Applied style:', style);
    }

    /**
     * Inject navigation elements for specific styles
     */
    function injectNavElements(style) {
        // Clean up existing injected elements
        const existingBottomNav = document.getElementById('dynamicBottomNav');
        const existingFloatingHud = document.getElementById('dynamicFloatingHud');
        
        if (existingBottomNav) existingBottomNav.remove();
        if (existingFloatingHud) existingFloatingHud.remove();

        // Get current active section for highlighting
        const activeNav = document.querySelector('.nav-item.active');
        const currentSection = activeNav?.dataset?.section || 'stream';

        if (style === 'bottom-tab') {
            injectBottomTabBar(currentSection);
        } else if (style === 'floating-hud') {
            injectFloatingHud(currentSection);
        }
    }

    /**
     * Create bottom tab bar navigation
     */
    function injectBottomTabBar(activeSection) {
        const bottomNav = document.createElement('nav');
        bottomNav.id = 'dynamicBottomNav';
        bottomNav.className = 'dynamic-bottom-nav';
        bottomNav.innerHTML = `
            <button class="bottom-nav-item${activeSection === 'home' ? ' active' : ''}" data-section="home">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                    <polyline points="9 22 9 12 15 12 15 22"/>
                </svg>
                <span>home</span>
            </button>
            <button class="bottom-nav-item${activeSection === 'stream' ? ' active' : ''}" data-section="stream">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="3" y1="12" x2="21" y2="12"/>
                    <line x1="3" y1="6" x2="21" y2="6"/>
                    <line x1="3" y1="18" x2="21" y2="18"/>
                </svg>
                <span>stream</span>
            </button>
            <button class="bottom-nav-item${activeSection === 'kx-cuts' ? ' active' : ''}" data-section="kx-cuts">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polygon points="10 8 16 12 10 16 10 8"/>
                </svg>
                <span>cuts</span>
            </button>
            <button class="bottom-nav-item${activeSection === 'circles' ? ' active' : ''}" data-section="circles">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
                <span>forums</span>
            </button>
        `;

        // Add click handlers
        bottomNav.querySelectorAll('.bottom-nav-item').forEach(btn => {
            btn.addEventListener('click', () => {
                const section = btn.dataset.section;
                navigateToSection(section);
                
                // Update active states
                bottomNav.querySelectorAll('.bottom-nav-item').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        document.body.appendChild(bottomNav);
    }

    /**
     * Create floating HUD pill navigation
     */
    function injectFloatingHud(activeSection) {
        const floatingHud = document.createElement('nav');
        floatingHud.id = 'dynamicFloatingHud';
        floatingHud.className = 'dynamic-floating-hud';
        floatingHud.innerHTML = `
            <button class="hud-nav-item${activeSection === 'home' ? ' active' : ''}" data-section="home">home</button>
            <button class="hud-nav-item${activeSection === 'stream' ? ' active' : ''}" data-section="stream">stream</button>
            <button class="hud-nav-item${activeSection === 'kx-cuts' ? ' active' : ''}" data-section="kx-cuts">cuts</button>
            <button class="hud-nav-item${activeSection === 'circles' ? ' active' : ''}" data-section="circles">forums</button>
        `;

        // Add click handlers
        floatingHud.querySelectorAll('.hud-nav-item').forEach(btn => {
            btn.addEventListener('click', () => {
                const section = btn.dataset.section;
                navigateToSection(section);
                
                // Update active states
                floatingHud.querySelectorAll('.hud-nav-item').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        document.body.appendChild(floatingHud);
    }

    /**
     * Navigate to a section (integrate with existing carousel navigation)
     */
    function navigateToSection(section) {
        // Try to use existing navigation system
        const navItem = document.querySelector(`.advanced-nav .nav-item[data-section="${section}"]`);
        if (navItem) {
            navItem.click();
        } else {
            // Fallback: dispatch custom event
            window.dispatchEvent(new CustomEvent('katanx:navigate', { detail: { section } }));
        }
    }

    /**
     * Initialize nav styles system
     */
    function init() {
        // Apply saved style immediately
        const savedStyle = getNavStyle();
        applyNavStyle(savedStyle);

        // Setup select dropdown handler
        const select = document.getElementById('navStyleSelect');
        if (select) {
            select.value = savedStyle;
            select.addEventListener('change', (e) => {
                applyNavStyle(e.target.value);
            });
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose for external use
    window.NavStyles = {
        apply: applyNavStyle,
        get: getNavStyle,
        styles: NAV_STYLES
    };

})();
