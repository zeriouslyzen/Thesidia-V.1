// Katanx Navigation System - Carousel with Swipe Gestures

class NavigationSystem {
    constructor() {
        this.currentSection = 'home';
        this.sections = ['home', 'stream', 'kx-cuts', 'circles', 'studio'];
        this.sectionIndex = 0;
        this.isTransitioning = false;
        this.touchStartX = 0;
        this.touchEndX = 0;
        this.swipeThreshold = 50;
        this.selectedCategory = null; // For filtering circles by category
        
        this.init();
    }
    
    init() {
        this.setupCarousel();
        this.setupNavigationButtons();
        this.setupSwipeGestures();
        this.setupKeyboardNavigation();
        this.loadInitialSection();
    }
    
    setupCarousel() {
        const carouselTrack = document.querySelector('.carousel-track');
        if (!carouselTrack) return;
        
        // Ensure carousel starts at position 0 (home section)
        this.sectionIndex = 0;
        this.currentSection = 'home';
        
        // Set initial position immediately (no transition)
        carouselTrack.style.transition = 'none';
        this.updateCarouselPosition();
        
        // Re-enable transitions after a brief moment
        setTimeout(() => {
            carouselTrack.style.transition = 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
        }, 50);
    }
    
    setupNavigationButtons() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach((item, index) => {
            // Remove any existing listeners to prevent duplicates
            const newItem = item.cloneNode(true);
            item.parentNode.replaceChild(newItem, item);
            
            newItem.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const section = newItem.dataset.section;
                console.log('Nav item clicked:', section);
                if (section) {
                    this.navigateToSection(section);
                }
            }, { once: false });
        });
        
        // Setup filter buttons for circles and studio
        this.setupFilterButtons();
    }
    
    setupFilterButtons() {
        // Circles filter buttons
        const circlesFilters = document.querySelectorAll('.circles-filters .filter-btn');
        circlesFilters.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                circlesFilters.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.loadCirclesContent();
            });
        });
        
        // Studio filter buttons
        const studioFilters = document.querySelectorAll('.studio-filters .filter-btn');
        studioFilters.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                studioFilters.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.loadStudioContent();
            });
        });
    }
    
    setupSwipeGestures() {
        const carousel = document.querySelector('.content-carousel');
        if (!carousel) return;
        
        // Touch events
        carousel.addEventListener('touchstart', (e) => {
            this.touchStartX = e.touches[0].clientX;
        }, { passive: true });
        
        carousel.addEventListener('touchmove', (e) => {
            // Allow default scrolling behavior
        }, { passive: true });
        
        carousel.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].clientX;
            this.handleSwipe();
        }, { passive: true });
        
        // Mouse events for desktop drag
        let isMouseDown = false;
        let mouseStartX = 0;
        
        carousel.addEventListener('mousedown', (e) => {
            isMouseDown = true;
            mouseStartX = e.clientX;
            carousel.style.cursor = 'grabbing';
        });
        
        carousel.addEventListener('mousemove', (e) => {
            if (!isMouseDown) return;
            // Prevent text selection during drag
            e.preventDefault();
        });
        
        carousel.addEventListener('mouseup', (e) => {
            if (isMouseDown) {
                const mouseEndX = e.clientX;
                this.touchStartX = mouseStartX;
                this.touchEndX = mouseEndX;
                this.handleSwipe();
                isMouseDown = false;
                carousel.style.cursor = '';
            }
        });
        
        carousel.addEventListener('mouseleave', () => {
            isMouseDown = false;
            carousel.style.cursor = '';
        });
    }
    
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (this.isTransitioning) return;
            
            if (e.key === 'ArrowLeft') {
                this.navigatePrevious();
            } else if (e.key === 'ArrowRight') {
                this.navigateNext();
            }
        });
    }
    
    handleSwipe() {
        if (this.isTransitioning) return;
        
        const swipeDistance = this.touchStartX - this.touchEndX;
        
        if (Math.abs(swipeDistance) > this.swipeThreshold) {
            if (swipeDistance > 0) {
                // Swipe left - next section
                this.navigateNext();
            } else {
                // Swipe right - previous section
                this.navigatePrevious();
            }
        }
    }
    
    navigateToSection(sectionName) {
        console.log('=== NAVIGATE TO SECTION ===', sectionName);
        console.log('Current state:', {
            isTransitioning: this.isTransitioning,
            currentSection: this.currentSection,
            sectionIndex: this.sectionIndex
        });
        
        if (this.isTransitioning) {
            console.log('Navigation blocked: already transitioning');
            return;
        }
        
        if (!this.sections.includes(sectionName)) {
            console.log('Navigation blocked: section not in list', sectionName);
            return;
        }
        
        const newIndex = this.sections.indexOf(sectionName);
        if (newIndex === this.sectionIndex) {
            console.log('Already on section, reloading content:', sectionName);
            this.loadSectionContent(sectionName).catch(err => console.error('Error reloading:', err));
            return;
        }
        
        console.log('Navigating from', this.sectionIndex, 'to', newIndex, '(', sectionName, ')');
        
        this.isTransitioning = true;
        this.sectionIndex = newIndex;
        this.currentSection = sectionName;
        
        // Update active section class
        const allSections = document.querySelectorAll('.carousel-section');
        console.log('Found', allSections.length, 'sections');
        allSections.forEach(section => {
            section.classList.remove('active');
            if (section.dataset.section === sectionName) {
                section.classList.add('active');
                console.log('Activated section:', sectionName);
            }
        });
        
        this.updateCarouselPosition();
        this.updateActiveNavState();
        
        // Load content immediately - don't wait
        console.log('Loading content for:', sectionName);
        this.loadSectionContent(sectionName).catch(err => {
            console.error('Error loading section content:', err);
        });
        
        // Reset transition flag after animation
        setTimeout(() => {
            this.isTransitioning = false;
            console.log('Navigation transition complete:', sectionName);
        }, 600);
    }
    
    navigateNext() {
        if (this.sectionIndex < this.sections.length - 1) {
            this.navigateToSection(this.sections[this.sectionIndex + 1]);
        }
    }
    
    navigatePrevious() {
        if (this.sectionIndex > 0) {
            this.navigateToSection(this.sections[this.sectionIndex - 1]);
        }
    }
    
    updateCarouselPosition() {
        const carouselTrack = document.querySelector('.carousel-track');
        const carouselContainer = document.querySelector('.content-carousel');
        if (!carouselTrack || !carouselContainer) return;
        
        // Calculate transform in pixels based on container width
        // Each section is 100% of container width
        const containerWidth = carouselContainer.offsetWidth;
        const translateX = -(this.sectionIndex * containerWidth);
        carouselTrack.style.transform = `translateX(${translateX}px)`;
        console.log('Carousel position updated:', {
            sectionIndex: this.sectionIndex,
            translateX: translateX + 'px',
            containerWidth: containerWidth,
            currentSection: this.currentSection
        });
    }
    
    updateActiveNavState() {
        const navItems = document.querySelectorAll('.nav-item');
        const activeItem = document.querySelector(`.nav-item[data-section="${this.currentSection}"]`);
        
        if (!activeItem) return;
        
        // Update active states
        navItems.forEach(item => item.classList.remove('active'));
        activeItem.classList.add('active');
    }
    
    loadInitialSection() {
        // Check URL hash or default to 'home'
        const hash = window.location.hash.slice(1);
        const initialSection = this.sections.includes(hash) ? hash : 'home';
        
        this.sectionIndex = this.sections.indexOf(initialSection);
        this.currentSection = initialSection;
        
        // Set initial active section
        const allSections = document.querySelectorAll('.carousel-section');
        allSections.forEach(section => {
            section.classList.remove('active');
            if (section.dataset.section === initialSection) {
                section.classList.add('active');
            }
        });
        
        this.updateCarouselPosition();
        this.updateActiveNavState();
        this.loadSectionContent(initialSection);
    }
    
    async loadSectionContent(sectionName) {
        console.log('=== LOAD SECTION CONTENT ===', sectionName);
        try {
            // Load content for the section
            switch (sectionName) {
                case 'home':
                    console.log('Loading home content...');
                    await this.loadHomeContent();
                    break;
                case 'stream':
                    console.log('Loading stream content...');
                    await this.loadStreamContent();
                    break;
                case 'kx-cuts':
                    console.log('Loading kx-cuts content...');
                    await this.loadKxCutsContent();
                    break;
                case 'circles':
                    console.log('Loading circles content...');
                    await this.loadCirclesContent();
                    break;
                case 'studio':
                    console.log('Loading studio content...');
                    await this.loadStudioContent();
                    break;
                default:
                    console.warn('Unknown section:', sectionName);
            }
            console.log('Section content loaded:', sectionName);
        } catch (error) {
            console.error('Error in loadSectionContent for', sectionName, ':', error);
            throw error;
        }
    }
    
    async loadHomeContent() {
        try {
            let userId = localStorage.getItem('thesidia_user_id');
            let sessionId = localStorage.getItem('thesidia_session_id');
            
            // Create session if doesn't exist
            if (!sessionId) {
                try {
                    const sessionResponse = await fetch('/api/user/session', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({})
                    });
                    const sessionData = await sessionResponse.json();
                    userId = sessionData.user_id;
                    sessionId = sessionData.session_id;
                    localStorage.setItem('thesidia_user_id', userId);
                    localStorage.setItem('thesidia_session_id', sessionId);
                } catch (e) {
                    console.warn('Could not create session, using mock data:', e);
                }
            }
            
            const url = `/api/sections/home?user_id=${userId || ''}&session_id=${sessionId || ''}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Home data loaded:', data);
            
            // Update dashboard widgets
            if (data.stats) {
                const postsCount = document.getElementById('homePostsCount');
                const interactionsCount = document.getElementById('homeInteractionsCount');
                const connectionsCount = document.getElementById('homeConnectionsCount');
                
                if (postsCount) postsCount.textContent = data.stats.posts || 0;
                if (interactionsCount) interactionsCount.textContent = data.stats.interactions || 0;
                if (connectionsCount) connectionsCount.textContent = data.stats.connections || 0;
            }
            
            // Update activity list
            const activityList = document.getElementById('homeActivityList');
            if (activityList) {
                if (data.recent_activity && data.recent_activity.length > 0) {
                    activityList.innerHTML = data.recent_activity.map(activity => `
                        <div class="activity-item">
                            <span class="activity-text">${activity.text}</span>
                            <span class="activity-time">${activity.time}</span>
                        </div>
                    `).join('');
                } else {
                    activityList.innerHTML = '<div class="activity-item">No recent activity</div>';
                }
            }
        } catch (error) {
            console.error('Error loading home content:', error);
            const activityList = document.getElementById('homeActivityList');
            if (activityList) {
                activityList.innerHTML = '<div class="activity-item">Error loading activity</div>';
            }
        }
    }
    
    async loadStreamContent() {
        console.log('=== LOAD STREAM CONTENT ===');
        try {
            let userId = localStorage.getItem('thesidia_user_id');
            let sessionId = localStorage.getItem('thesidia_session_id');
            
            if (!sessionId) {
                try {
                    const sessionResponse = await fetch('/api/user/session', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({})
                    });
                    const sessionData = await sessionResponse.json();
                    userId = sessionData.user_id;
                    sessionId = sessionData.session_id;
                    localStorage.setItem('thesidia_user_id', userId);
                    localStorage.setItem('thesidia_session_id', sessionId);
                } catch (e) {
                    console.warn('Could not create session:', e);
                }
            }
            
            const url = `/api/sections/stream?user_id=${userId || ''}&session_id=${sessionId || ''}&limit=20&offset=0`;
            console.log('Fetching Stream from:', url);
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Stream data loaded:', data);
            
            // Try multiple ways to find the element
            let streamFeed = document.getElementById('streamFeed');
            if (!streamFeed) {
                const activeSection = document.querySelector('.carousel-section[data-section="stream"]');
                if (activeSection) {
                    streamFeed = activeSection.querySelector('#streamFeed');
                }
            }
            if (!streamFeed) {
                const allSections = document.querySelectorAll('.carousel-section[data-section="stream"]');
                console.log('Searching in', allSections.length, 'stream sections');
                for (const section of allSections) {
                    streamFeed = section.querySelector('#streamFeed');
                    if (streamFeed) break;
                }
            }
            
            if (streamFeed) {
                console.log('✅ Found streamFeed, rendering', data.items?.length || 0, 'items');
                if (data.items && data.items.length > 0) {
                    // Use StreamPage renderPosts if available, otherwise render directly
                    if (window.streamPage && typeof window.streamPage.renderPosts === 'function') {
                        window.streamPage.posts = data.items;
                        window.streamPage.renderPosts();
                    } else {
                        // Fallback: render directly using Components or basic HTML
                        if (typeof Components !== 'undefined' && Components.createStreamItem) {
                            streamFeed.innerHTML = data.items.map(item => Components.createStreamItem(item)).join('');
                        } else {
                            // Basic rendering
                            streamFeed.innerHTML = data.items.map(item => `
                                <div class="stream-item">
                                    <div class="stream-item-content">${item.content || ''}</div>
                                </div>
                            `).join('');
                        }
                    }
                    console.log('✅ Rendered', data.items.length, 'stream items');
                } else {
                    streamFeed.innerHTML = '<div class="stream-loading">No posts available</div>';
                }
            } else {
                console.error('❌ Could not find streamFeed element');
                console.error('All sections:', document.querySelectorAll('.carousel-section'));
            }
        } catch (error) {
            console.error('❌ Error loading stream content:', error);
            const streamFeed = document.getElementById('streamFeed');
            if (streamFeed) {
                streamFeed.innerHTML = '<div class="stream-loading">Error loading stream: ' + error.message + '</div>';
            }
        }
    }
    
    async loadKxCutsContent() {
        console.log('Loading KX Cuts content...');
        try {
            let userId = localStorage.getItem('thesidia_user_id');
            let sessionId = localStorage.getItem('thesidia_session_id');
            
            if (!sessionId) {
                try {
                    const sessionResponse = await fetch('/api/user/session', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({})
                    });
                    const sessionData = await sessionResponse.json();
                    userId = sessionData.user_id;
                    sessionId = sessionData.session_id;
                    localStorage.setItem('thesidia_user_id', userId);
                    localStorage.setItem('thesidia_session_id', sessionId);
                } catch (e) {
                    console.warn('Could not create session:', e);
                }
            }
            
            const url = `/api/sections/kx-cuts?user_id=${userId || ''}&session_id=${sessionId || ''}&limit=20`;
            console.log('Fetching KX Cuts from:', url);
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('KX Cuts data loaded:', data);
            
            // Try multiple ways to find the element
            let cutsFeed = document.getElementById('cutsFeed');
            if (!cutsFeed) {
                const activeSection = document.querySelector('.carousel-section[data-section="kx-cuts"]');
                if (activeSection) {
                    cutsFeed = activeSection.querySelector('#cutsFeed');
                }
            }
            if (!cutsFeed) {
                // Try querying all sections
                const allSections = document.querySelectorAll('.carousel-section[data-section="kx-cuts"]');
                console.log('Searching in', allSections.length, 'kx-cuts sections');
                for (const section of allSections) {
                    cutsFeed = section.querySelector('#cutsFeed');
                    if (cutsFeed) break;
                }
            }
            
            if (cutsFeed) {
                console.log('✅ Found cutsFeed, rendering', data.items?.length || 0, 'items');
                if (data.items && data.items.length > 0) {
                    cutsFeed.innerHTML = data.items.map(cut => this.renderCut(cut)).join('');
                    console.log('✅ Rendered', data.items.length, 'cuts');
                    this.setupCutInteractions();
                } else {
                    cutsFeed.innerHTML = '<div class="cuts-loading">No cuts available</div>';
                }
            } else {
                console.error('❌ Could not find cutsFeed element');
                console.error('All sections:', document.querySelectorAll('.carousel-section'));
                console.error('kx-cuts sections:', document.querySelectorAll('.carousel-section[data-section="kx-cuts"]'));
            }
        } catch (error) {
            console.error('Error loading kx cuts content:', error);
            const activeSection = document.querySelector('.carousel-section[data-section="kx-cuts"]');
            const cutsFeed = activeSection ? activeSection.querySelector('#cutsFeed') : document.getElementById('cutsFeed');
            if (cutsFeed) {
                cutsFeed.innerHTML = '<div class="cuts-loading">Error loading cuts: ' + error.message + '</div>';
            }
        }
    }
    
    renderCut(cut) {
        if (!cut || !cut.id) {
            return '';
        }
        
        const interactions = cut.interactions || {};
        const recognizeCount = interactions.recognize || interactions.recognitions || 0;
        const growthCount = interactions.growth || 0;
        const connectCount = interactions.connect || interactions.connections || 0;
        
        const timeAgo = this.formatTimeAgo(cut.created_at || cut.timestamp || new Date().toISOString());
        const domain = (cut.domains && cut.domains.length > 0) ? cut.domains[0] : (cut.domain || null);
        const author = cut.author || {};
        const username = author.username || author.user_id || 'unknown';
        const avatarUrl = author.avatar_url || '/profile-image.jpg';
        const videoUrl = cut.video_url || cut.media_url || '';
        const thumbnailUrl = cut.thumbnail_url || cut.poster_url || '';
        
        // Escape HTML to prevent XSS
        const safeUsername = String(username).replace(/[<>&"']/g, '');
        const safeDomain = domain ? String(domain).replace(/[<>&"']/g, '') : '';
        const safeCutId = String(cut.id).replace(/[<>&"']/g, '');
        
        return `
            <article class="cut-item" data-cut-id="${safeCutId}">
                <div class="cut-video-container">
                    ${videoUrl ? `<video class="cut-video" src="${videoUrl}" ${thumbnailUrl ? `poster="${thumbnailUrl}"` : ''} muted loading="lazy"></video>` : `<div class="cut-video-placeholder"></div>`}
                    
                    <!-- Creator Info Overlay (Top-Left) -->
                    <div class="cut-creator-overlay">
                        <div class="cut-avatar">
                            <img src="${avatarUrl}" alt="${safeUsername}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'20\' height=\'20\'%3E%3Ccircle cx=\'10\' cy=\'10\' r=\'10\' fill=\'%23ffffff\' fill-opacity=\'0.1\'/%3E%3Ccircle cx=\'10\' cy=\'7\' r=\'3\' fill=\'%23ffffff\' fill-opacity=\'0.3\'/%3E%3Cpath d=\'M5 18 Q10 15 15 18\' stroke=\'%23ffffff\' stroke-width=\'1\' fill=\'none\' stroke-opacity=\'0.3\'/%3E%3C/svg%3E'">
                        </div>
                        <div class="cut-creator-name">@${safeUsername}</div>
                    </div>
                    
                    <!-- Metadata Overlay (Top-Right) -->
                    <div class="cut-metadata-overlay">
                        <span class="cut-time">${timeAgo}</span>
                    </div>
                    
                    ${safeDomain ? `
                    <!-- Domain Tag Overlay (Bottom-Left, Optional) -->
                    <div class="cut-domains-overlay">
                        <span class="cut-domain-tag">${safeDomain}</span>
                    </div>
                    ` : ''}
                    
                    <!-- Interactions Overlay (Bottom-Right, On Hover) -->
                    <div class="cut-interactions-overlay">
                        <button class="cut-interaction-btn" data-action="recognize" data-cut-id="${safeCutId}" title="Recognize">
                            <span class="interaction-dot"></span>
                            <span class="interaction-count">${recognizeCount}</span>
                        </button>
                        <button class="cut-interaction-btn" data-action="growth" data-cut-id="${safeCutId}" title="Growth">
                            <span class="interaction-dot"></span>
                            <span class="interaction-count">${growthCount}</span>
                        </button>
                        <button class="cut-interaction-btn" data-action="connect" data-cut-id="${safeCutId}" title="Connect">
                            <span class="interaction-dot"></span>
                            <span class="interaction-count">${connectCount}</span>
                        </button>
                    </div>
                </div>
            </article>
        `;
    }
    
    formatTimeAgo(timestamp) {
        if (!timestamp) return 'now';
        try {
            const now = new Date();
            const postTime = new Date(timestamp);
            const diffMs = now - postTime;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);
            
            if (diffMins < 1) return 'now';
            if (diffMins < 60) return `${diffMins}m`;
            if (diffHours < 24) return `${diffHours}h`;
            if (diffDays < 7) return `${diffDays}d`;
            return postTime.toLocaleDateString();
        } catch (e) {
            return 'recently';
        }
    }
    
    setupCutInteractions() {
        const cutsFeed = document.getElementById('cutsFeed');
        if (!cutsFeed) return;
        
        cutsFeed.addEventListener('click', (e) => {
            const btn = e.target.closest('.cut-interaction-btn');
            if (!btn) return;
            
            const action = btn.dataset.action;
            const cutId = btn.dataset.cutId;
            
            if (!action || !cutId) return;
            
            this.handleCutInteraction(cutId, action, btn);
        });
    }
    
    async handleCutInteraction(cutId, action, btn) {
        try {
            const userId = localStorage.getItem('thesidia_user_id');
            const sessionId = localStorage.getItem('thesidia_session_id');
            
            if (!userId || !cutId || !action) {
                return;
            }
            
            const response = await fetch(`/api/cuts/${cutId}/${action}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    session_id: sessionId
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                const countSpan = btn.querySelector('.interaction-count');
                if (countSpan && data.count !== undefined) {
                    const currentCount = parseInt(countSpan.textContent) || 0;
                    countSpan.textContent = currentCount + 1;
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                console.error('Error handling cut interaction:', errorData.error || 'Unknown error');
            }
        } catch (error) {
            console.error('Error handling cut interaction:', error);
        }
    }
    
    async loadCirclesContent() {
        console.log('Loading Circles content...');
        try {
            let userId = localStorage.getItem('thesidia_user_id');
            let sessionId = localStorage.getItem('thesidia_session_id');
            
            if (!sessionId) {
                try {
                    const sessionResponse = await fetch('/api/user/session', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({})
                    });
                    const sessionData = await sessionResponse.json();
                    userId = sessionData.user_id;
                    sessionId = sessionData.session_id;
                    localStorage.setItem('thesidia_user_id', userId);
                    localStorage.setItem('thesidia_session_id', sessionId);
                } catch (e) {
                    console.warn('Could not create session:', e);
                }
            }
            
            const activeSection = document.querySelector('.carousel-section[data-section="circles"]');
            const filterBtn = activeSection ? activeSection.querySelector('.circles-filters .filter-btn.active') : document.querySelector('.circles-filters .filter-btn.active');
            const filter = filterBtn?.dataset.filter || 'all';
            
            const url = `/api/sections/circles?user_id=${userId || ''}&session_id=${sessionId || ''}&filter=${filter}&limit=20`;
            console.log('Fetching Circles from:', url);
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Circles data loaded:', data);
            
            // Load categories first
            await this.loadCirclesCategories(data.categories || []);
            
            // Try multiple ways to find the element
            let threadsContainer = document.getElementById('circlesThreads');
            if (!threadsContainer && activeSection) {
                threadsContainer = activeSection.querySelector('#circlesThreads');
            }
            if (!threadsContainer) {
                const allSections = document.querySelectorAll('.carousel-section[data-section="circles"]');
                console.log('Searching in', allSections.length, 'circles sections');
                for (const section of allSections) {
                    threadsContainer = section.querySelector('#circlesThreads');
                    if (threadsContainer) break;
                }
            }
            
            if (threadsContainer) {
                console.log('✅ Found circlesThreads, rendering', data.threads?.length || 0, 'threads');
                if (data.threads && data.threads.length > 0) {
                    threadsContainer.innerHTML = data.threads.map(thread => this.renderThread(thread)).join('');
                    console.log('✅ Rendered', data.threads.length, 'threads');
                    
                    // Initialize shifting previews
                    this.initializeShiftingPreviews(data.threads);
                    
                    // Add click handlers for navigation to thread detail
                    this.initializeThreadClickHandlers(threadsContainer);
                } else {
                    threadsContainer.innerHTML = '<div class="threads-loading">No threads found.</div>';
                }
            } else {
                console.error('❌ Could not find circlesThreads element');
                console.error('All sections:', document.querySelectorAll('.carousel-section'));
            }
        } catch (error) {
            console.error('Error loading circles content:', error);
            const activeSection = document.querySelector('.carousel-section[data-section="circles"]');
            const threadsContainer = activeSection ? activeSection.querySelector('#circlesThreads') : document.getElementById('circlesThreads');
            if (threadsContainer) {
                threadsContainer.innerHTML = '<div class="threads-loading">Error loading threads: ' + error.message + '</div>';
            }
        }
    }
    
    async loadCirclesCategories(categories) {
        const activeSection = document.querySelector('.carousel-section[data-section="circles"]');
        let categoriesContainer = activeSection ? activeSection.querySelector('#circlesCategoriesScroll') : document.getElementById('circlesCategoriesScroll');
        
        if (!categoriesContainer) {
            console.warn('Categories container not found');
            return;
        }
        
        // Add "All" category at the beginning
        const allCategories = [
            {
                id: 'all',
                name: 'All',
                slug: 'all',
                thread_count: null,
                avatar_url: null
            },
            ...(categories || [])
        ];
        
        // Render categories
        categoriesContainer.innerHTML = allCategories.map(cat => this.renderCategory(cat)).join('');
        
        // Initialize swipe functionality
        this.initializeCategorySwipe(categoriesContainer);
        
        // Add click handlers for category filtering
        const categoryItems = categoriesContainer.querySelectorAll('.circle-category-item');
        categoryItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const category = item.dataset.category;
                if (category) {
                    this.filterByCategory(category);
                }
            });
        });
    }
    
    async filterByCategory(category) {
        // Update active category visual state
        const activeSection = document.querySelector('.carousel-section[data-section="circles"]');
        const categoriesContainer = activeSection ? activeSection.querySelector('#circlesCategoriesScroll') : document.getElementById('circlesCategoriesScroll');
        
        if (categoriesContainer) {
            const categoryItems = categoriesContainer.querySelectorAll('.circle-category-item');
            categoryItems.forEach(item => {
                item.classList.remove('active');
                if (item.dataset.category === category) {
                    item.classList.add('active');
                }
            });
        }
        
        // Store selected category for filtering
        this.selectedCategory = category === 'all' ? null : category;
        
        // Reload threads - filtering will be handled in loadCirclesContent if needed
        await this.loadCirclesContent();
    }
    
    renderCategory(category) {
        const name = category.name || category.slug || 'Category';
        const slug = category.slug || category.id || '';
        const threadCount = category.thread_count;
        const isAll = slug === 'all';
        
        // Special handling for "All" category
        let avatarUrl, fallbackAvatarUrl, initial, color;
        if (isAll) {
            // Use a special icon/avatar for "All"
            initial = '•';
            color = '#666';
            avatarUrl = `https://api.dicebear.com/7.x/shapes/svg?seed=all&size=64&backgroundColor=666&radius=50`;
            fallbackAvatarUrl = `https://ui-avatars.com/api/?name=All&background=666&color=fff&size=64&bold=true`;
        } else {
            avatarUrl = this.getAvatarUrl(slug, slug);
            fallbackAvatarUrl = this.getFallbackAvatarUrl(slug, slug);
            initial = this.getCircleInitial(slug);
            color = this.getCircleColor(slug);
        }
        
        return `
            <div class="circle-category-item ${isAll ? 'active' : ''}" data-category="${slug}">
                <div class="circle-category-avatar-wrapper">
                    <img 
                        src="${avatarUrl}" 
                        alt="${this.escapeHtml(name)}" 
                        class="circle-category-avatar"
                        onerror="this.onerror=null; this.src='${fallbackAvatarUrl}';"
                        loading="lazy"
                    >
                    <div class="circle-category-avatar-fallback" style="display: none; background-color: ${color};">
                    </div>
                </div>
                <div class="circle-category-name">${this.escapeHtml(name)}</div>
                ${threadCount !== null && threadCount > 0 ? `<div class="circle-category-count">${threadCount}</div>` : ''}
            </div>
        `;
    }
    
    initializeCategorySwipe(container) {
        if (!container) return;
        
        let isDown = false;
        let startX = 0;
        let scrollLeft = 0;
        
        // Mouse events
        container.addEventListener('mousedown', (e) => {
            isDown = true;
            container.style.cursor = 'grabbing';
            startX = e.pageX - container.offsetLeft;
            scrollLeft = container.scrollLeft;
        });
        
        container.addEventListener('mouseleave', () => {
            isDown = false;
            container.style.cursor = 'grab';
        });
        
        container.addEventListener('mouseup', () => {
            isDown = false;
            container.style.cursor = 'grab';
        });
        
        container.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - container.offsetLeft;
            const walk = (x - startX) * 2; // Scroll speed multiplier
            container.scrollLeft = scrollLeft - walk;
        });
        
        // Touch events for mobile
        let touchStartX = 0;
        let touchScrollLeft = 0;
        
        container.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].pageX - container.offsetLeft;
            touchScrollLeft = container.scrollLeft;
        }, { passive: true });
        
        container.addEventListener('touchmove', (e) => {
            if (!touchStartX) return;
            const x = e.touches[0].pageX - container.offsetLeft;
            const walk = (x - touchStartX) * 1.5;
            container.scrollLeft = touchScrollLeft - walk;
        }, { passive: true });
        
        container.addEventListener('touchend', () => {
            touchStartX = 0;
        });
        
        // Set initial cursor
        container.style.cursor = 'grab';
    }
    
    getCircleInitial(topic) {
        if (!topic) return '?';
        return topic.charAt(0).toUpperCase();
    }
    
    getCircleColor(topic) {
        if (!topic) return '#666';
        const colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52BE80',
            '#EC7063', '#5DADE2', '#58D68D', '#F4D03F', '#AF7AC5'
        ];
        let hash = 0;
        for (let i = 0; i < topic.length; i++) {
            hash = topic.charCodeAt(i) + ((hash << 5) - hash);
        }
        return colors[Math.abs(hash) % colors.length];
    }
    
    getAvatarUrl(topic, authorId = null, authorAvatarUrl = null) {
        // First, check if author has an avatar URL
        if (authorAvatarUrl && authorAvatarUrl.trim()) {
            return authorAvatarUrl;
        }
        
        // Use DiceBear API for realistic-looking avatars
        // Using 'personas' style for more photo-like appearance
        const seed = authorId || topic || 'default';
        
        // Generate consistent seed from topic/author
        let seedHash = 0;
        const seedString = seed.toString();
        for (let i = 0; i < seedString.length; i++) {
            seedHash = seedString.charCodeAt(i) + ((seedHash << 5) - seedHash);
        }
        const numericSeed = Math.abs(seedHash);
        
        // Use personas style for more realistic photo-like avatars
        // Alternatives: avataaars (cartoon), personas (more realistic), adventurer
        const style = 'personas'; // Most photo-like
        const size = 80;
        
        const params = new URLSearchParams({
            seed: numericSeed.toString(),
            size: size.toString(),
            backgroundColor: this.getCircleColor(topic).replace('#', ''),
            radius: '50'
        });
        
        return `https://api.dicebear.com/7.x/${style}/svg?${params.toString()}`;
    }
    
    getFallbackAvatarUrl(topic, authorId = null) {
        // Use RandomUser.me API for realistic profile photos
        // Generate consistent seed from topic/author
        const seed = authorId || topic || 'default';
        let seedHash = 0;
        const seedString = seed.toString();
        for (let i = 0; i < seedString.length; i++) {
            seedHash = seedString.charCodeAt(i) + ((seedHash << 5) - seedHash);
        }
        const numericSeed = Math.abs(seedHash);
        
        // Use randomuser.me with seed for consistent faces
        // This provides realistic profile photos
        return `https://randomuser.me/api/portraits/${numericSeed % 2 === 0 ? 'men' : 'women'}/${numericSeed % 99}.jpg`;
    }
    
    formatMessageTime(createdAt) {
        if (!createdAt) return '';
        const date = new Date(createdAt);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'now';
        if (diffMins < 60) return `${diffMins}m`;
        if (diffHours < 24) return `${diffHours}h`;
        if (diffDays < 7) return `${diffDays}d`;
        
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const year = date.getFullYear();
        const currentYear = now.getFullYear();
        
        if (year === currentYear) {
            return `${month}/${day}`;
        }
        return `${month}/${day}/${year.toString().slice(2)}`;
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    renderThread(thread) {
        const topic = thread.circle || thread.title || 'Topic';
        const authorId = thread.author_id || thread.author?.user_id || null;
        const authorAvatarUrl = thread.author?.avatar_url || null;
        const avatarUrl = this.getAvatarUrl(topic, authorId, authorAvatarUrl);
        const fallbackAvatarUrl = this.getFallbackAvatarUrl(topic, authorId);
        const timeAgo = this.formatMessageTime(thread.created_at);
        
        // Get first part of paragraph (static preview) - shorter for compact mobile view
        const bodyText = (thread.body || '').trim();
        const paragraphPreview = bodyText ? 
            this.escapeHtml(bodyText.length > 80 ? bodyText.substring(0, 77) + '...' : bodyText) : 
            'No content available';
        
        // Create shifting indicators for comments/upvotes
        const indicators = [];
        if (thread.comment_count > 0) {
            indicators.push(`${thread.comment_count} comment${thread.comment_count !== 1 ? 's' : ''}`);
        }
        if (thread.upvotes > 0) {
            indicators.push(`${thread.upvotes} upvote${thread.upvotes !== 1 ? 's' : ''}`);
        }
        if (thread.views > 0) {
            indicators.push(`${thread.views} view${thread.views !== 1 ? 's' : ''}`);
        }
        
        const threadId = thread.id || `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const upvotes = thread.upvotes || 0;
        const commentCount = thread.comment_count || 0;
        
        return `
            <div class="circle-message-item" data-thread-id="${threadId}" data-category="${this.escapeHtml(topic)}">
                <img 
                    src="${avatarUrl}" 
                    alt="${this.escapeHtml(topic)}" 
                    class="circle-avatar-image"
                    onerror="this.onerror=null; this.src='${fallbackAvatarUrl}';"
                    loading="lazy"
                >
                <div class="circle-avatar-fallback" style="display: none;">
                </div>
                <div class="circle-message-content">
                    <div class="circle-message-header">
                        <span class="circle-topic-name">${this.escapeHtml(topic)}</span>
                        <span class="circle-message-time">${timeAgo}</span>
                    </div>
                    <div class="circle-paragraph-preview">${paragraphPreview}</div>
                    <div class="circle-message-footer">
                        <div class="circle-indicators" data-thread-id="${threadId}">
                            ${indicators.length > 0 ? indicators[0] : 'No activity'}
                        </div>
                        <div class="circle-actions">
                            <button class="circle-action-btn" data-action="vote-up" data-thread-id="${threadId}" title="Upvote">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M18 15l-6-6-6 6"/>
                                </svg>
                                <span>${upvotes}</span>
                            </button>
                            <button class="circle-action-btn" data-action="comment" data-thread-id="${threadId}" title="Comments">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                                </svg>
                                <span>${commentCount}</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    initializeThreadClickHandlers(container) {
        const threadItems = container.querySelectorAll('.circle-message-item');
        threadItems.forEach(item => {
            const threadId = item.dataset.threadId;
            const category = item.dataset.category;
            
            // Make entire item clickable (except action buttons)
            item.style.cursor = 'pointer';
            item.addEventListener('click', (e) => {
                // Don't navigate if clicking on action buttons
                if (e.target.closest('.circle-action-btn')) {
                    return;
                }
                
                // Navigate to thread detail page
                if (threadId) {
                    // Store where we came from for back button
                    const referrer = window.location.pathname + window.location.search;
                    sessionStorage.setItem('thread_referrer', referrer);
                    
                    // Use pushState for proper history management
                    let path;
                    if (category) {
                        path = `/circles/${category}/${threadId}`;
                    } else {
                        path = `/thread/${threadId}`;
                    }
                    window.history.pushState({ threadId, category, referrer }, '', path);
                    
                    // Navigate to thread page
                    if (window.Router && window.Router.navigateToThread) {
                        window.Router.navigateToThread(threadId, category);
                    } else {
                        window.location.href = `/thread.html#${threadId}`;
                    }
                }
            });
        });
    }
    
    initializeShiftingPreviews(threads) {
        // Set up shifting indicators for comments/upvotes/views
        threads.forEach((thread, index) => {
            const indicators = [];
            if (thread.comment_count > 0) {
                indicators.push(`${thread.comment_count} comment${thread.comment_count !== 1 ? 's' : ''}`);
            }
            if (thread.upvotes > 0) {
                indicators.push(`${thread.upvotes} upvote${thread.upvotes !== 1 ? 's' : ''}`);
            }
            if (thread.views > 0) {
                indicators.push(`${thread.views} view${thread.views !== 1 ? 's' : ''}`);
            }
            
            if (indicators.length <= 1) return; // No need to rotate if only one indicator
            
            const threadId = thread.id || `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            
            // Use setTimeout to ensure DOM is ready
            setTimeout(() => {
                const indicatorElement = document.querySelector(`.circle-indicators[data-thread-id="${threadId}"]`);
                if (!indicatorElement) return;
                
                // Set initial state
                indicatorElement.style.opacity = '1';
                indicatorElement.style.transform = 'translateY(0)';
                
                let currentIndex = 0;
                
                // Rotate indicators every 5.5 seconds (slower, more advanced)
                const intervalId = setInterval(() => {
                    if (!indicatorElement.isConnected) {
                        clearInterval(intervalId);
                        return;
                    }
                    currentIndex = (currentIndex + 1) % indicators.length;
                    indicatorElement.style.opacity = '0';
                    indicatorElement.style.transform = 'translateY(4px)';
                    setTimeout(() => {
                        if (indicatorElement.isConnected) {
                            indicatorElement.textContent = indicators[currentIndex];
                            indicatorElement.style.opacity = '1';
                            indicatorElement.style.transform = 'translateY(0)';
                        }
                    }, 250);
                }, 5500); // 5.5 seconds - slower, more polished
                
                // Store interval ID for cleanup if needed
                indicatorElement.dataset.intervalId = intervalId;
            }, 150 * index); // Stagger initialization
        });
    }
    
    async loadStudioContent() {
        console.log('Loading Studio content...');
        try {
            let userId = localStorage.getItem('thesidia_user_id');
            let sessionId = localStorage.getItem('thesidia_session_id');
            
            if (!sessionId) {
                try {
                    const sessionResponse = await fetch('/api/user/session', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({})
                    });
                    const sessionData = await sessionResponse.json();
                    userId = sessionData.user_id;
                    sessionId = sessionData.session_id;
                    localStorage.setItem('thesidia_user_id', userId);
                    localStorage.setItem('thesidia_session_id', sessionId);
                } catch (e) {
                    console.warn('Could not create session:', e);
                }
            }
            
            const activeSection = document.querySelector('.carousel-section[data-section="studio"]');
            const filterBtn = activeSection ? activeSection.querySelector('.studio-filters .filter-btn.active') : document.querySelector('.studio-filters .filter-btn.active');
            const filter = filterBtn?.dataset.filter || 'all';
            
            const url = `/api/sections/studio?user_id=${userId || ''}&session_id=${sessionId || ''}&filter=${filter}`;
            console.log('Fetching Studio from:', url);
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Studio data loaded:', data);
            
            // Try multiple ways to find the element
            let programsContainer = document.getElementById('studioPrograms');
            if (!programsContainer && activeSection) {
                programsContainer = activeSection.querySelector('#studioPrograms');
            }
            if (!programsContainer) {
                const allSections = document.querySelectorAll('.carousel-section[data-section="studio"]');
                console.log('Searching in', allSections.length, 'studio sections');
                for (const section of allSections) {
                    programsContainer = section.querySelector('#studioPrograms');
                    if (programsContainer) break;
                }
            }
            
            if (programsContainer) {
                console.log('✅ Found studioPrograms, rendering', data.programs?.length || 0, 'programs');
                if (data.programs && data.programs.length > 0) {
                    programsContainer.innerHTML = data.programs.map(program => this.renderProgram(program)).join('');
                    console.log('✅ Rendered', data.programs.length, 'programs');
                } else {
                    programsContainer.innerHTML = '<div class="programs-loading">No programs found.</div>';
                }
            } else {
                console.error('❌ Could not find studioPrograms element');
                console.error('All sections:', document.querySelectorAll('.carousel-section'));
            }
        } catch (error) {
            console.error('Error loading studio content:', error);
            const activeSection = document.querySelector('.carousel-section[data-section="studio"]');
            const programsContainer = activeSection ? activeSection.querySelector('#studioPrograms') : document.getElementById('studioPrograms');
            if (programsContainer) {
                programsContainer.innerHTML = '<div class="programs-loading">Error loading programs: ' + error.message + '</div>';
            }
        }
    }
    
    renderProgram(program) {
        return `
            <div class="program-card" data-program-id="${program.id}">
                <div class="program-preview">
                    <video class="program-trailer" src="${program.trailer_url}" poster="${program.thumbnail_url}" muted></video>
                    <div class="program-overlay">
                        <button class="play-btn">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                                <polygon points="5 3 19 12 5 21 5 3"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="program-info">
                    <h3 class="program-title">${program.title || ''}</h3>
                    <p class="program-mentor">by ${program.mentor?.name || 'Unknown'}</p>
                    <p class="program-description">${program.description || ''}</p>
                    <div class="program-meta">
                        <span class="program-duration">${program.duration || ''}</span>
                        <span class="program-status ${program.status || 'upcoming'}">${program.status || 'Upcoming'}</span>
                    </div>
                    <button class="program-enroll-btn" data-program-id="${program.id}">Enroll</button>
                </div>
            </div>
        `;
    }
}

// Initialize navigation system when DOM is ready
// Wait a bit to ensure all other scripts are loaded
function initNavigationSystem() {
    const carouselTrack = document.querySelector('.carousel-track');
    if (carouselTrack) {
        console.log('Initializing NavigationSystem...');
        try {
            window.navigationSystem = new NavigationSystem();
            console.log('NavigationSystem initialized successfully');
        } catch (error) {
            console.error('Error initializing NavigationSystem:', error);
        }
    } else {
        // Retry if carousel not ready yet (max 5 seconds)
        const retries = window._navInitRetries || 0;
        if (retries < 50) {
            window._navInitRetries = retries + 1;
            setTimeout(initNavigationSystem, 100);
        } else {
            console.error('NavigationSystem: carousel-track not found after 5 seconds');
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(initNavigationSystem, 100);
    });
} else {
    setTimeout(initNavigationSystem, 100);
}

