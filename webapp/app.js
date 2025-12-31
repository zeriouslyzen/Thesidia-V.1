// Katanx Web App - Security-First, High-End Mobile Interface

class ThesidiaApp {
    constructor() {
        // Load API configuration (supports local and remote endpoints)
        let apiConfig = { API_ENDPOINT: '/api/thesidia', STATUS_ENDPOINT: '/api/status' };
        try {
            // Try to load from api-config.js if available
            if (typeof window !== 'undefined' && window.API_CONFIG) {
                apiConfig = window.API_CONFIG;
            }
        } catch (e) {
            // Fallback to default local endpoints
        }

        this.apiEndpoint = apiConfig.API_ENDPOINT || '/api/thesidia'; // Backend API endpoint
        this.statusEndpoint = apiConfig.STATUS_ENDPOINT || '/api/status'; // Status endpoint
        this.conversations = [];
        this.currentConversationId = null;
        this.isProcessing = false;
        this.showThinking = false;
        this.attachedFiles = []; // Store attached files

        // User session management
        this.userId = null;
        this.sessionId = null;

        // Message tracking for regeneration
        this.messageStore = new Map(); // messageId -> {query, params, timestamp, type}

        // TTS (Text-to-Speech) system - streaming voice
        this.ttsEnabled = false; // Global toggle
        this.ttsVoice = null; // Selected voice
        this.ttsUtterance = null; // Current utterance
        this.ttsQueue = []; // Queue for streaming chunks
        this.ttsSpeaking = false;
        this.currentTTSMessageId = null;
        this.thinkingSteps = {}; // Store thinking steps per message

        // Research mode: true = fast (regular search), false = deep research
        this.fastMode = true; // Default to fast mode

        // Edge AI (WebLLM)
        this.edgeAIReady = false;
        this.edgeAILoading = false;

        this.init();

        // Initialize TTS voices when available
        if ('speechSynthesis' in window) {
            // Store reference to this for voice loading callback
            const self = this;
            // Use arrow function to preserve 'this' context
            const initTTS = () => {
                if (self && typeof self.initializeTTS === 'function') {
                    self.initializeTTS();
                }
            };
            if (speechSynthesis.getVoices().length > 0) {
                initTTS();
            } else {
                speechSynthesis.onvoiceschanged = initTTS;
            }
        }
    }

    init() {
        // Detect current page
        this.currentPage = this.detectPage();

        this.setupUserSession();

        // Initialize Edge AI (WebLLM) in background
        this.initEdgeAI();

        // Initialize color theme
        this.initColorTheme();

        // Initialize appearance settings (dark/light mode, font stacks)
        this.initAppearance();

        // Universal sidebar infrastructure - setup for ALL pages
        this.setupSidebarInfrastructure();

        // Universal scroll behaviors - setup for ALL pages
        this.setupScrollBehaviors();

        // Only setup context-specific features if on contexts page
        if (this.currentPage === 'contexts') {
            this.setupEventListeners();
            // Load local cache immediately, then upgrade to server list if available
            this.loadConversations();
            this.loadConversationsFromServer();
            this.setupAutoResize();
            this.setupKeyboardShortcuts();
        } else if (this.currentPage === 'settings') {
            // Settings pages don't need any special setup - they have their own JS
            // Just ensure sidebar infrastructure is available
        } else {
            // Minimal setup for other pages (stream, profile, etc.)
            this.setupMinimalListeners();
        }

        this.checkStatus();
        this.startStatusPolling();
    }


    async initEdgeAI(retryCount = 0) {
        if (!window.edgeInference) {
            if (retryCount < 20) { // Retry for ~20 seconds then give up silently
                if (retryCount % 5 === 0) console.log("Waiting for Edge Inference module...");
                setTimeout(() => this.initEdgeAI(retryCount + 1), 1000);
            } else {
                console.warn("Edge Inference module failed to load. Fast mode may fallback to server.");
            }
            return;
        }

        try {
            // We don't auto-load the 1.6GB model immediately to save bandwidth
            // Instead, we mark it as available
            console.log("Edge AI Module Detected. Ready for initialization.");

            // If user has a preference or we want to pre-warm, we can call init()
            // For now, we'll wait for the first edge-eligible task
        } catch (error) {
            console.error("Failed to detect Edge AI:", error);
        }
    }

    async ensureEdgeAI() {
        if (this.edgeAIReady) return true;
        if (this.edgeAILoading) return false;

        this.edgeAILoading = true;
        if (this.updateHUDStatus) this.updateHUDStatus('Loading Edge AI...');

        try {
            await window.edgeInference.init((report) => {
                // Update HUD status
                if (this.updateHUDStatus) {
                    this.updateHUDStatus(`Edge AI: ${Math.round(report.progress * 100)}%`);
                }
                // Update inline control panel status
                const edgeStatusText = document.getElementById('edgeStatusText');
                if (edgeStatusText) {
                    edgeStatusText.textContent = `${Math.round(report.progress * 100)}%`;
                }
            });
            this.edgeAIReady = true;
            this.edgeAILoading = false;
            if (this.updateHUDStatus) this.updateHUDStatus('Edge AI Ready');
            return true;
        } catch (error) {
            this.edgeAILoading = false;
            console.error("Edge AI Loading Failed:", error);
            if (this.updateHUDStatus) this.updateHUDStatus('Edge AI Failed');
            return false;
        }
    }

    detectPage() {
        const path = window.location.pathname;
        if (path.includes('stream.html') || path === '/stream.html') return 'stream';
        if (path.includes('profile.html') || path === '/profile.html') return 'profile';
        if (path.includes('archive.html') || path === '/archive.html') return 'archive';
        if (path.includes('settings/') || path.includes('/settings')) return 'settings';
        if (path.includes('search.html') || path === '/search.html') return 'search';
        return 'contexts'; // Default to contexts
    }

