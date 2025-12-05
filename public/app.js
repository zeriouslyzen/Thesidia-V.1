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
        this.currentFormat = 'natural'; // 'natural' or 'structured'
        this.researchDepth = 2; // 1=Quick, 2=Deep, 3=Forensic
        this.attachedFiles = []; // Store attached files
        
        // User session management
        this.userId = null;
        this.sessionId = null;
        
        this.init();
    }
    
    init() {
        // Detect current page
        this.currentPage = this.detectPage();
        
        this.setupUserSession();
        
        // Initialize color theme
        this.initColorTheme();
        
        // Universal sidebar infrastructure - setup for ALL pages
        this.setupSidebarInfrastructure();
        
        // Only setup context-specific features if on contexts page
        if (this.currentPage === 'contexts') {
            this.setupEventListeners();
            this.loadConversations();
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
    
    detectPage() {
        const path = window.location.pathname;
        if (path.includes('stream.html') || path === '/stream.html') return 'stream';
        if (path.includes('profile.html') || path === '/profile.html') return 'profile';
        if (path.includes('archive.html') || path === '/archive.html') return 'archive';
        if (path.includes('settings/') || path.includes('/settings')) return 'settings';
        return 'contexts'; // Default to contexts
    }
    
    // Universal sidebar setup - called once for ALL pages
    setupSidebarInfrastructure() {
        const menuBtn = document.getElementById('menuBtn');
        const sidebar = document.getElementById('leftSidebar');
        const app = document.getElementById('app');
        const thesidiaTitle = document.getElementById('thesidiaTitle');
        
        if (!menuBtn || !sidebar || !app) return;
        
        // Menu toggle
        menuBtn.addEventListener('click', () => this.toggleLeftSidebar());
        
        // Click THESIDIA title to go to stream page
        if (thesidiaTitle) {
            thesidiaTitle.style.cursor = 'pointer';
            thesidiaTitle.addEventListener('click', () => {
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
    }
    
    setupSwipeGestures() {
        const sidebar = document.getElementById('leftSidebar');
        if (!sidebar) return;
        
        let touchStartX = 0;
        let touchStartY = 0;
        let touchEndX = 0;
        let touchEndY = 0;
        
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
                
                if (deltaX > 0 && !isOpen) {
                    // Swipe right to open
                    this.toggleLeftSidebar();
                } else if (deltaX < 0 && isOpen) {
                    // Swipe left to close
                    this.closeLeftSidebar();
                }
            }
            
            // Reset
            touchStartX = 0;
        }, { passive: true });
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
        document.body.classList.remove('theme-yellow', 'theme-green', 'theme-purple', 'theme-pink');
        document.documentElement.classList.remove('theme-yellow', 'theme-green', 'theme-purple', 'theme-pink');
        
        // Apply new theme (default doesn't need a class)
        if (theme !== 'default') {
            document.body.classList.add(`theme-${theme}`);
            document.documentElement.classList.add(`theme-${theme}`);
        }
        
        // Save to localStorage
        localStorage.setItem('thesidia_color_theme', theme);
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
        themeSelector.innerHTML = `
            <div class="settings-label" style="margin-top: 16px;">Color Theme</div>
            <div class="theme-options">
                <button class="theme-option ${localStorage.getItem('thesidia_color_theme') === 'default' ? 'active' : ''}" data-theme="default" title="Default White">
                    <span class="theme-color" style="background: #ffffff; box-shadow: 0 0 8px rgba(255,255,255,0.6);"></span>
                    <span>Default</span>
                </button>
                <button class="theme-option ${localStorage.getItem('thesidia_color_theme') === 'yellow' ? 'active' : ''}" data-theme="yellow" title="Yellow Neon">
                    <span class="theme-color" style="background: #ffff00; box-shadow: 0 0 8px rgba(255,255,0,0.6);"></span>
                    <span>Yellow</span>
                </button>
                <button class="theme-option ${localStorage.getItem('thesidia_color_theme') === 'green' ? 'active' : ''}" data-theme="green" title="Green Neon">
                    <span class="theme-color" style="background: #00ff00; box-shadow: 0 0 8px rgba(0,255,0,0.6);"></span>
                    <span>Green</span>
                </button>
                <button class="theme-option ${localStorage.getItem('thesidia_color_theme') === 'purple' ? 'active' : ''}" data-theme="purple" title="Purple Neon">
                    <span class="theme-color" style="background: #ff00ff; box-shadow: 0 0 8px rgba(255,0,255,0.6);"></span>
                    <span>Purple</span>
                </button>
                <button class="theme-option ${localStorage.getItem('thesidia_color_theme') === 'pink' ? 'active' : ''}" data-theme="pink" title="Pink Neon">
                    <span class="theme-color" style="background: #ff00aa; box-shadow: 0 0 8px rgba(255,0,170,0.6);"></span>
                    <span>Pink</span>
                </button>
            </div>
        `;
        
        // Insert after settings nav
        settingsNav.parentElement.appendChild(themeSelector);
        
        // Add click handlers
        themeSelector.querySelectorAll('.theme-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const theme = btn.dataset.theme;
                this.setColorTheme(theme);
                
                // Update active state
                themeSelector.querySelectorAll('.theme-option').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
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
            
            // Auto-resize textarea
            promptInput.addEventListener('input', () => this.autoResizeTextarea(promptInput));
            
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
        
        // Format selector (HUD controls)
        const formatNatural = document.getElementById('formatNatural');
        const formatStructured = document.getElementById('formatStructured');
        const formatDisplay = document.getElementById('formatDisplay');
        if (formatNatural && formatStructured) {
            formatNatural.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.currentFormat = 'natural';
                formatNatural.classList.add('active');
                formatStructured.classList.remove('active');
                if (formatDisplay) formatDisplay.textContent = 'NAT';
            });
            formatStructured.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.currentFormat = 'structured';
                formatStructured.classList.add('active');
                formatNatural.classList.remove('active');
                if (formatDisplay) formatDisplay.textContent = 'STR';
            });
        }
        
        // Research depth controls (HUD buttons)
        const depthButtons = document.querySelectorAll('.hud-control-btn[data-depth]');
        const depthDisplay = document.getElementById('depthDisplay');
        depthButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.researchDepth = parseInt(btn.dataset.depth);
                depthButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                if (depthDisplay) depthDisplay.textContent = this.researchDepth.toString();
            });
        });
        
        // Initialize HUD displays
        if (formatDisplay) formatDisplay.textContent = this.currentFormat === 'natural' ? 'NAT' : 'STR';
        if (depthDisplay) depthDisplay.textContent = this.researchDepth.toString();
        
        // Character count tracking
        const charDisplay = document.getElementById('charDisplay');
        const promptInput = document.getElementById('promptInput');
        if (promptInput && charDisplay) {
            promptInput.addEventListener('input', () => {
                const count = promptInput.value.length;
                charDisplay.textContent = count > 999 ? '999+' : count.toString();
            });
        }
        
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
        
        // Add user message
        this.addMessage('user', message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Disable send button
        this.isProcessing = true;
        this.updateSendButton();
        if (this.updateHUDStatus) this.updateHUDStatus('processing');
        
        try {
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
        
        // Use streaming by default
        return new Promise((resolve, reject) => {
            // Create message element for streaming
            const messagesContainer = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message thesidia';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            const textElement = document.createElement('p');
            textElement.textContent = '';
            contentDiv.appendChild(textElement);
            
            messageDiv.appendChild(contentDiv);
            messagesContainer.appendChild(messageDiv);
            
            // Progress indicator - Better styling
            const progressDiv = document.createElement('div');
            progressDiv.className = 'progress-indicator';
            progressDiv.style.display = 'none';
            progressDiv.style.marginTop = '12px';
            messageDiv.appendChild(progressDiv);
            
            // Thinking indicator (if enabled)
            let thinkingDiv = null;
            if (this.showThinking) {
                thinkingDiv = document.createElement('div');
                thinkingDiv.className = 'thinking-indicator';
                thinkingDiv.style.display = 'none';
                thinkingDiv.style.marginTop = '8px';
                messageDiv.appendChild(thinkingDiv);
            }
            
            // Use fetch - handle both streaming and non-streaming
            const useStreaming = true; // Enable streaming for better UX
            fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: sanitizedMessage,
                    conversation_id: this.currentConversationId,
                    show_thinking: this.showThinking,
                    format: this.currentFormat, // 'natural' or 'structured'
                    research_depth: this.researchDepth, // 1=Quick, 2=Deep, 3=Forensic
                    stream: useStreaming,
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            }).then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                // Check content type to determine if streaming or JSON
                const contentType = response.headers.get('content-type') || '';
                
                if (useStreaming && contentType.includes('text/event-stream')) {
                    // Handle streaming response (SSE)
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = '';
                    let fullResponse = '';
                    let currentEvent = null;
                    
                    const readChunk = () => {
                        reader.read().then(({ done, value }) => {
                            if (done) {
                                // Complete
                                this.hideTypingIndicator();
                                if (progressDiv.parentNode) {
                                    progressDiv.style.display = 'none';
                                }
                                this.scrollToBottom();
                                this.saveConversation(sanitizedMessage, fullResponse);
                                resolve(fullResponse);
                                return;
                            }
                            
                            buffer += decoder.decode(value, { stream: true });
                            const lines = buffer.split('\n');
                            buffer = lines.pop() || ''; // Keep incomplete line in buffer
                            
                            for (const line of lines) {
                                if (line.trim() === '') continue;
                                
                                if (line.startsWith('event: ')) {
                                    currentEvent = line.substring(7).trim();
                                    continue;
                                }
                                
                                if (line.startsWith('data: ')) {
                                    try {
                                        const data = JSON.parse(line.substring(6));
                                        
                                        if (data.phase === 'progress' || currentEvent === 'progress') {
                                            // Update progress indicator with better visibility
                                            progressDiv.style.display = 'block';
                                            progressDiv.textContent = `${data.message} (${Math.round(data.progress)}%)`;
                                            progressDiv.className = 'progress-indicator active';
                                            this.scrollToBottom();
                                        } else if (data.text || currentEvent === 'chunk') {
                                            // Stream text chunk with typing animation
                                            const chunk = data.text || '';
                                            fullResponse += chunk;
                                            
                                            // Update status to streaming
                                            if (this.updateHUDStatus && chunk.length > 0) {
                                                this.updateHUDStatus('streaming');
                                            }
                                            
                                            // Hide progress when streaming starts
                                            if (chunk.length > 0 && progressDiv.style.display !== 'none') {
                                                progressDiv.style.display = 'none';
                                            }
                                            
                                            // Add chunk to typing queue for smooth character-by-character display
                                            this.typeText(textElement, chunk, () => {
                                                this.scrollToBottom();
                                            });
                                        } else if (currentEvent === 'thinking' || data.thinking) {
                                            // Show thinking steps
                                            if (this.showThinking) {
                                                this.displayThinkingStep(data.step || 'thinking', data.message || data.thinking);
                                                
                                                // Also show inline thinking indicator
                                                if (thinkingDiv) {
                                                    thinkingDiv.style.display = 'block';
                                                    thinkingDiv.textContent = `${data.message || data.thinking}`;
                                                }
                                            }
                                        } else if (data.phase === 'complete' || currentEvent === 'complete') {
                                            // Complete
                                            progressDiv.style.display = 'none';
                                            this.hideTypingIndicator();
                                            if (this.updateHUDStatus) this.updateHUDStatus('ready');
                                        } else if (data.error || currentEvent === 'error') {
                                            // Error
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
                            console.error('Streaming error:', err);
                            this.hideTypingIndicator();
                            if (progressDiv.parentNode) {
                                progressDiv.style.display = 'none';
                            }
                            reject(err);
                        });
                    };
                    
                    readChunk();
                } else {
                    // Handle non-streaming JSON response
                    return response.json().then(data => {
                        this.hideTypingIndicator();
                        if (progressDiv.parentNode) {
                            progressDiv.style.display = 'none';
                        }
                        
                        const responseText = data.response || data.message || 'No response';
                        textElement.textContent = responseText;
                        this.scrollToBottom();
                        this.saveConversation(sanitizedMessage, responseText);
                        resolve(responseText);
                    });
                }
            }).catch(err => {
                console.error('Fetch error:', err);
                this.hideTypingIndicator();
                if (progressDiv.parentNode) {
                    progressDiv.style.display = 'none';
                }
                textElement.textContent = `Error: ${err.message}`;
                reject(err);
            });
        });
    }
    
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
                format: this.currentFormat, // 'natural' or 'structured'
                research_depth: this.researchDepth, // 1=Quick, 2=Deep, 3=Forensic
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
    
    addMessage(type, content) {
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Format content (support markdown-like formatting)
        const formattedContent = this.formatMessage(content);
        contentDiv.innerHTML = formattedContent;
        
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Remove system message if exists
        const systemMessage = messagesContainer.querySelector('.system-message');
        if (systemMessage && type !== 'system') {
            systemMessage.remove();
        }
    }
    
    formatMessage(content) {
        // Simple formatting - convert code blocks, preserve line breaks
        return content
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
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
        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = '';
        
        conversation.messages.forEach(msg => {
            this.addMessage(msg.type, msg.content);
        });
        
        this.updateConversationsList();
        this.closeLeftSidebar();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
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

// Service Worker for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Service worker registration can be added here
    });
}