    // Universal sidebar setup - called once for ALL pages
    setupSidebarInfrastructure() {
        const menuBtn = document.getElementById('menuBtn');
        const sidebar = document.getElementById('leftSidebar');
        const app = document.getElementById('app');
        if (!menuBtn || !sidebar || !app) return;

        // Menu toggle
        menuBtn.addEventListener('click', () => this.toggleLeftSidebar());

        // Click katanx branding to go to stream page
        const headerBranding = document.querySelector('.header-branding');
        if (headerBranding) {
            headerBranding.style.cursor = 'pointer';
            headerBranding.addEventListener('click', () => {
                window.location.href = '/stream.html';
            });
        }

        // Swipe gesture handlers for sidebar
        this.setupSwipeGestures();

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sidebar.classList.contains('open')) {
                this.closeLeftSidebar();
            }
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('open') &&
                !sidebar.contains(e.target) &&
                !menuBtn.contains(e.target) &&
                app.contains(e.target)) {
                this.closeLeftSidebar();
            }
        });

        // Setup navigation button click handlers
        this.setupNavigation();
    }

    // Navigation setup - redirects nav-item buttons to stream.html with section hash
    // Navigation setup
    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                // If it's a link with a direct HREF, let it navigate normally
                if (item.tagName === 'A' && item.getAttribute('href')) {
                    // Do not prevent default
                    return;
                }

                // Otherwise, handle as section button
                if (item.dataset.section) {
                    e.preventDefault();
                    const section = item.dataset.section;
                    // Navigate to stream.html with the section as hash
                    window.location.href = `/stream.html#${section}`;
                }
            });
        });
    }

    setupSwipeGestures() {
        const sidebar = document.getElementById('leftSidebar');
        if (!sidebar) return;

        let touchStartX = 0;
        let touchStartY = 0;
        let touchEndX = 0;
        let touchEndY = 0;

        // Helper to check if we're on home page
        const isOnHomePage = () => {
            // Only allow sidebar swipe when explicitly on the home section
            if (window.navigationSystem && window.navigationSystem.currentSection === 'home') {
                return true;
            }
            // Fallback: only the root home pages count as home
            const path = window.location.pathname;
            return path === '/home' || path === '/index.html';
        };

        // Touch start
        document.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }, { passive: true });

        // Touch end - detect swipe
        document.addEventListener('touchend', (e) => {
            if (!touchStartX) return;

            touchEndX = e.changedTouches[0].clientX;
            touchEndY = e.changedTouches[0].clientY;

            const deltaX = touchEndX - touchStartX;
            const deltaY = Math.abs(touchEndY - touchStartY);
            const absDeltaX = Math.abs(deltaX);

            // Only trigger if horizontal swipe is dominant and significant
            if (absDeltaX > 50 && absDeltaX > deltaY) {
                const isOpen = sidebar.classList.contains('open');

                // Check if we're on home section (for carousel navigation)
                // Check multiple ways to be sure
                let isOnHome = false;
                if (window.navigationSystem) {
                    isOnHome = window.navigationSystem.currentSection === 'home';
                }
                // Also check if we're on a page that should allow sidebar swipe
                if (!isOnHome) {
                    isOnHome = isOnHomePage();
                }

                if (deltaX > 0 && !isOpen) {
                    // Swipe right to open - ONLY on home page
                    if (isOnHome) {
                        this.toggleLeftSidebar();
                    }
                    // If not on home, do nothing - let navigation.js handle it
                } else if (deltaX < 0 && isOpen) {
                    // Swipe left to close - always allowed
                    this.closeLeftSidebar();
                }
            }

            // Reset
            touchStartX = 0;
        }, { passive: true });
    }

    setupScrollBehaviors() {
        // Scroll-based UI behaviors with high sensitivity and synchronized animations
        // Works on ALL pages that have header-submenu and fab-orb
        let ticking = false;
        let lastScrollTop = 0;

        const headerSubmenu = document.querySelector('.header-submenu');
        const fabOrb = document.getElementById('fabOrb');
        const fabOrbGlow = fabOrb ? fabOrb.querySelector('.fab-orb-glow') : null;
        const scrollContainers = document.querySelectorAll('.carousel-section');
        const mainScrollContainer = document.querySelector('main') || document.querySelector('.chat-container') || window;

        // High sensitivity scroll threshold - reacts to small movements
        const scrollThreshold = 20; // Very sensitive - reacts after 20px
        const maxScrollForFullEffect = 100; // Full effect at 100px scroll

        function updateScrollState() {
            let currentScrollTop = 0;
            let activeContainer = null;
            let scrollDirection = 'none';

            // Find the active scroll container (carousel sections first)
            scrollContainers.forEach(container => {
                if (container.classList.contains('active')) {
                    activeContainer = container;
                    currentScrollTop = container.scrollTop;
                }
            });

            // Fallback to main scroll container or window
            if (!activeContainer) {
                if (mainScrollContainer && mainScrollContainer !== window) {
                    currentScrollTop = mainScrollContainer.scrollTop || 0;
                } else {
                    currentScrollTop = window.scrollY || document.documentElement.scrollTop;
                }
            }

            // Calculate scroll progress (0 to 1) for smooth proportional animations
            const scrollProgress = Math.min(currentScrollTop / maxScrollForFullEffect, 1);
            const scrollDelta = currentScrollTop - lastScrollTop;
            if (scrollDelta > 2) scrollDirection = 'down';
            if (scrollDelta < -2) scrollDirection = 'up';

            // High sensitivity: Update on any scroll movement
            if (Math.abs(scrollDelta) > 0) {
                const header = document.querySelector('.header');

                // Update header - add scrolled class
                if (header) {
                    if (scrollDirection === 'down' && currentScrollTop > scrollThreshold) {
                        header.classList.add('scrolled-down');
                    } else if (scrollDirection === 'up') {
                        header.classList.remove('scrolled-down');
                    }
                }

                // Update header submenu - FIXED: use CSS variable instead of direct manipulation
                if (headerSubmenu) {
                    // Set CSS variable - let CSS handle the animation
                    headerSubmenu.style.setProperty('--scroll-progress', scrollProgress);

                    // Add class for CSS transitions (no direct style manipulation)
                    if (scrollDirection === 'down' && currentScrollTop > scrollThreshold) {
                        headerSubmenu.classList.add('scrolled-down');
                    } else if (scrollDirection === 'up') {
                        headerSubmenu.classList.remove('scrolled-down');
                    }
                }

                // Update FAB orb - FIXED: use CSS variable, removed expensive box-shadow recalculations
                if (fabOrb) {
                    // Set CSS variable - let CSS handle opacity transitions
                    fabOrb.style.setProperty('--scroll-progress', scrollProgress);

                    // Add class for state tracking and CSS transitions
                    if (scrollDirection === 'down' && currentScrollTop > scrollThreshold) {
                        fabOrb.classList.remove('scrolled-up');
                        fabOrb.classList.add('scrolled-down');
                    } else if (scrollDirection === 'up') {
                        fabOrb.classList.remove('scrolled-down');
                        fabOrb.classList.add('scrolled-up');
                    }
                }
            }

            lastScrollTop = currentScrollTop;
            ticking = false;
        }

        function onScroll() {
            if (!ticking) {
                window.requestAnimationFrame(updateScrollState);
                ticking = true;
            }
        }

        // Attach scroll listeners with high sensitivity
        scrollContainers.forEach(container => {
            container.addEventListener('scroll', onScroll, { passive: true });
        });

        // Main scroll container
        if (mainScrollContainer && mainScrollContainer !== window) {
            mainScrollContainer.addEventListener('scroll', onScroll, { passive: true });
        }

        // Window scroll fallback
        window.addEventListener('scroll', onScroll, { passive: true });

        // Touch events for mobile sensitivity
        let touchStartY = 0;
        document.addEventListener('touchstart', (e) => {
            touchStartY = e.touches[0].clientY;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            const touchY = e.touches[0].clientY;
            const touchDelta = touchStartY - touchY;
            if (Math.abs(touchDelta) > 5) { // High sensitivity for touch
                onScroll();
            }
        }, { passive: true });

        // Initialize state
        updateScrollState();
    }

    initColorTheme() {
        // Load saved theme from localStorage
        const savedTheme = localStorage.getItem('thesidia_color_theme') || 'default';
        this.setColorTheme(savedTheme);

        // Setup theme selector in sidebar if it exists
        this.setupThemeSelector();
    }

    setColorTheme(theme) {
        // Remove all theme classes
        document.body.classList.remove('theme-yellow', 'theme-tan', 'theme-red', 'theme-orange', 'theme-blue');
        document.documentElement.classList.remove('theme-yellow', 'theme-tan', 'theme-red', 'theme-orange', 'theme-blue');

        // Apply new theme (default doesn't need a class)
        if (theme && theme !== 'default') {
            document.body.classList.add(`theme-${theme}`);
            document.documentElement.classList.add(`theme-${theme}`);
        }

        // Save to localStorage
        localStorage.setItem('thesidia_color_theme', theme || 'default');
    }

    setupThemeSelector() {
        // Find or create theme selector in sidebar settings
        const settingsNav = document.querySelector('.settings-nav');
        if (!settingsNav) return;

        // Check if theme selector already exists
        if (document.getElementById('themeSelector')) return;

        // Create theme selector
        const themeSelector = document.createElement('div');
        themeSelector.id = 'themeSelector';
        themeSelector.className = 'theme-selector';
        const currentTheme = localStorage.getItem('thesidia_color_theme') || 'default';
        const themeLabels = {
            'default': 'Default',
            'yellow': 'Yellow',
            'tan': 'Tan',
            'red': 'Red',
            'orange': 'Orange',
            'blue': 'Blue'
        };

        themeSelector.innerHTML = `
            <div class="settings-label" style="margin-top: 16px;">Color Theme</div>
            <div class="theme-dropdown-wrapper">
                <button class="theme-dropdown-btn" id="themeDropdownBtn">
                    <span class="theme-dropdown-label">
                        <span class="theme-color-preview" style="background: ${currentTheme === 'default' ? '#ffffff' : currentTheme === 'yellow' ? '#d4d400' : currentTheme === 'tan' ? '#d2b48c' : currentTheme === 'red' ? '#ff4444' : currentTheme === 'orange' ? '#ff8800' : '#4488ff'};"></span>
                        <span>${themeLabels[currentTheme]}</span>
                    </span>
                    <svg class="theme-dropdown-arrow" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                </button>
                <div class="theme-dropdown-menu" id="themeDropdownMenu">
                    <button class="theme-dropdown-option ${currentTheme === 'default' ? 'active' : ''}" data-theme="default">
                        <span class="theme-color" style="background: #ffffff;"></span>
                        <span>Default</span>
                    </button>
                    <button class="theme-dropdown-option ${currentTheme === 'yellow' ? 'active' : ''}" data-theme="yellow">
                        <span class="theme-color" style="background: #d4d400;"></span>
                        <span>Yellow</span>
                    </button>
                    <button class="theme-dropdown-option ${currentTheme === 'tan' ? 'active' : ''}" data-theme="tan">
                        <span class="theme-color" style="background: #d2b48c;"></span>
                        <span>Tan</span>
                    </button>
                    <button class="theme-dropdown-option ${currentTheme === 'red' ? 'active' : ''}" data-theme="red">
                        <span class="theme-color" style="background: #ff4444;"></span>
                        <span>Red</span>
                    </button>
                    <button class="theme-dropdown-option ${currentTheme === 'orange' ? 'active' : ''}" data-theme="orange">
                        <span class="theme-color" style="background: #ff8800;"></span>
                        <span>Orange</span>
                    </button>
                    <button class="theme-dropdown-option ${currentTheme === 'blue' ? 'active' : ''}" data-theme="blue">
                        <span class="theme-color" style="background: #4488ff;"></span>
                        <span>Blue</span>
                    </button>
                </div>
            </div>
        `;

        // Insert after settings nav
        settingsNav.parentElement.appendChild(themeSelector);

        // Setup dropdown toggle
        const dropdownBtn = document.getElementById('themeDropdownBtn');
        const dropdownMenu = document.getElementById('themeDropdownMenu');
        const dropdownWrapper = dropdownBtn?.closest('.theme-dropdown-wrapper');

        if (dropdownBtn && dropdownMenu && dropdownWrapper) {
            dropdownBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdownWrapper.classList.toggle('open');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!dropdownWrapper.contains(e.target)) {
                    dropdownWrapper.classList.remove('open');
                }
            });

            // Handle option clicks
            dropdownMenu.querySelectorAll('.theme-dropdown-option').forEach(option => {
                option.addEventListener('click', () => {
                    const theme = option.dataset.theme;
                    this.setColorTheme(theme);

                    // Update button label
                    const label = dropdownBtn.querySelector('.theme-dropdown-label span:last-child');
                    const preview = dropdownBtn.querySelector('.theme-color-preview');
                    if (label) label.textContent = themeLabels[theme];
                    if (preview) {
                        const colors = {
                            'default': '#ffffff',
                            'yellow': '#d4d400',
                            'tan': '#d2b48c',
                            'red': '#ff4444',
                            'orange': '#ff8800',
                            'blue': '#4488ff'
                        };
                        preview.style.background = colors[theme];
                    }

                    // Update active state
                    dropdownMenu.querySelectorAll('.theme-dropdown-option').forEach(opt => opt.classList.remove('active'));
                    option.classList.add('active');

                    // Close dropdown
                    dropdownWrapper.classList.remove('open');
                });
            });
        }
    }

    initAppearance() {
        // Load saved appearance settings from localStorage
        const savedThemeMode = localStorage.getItem('kx_theme_mode') || 'dark';
        const savedFontStack = localStorage.getItem('kx_font_stack') || 'cyberx';

        // Apply saved settings to document
        this.setThemeMode(savedThemeMode);
        this.setFontStack(savedFontStack);

        // Setup UI controls
        this.setupAppearanceControls();
    }

    setThemeMode(mode) {
        // Set data attribute on html element
        document.documentElement.setAttribute('data-theme', mode);
        localStorage.setItem('kx_theme_mode', mode);

        // Update meta theme-color for browser chrome
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', mode === 'light' ? '#f5f0e8' : '#000000');
        }
    }

    setFontStack(stack) {
        // Set data attribute on html element
        document.documentElement.setAttribute('data-font-stack', stack);
        localStorage.setItem('kx_font_stack', stack);
    }

    setupAppearanceControls() {
        // Theme toggle buttons
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const themeBtns = themeToggle.querySelectorAll('.theme-btn');
            const currentMode = localStorage.getItem('kx_theme_mode') || 'dark';

            // Set initial active state
            themeBtns.forEach(btn => {
                btn.classList.toggle('active', btn.dataset.theme === currentMode);
            });

            // Add click handlers
            themeBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const mode = btn.dataset.theme;
                    this.setThemeMode(mode);

                    // Update active states
                    themeBtns.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                });
            });
        }

        // Font stack selector
        const fontStackSelect = document.getElementById('fontStackSelect');
        if (fontStackSelect) {
            const currentStack = localStorage.getItem('kx_font_stack') || 'cyberx';
            fontStackSelect.value = currentStack;

            fontStackSelect.addEventListener('change', (e) => {
                this.setFontStack(e.target.value);
            });
        }
    }

    setupMinimalListeners() {
        try {
            // Profile picture upload (if on pages with sidebar)
            const profilePictureContainer = document.getElementById('profilePictureContainer');
            const profileImageInput = document.getElementById('profileImageInput');
            const profilePicture = document.getElementById('profilePicture');

            if (profilePictureContainer && profileImageInput) {
                // Load saved profile picture from localStorage
                const savedProfileImage = localStorage.getItem('profileImage');
                if (savedProfileImage && profilePicture) {
                    profilePicture.src = savedProfileImage;
                }

                // Click to upload
                profilePictureContainer.addEventListener('click', () => {
                    profileImageInput.click();
                });

                // Handle image selection
                profileImageInput.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (file && file.type.startsWith('image/') && profilePicture) {
                        this.handleProfileImageUpload(file, profilePicture);
                    }
                });
            }

            // Submenu filter items (Friends, Fans, Communities, Labs)
            const submenuFilters = document.querySelectorAll('.submenu-item[data-filter]');
            submenuFilters.forEach(item => {
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    const filterType = item.dataset.filter;

                    // Update active state
                    submenuFilters.forEach(i => i.classList.remove('active'));
                    item.classList.add('active');

                    // Set filter type in localStorage
                    localStorage.setItem('feed_type', filterType);

                    // If on stream page, reload feed; otherwise navigate to stream
                    if (this.currentPage === 'stream') {
                        // Trigger reload if stream page is loaded
                        const streamPage = window.streamPage;
                        if (streamPage && typeof streamPage.loadPosts === 'function') {
                            streamPage.currentPage = 0;
                            streamPage.posts = [];
                            streamPage.loadPosts(0, 20);
                        }
                    } else {
                        // Navigate to stream page with filter applied
                        window.location.href = '/stream.html';
                    }
                });
            });

            // Set active filter on page load
            const currentFilter = localStorage.getItem('feed_type');
            if (currentFilter && ['friends', 'fans', 'communities', 'labs'].includes(currentFilter)) {
                const activeFilter = document.querySelector(`.submenu-item[data-filter="${currentFilter}"]`);
                if (activeFilter) {
                    activeFilter.classList.add('active');
                }
            }
        } catch (error) {
            console.error('Error setting up minimal listeners:', error);
        }

        // FAB orb haptics (best-effort; vibrate when supported)
        try {
            const fabOrb = document.getElementById('fabOrb');
            if (fabOrb) {
                // Avoid duplicate handlers
                fabOrb.replaceWith(fabOrb.cloneNode(true));
                const freshFabOrb = document.getElementById('fabOrb');
                if (freshFabOrb) {
                    freshFabOrb.addEventListener('click', () => {
                        if (navigator.vibrate) {
                            navigator.vibrate(15); // short haptic
                        }
                    });
                }
            }
        } catch (err) {
            console.warn('FAB haptic setup failed:', err);
        }
    }

    async setupUserSession() {
        // Get user session from localStorage or create new one
        this.userId = localStorage.getItem('thesidia_user_id');
        this.sessionId = localStorage.getItem('thesidia_session_id');

        // AUTHENTICATION DISABLED: Auto-create session if none exists
        // No redirect to auth page - allow anonymous access

        try {
            const response = await fetch('/api/user/session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                // Session invalid - create new anonymous session instead of redirecting
                console.log('Session invalid, creating new anonymous session');
                this.userId = null;
                this.sessionId = null;
                // Try again with null values to create new session
                const retryResponse = await fetch('/api/user/session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: null,
                        session_id: null
                    })
                });

                if (retryResponse.ok) {
                    const userData = await retryResponse.json();
                    this.userId = userData.user_id;
                    this.sessionId = userData.session_id;
                    localStorage.setItem('thesidia_user_id', this.userId);
                    localStorage.setItem('thesidia_session_id', this.sessionId);
                    console.log('Created new anonymous session:', { user_id: this.userId, session_id: this.sessionId });
                } else {
                    // If session creation fails, continue without session (graceful degradation)
                    console.warn('Could not create session, continuing without authentication');
                    this.userId = 'anonymous_' + Date.now();
                    this.sessionId = 'session_' + Date.now();
                }
            } else {
                const userData = await response.json();
                this.userId = userData.user_id;
                this.sessionId = userData.session_id;

                // Store in localStorage
                localStorage.setItem('thesidia_user_id', this.userId);
                localStorage.setItem('thesidia_session_id', this.sessionId);
            }

            // Load user profile (if available)
            await this.loadUserProfile();

            console.log('User session initialized:', { user_id: this.userId, session_id: this.sessionId });
        } catch (error) {
            console.error('Error setting up user session:', error);
            // AUTHENTICATION DISABLED: Continue without session instead of redirecting
            // Create fallback anonymous session
            if (!this.userId || !this.sessionId) {
                this.userId = 'anonymous_' + Date.now();
                this.sessionId = 'session_' + Date.now();
                localStorage.setItem('thesidia_user_id', this.userId);
                localStorage.setItem('thesidia_session_id', this.sessionId);
                console.log('Created fallback anonymous session:', { user_id: this.userId, session_id: this.sessionId });
            }
        }
    }

    async loadUserProfile() {
        if (!this.userId) return;

        try {
            // Try to get profile from settings
            const response = await fetch(`/api/settings?user_id=${this.userId}&session_id=${this.sessionId}`);
            if (response.ok) {
                const settings = await response.json();
                const account = settings.get?.('account', {}) || settings.account || {};

                // Update sidebar profile if elements exist
                const profileName = document.getElementById('sidebarProfileName');
                const profileTag = document.getElementById('sidebarProfileTag');

                if (profileName) {
                    profileName.textContent = account.display_name || account.username || 'User';
                }
                if (profileTag) {
                    profileTag.textContent = account.username ? `@${account.username}` : '@user';
                }
            }
        } catch (error) {
            console.error('Error loading user profile:', error);
            // Set defaults
            const profileName = document.getElementById('sidebarProfileName');
            const profileTag = document.getElementById('sidebarProfileTag');
            if (profileName) profileName.textContent = 'User';
            if (profileTag) profileTag.textContent = '@user';
        }
    }

    async exportConversation() {
        if (!this.userId && !this.sessionId) {
            alert('No user session found. Please refresh the page.');
            return;
        }

        try {
            const response = await fetch('/api/user/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error('Export failed');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `thesidia_conversation_${this.userId || 'export'}_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting conversation:', error);
            alert('Error exporting conversation. Please try again.');
        }
    }

    async checkStatus() {
        try {
            const response = await fetch(this.statusEndpoint);
            const data = await response.json();

            this.updateStatusIndicators(data);
        } catch (error) {
            console.error('Status check error:', error);
            this.updateStatusIndicators({
                ollama_status: false,
                thesidia_ready: false
            });
        }
    }

    updateStatusIndicators(status) {
        const ollamaStatus = document.getElementById('ollamaStatus');
        const thesidiaStatus = document.getElementById('thesidiaStatus');

        // Status indicators only exist on contexts page - silently return if not found
        if (!ollamaStatus || !thesidiaStatus) {
            return;
        }

        // Ollama status
        const ollamaDot = ollamaStatus.querySelector('.status-dot');
        if (ollamaDot) {
            if (status.ollama_status) {
                ollamaDot.classList.add('online');
                ollamaDot.classList.remove('offline');
            } else {
                ollamaDot.classList.add('offline');
                ollamaDot.classList.remove('online');
            }
        }

        // Thesidia status
        const thesidiaDot = thesidiaStatus.querySelector('.status-dot');
        if (thesidiaDot) {
            if (status.thesidia_ready && status.ollama_status) {
                thesidiaDot.classList.add('ready');
                thesidiaDot.classList.remove('offline');
            } else {
                thesidiaDot.classList.add('offline');
                thesidiaDot.classList.remove('ready');
            }
        }
    }

    startStatusPolling() {
        // Check status every 5 seconds
        setInterval(() => {
            this.checkStatus();
        }, 5000);
    }

    setupEventListeners() {
        try {
            // Send button
            const sendBtn = document.getElementById('sendBtn');
            const promptInput = document.getElementById('promptInput');

            if (!sendBtn || !promptInput) {
                console.error('Critical elements not found: sendBtn or promptInput');
                return;
            }

            sendBtn.addEventListener('click', () => this.sendMessage());
            promptInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Auto-resize textarea and update cursor placeholder
            promptInput.addEventListener('input', () => {
                this.autoResizeTextarea(promptInput);
                this.updateCursorPlaceholder();
            });

            // Update cursor placeholder on focus/blur
            promptInput.addEventListener('focus', () => this.updateCursorPlaceholder());
            promptInput.addEventListener('blur', () => this.updateCursorPlaceholder());

            // Initial cursor placeholder state
            this.updateCursorPlaceholder();

            // Set active nav item based on current page
            this.setActiveNavItem();

            // Profile picture upload
            const profilePictureContainer = document.getElementById('profilePictureContainer');
            const profileImageInput = document.getElementById('profileImageInput');
            const profilePicture = document.getElementById('profilePicture');

            if (profilePictureContainer && profileImageInput) {
                // Load saved profile picture from localStorage
                const savedProfileImage = localStorage.getItem('profileImage');
                if (savedProfileImage && profilePicture) {
                    profilePicture.src = savedProfileImage;
                }

                // Click to upload
                profilePictureContainer.addEventListener('click', () => {
                    profileImageInput.click();
                });

                // Handle image selection
                profileImageInput.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (file && file.type.startsWith('image/') && profilePicture) {
                        this.handleProfileImageUpload(file, profilePicture);
                    }
                });
            }

            // New chat
            const newChatBtn = document.getElementById('newChatBtn');
            if (newChatBtn) newChatBtn.addEventListener('click', () => this.newConversation());

            const exportBtn = document.getElementById('exportBtn');
            if (exportBtn) exportBtn.addEventListener('click', () => this.exportConversation());
        } catch (error) {
            console.error('Error setting up event listeners:', error);
        }

        // Thinking toggle
        const thinkingToggle = document.getElementById('showThinkingToggle');
        if (thinkingToggle) {
            thinkingToggle.addEventListener('change', (e) => {
                this.showThinking = e.target.checked;
                const thinkingBtn = document.getElementById('thinkingBtn');
                if (thinkingBtn) {
                    if (this.showThinking) {
                        thinkingBtn.classList.add('active');
                    } else {
                        thinkingBtn.classList.remove('active');
                    }
                }
            });
        }

        // Deep research toggle
        const deepResearchToggle = document.getElementById('deepResearchToggle');
        if (deepResearchToggle) {
            deepResearchToggle.addEventListener('change', (e) => {
                this.deepResearchMode = e.target.checked;
                // Disable auto-detect when manual mode is enabled
                if (this.deepResearchMode) {
                    const autoDetectToggle = document.getElementById('autoDetectToggle');
                    if (autoDetectToggle) {
                        autoDetectToggle.checked = false;
                        this.autoDetect = false;
                    }
                }
            });
        }

        // Format selector and depth slider are handled in advanced options section below

        // Toggle thinking display
        const toggleThinking = document.getElementById('toggleThinking');
        if (toggleThinking) {
            toggleThinking.addEventListener('click', () => {
                const thinkingSteps = document.getElementById('thinkingSteps');
                if (thinkingSteps) {
                    if (thinkingSteps.style.display === 'none') {
                        thinkingSteps.style.display = 'block';
                        toggleThinking.textContent = 'Hide';
                    } else {
                        thinkingSteps.style.display = 'none';
                        toggleThinking.textContent = 'Show';
                    }
                }
            });
        }

        // HUD Module Panel Toggle with Animation
        const hudModuleToggle = document.getElementById('hudModuleToggle');
        const hudModulePanel = document.getElementById('hudModulePanel');
        const hudModules = document.querySelectorAll('.hud-module[data-module]');

        // Load saved panel state
        const savedPanelState = localStorage.getItem('hudPanelOpen') === 'true';

        const togglePanel = (show) => {
            if (!hudModulePanel) return;

            if (show) {
                hudModulePanel.style.display = 'block';
                // Trigger reflow for animation
                setTimeout(() => {
                    hudModulePanel.classList.add('show');
                }, 10);
                hudModuleToggle?.classList.add('active');
                localStorage.setItem('hudPanelOpen', 'true');
            } else {
                hudModulePanel.classList.remove('show');
                setTimeout(() => {
                    hudModulePanel.style.display = 'none';
                }, 300);
                hudModuleToggle?.classList.remove('active');
                localStorage.setItem('hudPanelOpen', 'false');
            }
        };

        if (hudModuleToggle && hudModulePanel) {
            // Initialize panel state
            if (savedPanelState) {
                togglePanel(true);
            }

            hudModuleToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = hudModulePanel.classList.contains('show');
                togglePanel(!isVisible);
            });

            // Make modules clickable to open panel
            hudModules.forEach(module => {
                module.addEventListener('click', (e) => {
                    e.stopPropagation();
                    if (!hudModulePanel.classList.contains('show')) {
                        togglePanel(true);
                    }
                });
            });

            // Click outside to close
            document.addEventListener('click', (e) => {
                if (hudModulePanel.classList.contains('show') &&
                    !hudModulePanel.contains(e.target) &&
                    !hudModuleToggle.contains(e.target) &&
                    !Array.from(hudModules).some(m => m.contains(e.target))) {
                    togglePanel(false);
                }
            });

            // Auto-hide after selection (2s delay)
            const controlButtons = document.querySelectorAll('.hud-control-btn');
            controlButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    setTimeout(() => {
                        if (hudModulePanel.classList.contains('show')) {
                            togglePanel(false);
                        }
                    }, 2000);
                });
            });
        }

        // File upload
        const fileInput = document.getElementById('fileInput');
        const attachBtn = document.getElementById('attachBtn');
        const attachedFiles = document.getElementById('attachedFiles');
        if (attachBtn && fileInput) {
            attachBtn.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', (e) => {
                this.handleFileUpload(e.target.files, attachedFiles);
            });
        }

        // Control Panel
        this.setupControlPanel();

        // Format selector (HUD controls)
        // Removed all format/depth controls - Thesidia determines these automatically

        // Status display updates
        const statusDisplay = document.getElementById('statusDisplay');
        if (statusDisplay) {
            // Update status based on connection
            this.updateHUDStatus = (status) => {
                if (statusDisplay) {
                    const statusMap = {
                        'ready': 'RDY',
                        'processing': 'PRC',
                        'streaming': 'STR',
                        'error': 'ERR',
                        'offline': 'OFF'
                    };
                    statusDisplay.textContent = statusMap[status] || 'RDY';
                }
            };

            // Check initial status
            this.checkStatus().then(() => {
                this.updateHUDStatus('ready');
            }).catch(() => {
                this.updateHUDStatus('offline');
            });
        }
    }

    handleFileUpload(files, container) {
        if (!files || files.length === 0) return;

        container.style.display = 'flex';
        container.innerHTML = '';

        Array.from(files).forEach((file, index) => {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'hud-attached-file';
            const fileName = file.name.length > 15 ? file.name.substring(0, 12) + '...' : file.name;
            fileDiv.innerHTML = `
                <span>${fileName}</span>
                <button onclick="this.parentElement.remove(); if(document.getElementById('attachedFiles').children.length === 0) document.getElementById('attachedFiles').style.display = 'none';" aria-label="Remove file">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            `;
            container.appendChild(fileDiv);
        });

        // Store files for sending
        this.attachedFiles = Array.from(files);
    }

    setupAutoResize() {
        const promptInput = document.getElementById('promptInput');
        if (!promptInput) return; // Element doesn't exist on this page
        promptInput.addEventListener('input', () => {
            promptInput.style.height = 'auto';
            promptInput.style.height = Math.min(promptInput.scrollHeight, 200) + 'px';
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Cmd/Ctrl + K for new chat
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.newConversation();
            }

            // Escape to close sidebar
            if (e.key === 'Escape') {
                this.closeLeftSidebar();
            }
        });
    }

    async sendMessage() {
        const promptInput = document.getElementById('promptInput');
        const message = promptInput.value.trim();

        if (!message || this.isProcessing) return;

        // Clear input
        promptInput.value = '';
        promptInput.style.height = 'auto';
        this.updateCursorPlaceholder();

        // Add user message
        this.addMessage('user', message);

        // Show typing indicator
        this.showTypingIndicator();

        // Disable send button
        this.isProcessing = true;
        this.updateSendButton();
        if (this.updateHUDStatus) this.updateHUDStatus('processing');

        try {
            console.log('Calling Thesidia API with message:', message);

            // Phase 3: Edge AI Pre-processing (Bot Detection / Sentiment)
            // if (this.edgeAIReady) {
            //     console.log("Running Edge AI Bot Detection...");
            //     window.edgeInference.classifyBot(message).then(analysis => {
            //         console.log("Edge AI Analysis:", analysis);
            //         if (analysis.is_bot && analysis.confidence > 0.8) {
            //             console.warn("Edge AI detected high bot probability:", analysis.reason);
            //             // We could flag the message here or show a warning
            //         }
            //     });
            // }

            // Send to backend (streaming handles UI updates)
            await this.callThesidiaAPI(message);

            // Hide typing indicator (streaming will handle this)
            this.hideTypingIndicator();

        } catch (error) {
            console.error('Error:', error);
            this.hideTypingIndicator();
            this.addMessage('thesidia', 'Error: Could not process request. Please try again.');
            if (this.updateHUDStatus) this.updateHUDStatus('error');
        } finally {
            this.isProcessing = false;
            this.updateSendButton();
            if (this.updateHUDStatus) this.updateHUDStatus('ready');
        }
    }

    async callThesidiaAPI(message) {
        // Security: Sanitize input
        let sanitizedMessage = this.sanitizeInput(message);

        // Format and depth are now controlled by UI, not auto-detection

        // Preserve this context for nested callbacks
        const self = this;

        // Use streaming by default
        return new Promise((resolve, reject) => {
            // Generate message ID for tracking
            const messageId = this.generateMessageId();

            // Initialize thinking steps storage for this message
            if (!self.thinkingSteps[messageId]) {
                self.thinkingSteps[messageId] = [];
            }

            // Use streaming by default
            const useStreaming = true; // Enable streaming for better UX

            // Store query data for regeneration
            const queryData = {
                query: sanitizedMessage,
                params: {
                    conversation_id: this.currentConversationId,
                    show_thinking: this.showThinking,
                    stream: useStreaming,
                    user_id: this.userId,
                    session_id: this.sessionId
                }
            };

            // Create message element for streaming
            const messagesContainer = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message thesidia';
            messageDiv.setAttribute('data-message-id', messageId);

            // Add identity header
            const identityHeader = document.createElement('div');
            identityHeader.className = 'message-identity';
            identityHeader.textContent = 'THESIDIA';
            messageDiv.appendChild(identityHeader);

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';

            const textElement = document.createElement('p');
            textElement.textContent = '';
            contentDiv.appendChild(textElement);

            messageDiv.appendChild(contentDiv);
            messagesContainer.appendChild(messageDiv);

            // Store message data for regeneration
            this.messageStore.set(messageId, {
                query: sanitizedMessage,
                params: queryData.params,
                timestamp: new Date().toISOString(),
                type: 'thesidia'
            });

            // Progress indicator - Better styling
            const progressDiv = document.createElement('div');
            progressDiv.className = 'progress-indicator';
            progressDiv.style.display = 'none';
            progressDiv.style.marginTop = '12px';
            messageDiv.appendChild(progressDiv);

            // Cool reasoning visualization (always show, but styled differently)
            const reasoningDiv = document.createElement('div');
            reasoningDiv.className = 'reasoning-visualization';
            reasoningDiv.style.display = 'none';
            reasoningDiv.innerHTML = `
                <div class="reasoning-container">
                    <div class="reasoning-thoughts">
                        <div class="reasoning-thought active">Analyzing query...</div>
                        <div class="reasoning-thought">Routing to best system...</div>
                        <div class="reasoning-thought">Gathering context...</div>
                        <div class="reasoning-thought">Synthesizing response...</div>
                    </div>
                    <div class="reasoning-progress">
                        <div class="reasoning-bar"></div>
                    </div>
                </div>
            `;
            messageDiv.appendChild(reasoningDiv);

            // Thinking indicator (if enabled - for detailed steps)
            let thinkingDiv = null;
            if (this.showThinking) {
                thinkingDiv = document.createElement('div');
                thinkingDiv.className = 'thinking-indicator';
                thinkingDiv.style.display = 'none';
                thinkingDiv.style.marginTop = '8px';
                messageDiv.appendChild(thinkingDiv);
            }

            // Use fetch - handle both streaming and non-streaming
            console.log('Making fetch request to:', this.apiEndpoint, { message: sanitizedMessage });
            // Abort + timeout protection (prevents hanging UI on stalled streams)
            const controller = new AbortController();
            const timeoutMs = 600000; // 10 minutes (increased for deep research mode)
            const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

            const doFetch = (attempt = 0) => fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: sanitizedMessage,
                    conversation_id: this.currentConversationId,
                    show_thinking: this.showThinking,
                    stream: useStreaming,
                    user_id: this.userId,
                    session_id: this.sessionId,
                    fast_mode: this.fastMode,
                    research_depth: this.fastMode ? 1 : 3
                }),
                signal: controller.signal
            }).then(response => {
                // WATCHDOG: Clear the initial connection timeout
                clearTimeout(timeoutId);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const contentType = response.headers.get('content-type') || '';

                if (useStreaming && contentType.includes('text/event-stream')) {
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = '';
                    let fullResponse = '';
                    let currentEvent = null;

                    // STREAM WATCHDOG: Detect hung streams
                    let watchdogTimer = null;
                    const WATCHDOG_TIMEOUT = 8000; // 8 seconds silence = reconnect

                    const resetWatchdog = () => {
                        if (watchdogTimer) clearTimeout(watchdogTimer);
                        watchdogTimer = setTimeout(() => {
                            console.warn("Stream stalled (Watchdog triggered). Aborting and retrying...");
                            reader.cancel();
                            controller.abort();
                            // This rejection will be caught by the outer catch, triggering retry logic
                            reject(new Error("Stream stalled"));
                        }, WATCHDOG_TIMEOUT);
                    };

                    const readChunk = () => {
                        resetWatchdog(); // Pulse the watchdog

                        reader.read().then(({ done, value }) => {
                            if (done) {
                                if (watchdogTimer) clearTimeout(watchdogTimer);

                                // VALIDATION: streaming completed but empty?
                                if (!fullResponse.trim()) {
                                    throw new Error("Empty streaming response");
                                }

                                self.hideTypingIndicator();
                                if (progressDiv.parentNode) progressDiv.style.display = 'none';
                                self.scrollToBottom();
                                self.saveConversation(sanitizedMessage, fullResponse);

                                if (fullResponse && fullResponse.trim().length > 0) {
                                    self.addMessageActions(messageDiv, 'thesidia', fullResponse, messageId, queryData);
                                }

                                resolve(fullResponse);
                                return;
                            }

                            buffer += decoder.decode(value, { stream: true });
                            const lines = buffer.split('\n');
                            buffer = lines.pop() || '';

                            for (const line of lines) {
                                if (line.trim() === '') continue;
                                if (line.startsWith('event: ')) {
                                    currentEvent = line.substring(7).trim();
                                    continue;
                                }
                                if (line.startsWith('data: ')) {
                                    try {
                                        const data = JSON.parse(line.substring(6));

                                        // Standard processing...
                                        if (data.phase === 'progress' || currentEvent === 'progress') {
                                            if (reasoningDiv) {
                                                reasoningDiv.style.display = 'block';
                                                const thoughts = reasoningDiv.querySelectorAll('.reasoning-thought');
                                                const thoughtIndex = Math.min(Math.floor(data.progress / 25), thoughts.length - 1);
                                                thoughts.forEach((thought, idx) => thought.classList.toggle('active', idx === thoughtIndex));
                                                const progressBar = reasoningDiv.querySelector('.reasoning-bar');
                                                if (progressBar) progressBar.style.width = `${data.progress}%`;
                                            }
                                            progressDiv.style.display = 'block';
                                            progressDiv.textContent = `${data.message} (${Math.round(data.progress)}%)`;
                                            progressDiv.className = 'progress-indicator active';
                                            this.scrollToBottom();
                                        } else if (data.text || currentEvent === 'chunk') {
                                            const chunk = data.text || '';
                                            if (reasoningDiv && chunk.length > 0) reasoningDiv.style.display = 'none';
                                            fullResponse += chunk;

                                            if (self.updateHUDStatus && chunk.length > 0) self.updateHUDStatus('streaming');

                                            // Hide loading indicators on first token
                                            if (chunk.length > 0) {
                                                if (progressDiv.style.display !== 'none') progressDiv.style.display = 'none';
                                            }

                                            self.typeText(textElement, chunk, () => self.scrollToBottom());
                                            if (self.ttsEnabled && self.speakChunk) self.speakChunk(chunk, messageId);

                                        } else if (currentEvent === 'thinking' || data.thinking) {
                                            // Thinking logic...
                                            if (!self.thinkingSteps[messageId]) self.thinkingSteps[messageId] = [];
                                            self.thinkingSteps[messageId].push({
                                                step: data.step || 'thinking',
                                                message: data.message || data.thinking,
                                                timestamp: new Date().toISOString()
                                            });
                                            if (self.showThinking) {
                                                self.displayThinkingStep(data.step || 'thinking', data.message || data.thinking);
                                                if (thinkingDiv) {
                                                    thinkingDiv.style.display = 'block';
                                                    thinkingDiv.textContent = `${data.message || data.thinking}`;
                                                }
                                            }
                                        } else if (data.phase === 'complete' || currentEvent === 'complete') {
                                            progressDiv.style.display = 'none';
                                            self.hideTypingIndicator();
                                            if (self.updateHUDStatus) self.updateHUDStatus('ready');
                                            if (fullResponse && fullResponse.trim().length > 0) {
                                                self.addMessageActions(messageDiv, 'thesidia', fullResponse, messageId, queryData);
                                            }
                                        } else if (data.error || currentEvent === 'error') {
                                            throw new Error(data.message || data.error || 'Unknown error');
                                        }
                                    } catch (e) {
                                        console.error('Error parsing SSE data:', e, line);
                                    }
                                    currentEvent = null;
                                }
                            }
                            readChunk();
                        }).catch(err => {
                            if (watchdogTimer) clearTimeout(watchdogTimer);
                            throw err; // Propagate to retry logic below
                        });
                    };

                    readChunk();
                } else {
                    // Non-streaming JSON validation
                    return response.json().then(data => {
                        if (watchdogTimer) clearTimeout(watchdogTimer); // Clean up just in case
                        self.hideTypingIndicator();
                        if (progressDiv.parentNode) progressDiv.style.display = 'none';

                        const responseText = data.response || data.message;

                        // VALIDATION: Reject empty responses
                        if (!responseText || !responseText.trim() || responseText === 'No response') {
                            throw new Error("Server returned empty JSON response");
                        }

                        console.log('Rendering response to UI:', responseText);
                        textElement.textContent = responseText;
                        this.addMessageActions(messageDiv, 'thesidia', responseText, messageId, queryData);
                        this.scrollToBottom();
                        this.saveConversation(sanitizedMessage, responseText);
                        resolve(responseText);
                    });
                }
            }).catch(err => {
                console.error('Fetch error:', err);
                self.hideTypingIndicator();
                if (progressDiv.parentNode) progressDiv.style.display = 'none';

                // Retry logic with Visual Toast
                if (attempt < 2) { // Retry up to 2 times (total 3 attempts)
                    const backoff = 1000 * (attempt + 1);

                    // Show toast (if notify function exists, otherwise simple log)
                    const toastMsg = `Connection unstable. Retrying (${attempt + 1}/2)...`;
                    if (self.showToast) self.showToast(toastMsg, 'warning');
                    else console.log(toastMsg);

                    // Update UI text to show retry status
                    textElement.innerHTML = `<em>${toastMsg}</em>`;

                    setTimeout(() => doFetch(attempt + 1).then(() => { }).catch(reject), backoff);
                    return;
                }

                textElement.textContent = `Error: ${err.message}. Please try again.`;
                reject(err);
            });

    async callThesidiaAPIFallback(message) {
                // Fallback non-streaming method
                const response = await fetch(this.apiEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        conversation_id: this.currentConversationId,
                        show_thinking: this.showThinking,
                        stream: false,
                        user_id: this.userId,
                        session_id: this.sessionId
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                // Display thinking steps if available
                if (data.thinking_steps && data.thinking_steps.length > 0) {
                    this.displayThinkingSteps(data.thinking_steps);
                }

                return data.response || data.message || 'No response received';
            }

            displayThinkingSteps(steps) {
                const thinkingContent = document.getElementById('thinkingContent');
                const thinkingSteps = document.getElementById('thinkingSteps');

                if (!thinkingContent || !thinkingSteps) return;

                thinkingContent.innerHTML = '';

                steps.forEach((step, index) => {
                    const stepDiv = document.createElement('div');
                    stepDiv.className = 'thinking-step';
                    stepDiv.style.animationDelay = `${index * 0.1}s`;

                    stepDiv.innerHTML = `
                <div class="thinking-step-header">${this.escapeHtml(step.step)}</div>
                <div class="thinking-step-detail">${this.escapeHtml(step.detail)}</div>
                <div class="thinking-step-time">${new Date(step.timestamp).toLocaleTimeString()}</div>
            `;

                    thinkingContent.appendChild(stepDiv);
                });

                thinkingSteps.style.display = 'block';
                this.scrollToBottom();
            }

            displayThinkingStep(step, message) {
                // Display real-time thinking step
                const thinkingContent = document.getElementById('thinkingContent');
                const thinkingSteps = document.getElementById('thinkingSteps');

                if (!thinkingContent || !thinkingSteps || !this.showThinking) return;

                // Show thinking steps container
                thinkingSteps.style.display = 'block';

                // Add or update thinking step
                const stepDiv = document.createElement('div');
                stepDiv.className = 'thinking-step';
                stepDiv.innerHTML = `
            <div class="thinking-step-header">${this.escapeHtml(step)}</div>
            <div class="thinking-step-detail">${this.escapeHtml(message)}</div>
            <div class="thinking-step-time">${new Date().toLocaleTimeString()}</div>
        `;

                thinkingContent.appendChild(stepDiv);
                this.scrollToBottom();
            }

            sanitizeInput(input) {
                // Basic sanitization - remove potentially dangerous characters
                return input
                    .replace(/[<>]/g, '') // Remove < and >
                    .trim()
                    .slice(0, 10000); // Limit length
            }

            addMessageWithTyping(type, text, speed = 15) {
                // Create message element
                const messagesContainer = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;

                // Add identity header
                const identityHeader = document.createElement('div');
                identityHeader.className = 'message-identity';
                identityHeader.textContent = type === 'user' ? 'USER' : 'THESIDIA';
                messageDiv.appendChild(identityHeader);

                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';

                const textElement = document.createElement('p');
                textElement.textContent = '';
                contentDiv.appendChild(textElement);

                messageDiv.appendChild(contentDiv);
                messagesContainer.appendChild(messageDiv);

                // Scroll to bottom
                this.scrollToBottom();

                // Remove system message if exists
                const systemMessage = messagesContainer.querySelector('.system-message');
                if (systemMessage && type !== 'system') {
                    systemMessage.remove();
                }

                // Type out the text letter by letter
                let index = 0;
                const typingInterval = setInterval(() => {
                    if (index < text.length) {
                        // Handle special characters and formatting
                        if (text[index] === '\n') {
                            textElement.innerHTML += '<br>';
                        } else if (text[index] === '*' && index + 1 < text.length && text[index + 1] === '*') {
                            // Handle bold markdown
                            let boldEnd = text.indexOf('**', index + 2);
                            if (boldEnd !== -1) {
                                textElement.innerHTML += '<strong>' + text.substring(index + 2, boldEnd) + '</strong>';
                                index = boldEnd + 1;
                            } else {
                                textElement.textContent += text[index];
                            }
                        } else {
                            textElement.textContent += text[index];
                        }
                        index++;
                        // Auto-scroll as text appears
                        this.scrollToBottom();
                    } else {
                        clearInterval(typingInterval);
                    }
                }, speed);
            }

            addMessage(type, content, messageId = null, queryData = null) {
                const messagesContainer = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;

                // Generate message ID if not provided
                if (!messageId) {
                    messageId = this.generateMessageId();
                }
                messageDiv.setAttribute('data-message-id', messageId);

                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';

                // Format content (support markdown-like formatting)
                const formattedContent = this.formatMessage(content);
                contentDiv.innerHTML = formattedContent;

                // Set up event delegation for action suggestion buttons
                const actionButtons = contentDiv.querySelectorAll('.action-suggestion-btn');
                actionButtons.forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const action = btn.getAttribute('data-action');
                        if (action) {
                            this.handleActionSuggestion(action);
                        }
                    });
                });

                // Add identity header
                const identityHeader = document.createElement('div');
                identityHeader.className = 'message-identity';
                identityHeader.textContent = type === 'user' ? 'USER' : 'THESIDIA';
                messageDiv.appendChild(identityHeader);

                messageDiv.appendChild(contentDiv);

                // Add action buttons for Thesidia messages
                if (type === 'thesidia') {
                    this.addMessageActions(messageDiv, type, content, messageId, queryData);
                }

                messagesContainer.appendChild(messageDiv);

                // Store message data for regeneration (only for Thesidia responses)
                if (type === 'thesidia' && queryData) {
                    this.messageStore.set(messageId, {
                        query: queryData.query,
                        params: queryData.params,
                        timestamp: new Date().toISOString(),
                        type: type
                    });
                }

                // Scroll to bottom
                this.scrollToBottom();

                // Remove system message if exists
                const systemMessage = messagesContainer.querySelector('.system-message');
                if (systemMessage && type !== 'system') {
                    systemMessage.remove();
                }
            }

            generateMessageId() {
                return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            }

            addMessageActions(messageDiv, messageType, content, messageId, queryData) {
                // Check if actions already exist to prevent duplication
                const existingActions = messageDiv.querySelector('.message-actions');
                if (existingActions) {
                    existingActions.remove(); // Remove old actions before adding new ones
                }

                const actionsDiv = document.createElement('div');
                actionsDiv.className = 'message-actions';

                // Regenerate button (only if we have query data)
                if (queryData) {
                    const regenerateBtn = document.createElement('button');
                    regenerateBtn.className = 'message-action';
                    regenerateBtn.textContent = 'regenerate';
                    regenerateBtn.setAttribute('aria-label', 'Regenerate response');
                    regenerateBtn.onclick = () => this.regenerateMessage(messageId);
                    actionsDiv.appendChild(regenerateBtn);
                }

                // Sources button (if sources exist)
                const sourcesData = this.extractSourcesData(content, messageId);
                if (sourcesData.hasSources) {
                    const sourcesBtn = document.createElement('button');
                    sourcesBtn.className = 'message-action sources-action';
                    sourcesBtn.textContent = `sources (${sourcesData.citations.length})`;
                    sourcesBtn.setAttribute('aria-label', 'View sources');
                    sourcesBtn.onclick = () => this.showSourcesPanel(messageId, sourcesData);
                    actionsDiv.appendChild(sourcesBtn);
                }

                // Read button - play message with selected voice
                const readBtn = document.createElement('button');
                readBtn.className = 'message-action read-action';
                readBtn.textContent = 'read';
                readBtn.setAttribute('aria-label', 'Read message aloud');
                const self = this; // Preserve context
                readBtn.onclick = function () {
                    console.log('Read button clicked', { hasSelf: !!self, hasReadMessage: !!(self && self.readMessage) });
                    // Direct call - function should exist
                    if (self) {
                        try {
                            self.readMessage(content, messageId, readBtn);
                        } catch (error) {
                            console.error('Error calling readMessage:', error);
                            alert(`Error: ${error.message}. Please check console for details.`);
                        }
                    } else {
                        console.error('self is not available');
                        alert('Read function not available. Please refresh the page.');
                    }
                };
                actionsDiv.appendChild(readBtn);

                // Copy button
                const copyBtn = document.createElement('button');
                copyBtn.className = 'message-action';
                copyBtn.textContent = 'copy';
                copyBtn.setAttribute('aria-label', 'Copy message');
                copyBtn.onclick = () => this.copyMessage(content);
                actionsDiv.appendChild(copyBtn);

                // Share button
                const shareBtn = document.createElement('button');
                shareBtn.className = 'message-action';
                shareBtn.textContent = 'share';
                shareBtn.setAttribute('aria-label', 'Share message');
                shareBtn.onclick = (e) => this.shareMessage(content, e);
                actionsDiv.appendChild(shareBtn);

                messageDiv.appendChild(actionsDiv);
            }

            saveMessage(messageId, content, event = null) {
                // Save is already handled by saveConversation, but we can show feedback
                const btn = event?.target || document.querySelector(`[data-message-id="${messageId}"] .message-action`);
                if (btn) {
                    const originalText = btn.textContent;
                    btn.textContent = 'saved';
                    setTimeout(() => {
                        btn.textContent = originalText;
                    }, 2000);
                }
                // Note: Actual saving happens via saveConversation() which is called after message completion
            }

    async regenerateMessage(messageId) {
                const messageData = this.messageStore.get(messageId);
                if (!messageData) {
                    console.error('Message data not found for regeneration');
                    return;
                }

                const messageDiv = document.querySelector(`[data-message-id="${messageId}"]`);
                if (!messageDiv) {
                    console.error('Message element not found');
                    return;
                }

                // Show loading state
                const regenerateBtn = messageDiv.querySelector('.message-action:nth-of-type(2)');
                if (regenerateBtn) {
                    regenerateBtn.textContent = 'regenerating...';
                    regenerateBtn.disabled = true;
                }

                // Get original query and params
                const originalQuery = messageData.query;
                const originalParams = messageData.params || {};

                // Call API again with same parameters
                try {
                    await this.callThesidiaAPI(originalQuery);
                    // The new message will be added by callThesidiaAPI
                } catch (error) {
                    console.error('Regeneration error:', error);
                    if (regenerateBtn) {
                        regenerateBtn.textContent = 'regenerate';
                        regenerateBtn.disabled = false;
                    }
                }
            }

    async copyMessage(content, event = null) {
                try {
                    // Strip HTML tags for plain text copy
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = content;
                    const plainText = tempDiv.textContent || tempDiv.innerText || content;

                    await navigator.clipboard.writeText(plainText);

                    // Show feedback
                    const btn = event?.target || document.activeElement;
                    if (btn && btn.classList.contains('message-action')) {
                        const originalText = btn.textContent;
                        btn.textContent = 'copied!';
                        setTimeout(() => {
                            btn.textContent = originalText;
                        }, 2000);
                    }
                } catch (err) {
                    console.error('Failed to copy:', err);
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = content.replace(/<[^>]*>/g, '');
                    document.body.appendChild(textArea);
                    textArea.select();
                    try {
                        document.execCommand('copy');
                        const btn = event?.target;
                        if (btn) {
                            const originalText = btn.textContent;
                            btn.textContent = 'copied!';
                            setTimeout(() => {
                                btn.textContent = originalText;
                            }, 2000);
                        }
                    } catch (e) {
                        console.error('Fallback copy failed:', e);
                    }
                    document.body.removeChild(textArea);
                }
            }

    async shareMessage(content, event = null) {
                // Strip HTML for sharing
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = content;
                const plainText = tempDiv.textContent || tempDiv.innerText || content;

                const shareData = {
                    title: 'Thesidia Response',
                    text: plainText.substring(0, 1000), // Limit length
                    url: window.location.href
                };

                try {
                    if (navigator.share && navigator.share.canShare && navigator.share.canShare(shareData)) {
                        await navigator.share(shareData);
                    } else {
                        // Fallback: copy shareable link or text
                        const shareUrl = `${window.location.origin}${window.location.pathname}?share=${encodeURIComponent(plainText.substring(0, 200))}`;
                        await navigator.clipboard.writeText(shareUrl);

                        const btn = event?.target || document.activeElement;
                        if (btn && btn.classList.contains('message-action')) {
                            const originalText = btn.textContent;
                            btn.textContent = 'link copied!';
                            setTimeout(() => {
                                btn.textContent = originalText;
                            }, 2000);
                        }
                    }
                } catch (err) {
                    if (err.name !== 'AbortError') {
                        console.error('Share failed:', err);
                        // Fallback to copy
                        this.copyMessage(content, null);
                    }
                }
            }

            formatMessage(content) {
                // Remove leaked "General Framework" blocks
                content = content.replace(/\*{0,2}\s*General Framework:\s*\*{0,2}[\s\S]*$/gi, '');
                content = content.replace(/\*{0,2}\s*Foundation:\s*\*{0,2}.*?\n/gi, '');
                content = content.replace(/\*{0,2}\s*Practice:\s*\*{0,2}.*?\n/gi, '');
                content = content.replace(/\*{0,2}\s*Learning:\s*\*{0,2}.*?\n/gi, '');
                content = content.replace(/\*{0,2}\s*Growth:\s*\*{0,2}.*?\n/gi, '');

                // Convert "I can also" section to clickable action buttons
                const iCanAlsoMatch = content.match(/\*\*I can also:\*\*([\s\S]*?)(?=\n\n|$)/i);
                if (iCanAlsoMatch) {
                    const actionsText = iCanAlsoMatch[1];
                    let actions = [];
                    const numberedMatches = [...actionsText.matchAll(/(\d+\.\s*[^\d\n][^\n]*?)(?=\s+\d+\.|$)/g)];
                    if (numberedMatches.length > 0) {
                        actions = numberedMatches
                            .map(m => m[1].replace(/^\d+\.\s*/, '').trim())
                            .filter(Boolean);
                    } else {
                        const actionLines = actionsText.split('\n').filter(line => line.trim());
                        actions = actionLines.map(line => {
                            const actionText = line.replace(/^\d+\.\s*/, '').replace(/^[-•]\s*/, '').trim();
                            return actionText || null;
                        }).filter(Boolean);
                    }

                    if (actions.length > 0) {
                        const actionsHtml = actions.map(action => {
                            const escapedAction = this.escapeHtml(action);
                            return `<button class="action-suggestion-btn" data-action="${escapedAction.replace(/"/g, '&quot;')}">${escapedAction}</button>`;
                        }).join('');

                        content = content.replace(
                            /\*\*I can also:\*\*[\s\S]*?(?=\n\n|$)/i,
                            `<div class="action-suggestions"><strong>I CAN ALSO:</strong><div class="action-suggestions-list">${actionsHtml}</div></div>`
                        );
                    }
                }

                // ---- REFINED FORMATTING ----

                // 1. Headers (### Header)
                content = content.replace(/^### (.*$)/gm, '<h3>$1</h3>');
                content = content.replace(/^## (.*$)/gm, '<h3>$1</h3>'); // Map h2 to h3 for aesthetics

                // 2. Bold and Italic
                content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');

                // 3. Lists
                // Wrap bulleted lines in <li>
                content = content.replace(/^\s*[-*]\s+(.*$)/gm, '<li>$1</li>');

                // Handle numbered lists (standard)
                content = content.replace(/^\s*\d+\.\s+(.*$)/gm, '<li>$1</li>');

                // Handle inline numbered lists (heuristic for "1. Item 2. Item")
                content = content.replace(/(\s|^)\d+\.\s+([^\n]+?)(?=(\s\d+\.\s+)|$)/g, '$1<li>$2</li>');

                // Wrap consecutive <li> into <ul>
                // This simple regex strategy might need a more robust parser for nested lists, 
                // but works for basic blocks.
                // We'll replace double newlines to ensure paragraphs work first

                // 4. Citation Circles: [text](link) -> <a href="link" class="citation-circle" title="text"></a>
                content = content.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="citation-circle" target="_blank" title="$1"></a>');

                // 5. Code Blocks
                content = content.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
                content = content.replace(/`([^`]+)`/g, '<code>$1</code>');

                // 6. Paragraphs
                // Split by double newlines, wrap non-HTML blocks in <p>
                const sections = content.split(/\n\s*\n/);
                const formattedSections = sections.map(section => {
                    section = section.trim();
                    if (!section) return '';

                    // If it starts with an HTML block tag we added, don't wrap in P
                    if (section.startsWith('<h3>') || section.startsWith('<div') || section.startsWith('<pre>')) {
                        return section;
                    }

                    // Check for list items
                    if (section.includes('<li>')) {
                        // If the entire section is just li's, wrap in ul
                        if (section.match(/^(<li>.*<\/li>\s*)+$/s)) {
                            return `<ul>${section}</ul>`;
                        }
                        // If it contains li's but mixed, try to wrap the group
                        // For simplicity in this regex pass, we'll just wrap the whole thing if it looks like a list block
                        return `<ul>${section}</ul>`;
                    }

                    return `<p>${section.replace(/\n/g, '<br>')}</p>`;
                });

                return formattedSections.join('');
            }

            handleActionSuggestion(actionText) {
                // When user clicks an action suggestion, send it as a new message
                const promptInput = document.getElementById('promptInput');
                if (promptInput) {
                    promptInput.value = actionText;
                    // Trigger send
                    const sendBtn = document.getElementById('sendBtn');
                    if (sendBtn && !sendBtn.disabled) {
                        sendBtn.click();
                    }
                }
            }

            showTypingIndicator() {
                const typingIndicator = document.getElementById('typingIndicator');
                typingIndicator.style.display = 'block';
                this.scrollToBottom();
            }

            hideTypingIndicator() {
                const typingIndicator = document.getElementById('typingIndicator');
                typingIndicator.style.display = 'none';
            }

            // Typing animation queue for smooth character-by-character display
            typingQueues = new Map();

            typeText(element, text, onComplete = null) {
                // Get or create typing queue for this element
                if (!this.typingQueues.has(element)) {
                    this.typingQueues.set(element, {
                        queue: '',
                        isTyping: false,
                        speed: 20,  // milliseconds per character (50 chars/sec - optimal for UX)
                        callbacks: []
                    });
                }

                const queue = this.typingQueues.get(element);
                queue.queue += text;

                // Add callback if provided
                if (onComplete) {
                    queue.callbacks.push(onComplete);
                }

                // Start typing if not already typing
                if (!queue.isTyping) {
                    this._processTypingQueue(element, queue);
                }
            }

            _processTypingQueue(element, queue) {
                if (queue.queue.length === 0) {
                    queue.isTyping = false;
                    // Call all pending callbacks
                    queue.callbacks.forEach(cb => cb());
                    queue.callbacks = [];
                    return;
                }

                queue.isTyping = true;

                // Type one character
                const char = queue.queue[0];
                queue.queue = queue.queue.slice(1);

                // Handle special characters
                if (char === '\n') {
                    element.innerHTML += '<br>';
                } else {
                    element.textContent += char;
                }

                // Scroll to bottom as text appears
                this.scrollToBottom();

                // Continue typing next character
                setTimeout(() => {
                    this._processTypingQueue(element, queue);
                }, queue.speed);
            }

            showToast(message, type = 'info') {
                const toast = document.createElement('div');
                toast.className = `toast toast-${type}`;
                toast.textContent = message;

                // Add styles if not present in CSS
                toast.style.position = 'fixed';
                toast.style.bottom = '80px';
                toast.style.left = '50%';
                toast.style.transform = 'translateX(-50%)';
                toast.style.padding = '8px 16px';
                toast.style.borderRadius = '20px';
                toast.style.background = 'rgba(0, 0, 0, 0.8)';
                toast.style.color = 'white';
                toast.style.fontSize = '14px';
                toast.style.zIndex = '1000';
                toast.style.backdropFilter = 'blur(10px)';
                toast.style.border = '1px solid rgba(255, 255, 255, 0.1)';
                toast.style.transition = 'opacity 0.3s ease';

                if (type === 'warning') {
                    toast.style.border = '1px solid rgba(255, 165, 0, 0.5)';
                    toast.style.color = '#ffaa00';
                }

                document.body.appendChild(toast);

                // Animate out
                setTimeout(() => {
                    toast.style.opacity = '0';
                    setTimeout(() => toast.remove(), 300);
                }, 3000);
            }

            scrollToBottom() {
                const chatContainer = document.getElementById('chatContainer');
                setTimeout(() => {
                    chatContainer.scrollTo({
                        top: chatContainer.scrollHeight,
                        behavior: 'smooth'
                    });
                }, 100);
            }

            updateSendButton() {
                const sendBtn = document.getElementById('sendBtn');
                sendBtn.disabled = this.isProcessing;
            }

            toggleLeftSidebar() {
                const sidebar = document.getElementById('leftSidebar');
                const app = document.getElementById('app');

                if (sidebar && app) {
                    const isOpen = sidebar.classList.contains('open');

                    if (isOpen) {
                        this.closeLeftSidebar();
                    } else {
                        // Adjust prompt bar position
                        this.adjustPromptBarForSidebar(true);
                        // Apply classes immediately for smooth single motion
                        sidebar.classList.add('open');
                        app.classList.add('sidebar-pushed');
                        // Prevent body scroll when sidebar is open
                        document.body.style.overflow = 'hidden';
                    }
                }
            }

            closeLeftSidebar() {
                const sidebar = document.getElementById('leftSidebar');
                const app = document.getElementById('app');

                if (sidebar && app) {
                    // Adjust prompt bar position
                    this.adjustPromptBarForSidebar(false);
                    // Apply classes immediately for smooth single motion
                    sidebar.classList.remove('open');
                    app.classList.remove('sidebar-pushed');
                    // Restore body scroll
                    document.body.style.overflow = '';
                }
            }

            adjustPromptBarForSidebar(isOpen) {
                // Handle both prompt bar types
                const hudPromptBar = document.querySelector('.hud-prompt-container');
                const promptBar = document.querySelector('.prompt-bar-container');
                const targetBar = hudPromptBar || promptBar;

                if (!targetBar) return;

                // Get sidebar width
                const sidebar = document.getElementById('leftSidebar');
                const sidebarWidth = sidebar ? (sidebar.offsetWidth || 240) : 240;

                if (isOpen) {
                    // Adjust left and remove right to allow proper width calculation
                    targetBar.style.left = `${sidebarWidth}px`;
                    targetBar.style.right = '0';
                } else {
                    // Reset to full width
                    targetBar.style.left = '0';
                    targetBar.style.right = '0';
                }
            }

            handleProfileImageUpload(file, imgElement) {
                if (!file || !imgElement) return;

                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = new Image();
                    img.onload = () => {
                        // Create canvas to resize and crop image
                        const canvas = document.createElement('canvas');
                        const size = 120; // 2x for retina displays
                        canvas.width = size;
                        canvas.height = size;
                        const ctx = canvas.getContext('2d');

                        // Calculate crop to make it square (center crop)
                        let sourceX = 0;
                        let sourceY = 0;
                        let sourceSize = Math.min(img.width, img.height);

                        if (img.width > img.height) {
                            sourceX = (img.width - img.height) / 2;
                        } else {
                            sourceY = (img.height - img.width) / 2;
                        }

                        // Draw image centered and cropped to square
                        ctx.drawImage(
                            img,
                            sourceX, sourceY, sourceSize, sourceSize, // Source (cropped square)
                            0, 0, size, size // Destination (canvas)
                        );

                        // Convert to data URL and set as image source
                        const dataURL = canvas.toDataURL('image/jpeg', 0.9);
                        imgElement.src = dataURL;

                        // Save to localStorage for persistence
                        localStorage.setItem('profileImage', dataURL);

                        // Also update header profile picture if it exists
                        const headerProfile = document.getElementById('headerProfilePicture');
                        if (headerProfile) {
                            const headerImg = headerProfile.querySelector('img');
                            if (headerImg) {
                                headerImg.src = dataURL;
                            }
                        }

                        console.log('Profile picture updated');
                    };
                    img.onerror = () => {
                        console.error('Error loading image');
                    };
                    img.src = e.target.result;
                };
                reader.onerror = () => {
                    console.error('Error reading file');
                };
                reader.readAsDataURL(file);
            }

            setActiveNavItem() {
                const navItems = document.querySelectorAll('.nav-item');
                const currentPath = window.location.pathname;

                navItems.forEach(item => {
                    const href = item.getAttribute('href');
                    if (href === currentPath ||
                        (currentPath === '/' && href === '/') ||
                        (currentPath === '/contexts.html' && href === '/')) {
                        item.classList.add('active');
                    } else {
                        item.classList.remove('active');
                    }
                });
            }

            newConversation() {
                this.currentConversationId = null;
                const messagesContainer = document.getElementById('messages');
                messagesContainer.innerHTML = `
            <div class="message system-message">
                <div class="message-content">
                    <p>Execute directives directly. Build websites, devices, blueprints, training programs.</p>
                </div>
            </div>
        `;
                this.closeLeftSidebar();
            }

            saveConversation(userMessage, thesidiaResponse) {
                if (!this.currentConversationId) {
                    this.currentConversationId = Date.now().toString();
                }

                const conversation = {
                    id: this.currentConversationId,
                    title: userMessage.slice(0, 50),
                    preview: thesidiaResponse.slice(0, 100),
                    timestamp: Date.now(),
                    messages: [
                        { type: 'user', content: userMessage },
                        { type: 'thesidia', content: thesidiaResponse }
                    ]
                };

                // Save to localStorage (in production, use secure backend)
                this.conversations.unshift(conversation);
                this.conversations = this.conversations.slice(0, 50); // Keep last 50
                localStorage.setItem('thesidia_conversations', JSON.stringify(this.conversations));

                this.updateConversationsList();

                // Best-effort server sync (non-blocking)
                this.syncConversationToServer(conversation).catch(() => { });
            }

    async syncConversationToServer(conversation) {
                // Server-side persistence (SQLite default). Safe fallback to local-only if server doesn't support it.
                try {
                    const resp = await fetch(`/api/conversations/${encodeURIComponent(conversation.id)}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_id: this.userId,
                            session_id: this.sessionId,
                            title: conversation.title,
                            preview: conversation.preview,
                            messages: (conversation.messages || []).map(m => ({
                                type: m.type,
                                content: m.content,
                                timestamp: Date.now()
                            }))
                        })
                    });
                    if (!resp.ok) return;
                    const data = await resp.json().catch(() => ({}));
                    if (!data.ok) return;
                } catch (e) {
                    // Silent: localStorage remains the source of truth if server is unreachable
                }
            }

            loadConversations() {
                try {
                    const stored = localStorage.getItem('thesidia_conversations');
                    if (stored) {
                        this.conversations = JSON.parse(stored);
                        this.updateConversationsList();
                    }
                } catch (error) {
                    console.error('Error loading conversations:', error);
                }
            }

    async loadConversationsFromServer() {
                // Prefer server list when available; fall back to localStorage.
                try {
                    const params = new URLSearchParams();
                    if (this.userId) params.set('user_id', this.userId);
                    if (this.sessionId) params.set('session_id', this.sessionId);
                    params.set('limit', '50');
                    const resp = await fetch(`/api/conversations?${params.toString()}`);
                    if (!resp.ok) return false;
                    const data = await resp.json().catch(() => null);
                    if (!data || !Array.isArray(data.conversations)) return false;
                    // Server list is lightweight; we keep it in-memory/local to drive the sidebar.
                    this.conversations = data.conversations.map(c => ({
                        id: c.id,
                        title: c.title,
                        preview: c.preview,
                        timestamp: c.timestamp,
                        messages: [] // loaded on demand
                    }));
                    localStorage.setItem('thesidia_conversations', JSON.stringify(this.conversations));
                    this.updateConversationsList();
                    return true;
                } catch (e) {
                    return false;
                }
            }

            updateConversationsList() {
                const listContainer = document.getElementById('conversationsList');
                if (!listContainer) return; // Not on contexts page
                listContainer.innerHTML = '';

                this.conversations.forEach(conv => {
                    const item = document.createElement('div');
                    item.className = 'conversation-item';
                    if (conv.id === this.currentConversationId) {
                        item.classList.add('active');
                    }

                    item.innerHTML = `
                <div class="conversation-title">${this.escapeHtml(conv.title)}</div>
                <div class="conversation-preview">${this.escapeHtml(conv.preview)}</div>
            `;

                    item.addEventListener('click', () => this.loadConversation(conv.id));
                    listContainer.appendChild(item);
                });
            }

            loadConversation(conversationId) {
                const conversation = this.conversations.find(c => c.id === conversationId);
                if (!conversation) return;

                this.currentConversationId = conversationId;

                // If we have messages locally, render immediately; otherwise pull from server.
                if (conversation.messages && conversation.messages.length > 0) {
                    const messagesContainer = document.getElementById('messages');
                    messagesContainer.innerHTML = '';
                    conversation.messages.forEach(msg => this.addMessage(msg.type, msg.content));
                    this.updateConversationsList();
                    this.closeLeftSidebar();
                    return;
                }

                this.loadConversationFromServer(conversationId).then(loaded => {
                    if (!loaded) {
                        // Fallback: render what we have (usually none)
                        const messagesContainer = document.getElementById('messages');
                        messagesContainer.innerHTML = '';
                        this.addMessage('thesidia', 'Could not load this conversation from server.');
                    }
                    this.updateConversationsList();
                    this.closeLeftSidebar();
                });
            }

    async loadConversationFromServer(conversationId) {
                try {
                    const params = new URLSearchParams();
                    if (this.userId) params.set('user_id', this.userId);
                    if (this.sessionId) params.set('session_id', this.sessionId);
                    const resp = await fetch(`/api/conversations/${encodeURIComponent(conversationId)}?${params.toString()}`);
                    if (!resp.ok) return false;
                    const data = await resp.json().catch(() => null);
                    if (!data || !Array.isArray(data.messages)) return false;
                    const messagesContainer = document.getElementById('messages');
                    messagesContainer.innerHTML = '';
                    data.messages.forEach(msg => this.addMessage(msg.type, msg.content));
                    // Cache messages in local list
                    const idx = this.conversations.findIndex(c => c.id === conversationId);
                    if (idx >= 0) {
                        this.conversations[idx].messages = data.messages.map(m => ({ type: m.type, content: m.content }));
                        localStorage.setItem('thesidia_conversations', JSON.stringify(this.conversations));
                    }
                    return true;
                } catch (e) {
                    return false;
                }
            }

            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            // Sources Panel - Slide up from bottom
            extractSourcesData(content, messageId = null) {
                /**Extract sources, citations, and thinking steps from response*/
                const sourcesData = {
                    hasSources: false,
                    citations: [],
                    thinkingSteps: []
                };

                // Extract ::SOURCES:: section
                const sourcesMatch = content.match(/::SOURCES::\s*\n([\s\S]*?)(?=\n\n|$)/);
                if (sourcesMatch) {
                    const sourcesText = sourcesMatch[1].trim();
                    const citationLines = sourcesText.split('\n').filter(line => line.trim());

                    sourcesData.citations = citationLines.map(line => {
                        const match = line.match(/\[(\d+)\]\s*(.+?)\s*-\s*(.+)/);
                        if (match) {
                            return {
                                number: match[1],
                                title: match[2].trim(),
                                url: match[3].trim()
                            };
                        }
                        return {
                            number: null,
                            title: line.trim(),
                            url: null
                        };
                    });

                    sourcesData.hasSources = sourcesData.citations.length > 0;
                }

                // Get thinking steps if stored
                if (messageId && this.thinkingSteps && this.thinkingSteps[messageId]) {
                    sourcesData.thinkingSteps = this.thinkingSteps[messageId];
                    if (sourcesData.thinkingSteps.length > 0) {
                        sourcesData.hasSources = true;
                    }
                }

                return sourcesData;
            }

            showSourcesPanel(messageId, sourcesData) {
                /**Show slide-up panel from bottom with sources, citations, thinking steps*/
                // Remove existing panel
                const existingPanel = document.getElementById('sources-panel');
                if (existingPanel) {
                    existingPanel.remove();
                }

                // Create panel
                const panel = document.createElement('div');
                panel.id = 'sources-panel';
                panel.className = 'sources-panel';

                const panelContent = document.createElement('div');
                panelContent.className = 'sources-panel-content';

                // Header
                const header = document.createElement('div');
                header.className = 'sources-panel-header';
                header.innerHTML = `
            <h3>Sources & Citations</h3>
            <button class="sources-panel-close" aria-label="Close">×</button>
        `;
                panelContent.appendChild(header);

                // Body
                const body = document.createElement('div');
                body.className = 'sources-panel-body';

                // Citations
                if (sourcesData.citations && sourcesData.citations.length > 0) {
                    const citationsSection = document.createElement('div');
                    citationsSection.className = 'sources-section';
                    citationsSection.innerHTML = '<h4>Citations</h4>';

                    const citationsList = document.createElement('div');
                    citationsList.className = 'sources-list';

                    sourcesData.citations.forEach((citation, index) => {
                        const item = document.createElement('div');
                        item.className = 'source-item';

                        if (citation.url) {
                            item.innerHTML = `
                        <div class="source-number">${citation.number || index + 1}</div>
                        <div class="source-content">
                            <a href="${citation.url}" target="_blank" rel="noopener" class="source-link">${this.escapeHtml(citation.title)}</a>
                            <div class="source-url">${this.escapeHtml(citation.url)}</div>
                        </div>
                    `;
                        } else {
                            item.innerHTML = `
                        <div class="source-number">${citation.number || index + 1}</div>
                        <div class="source-content">
                            <div class="source-title">${this.escapeHtml(citation.title)}</div>
                        </div>
                    `;
                        }

                        citationsList.appendChild(item);
                    });

                    citationsSection.appendChild(citationsList);
                    body.appendChild(citationsSection);
                }

                // Thinking steps
                if (sourcesData.thinkingSteps && sourcesData.thinkingSteps.length > 0) {
                    const thinkingSection = document.createElement('div');
                    thinkingSection.className = 'sources-section';
                    thinkingSection.innerHTML = '<h4>Thinking Steps</h4>';

                    const thinkingList = document.createElement('div');
                    thinkingList.className = 'thinking-steps-list';

                    sourcesData.thinkingSteps.forEach((step, index) => {
                        const stepItem = document.createElement('div');
                        stepItem.className = 'thinking-step-item';
                        stepItem.innerHTML = `
                    <div class="thinking-step-number">${index + 1}</div>
                    <div class="thinking-step-content">${this.escapeHtml(step.message || step)}</div>
                `;
                        thinkingList.appendChild(stepItem);
                    });

                    thinkingSection.appendChild(thinkingList);
                    body.appendChild(thinkingSection);
                }

                panelContent.appendChild(body);
                panel.appendChild(panelContent);
                document.body.appendChild(panel);

                // Animate slide up
                setTimeout(() => {
                    panel.classList.add('sources-panel-visible');
                }, 10);

                // Close handlers
                header.querySelector('.sources-panel-close').onclick = () => this.closeSourcesPanel();
                panel.onclick = (e) => {
                    if (e.target === panel) this.closeSourcesPanel();
                };

                const escapeHandler = (e) => {
                    if (e.key === 'Escape') {
                        this.closeSourcesPanel();
                        document.removeEventListener('keydown', escapeHandler);
                    }
                };
                document.addEventListener('keydown', escapeHandler);
            }

            closeSourcesPanel() {
                const panel = document.getElementById('sources-panel');
                if (panel) {
                    panel.classList.remove('sources-panel-visible');
                    setTimeout(() => panel.remove(), 300);
                }
            }

            // TTS (Text-to-Speech) - Streaming voice for Thesidia's replies
            speakChunk(chunk, messageId) {
                /**Speak chunk as it streams - real-time TTS following best practices*/
                if (!this.ttsEnabled || !chunk || !chunk.trim()) {
                    return;
                }

                // Stop previous message if switching
                if (this.currentTTSMessageId && this.currentTTSMessageId !== messageId) {
                    speechSynthesis.cancel();
                    this.ttsQueue = [];
                    this.ttsSpeaking = false;
                }

                this.currentTTSMessageId = messageId;

                // Clean chunk
                const cleanChunk = this.cleanTextForTTS(chunk);
                if (!cleanChunk || cleanChunk.trim().length === 0) {
                    return;
                }

                // Create utterance for chunk
                const utterance = new SpeechSynthesisUtterance(cleanChunk);

                // Use selected voice
                if (this.ttsVoice) {
                    utterance.voice = this.ttsVoice;
                }

                // Optimized for most realistic, natural, expressive speech
                // Rate: 0.9-0.95 is most natural (research shows slower = more human)
                utterance.rate = 0.93; // Slightly slower = more natural, less robotic
                // Pitch: 0.95-1.0 sounds more human (not synthetic)
                utterance.pitch = 0.98; // Natural pitch for realistic sound
                utterance.volume = 0.9; // Clear, audible volume
                utterance.lang = 'en-US';

                // Queue chunk
                this.ttsQueue.push(utterance);

                // Process queue
                if (!this.ttsSpeaking) {
                    this.processTTSQueue();
                }
            }

            processTTSQueue() {
                /**Process TTS queue for streaming chunks - best practices for real-time TTS*/
                if (this.ttsQueue.length === 0) {
                    this.ttsSpeaking = false;
                    return;
                }

                this.ttsSpeaking = true;
                const utterance = this.ttsQueue.shift();
                this.ttsUtterance = utterance;

                utterance.onend = () => {
                    this.processTTSQueue();
                };

                utterance.onerror = (e) => {
                    console.warn('TTS error:', e);
                    this.processTTSQueue();
                };

                speechSynthesis.speak(utterance);
            }

            stopTTS() {
                /**Stop all TTS playback"""
                speechSynthesis.cancel();
                this.ttsQueue = [];
                this.ttsSpeaking = false;
                this.ttsUtterance = null;
                this.currentTTSMessageId = null;
                
                // Reset all read buttons
                document.querySelectorAll('.message-action.read-action').forEach(btn => {
                    btn.textContent = 'read';
                    btn.classList.remove('reading');
                });
            }
            
            readMessage(content, messageId, buttonElement) {
                /**Read a complete message aloud using selected voice"""
                console.log('readMessage called', { content: content.substring(0, 50), messageId, hasVoice: !!this.ttsVoice });
                
                // Check if speech synthesis is available
                if (!('speechSynthesis' in window)) {
                    alert('Text-to-speech is not supported in this browser.');
                    return;
                }
                
                // Stop any currently playing TTS
                if (this.ttsSpeaking || this.ttsQueue.length > 0) {
                    this.stopTTS();
                    // If clicking the same button that's playing, just stop
                    if (buttonElement && buttonElement.classList.contains('reading')) {
                        return;
                    }
                }
                
                // Check if voice is available - try to get it from selector first
                const voiceSelector = document.getElementById('voiceSelector');
                if (voiceSelector && voiceSelector.value) {
                    const voices = speechSynthesis.getVoices();
                    const selectedIndex = parseInt(voiceSelector.value);
                    if (voices[selectedIndex]) {
                        this.ttsVoice = voices[selectedIndex];
                        console.log('Voice selected from dropdown:', this.ttsVoice.name);
                    }
                }
                
                // If still no voice, try to initialize
                if (!this.ttsVoice) {
                    console.log('No voice found, initializing...');
                    this.initializeTTS();
                    if (!this.ttsVoice) {
                        // Try getting any available voice as fallback
                        const voices = speechSynthesis.getVoices();
                        if (voices.length > 0) {
                            this.ttsVoice = voices[0];
                            console.log('Using fallback voice:', this.ttsVoice.name);
                        } else {
                            alert('No voices available. Please select a voice in the Control Panel first.');
                            return;
                        }
                    }
                }
                
                console.log('Using voice:', this.ttsVoice ? this.ttsVoice.name : 'none');
                
                // Extract plain text from HTML content
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = content;
                let plainText = tempDiv.textContent || tempDiv.innerText || content;
                
                // Clean text for TTS
                plainText = this.cleanTextForTTS(plainText);
                
                if (!plainText || plainText.trim().length === 0) {
                    console.warn('No text to read after cleaning');
                    return;
                }
                
                console.log('Text to read:', plainText.substring(0, 100));
                
                // Update button state
                if (buttonElement) {
                    buttonElement.textContent = 'reading...';
                    buttonElement.classList.add('reading');
                }
                
                // Set current message ID
                this.currentTTSMessageId = messageId;
                
                // Create utterance for entire message
                const utterance = new SpeechSynthesisUtterance(plainText);
                
                // Use selected voice
                if (this.ttsVoice) {
                    utterance.voice = this.ttsVoice;
                }
                
                // Optimized settings for realistic speech
                utterance.rate = 0.93;
                utterance.pitch = 0.98;
                utterance.volume = 0.9;
                utterance.lang = 'en-US';
                
                // Handle completion
                utterance.onend = () => {
                    console.log('TTS finished');
                    this.ttsSpeaking = false;
                    this.currentTTSMessageId = null;
                    if (buttonElement) {
                        buttonElement.textContent = 'read';
                        buttonElement.classList.remove('reading');
                    }
                };
                
                // Handle errors
                utterance.onerror = (event) => {
                    console.error('TTS error:', event);
                    alert(`TTS Error: ${event.error}. Please check your system audio settings.`);
                    this.ttsSpeaking = false;
                    this.currentTTSMessageId = null;
                    if (buttonElement) {
                        buttonElement.textContent = 'read';
                        buttonElement.classList.remove('reading');
                    }
                };
                
                // Handle start
                utterance.onstart = () => {
                    console.log('TTS started');
                };
                
                // Start speaking
                try {
                    this.ttsSpeaking = true;
                    speechSynthesis.speak(utterance);
                    console.log('speechSynthesis.speak() called');
                } catch (error) {
                    console.error('Error calling speechSynthesis.speak():', error);
                    alert(`Error: ${error.message}`);
                    this.ttsSpeaking = false;
                    if (buttonElement) {
                        buttonElement.textContent = 'read';
                        buttonElement.classList.remove('reading');
                    }
                }
            }
            
            initializeTTS() {
                /**Initialize TTS with most realistic voices prioritized"""
                if (!('speechSynthesis' in window)) {
                    return false;
                }
                
                const voices = speechSynthesis.getVoices();
                
                // Try to load saved voice first
                const savedVoiceIndex = localStorage.getItem('ttsVoiceIndex');
                if (savedVoiceIndex !== null && voices[savedVoiceIndex]) {
                    this.ttsVoice = voices[savedVoiceIndex];
                    return true;
                }
                
                // Most realistic voices prioritized (Premium > Neural > Wavenet > Standard)
                // macOS Premium voices are the MOST realistic available
                const voicePriority = [
                    // Tier 1: Premium voices (MOST REALISTIC)
                    { pattern: 'premium', exact: false },
                    // Tier 2: Neural voices (VERY REALISTIC)
                    { pattern: 'neural', exact: false },
                    { pattern: 'wavenet', exact: false },
                    // Tier 3: High-quality standard voices
                    { pattern: 'samantha', exact: false },
                    { pattern: 'alex', exact: false },
                    { pattern: 'victoria', exact: false },
                    { pattern: 'aria', exact: false },
                    { pattern: 'jenny', exact: false },
                    { pattern: 'karen', exact: false },
                ];
                
                // Find voice by priority
                for (const { pattern } of voicePriority) {
                    const voice = voices.find(v => 
                        v.name.toLowerCase().includes(pattern)
                    );
                    if (voice) {
                        this.ttsVoice = voice;
                        return true;
                    }
                }
                
                // Fallback: Any neural/premium/wavenet
                const fallbackVoice = voices.find(v => {
                    const name = v.name.toLowerCase();
                    return name.includes('neural') || name.includes('premium') || name.includes('wavenet');
                });
                if (fallbackVoice) {
                    this.ttsVoice = fallbackVoice;
                    return true;
                }
                
                // Last resort: first available
                if (voices.length > 0) {
                    this.ttsVoice = voices[0];
                }
                
                return true;
            }
            
            cleanTextForTTS(text) {
                /**Remove markdown, citations, and formatting for clean TTS output - best practices for AI voice synthesis*/
                let clean = text;

                // Remove markdown
                clean = clean.replace(/\*\*(.*?)\*\*/g, '$1'); // Bold
                clean = clean.replace(/\*(.*?)\*/g, '$1'); // Italic
                clean = clean.replace(/`(.*?)`/g, '$1'); // Code
                clean = clean.replace(/```[\s\S]*?```/g, ''); // Code blocks

                // Remove citations section
                clean = clean.replace(/::SOURCES::[\s\S]*/g, '');

                // Remove URLs
                clean = clean.replace(/https?:\/\/([^\s]+)/g, '');

                // Remove special markers
                clean = clean.replace(/::[A-Z_]+::/g, '');

                // Clean up whitespace
                clean = clean.replace(/\n{3,}/g, '\n\n');
                clean = clean.trim();

                return clean;
            }

            autoResizeTextarea(textarea) {
                textarea.style.height = 'auto';
                textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
            }

            updateCursorPlaceholder() {
                const promptInput = document.getElementById('promptInput');
                const cursorPlaceholder = document.getElementById('cursorPlaceholder');
                if (!promptInput || !cursorPlaceholder) return;

                const isEmpty = promptInput.value.trim().length === 0;
                const isFocused = document.activeElement === promptInput;

                if (isEmpty && isFocused) {
                    cursorPlaceholder.style.opacity = '1';
                } else {
                    cursorPlaceholder.style.opacity = '0';
                }
            }

            setupControlPanel() {
                const controlPanelTab = document.getElementById('controlPanelTab');
                const controlPanelDashboard = document.getElementById('controlPanelDashboard');
                const controlPanelClose = document.getElementById('controlPanelClose');

                if (!controlPanelTab || !controlPanelDashboard) return;

                // Toggle panel
                controlPanelTab.addEventListener('click', () => {
                    const isOpen = controlPanelDashboard.classList.contains('open');
                    if (isOpen) {
                        controlPanelDashboard.classList.remove('open');
                        controlPanelTab.classList.remove('active');
                    } else {
                        controlPanelDashboard.classList.add('open');
                        controlPanelTab.classList.add('active');
                    }
                });

                // Close button
                if (controlPanelClose) {
                    controlPanelClose.addEventListener('click', () => {
                        controlPanelDashboard.classList.remove('open');
                        controlPanelTab.classList.remove('active');
                    });
                }

                // Research mode toggle (Fast vs Deep Research)
                const deepResearchToggle = document.getElementById('deepResearchToggle');
                const modeLabel = document.getElementById('modeLabel');
                if (deepResearchToggle) {
                    const savedMode = localStorage.getItem('fastMode');
                    this.fastMode = savedMode === null ? true : savedMode === 'true'; // Default to fast
                    deepResearchToggle.checked = !this.fastMode; // Toggle is "deep research", so inverted

                    if (modeLabel) {
                        modeLabel.textContent = this.fastMode ? 'Fast' : 'Deep';
                    }

                    deepResearchToggle.addEventListener('change', (e) => {
                        this.fastMode = !e.target.checked; // Toggle is "deep research", so invert
                        localStorage.setItem('fastMode', this.fastMode);

                        if (modeLabel) {
                            modeLabel.textContent = this.fastMode ? 'Fast' : 'Deep';
                        }
                    });
                }

                // Thinking toggle
                const thinkingToggle = document.getElementById('thinkingToggle');
                if (thinkingToggle) {
                    // Load saved state
                    const savedThinking = localStorage.getItem('showThinking') === 'true';
                    thinkingToggle.checked = savedThinking;
                    this.showThinking = savedThinking;

                    thinkingToggle.addEventListener('change', (e) => {
                        this.showThinking = e.target.checked;
                        localStorage.setItem('showThinking', e.target.checked);
                    });
                }

                // Voice toggle
                const voiceToggle = document.getElementById('voiceToggle');
                const voiceSelectorItem = document.getElementById('voiceSelectorItem');

                // Edge AI Load button
                const loadEdgeBtn = document.getElementById('loadEdgeBtn');
                const edgeStatus = document.getElementById('edgeStatus');
                const edgeStatusText = document.getElementById('edgeStatusText');
                if (loadEdgeBtn) {
                    loadEdgeBtn.addEventListener('click', async () => {
                        loadEdgeBtn.style.display = 'none';
                        if (edgeStatus) {
                            edgeStatus.style.display = 'flex';
                            edgeStatus.classList.add('loading');
                        }

                        try {
                            await this.ensureEdgeAI();
                            if (edgeStatus) {
                                edgeStatus.classList.remove('loading');
                                edgeStatus.classList.add('ready');
                                if (edgeStatusText) edgeStatusText.textContent = 'Ready';
                            }
                        } catch (error) {
                            if (edgeStatus) {
                                edgeStatus.classList.remove('loading');
                                if (edgeStatusText) edgeStatusText.textContent = 'Error';
                            }
                            loadEdgeBtn.style.display = 'block';
                        }
                    });
                }
                const voiceSelector = document.getElementById('voiceSelector');

                if (voiceToggle) {
                    const self = this; // Preserve this context
                    const savedVoice = localStorage.getItem('ttsEnabled') === 'true';
                    voiceToggle.checked = savedVoice;
                    self.ttsEnabled = savedVoice;

                    voiceToggle.addEventListener('change', (e) => {
                        self.ttsEnabled = e.target.checked;
                        localStorage.setItem('ttsEnabled', e.target.checked);

                        if (e.target.checked) {
                            voiceSelectorItem.style.display = 'block';
                            // Always reinitialize to get best voice
                            if (self && typeof self.initializeTTS === 'function') {
                                self.initializeTTS();
                            }
                            // Reload voice selector to show updated list
                            if (voiceSelector) {
                                const voices = speechSynthesis.getVoices();
                                if (voices.length > 0) {
                                    const loadVoicesInner = () => {
                                        const voices = speechSynthesis.getVoices();
                                        if (!voices || voices.length === 0) {
                                            voiceSelector.innerHTML = '<option value="">No voices available</option>';
                                            return;
                                        }

                                        voiceSelector.innerHTML = '';

                                        const realisticVoices = [];
                                        const otherVoices = [];

                                        voices.forEach((voice, index) => {
                                            const name = voice.name.toLowerCase();
                                            const isRealistic =
                                                name.includes('premium') ||
                                                name.includes('neural') ||
                                                name.includes('wavenet') ||
                                                name.includes('aria') ||
                                                name.includes('jenny') ||
                                                name.includes('samantha') ||
                                                name.includes('alex') ||
                                                name.includes('victoria') ||
                                                name.includes('karen');

                                            const voiceData = { voice, index, name: voice.name, lang: voice.lang };

                                            if (isRealistic) {
                                                realisticVoices.push(voiceData);
                                            } else {
                                                otherVoices.push(voiceData);
                                            }
                                        });

                                        if (realisticVoices.length > 0) {
                                            const optgroup = document.createElement('optgroup');
                                            optgroup.label = 'Most Realistic';
                                            realisticVoices.forEach(({ voice, index }) => {
                                                const option = document.createElement('option');
                                                option.value = index;
                                                // Mark Premium/Neural voices as most realistic
                                                const isPremium = voice.name.includes('Premium') || voice.name.includes('Neural');
                                                const label = isPremium
                                                    ? `${voice.name} ⭐ MOST REALISTIC (${voice.lang})`
                                                    : `${voice.name} (${voice.lang})`;
                                                option.textContent = label;
                                                if (voice === self.ttsVoice) {
                                                    option.selected = true;
                                                }
                                                optgroup.appendChild(option);
                                            });
                                            voiceSelector.appendChild(optgroup);
                                        }

                                        if (otherVoices.length > 0) {
                                            const optgroup = document.createElement('optgroup');
                                            optgroup.label = 'Other Voices';
                                            otherVoices.forEach(({ voice, index }) => {
                                                const option = document.createElement('option');
                                                option.value = index;
                                                option.textContent = `${voice.name} (${voice.lang})`;
                                                if (voice === self.ttsVoice) {
                                                    option.selected = true;
                                                }
                                                optgroup.appendChild(option);
                                            });
                                            voiceSelector.appendChild(optgroup);
                                        }
                                    };

                                    // Try to load voices immediately
                                    const voicesCheck = speechSynthesis.getVoices();
                                    if (voicesCheck && voicesCheck.length > 0) {
                                        loadVoicesInner();
                                    } else {
                                        speechSynthesis.onvoiceschanged = loadVoicesInner;
                                        // Fallback: Try again after delay
                                        setTimeout(() => {
                                            const delayedVoices = speechSynthesis.getVoices();
                                            if (delayedVoices && delayedVoices.length > 0) {
                                                loadVoicesInner();
                                            }
                                        }, 500);
                                    }
                                }
                            }
                        } else {
                            voiceSelectorItem.style.display = 'none';
                            if (self && typeof self.stopTTS === 'function') {
                                self.stopTTS();
                            }
                        }
                    });
                }

                // Voice selector - prioritize realistic voices
                if (voiceSelector) {
                    const self = this; // Preserve this context
                    // Load voices when available, prioritizing realistic ones
                    const loadVoices = () => {
                        const voices = speechSynthesis.getVoices();
                        if (!voices || voices.length === 0) {
                            voiceSelector.innerHTML = '<option value="">No voices available</option>';
                            return;
                        }

                        voiceSelector.innerHTML = '';

                        // Separate realistic voices from others
                        const realisticVoices = [];
                        const otherVoices = [];

                        voices.forEach((voice, index) => {
                            const name = voice.name.toLowerCase();
                            // Prioritize Premium and Neural voices (MOST REALISTIC)
                            // Premium voices are highest quality, then Neural, then high-quality standards
                            const isRealistic =
                                name.includes('premium') ||   // macOS Premium (MOST REALISTIC)
                                name.includes('neural') ||    // Windows/Chrome Neural (VERY REALISTIC)
                                name.includes('wavenet') ||   // Google Wavenet (high quality)
                                name.includes('aria') ||      // Windows Neural (realistic)
                                name.includes('jenny') ||     // Windows Neural (realistic)
                                name.includes('samantha') ||  // macOS (very realistic)
                                name.includes('alex') ||      // macOS (very realistic)
                                name.includes('victoria') ||  // macOS (very realistic)
                                name.includes('karen');       // macOS (very realistic)

                            const voiceData = { voice, index, name: voice.name, lang: voice.lang };

                            if (isRealistic) {
                                realisticVoices.push(voiceData);
                            } else {
                                otherVoices.push(voiceData);
                            }
                        });

                        // Add realistic voices first with label
                        if (realisticVoices.length > 0) {
                            const optgroup = document.createElement('optgroup');
                            optgroup.label = 'Most Realistic';
                            realisticVoices.forEach(({ voice, index }) => {
                                const option = document.createElement('option');
                                option.value = index;
                                // Mark Premium/Neural as most realistic
                                const isPremium = voice.name.includes('Premium') || voice.name.includes('Neural');
                                const label = isPremium
                                    ? `${voice.name} ⭐ MOST REALISTIC (${voice.lang})`
                                    : `${voice.name} (${voice.lang})`;
                                option.textContent = label;
                                if (voice === self.ttsVoice) {
                                    option.selected = true;
                                }
                                optgroup.appendChild(option);
                            });
                            voiceSelector.appendChild(optgroup);
                        }

                        // Add other voices
                        if (otherVoices.length > 0) {
                            const optgroup = document.createElement('optgroup');
                            optgroup.label = 'Other Voices';
                            otherVoices.forEach(({ voice, index }) => {
                                const option = document.createElement('option');
                                option.value = index;
                                option.textContent = `${voice.name} (${voice.lang})`;
                                if (voice === self.ttsVoice) {
                                    option.selected = true;
                                }
                                optgroup.appendChild(option);
                            });
                            voiceSelector.appendChild(optgroup);
                        }

                        // Show selector if voice is enabled
                        if (self.ttsEnabled) {
                            voiceSelectorItem.style.display = 'block';
                        }
                    };

                    // Try to load voices immediately
                    const voices = speechSynthesis.getVoices();
                    if (voices && voices.length > 0) {
                        loadVoices();
                    } else {
                        // Wait for voices to load (some browsers require user interaction)
                        speechSynthesis.onvoiceschanged = loadVoices;
                        // Fallback: Try again after a short delay
                        setTimeout(() => {
                            const delayedVoices = speechSynthesis.getVoices();
                            if (delayedVoices && delayedVoices.length > 0) {
                                loadVoices();
                            } else {
                                // Update message to indicate user needs to click
                                voiceSelector.innerHTML = '<option value="">Click dropdown to load voices...</option>';
                            }
                        }, 500);

                        // Also try loading when user clicks the dropdown (required by some browsers)
                        voiceSelector.addEventListener('mousedown', function loadOnClick() {
                            const clickedVoices = speechSynthesis.getVoices();
                            if (clickedVoices && clickedVoices.length > 0 && voiceSelector.innerHTML.includes('Click')) {
                                loadVoices();
                            }
                        }, { once: true });
                    }

                    // Always try to load voices when dropdown is opened
                    voiceSelector.addEventListener('mousedown', function loadOnOpen() {
                        const clickedVoices = speechSynthesis.getVoices();
                        if (clickedVoices && clickedVoices.length > 0 && voiceSelector.innerHTML.includes('Loading')) {
                            loadVoices();
                        }
                    });

                    voiceSelector.addEventListener('change', (e) => {
                        const voices = speechSynthesis.getVoices();
                        const selectedIndex = parseInt(e.target.value);
                        if (voices[selectedIndex]) {
                            self.ttsVoice = voices[selectedIndex];
                            localStorage.setItem('ttsVoiceIndex', selectedIndex);
                            // Stop current speech and restart with new voice
                            self.stopTTS();
                        }
                    });

                    // Load saved voice or auto-select most realistic
                    const savedVoiceIndex = localStorage.getItem('ttsVoiceIndex');
                    if (savedVoiceIndex !== null) {
                        setTimeout(() => {
                            const voices = speechSynthesis.getVoices();
                            if (voices[savedVoiceIndex]) {
                                self.ttsVoice = voices[savedVoiceIndex];
                                voiceSelector.value = savedVoiceIndex;
                            } else {
                                // Saved voice not found, auto-select most realistic
                                if (self && typeof self.initializeTTS === 'function') {
                                    self.initializeTTS();
                                    if (self.ttsVoice) {
                                        const index = voices.indexOf(self.ttsVoice);
                                        if (index >= 0) {
                                            voiceSelector.value = index;
                                        }
                                    }
                                }
                            }
                        }, 500);
                    } else {
                        // No saved voice - auto-select most realistic
                        setTimeout(() => {
                            if (self && typeof self.initializeTTS === 'function') {
                                self.initializeTTS();
                                if (self.ttsVoice) {
                                    const voices = speechSynthesis.getVoices();
                                    const index = voices.indexOf(self.ttsVoice);
                                    if (index >= 0) {
                                        voiceSelector.value = index;
                                        localStorage.setItem('ttsVoiceIndex', index);
                                    }
                                }
                            }
                        }, 500);
                    }
                }

                // Close panel when clicking outside
                document.addEventListener('click', (e) => {
                    if (controlPanelDashboard.classList.contains('open')) {
                        if (!controlPanelDashboard.contains(e.target) &&
                            !controlPanelTab.contains(e.target)) {
                            controlPanelDashboard.classList.remove('open');
                            controlPanelTab.classList.remove('active');
                        }
                    }
                });
            }
        }

// Initialize app when DOM is ready
try {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    try {
                        window.thesidiaApp = new ThesidiaApp();
                        console.log('Thesidia app initialized');

                        // Initialize nano dust and header profile
                        initNanoDust();
                        loadHeaderProfileImage();

                        // Initialize astrological time
                        initAstrologicalTime();

                        // Initialize star notepad
                        initStarNotepad();

                        // Initialize status selector
                        initStatusSelector();
                    } catch (error) {
                        console.error('Error initializing Thesidia app:', error);
                        // Show error message to user
                        const app = document.getElementById('app');
                        if (app) {
                            app.innerHTML = `
                        <div style="padding: 20px; color: #fff; background: #000;">
                            <h1>Error Loading Thesidia</h1>
                            <p>There was an error initializing the app. Please check the console for details.</p>
                            <p>Error: ${error.message}</p>
                        </div>
                    `;
                        }
                    }
                });
            } else {
                try {
                    window.thesidiaApp = new ThesidiaApp();
                    console.log('Thesidia app initialized');

                    // Initialize nano dust and header profile
                    initNanoDust();
                    loadHeaderProfileImage();

                    // Initialize astrological time
                    initAstrologicalTime();

                    // Initialize star notepad
                    initStarNotepad();

                    // Initialize status selector
                    initStatusSelector();
                } catch (error) {
                    console.error('Error initializing Thesidia app:', error);
                    const app = document.getElementById('app');
                    if (app) {
                        app.innerHTML = `
                    <div style="padding: 20px; color: #fff; background: #000;">
                        <h1>Error Loading Thesidia</h1>
                        <p>There was an error initializing the app. Please check the console for details.</p>
                        <p>Error: ${error.message}</p>
                    </div>
                `;
                    }
                }
            }
        } catch (error) {
            console.error('Fatal error:', error);
        }

        // Nano Dust Particles Animation - Fine particles emanating from letters
        function initNanoDust() {
            const canvas = document.getElementById('nanoDustCanvas');
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            const particles = [];
            const particleCount = 80; // More particles for finer effect

            // Set canvas size
            canvas.width = 200;
            canvas.height = 60;

            // Text position (centered)
            const textCenterX = canvas.width / 2;
            const textCenterY = canvas.height / 2;
            const textWidth = 140; // Approximate width of "THESIDIA"
            const textHeight = 30; // Approximate height

            // Create particles emanating from text area
            for (let i = 0; i < particleCount; i++) {
                // Start particles near the text (within text bounds)
                const startX = textCenterX + (Math.random() - 0.5) * textWidth;
                const startY = textCenterY + (Math.random() - 0.5) * textHeight;

                // Calculate direction away from center
                const angle = Math.atan2(startY - textCenterY, startX - textCenterX);
                const speed = Math.random() * 0.3 + 0.1; // Slow, fine movement

                particles.push({
                    x: startX,
                    y: startY,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed,
                    size: Math.random() * 0.8 + 0.3, // Much finer particles (0.3-1.1px)
                    opacity: Math.random() * 0.4 + 0.1, // Very subtle (0.1-0.5)
                    life: Math.random() * 100,
                    maxDistance: Math.random() * 40 + 20 // Distance before respawn
                });
            }

            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                particles.forEach(particle => {
                    // Update position - moving away from text
                    particle.x += particle.vx;
                    particle.y += particle.vy;
                    particle.life += 0.3;

                    // Calculate distance from text center
                    const dx = particle.x - textCenterX;
                    const dy = particle.y - textCenterY;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    // Respawn particle near text if it moves too far
                    if (distance > particle.maxDistance) {
                        // Respawn near text with new random position
                        particle.x = textCenterX + (Math.random() - 0.5) * textWidth;
                        particle.y = textCenterY + (Math.random() - 0.5) * textHeight;

                        // New direction away from center
                        const angle = Math.atan2(particle.y - textCenterY, particle.x - textCenterX);
                        const speed = Math.random() * 0.3 + 0.1;
                        particle.vx = Math.cos(angle) * speed;
                        particle.vy = Math.sin(angle) * speed;
                        particle.life = 0;
                    }

                    // Fade out as particles move away
                    const fadeDistance = Math.min(distance / particle.maxDistance, 1);
                    const pulse = Math.sin(particle.life * 0.1) * 0.2 + 0.8;
                    const alpha = particle.opacity * (1 - fadeDistance * 0.7) * pulse;

                    // Draw very fine particle
                    ctx.beginPath();
                    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
                    ctx.fill();
                });

                requestAnimationFrame(animate);
            }

            animate();
        }

        // Load header profile image
        function loadHeaderProfileImage() {
            const headerProfile = document.getElementById('headerProfilePicture');
            if (!headerProfile) return;

            const img = headerProfile.querySelector('img');
            if (!img) return;

            const savedImage = localStorage.getItem('profileImage');
            if (savedImage) {
                img.src = savedImage;
            }

            // Click to open sidebar
            headerProfile.addEventListener('click', () => {
                if (window.thesidiaApp) {
                    window.thesidiaApp.toggleLeftSidebar();
                }
            });
        }

        // Initialize Astrological Time
        async function initAstrologicalTime() {
            const indicator = document.getElementById('astroTimeIndicator');
            const timeText = document.getElementById('astroTimeText');
            if (!indicator || !timeText) return;

            async function updateAstroTime() {
                try {
                    const response = await fetch('/api/astronomical/current');
                    if (response.ok) {
                        const data = await response.json();

                        // Get current time in a format that shows astronomical significance
                        const now = new Date();
                        const hours = now.getHours().toString().padStart(2, '0');
                        const minutes = now.getMinutes().toString().padStart(2, '0');

                        // Format: HH:MM (very faint, small)
                        timeText.textContent = `${hours}:${minutes}`;
                    } else {
                        // Fallback to regular time
                        const now = new Date();
                        const hours = now.getHours().toString().padStart(2, '0');
                        const minutes = now.getMinutes().toString().padStart(2, '0');
                        timeText.textContent = `${hours}:${minutes}`;
                    }
                } catch (error) {
                    // Fallback to regular time
                    const now = new Date();
                    const hours = now.getHours().toString().padStart(2, '0');
                    const minutes = now.getMinutes().toString().padStart(2, '0');
                    timeText.textContent = `${hours}:${minutes}`;
                }
            }

            // Update immediately and then every minute
            updateAstroTime();
            setInterval(updateAstroTime, 60000);
        }

        // Initialize Star Notepad
        function initStarNotepad() {
            const notepadBtn = document.getElementById('starNotepadBtn');
            const notepadPanel = document.getElementById('starNotepadPanel');
            const notepadClose = document.getElementById('notepadClose');
            const notepadTextarea = document.getElementById('notepadTextarea');

            if (!notepadBtn || !notepadPanel || !notepadClose || !notepadTextarea) return;

            // Load saved notes from localStorage
            const savedNotes = localStorage.getItem('thesidia_notes');
            if (savedNotes) {
                notepadTextarea.value = savedNotes;
            }

            // Save notes on input
            notepadTextarea.addEventListener('input', () => {
                localStorage.setItem('thesidia_notes', notepadTextarea.value);
            });

            // Toggle notepad
            notepadBtn.addEventListener('click', () => {
                notepadPanel.classList.toggle('open');
            });

            // Close notepad
            notepadClose.addEventListener('click', () => {
                notepadPanel.classList.remove('open');
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && notepadPanel.classList.contains('open')) {
                    notepadPanel.classList.remove('open');
                }
            });

            // Close when clicking outside
            document.addEventListener('click', (e) => {
                if (notepadPanel.classList.contains('open') &&
                    !notepadPanel.contains(e.target) &&
                    !notepadBtn.contains(e.target)) {
                    notepadPanel.classList.remove('open');
                }
            });
        }

        // Initialize Status Selector
        function initStatusSelector() {
            const userNameText = document.getElementById('userNameText');
            const statusOrb = document.getElementById('statusOrb');
            const statusDropdown = document.getElementById('statusSelectorDropdown');

            if (!userNameText || !statusOrb || !statusDropdown) {
                console.warn('Status selector elements not found, retrying...');
                setTimeout(initStatusSelector, 100);
                return;
            }

            console.log('Initializing status selector...');

            // Load saved status from localStorage
            const savedStatus = localStorage.getItem('userStatus') || 'online';
            updateStatus(savedStatus);

            // Toggle dropdown on name click - use multiple event types for reliability
            function handleClick(e) {
                e.stopPropagation();
                e.preventDefault();
                statusDropdown.classList.toggle('open');
                console.log('Status selector clicked, dropdown open:', statusDropdown.classList.contains('open'));
            }

            // Remove any existing handlers first
            userNameText.onclick = null;
            const newHandler = handleClick;

            // Set onclick handler
            userNameText.onclick = newHandler;

            // Also add event listeners for mouse events
            userNameText.addEventListener('click', newHandler, false);
            userNameText.addEventListener('mousedown', function (e) {
                e.stopPropagation();
                statusDropdown.classList.toggle('open');
            }, false);

            // Handle status option clicks
            statusDropdown.querySelectorAll('.status-option').forEach(option => {
                option.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const status = option.dataset.status;
                    updateStatus(status);
                    localStorage.setItem('userStatus', status);
                    statusDropdown.classList.remove('open');
                });
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (statusDropdown.classList.contains('open') &&
                    !statusDropdown.contains(e.target) &&
                    !userNameText.contains(e.target)) {
                    statusDropdown.classList.remove('open');
                }
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && statusDropdown.classList.contains('open')) {
                    statusDropdown.classList.remove('open');
                }
            });

            function updateStatus(status) {
                // Remove all status classes
                statusOrb.classList.remove('status-online', 'status-offline', 'status-away', 'status-focused');
                // Add new status class
                statusOrb.classList.add(`status-${status}`);
                // Update title
                const statusNames = {
                    'online': 'Online',
                    'offline': 'Offline',
                    'away': 'Away',
                    'focused': 'Focused'
                };
                statusOrb.title = `Status: ${statusNames[status]}`;
            }
        }

        // Clean prompt bar - no controls needed, Thesidia handles everything automatically

        // Service Worker for PWA (optional)
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                // Service worker registration can be added here
            });
        }

