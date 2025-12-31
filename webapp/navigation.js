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
        this.followSuggestions = [];
        this.currentSuggestionIndex = 0;
        this.followRotationInterval = null;

        this.init();
    }

    async renderFollowSuggestions() {
        const listEl = document.getElementById('peopleToFollowList');
        if (!listEl) return;

        try {
            const res = await fetch('/mock-profiles.json');
            const data = await res.json();
            const profiles = (data.profiles || []).slice(0, 10); // Get more profiles for rotation

            if (profiles.length === 0) {
                listEl.innerHTML = '<div class="text-secondary" style="font-size:12px;">No suggestions yet.</div>';
                return;
            }

            // Store profiles for rotation
            this.followSuggestions = profiles;
            this.currentSuggestionIndex = 0;

            // Render first suggestion
            this.renderCurrentSuggestion();

            // Start slideshow rotation every 2 seconds
            if (this.followRotationInterval) {
                clearInterval(this.followRotationInterval);
            }
            this.followRotationInterval = setInterval(() => {
                this.currentSuggestionIndex = (this.currentSuggestionIndex + 1) % this.followSuggestions.length;
                this.renderCurrentSuggestion();
            }, 2000);
        } catch (error) {
            console.warn('Could not render follow suggestions', error);
            listEl.innerHTML = '<div class="text-secondary" style="font-size:12px;">Unable to load suggestions.</div>';
        }
    }

    renderCurrentSuggestion() {
        const listEl = document.getElementById('peopleToFollowList');
        if (!listEl || !this.followSuggestions || this.followSuggestions.length === 0) return;

        const profile = this.followSuggestions[this.currentSuggestionIndex];

        listEl.innerHTML = `
            <a class="sidebar-follow-item" href="/profile.html?user_id=${encodeURIComponent(profile.user_id)}">
                <div class="sidebar-follow-avatar">
                    <img src="${profile.avatar_url}" alt="${profile.display_name}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2228%22 height=%2228%22%3E%3Ccircle cx=%2214%22 cy=%2214%22 r=%2214%22 fill=%22%23ffffff%22 fill-opacity=%220.08%22/%3E%3C/svg%3E'">
                </div>
                <div class="sidebar-follow-meta">
                    <div class="sidebar-follow-name">${this.escapeHtml(profile.display_name)}</div>
                    <div class="sidebar-follow-handle">@${this.escapeHtml(profile.username)}</div>
                    ${profile.domains ? `<div class="sidebar-follow-domain">${this.escapeHtml(profile.domains.slice(0, 2).join(' · '))}</div>` : ''}
                </div>
            </a>
        `;
    }

    init() {
        this.setupCarousel();
        this.setupNavigationButtons();
        this.setupSwipeGestures();
        this.setupKeyboardNavigation();
        this.initLoadingScreen();
        this.loadInitialSection();
    }

    /**
     * Initialize loading screen and handle graceful entry
     */
    initLoadingScreen() {
        const loadingScreen = document.getElementById('katanxLoadingScreen');
        const pageContainer = document.querySelector('.stream-page-container');

        if (!loadingScreen) return;

        // Hide loading screen after initial load
        // Wait for DOM to be ready and initial content to start loading
        window.addEventListener('load', () => {
            // Small delay to ensure smooth transition
            setTimeout(() => {
                this.hideLoadingScreen();
            }, 800); // Minimum display time for branding
        });

        // Also hide if page container is ready
        if (pageContainer) {
            pageContainer.classList.add('loaded');
        }
    }

    /**
     * Hide loading screen with fade-out animation
     */
    hideLoadingScreen() {
        const loadingScreen = document.getElementById('katanxLoadingScreen');
        if (loadingScreen && !loadingScreen.classList.contains('hidden')) {
            loadingScreen.classList.add('hidden');
            // Remove from DOM after animation completes
            setTimeout(() => {
                if (loadingScreen.parentNode) {
                    loadingScreen.parentNode.removeChild(loadingScreen);
                }
            }, 600);
        }
    }

    /**
     * Trigger fade-in animations for widgets
     */
    triggerWidgetFadeIns() {
        // Get all widget cards
        const widgets = document.querySelectorAll('.widget-card');

        // Use Intersection Observer for progressive reveal
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe all widgets
        widgets.forEach(widget => {
            observer.observe(widget);
        });

        // Also trigger immediate fade-in for visible widgets (fallback)
        setTimeout(() => {
            widgets.forEach((widget, index) => {
                const rect = widget.getBoundingClientRect();
                const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
                if (isVisible) {
                    setTimeout(() => {
                        widget.classList.add('fade-in');
                    }, index * 100); // Stagger by 100ms
                }
            });
        }, 100);
    }

    /**
     * Fade in content within a widget after it's loaded
     */
    fadeInWidgetContent(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.classList.add('widget-content-loaded');
        }
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
            // Don't handle swipe if touch started in circles area (categories scroll or threads)
            const circlesContainer = e.target.closest('.circles-container');
            const categoriesScroll = e.target.closest('.circles-categories-scroll');
            const circlesThreads = e.target.closest('.circles-threads');

            if (circlesContainer || categoriesScroll || circlesThreads) {
                // Let circles handle its own scrolling/swiping
                return;
            }

            this.touchStartX = e.touches[0].clientX;
        }, { passive: true });

        carousel.addEventListener('touchmove', (e) => {
            // Don't handle swipe if touch is in circles area
            const circlesContainer = e.target.closest('.circles-container');
            const categoriesScroll = e.target.closest('.circles-categories-scroll');
            const circlesThreads = e.target.closest('.circles-threads');

            if (circlesContainer || categoriesScroll || circlesThreads) {
                return;
            }
            // Allow default scrolling behavior
        }, { passive: true });

        carousel.addEventListener('touchend', (e) => {
            // Don't handle swipe if touch ended in circles area
            const circlesContainer = e.target.closest('.circles-container');
            const categoriesScroll = e.target.closest('.circles-categories-scroll');
            const circlesThreads = e.target.closest('.circles-threads');

            if (circlesContainer || categoriesScroll || circlesThreads) {
                return;
            }

            this.touchEndX = e.changedTouches[0].clientX;
            this.handleSwipe();
        }, { passive: true });

        // Mouse events for desktop drag
        let isMouseDown = false;
        let mouseStartX = 0;

        carousel.addEventListener('mousedown', (e) => {
            // Don't handle swipe if click started in circles area
            const circlesContainer = e.target.closest('.circles-container');
            const categoriesScroll = e.target.closest('.circles-categories-scroll');
            const circlesThreads = e.target.closest('.circles-threads');

            if (circlesContainer || categoriesScroll || circlesThreads) {
                return;
            }

            isMouseDown = true;
            mouseStartX = e.clientX;
            carousel.style.cursor = 'grabbing';
        });

        carousel.addEventListener('mousemove', (e) => {
            if (!isMouseDown) return;

            // Don't handle swipe if moving in circles area
            const circlesContainer = e.target.closest('.circles-container');
            const categoriesScroll = e.target.closest('.circles-categories-scroll');
            const circlesThreads = e.target.closest('.circles-threads');

            if (circlesContainer || categoriesScroll || circlesThreads) {
                isMouseDown = false;
                carousel.style.cursor = '';
                return;
            }

            // Prevent text selection during drag
            e.preventDefault();
        });

        carousel.addEventListener('mouseup', (e) => {
            if (isMouseDown) {
                // Don't handle swipe if click ended in circles area
                const circlesContainer = e.target.closest('.circles-container');
                const categoriesScroll = e.target.closest('.circles-categories-scroll');
                const circlesThreads = e.target.closest('.circles-threads');

                if (!circlesContainer && !categoriesScroll && !circlesThreads) {
                    const mouseEndX = e.clientX;
                    this.touchStartX = mouseStartX;
                    this.touchEndX = mouseEndX;
                    this.handleSwipe();
                }

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
                // Swipe right - previous section or open menu if on home
                if (this.currentSection === 'home') {
                    // Open sidebar menu on home when swiping right
                    if (window.thesidiaApp && typeof window.thesidiaApp.toggleLeftSidebar === 'function') {
                        window.thesidiaApp.toggleLeftSidebar();
                    } else {
                        // Fallback if thesidiaApp not available
                        const sidebar = document.getElementById('leftSidebar');
                        const app = document.getElementById('app');
                        if (sidebar && app) {
                            sidebar.classList.add('open');
                            app.classList.add('sidebar-pushed');
                        }
                    }
                } else {
                    this.navigatePrevious();
                }
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
            console.log('Already on section, scrolling to top:', sectionName);
            // If already on this section, scroll to top instead of reloading
            const activeSection = document.querySelector('.carousel-section.active');
            if (activeSection) {
                activeSection.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
                // Fallback: scroll window to top
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
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

            // Welcome hero - only keeping "welcome back" eyebrow text
            // Removed: "hey friend" and "You're on track" messages

            // People to follow rail (mock profiles)
            await this.renderFollowSuggestions();

            // What You're Following widget
            await this.loadFollowingWidget();

            // Activity widget
            await this.loadActivityWidget();

            // Mindful Tips widget
            await this.loadMindfulTipsWidget();

            // Legacy goals widget (removed but keeping code for reference)
            const goalsList = document.getElementById('homeGoalsList');
            const goalsMeta = document.getElementById('homeGoalsMeta');
            if (goalsList || goalsMeta) {
                // Widget removed, skip
            }

            // Legacy code kept for reference:
            /*
            const goals = (data.goals && data.goals.length) ? data.goals : [
                { title: 'Post once today', current: stats.posts || 0, target: 1 },
                { title: 'Engagement momentum', current: engagement, target: Math.max(10, engagement || 10) },
                { title: 'Consistency streak', current: streak, target: streak + 1 }
            ];
            if (goalsMeta) goalsMeta.textContent = `${goals.length} goals`;
            if (goalsList) {
                goalsList.innerHTML = goals.map(goal => {
                    const target = goal.target || 1;
                    const pct = Math.min(100, Math.round((goal.current || 0) / target * 100));
                    return `
                        <div class="goal-row">
                            <div class="goal-text">
                                <div class="goal-title">${goal.title || 'Goal'}</div>
                                <div class="goal-subtext">${goal.current || 0} / ${target}</div>
                            </div>
                            <div class="goal-progress">
                                <div class="goal-progress-fill" style="width:${pct}%"></div>
                            </div>
                        </div>
                    `;
                }).join('');
            }
            */

            // News widget
            const newsTiles = document.getElementById('homeNewsTiles');
            const news = (data.news && data.news.length) ? data.news.slice(0, 6) : [
                { title: 'AI research breakthrough reshapes creative tooling', source: 'Signal Desk', image: 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?auto=format&fit=crop&w=600&q=60' },
                { title: 'Communities lean into micro-stories with higher retention', source: 'Insight Brief', image: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=60' },
                { title: 'New engagement patterns favor short-form synthesis', source: 'Pulse', image: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=600&q=60' }
            ];
            if (newsTiles) {
                // Clear skeleton
                newsTiles.innerHTML = '';
                // Add news tiles with fade-in
                news.forEach((item, index) => {
                    const tile = document.createElement('div');
                    tile.className = 'news-tile';
                    tile.style.opacity = '0';
                    tile.style.transition = `opacity 0.4s ease ${index * 0.1}s`;
                    tile.innerHTML = `
                        ${item.image ? `<img src="${item.image}" alt="${item.title || 'news'}" loading="lazy" />` : ''}
                        <div class="news-overlay">
                            <div class="news-title">${item.title || 'Untitled'}</div>
                            <div class="news-source">${item.source || 'Signal'}</div>
                        </div>
                    `;
                    newsTiles.appendChild(tile);
                    // Trigger fade-in
                    requestAnimationFrame(() => {
                        tile.style.opacity = '1';
                    });
                });
            }

            // Trigger widget fade-ins after content is loaded
            setTimeout(() => {
                this.triggerWidgetFadeIns();
                // Fade in specific widget contents
                this.fadeInWidgetContent('homeNewsTiles');
                this.fadeInWidgetContent('followingGrid');
                this.fadeInWidgetContent('activityList');
                this.fadeInWidgetContent('tipsContainer');
            }, 200);

            // Hide loading screen once home content is ready
            this.hideLoadingScreen();

            // Legacy quick actions removed - widgets replaced
        } catch (error) {
            console.error('Error loading home content:', error);
            // Hide loading screen even on error
            this.hideLoadingScreen();
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
        const authorId = author.user_id || cut.author_id || 'unknown';
        const username = author.username || author.user_id || 'unknown';

        // Mock avatar images - tiny HD, no cartoon/nature
        // Using placeholder service with realistic portraits
        const avatarIndex = (username.charCodeAt(0) || 0) % 10;
        const avatarUrl = author.avatar_url || `https://i.pravatar.cc/40?img=${avatarIndex + 1}`;

        // Mock topic-related GIFs based on domain
        const topicGifs = {
            'movement': 'https://media.giphy.com/media/l0MYC0Lajbo1e6mdy/giphy.gif',
            'visual': 'https://media.giphy.com/media/3o7aCTPPm4OHfRLSH6/giphy.gif',
            'music': 'https://media.giphy.com/media/l0HlBO7eyXzSZkJri/giphy.gif',
            'craft': 'https://media.giphy.com/media/3o7aD2sa0qC3XtSitO/giphy.gif',
            'writing': 'https://media.giphy.com/media/3o7abKh2uIh5V0s0k0/giphy.gif',
            'teaching': 'https://media.giphy.com/media/l0HlNQ03J5JxX6lva/giphy.gif',
            'performance': 'https://media.giphy.com/media/l0HlBO7eyXzSZkJri/giphy.gif'
        };
        const topicGif = domain && topicGifs[domain.toLowerCase()] ? topicGifs[domain.toLowerCase()] : null;

        const videoUrl = cut.video_url || cut.media_url || '';
        const thumbnailUrl = cut.thumbnail_url || cut.poster_url || topicGif || '';

        // Escape HTML to prevent XSS
        const safeUsername = String(username).replace(/[<>&"']/g, '');
        const safeDomain = domain ? String(domain).replace(/[<>&"']/g, '') : '';
        const safeCutId = String(cut.id).replace(/[<>&"']/g, '');
        const safeAuthorId = String(authorId).replace(/[<>&"']/g, '');
        const profileHref = `/profile.html?user_id=${encodeURIComponent(safeAuthorId)}`;

        return `
            <article class="cut-item" data-cut-id="${safeCutId}">
                <div class="cut-video-container">
                    ${videoUrl ? `<video class="cut-video" src="${videoUrl}" ${thumbnailUrl ? `poster="${thumbnailUrl}"` : ''} muted loading="lazy"></video>` : `<div class="cut-video-placeholder"></div>`}
                    
                    <!-- Creator Info Overlay (Top-Left) -->
                    <a class="cut-creator-overlay" href="${profileHref}">
                        <div class="cut-avatar">
                            <img src="${avatarUrl}" alt="${safeUsername}" style="width: 20px; height: 20px; border-radius: 50%; object-fit: cover;" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'20\' height=\'20\'%3E%3Ccircle cx=\'10\' cy=\'10\' r=\'10\' fill=\'%23ffffff\' fill-opacity=\'0.1\'/%3E%3Ccircle cx=\'10\' cy=\'7\' r=\'3\' fill=\'%23ffffff\' fill-opacity=\'0.3\'/%3E%3Cpath d=\'M5 18 Q10 15 15 18\' stroke=\'%23ffffff\' stroke-width=\'1\' fill=\'none\' stroke-opacity=\'0.3\'/%3E%3C/svg%3E'">
                        </div>
                        <div class="cut-creator-name">/${safeUsername}</div>
                    </a>
                    
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

            // Add category filter to URL if selected
            let url = `/api/sections/circles?user_id=${userId || ''}&session_id=${sessionId || ''}&filter=${filter}&limit=20`;
            if (this.selectedCategory && this.selectedCategory !== 'all') {
                url += `&category=${encodeURIComponent(this.selectedCategory)}`;
            }

            console.log('Fetching Circles from:', url);
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Circles data loaded:', data);

            // Filter threads by selected category if needed
            let threadsToDisplay = data.threads || [];
            if (this.selectedCategory && this.selectedCategory !== 'all') {
                threadsToDisplay = threadsToDisplay.filter(thread => {
                    const threadCircle = thread.circle || '';
                    const threadCategoryId = thread.category_id || '';
                    // Match exact circle path or category ID
                    return threadCircle === this.selectedCategory ||
                        threadCircle.startsWith(this.selectedCategory + '/') ||
                        threadCategoryId === this.selectedCategory ||
                        threadCircle.split('/')[0] === this.selectedCategory;
                });
            }

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
                console.log('✅ Found circlesThreads, rendering', threadsToDisplay.length, 'threads');
                if (threadsToDisplay.length > 0) {
                    threadsContainer.innerHTML = threadsToDisplay.map(thread => this.renderThread(thread)).join('');
                    console.log('✅ Rendered', threadsToDisplay.length, 'threads');

                    // Initialize shifting previews
                    this.initializeShiftingPreviews(threadsToDisplay);

                    // Add click handlers for navigation to thread detail
                    this.initializeThreadClickHandlers(threadsContainer);
                } else {
                    threadsContainer.innerHTML = '<div class="threads-loading">No threads found in this category.</div>';
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
                const category = item.dataset.category; // Use full ID (includes category-id/subcategory-id for subcategories)
                if (category) {
                    this.filterByCategory(category);
                }
            });
        });

        // Show main categories first, then subcategories (or group by parent)
        // This could be enhanced to show hierarchical structure
    }

    async filterByCategory(category) {
        // Update active category visual state
        const activeSection = document.querySelector('.carousel-section[data-section="circles"]');
        const categoriesContainer = activeSection ? activeSection.querySelector('#circlesCategoriesScroll') : document.getElementById('circlesCategoriesScroll');

        if (categoriesContainer) {
            const categoryItems = categoriesContainer.querySelectorAll('.circle-category-item');
            categoryItems.forEach(item => {
                item.classList.remove('active');
                // Match by category ID or slug
                const itemCategory = item.dataset.category;
                if (itemCategory === category || itemCategory === category.split('/')[0]) {
                    item.classList.add('active');
                }
            });
        }

        // Store selected category for filtering
        this.selectedCategory = category === 'all' ? null : category;

        // Reload threads with category filter
        await this.loadCirclesContent();
    }

    renderCategory(category) {
        const name = category.name || category.slug || 'Category';
        const slug = category.slug || category.id || '';
        const threadCount = category.thread_count;
        const isAll = slug === 'all';
        const isSubcategory = category.type === 'subcategory';
        const categoryId = category.id || slug; // Use full ID for subcategories (category-id/subcategory-id)

        // Special handling for "All" category
        let avatarUrl, fallbackAvatarUrl, initial, color;
        if (isAll) {
            // Use a special icon/avatar for "All"
            initial = '•';
            color = '#666';
            avatarUrl = `https://api.dicebear.com/7.x/shapes/svg?seed=all&size=64&backgroundColor=666&radius=50`;
            fallbackAvatarUrl = `https://ui-avatars.com/api/?name=All&background=666&color=fff&size=64&bold=true`;
        } else {
            // Use real photos for categories too
            const seed = categoryId || slug || 'default';
            let seedHash = 0;
            const seedString = seed.toString();
            for (let i = 0; i < seedString.length; i++) {
                seedHash = seedString.charCodeAt(i) + ((seedHash << 5) - seedHash);
            }
            const numericSeed = Math.abs(seedHash);
            const seedNum = numericSeed % 1000;

            // Use Unsplash for category photos (portrait/face style)
            avatarUrl = `https://source.unsplash.com/200x200/?portrait,face&sig=${seedNum}`;
            fallbackAvatarUrl = this.getFallbackAvatarUrl(slug, slug);
            initial = this.getCircleInitial(slug);
            color = this.getCircleColor(slug);
        }

        // Add visual indicator for subcategories
        const subcategoryClass = isSubcategory ? 'subcategory' : '';
        const parentIndicator = isSubcategory && category.parent_category_name ?
            `<div class="category-parent-name">${this.escapeHtml(category.parent_category_name)}</div>` : '';

        return `
            <div class="circle-category-item ${isAll ? 'active' : ''} ${subcategoryClass}" data-category="${categoryId}" data-slug="${slug}">
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
                ${parentIndicator}
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

        // Use Unsplash Source API for real photos
        // Generate consistent seed from topic/author
        const seed = authorId || topic || 'default';
        let seedHash = 0;
        const seedString = seed.toString();
        for (let i = 0; i < seedString.length; i++) {
            seedHash = seedString.charCodeAt(i) + ((seedHash << 5) - seedHash);
        }
        const numericSeed = Math.abs(seedHash);

        // Use Unsplash Source for real profile photos
        // Using portrait orientation and face focus
        const width = 200;
        const height = 200;
        const seedNum = numericSeed % 1000; // Use for consistent selection

        return `https://source.unsplash.com/${width}x${height}/?portrait,face&sig=${seedNum}`;
    }

    getFallbackAvatarUrl(topic, authorId = null) {
        // Use RandomUser.me API for realistic profile photos as fallback
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
        // Get category display name - prefer structured names, fallback to circle
        let categoryDisplay = '';
        if (thread.subcategory_name && thread.category_name) {
            categoryDisplay = `${thread.category_name} • ${thread.subcategory_name}`;
        } else if (thread.category_name) {
            categoryDisplay = thread.category_name;
        } else if (thread.circle) {
            // Parse circle path (category-id/subcategory-id) or use as-is
            const circleParts = thread.circle.split('/');
            if (circleParts.length === 2) {
                // Format: "Category Name • Subcategory Name"
                categoryDisplay = circleParts.map(part =>
                    part.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
                ).join(' • ');
            } else {
                categoryDisplay = thread.circle.split('-').map(word =>
                    word.charAt(0).toUpperCase() + word.slice(1)
                ).join(' ');
            }
        } else {
            categoryDisplay = thread.title || 'Topic';
        }

        const topic = categoryDisplay;
        const authorId = thread.author_id || thread.author?.user_id || null;
        const authorAvatarUrl = thread.author?.avatar_url || null;
        const avatarUrl = this.getAvatarUrl(topic, authorId, authorAvatarUrl);
        const fallbackAvatarUrl = this.getFallbackAvatarUrl(topic, authorId);
        const timeAgo = this.formatMessageTime(thread.created_at);

        // Get thread title for display
        const threadTitle = thread.title || 'Untitled Thread';

        // Get first part of paragraph (static preview) - shorter for compact mobile view
        const bodyText = (thread.body || '').trim();
        const paragraphPreview = bodyText ?
            this.escapeHtml(bodyText.length > 80 ? bodyText.substring(0, 77) + '...' : bodyText) :
            'No content available';

        // Create shifting indicators for comments/resonate/respect
        const indicators = [];
        if (thread.comment_count > 0) {
            indicators.push(`${thread.comment_count} comment${thread.comment_count !== 1 ? 's' : ''}`);
        }
        const resonateCount = thread.resonate_count || thread.upvotes || 0;
        const respectCount = thread.respect_count || 0;
        if (resonateCount > 0) {
            indicators.push(`${resonateCount} resonate${resonateCount !== 1 ? 's' : ''}`);
        }
        if (respectCount > 0) {
            indicators.push(`${respectCount} respect${respectCount !== 1 ? 's' : ''}`);
        }
        if (thread.views > 0) {
            indicators.push(`${thread.views} view${thread.views !== 1 ? 's' : ''}`);
        }

        const threadId = thread.id || `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const commentCount = thread.comment_count || 0;
        const circlePath = thread.circle || '';

        // Build tag badges if tag_metadata exists
        let tagBadges = '';
        if (thread.tag_metadata) {
            const tags = [];
            if (thread.tag_metadata.level) {
                tags.push(`<span class="thread-tag level-${thread.tag_metadata.level}">${thread.tag_metadata.level}</span>`);
            }
            if (thread.tag_metadata.format) {
                tags.push(`<span class="thread-tag format-${thread.tag_metadata.format}">${thread.tag_metadata.format}</span>`);
            }
            if (thread.tag_metadata.sourcing) {
                tags.push(`<span class="thread-tag sourcing-${thread.tag_metadata.sourcing}">${thread.tag_metadata.sourcing}</span>`);
            }
            if (tags.length > 0) {
                tagBadges = `<div class="thread-tags">${tags.join('')}</div>`;
            }
        }

        return `
            <div class="circle-message-item" data-thread-id="${threadId}" data-category="${this.escapeHtml(circlePath)}">
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
                        <div class="circle-header-top">
                            <span class="circle-topic-name">${this.escapeHtml(categoryDisplay)}</span>
                            <span class="circle-message-time">${timeAgo}</span>
                        </div>
                        <div class="circle-thread-title">${this.escapeHtml(threadTitle)}</div>
                        ${tagBadges}
                    </div>
                    <div class="circle-paragraph-preview">${paragraphPreview}</div>
                    <div class="circle-message-footer">
                        <div class="circle-indicators" data-thread-id="${threadId}">
                            ${indicators.length > 0 ? indicators[0] : 'No activity'}
                        </div>
                        <div class="circle-actions">
                            <button class="circle-action-btn" data-action="resonate" data-thread-id="${threadId}" title="Resonate">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M18 15l-6-6-6 6"/>
                                </svg>
                                <span>${resonateCount || 0}</span>
                            </button>
                            <button class="circle-action-btn" data-action="respect" data-thread-id="${threadId}" title="Respect">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                                </svg>
                                <span>${respectCount || 0}</span>
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
        // Set up shifting indicators for comments/resonate/respect/views
        threads.forEach((thread, index) => {
            const indicators = [];
            if (thread.comment_count > 0) {
                indicators.push(`${thread.comment_count} comment${thread.comment_count !== 1 ? 's' : ''}`);
            }
            const resonateCount = thread.resonate_count || thread.upvotes || 0;
            const respectCount = thread.respect_count || 0;
            if (resonateCount > 0) {
                indicators.push(`${resonateCount} resonate${resonateCount !== 1 ? 's' : ''}`);
            }
            if (respectCount > 0) {
                indicators.push(`${respectCount} respect${respectCount !== 1 ? 's' : ''}`);
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

    async loadFollowingWidget() {
        const carouselContainer = document.getElementById('followingCarouselContainer');
        const carouselTrack = document.getElementById('followingCarouselTrack');

        if (!carouselContainer || !carouselTrack) {
            console.warn('Following carousel elements not found');
            return;
        }

        try {
            console.log('Loading following widget with post previews...');

            // Generate mock post previews showing different content types
            const mockPosts = [
                {
                    authorName: 'Alex Chen',
                    authorHandle: 'alexchen',
                    authorInitials: 'AC',
                    timeAgo: '2h',
                    content: 'Just finished a deep dive into quantum consciousness. The implications for AI development are fascinating—especially how measurement affects reality.',
                    tags: ['quantum', 'consciousness', 'ai'],
                    hasMedia: true,
                    mediaUrl: 'https://images.unsplash.com/photo-1635070041078-e3dcc6b3b8e0?w=400&h=300&fit=crop',
                    stats: { likes: 42, comments: 8, validates: 12 }
                },
                {
                    authorName: 'Maya Patel',
                    authorHandle: 'mayapatel',
                    authorInitials: 'MP',
                    timeAgo: '5h',
                    content: 'New insights on pattern recognition across different domains. The same structures appear in nature, code, and consciousness.',
                    tags: ['patterns', 'systems'],
                    hasMedia: false,
                    stats: { likes: 28, comments: 5, validates: 7 }
                },
                {
                    authorName: 'Jordan Kim',
                    authorHandle: 'jordankim',
                    authorInitials: 'JK',
                    timeAgo: '1d',
                    content: 'Exploring the intersection of movement arts and cognitive science. How does physical practice reshape neural pathways?',
                    tags: ['movement', 'neuroscience', 'practice'],
                    hasMedia: true,
                    mediaUrl: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400&h=300&fit=crop',
                    stats: { likes: 67, comments: 14, validates: 19 }
                },
                {
                    authorName: 'Sam Rivera',
                    authorHandle: 'samrivera',
                    authorInitials: 'SR',
                    timeAgo: '3h',
                    content: 'The relationship between creativity and constraint is more complex than we think. Limitations often unlock new possibilities.',
                    tags: ['creativity', 'philosophy'],
                    hasMedia: false,
                    stats: { likes: 35, comments: 9, validates: 11 }
                }
            ];

            // Clear existing content
            carouselTrack.innerHTML = '';

            // Create carousel items with post previews
            mockPosts.forEach((post, index) => {
                const itemEl = document.createElement('div');
                itemEl.className = 'following-item';

                const tagsHtml = post.tags && post.tags.length > 0 ? `
                    <div class="following-post-tags">
                        ${post.tags.map(tag => `<span class="following-post-tag">//${this.escapeHtml(tag)}</span>`).join('')}
                    </div>
                ` : '';

                const mediaHtml = post.hasMedia && post.mediaUrl ? `
                    <img src="${post.mediaUrl}" alt="Post preview" class="following-post-media" loading="lazy" onerror="this.style.display='none'">
                ` : '';

                itemEl.innerHTML = `
                    <div class="following-post-preview">
                        <div class="following-post-header">
                            <div class="following-post-avatar">${post.authorInitials}</div>
                            <div class="following-post-author">
                                <div class="following-post-author-name">${this.escapeHtml(post.authorName)}</div>
                                <div class="following-post-author-handle">//${this.escapeHtml(post.authorHandle)}</div>
                            </div>
                            <div class="following-post-time">${post.timeAgo}</div>
                        </div>
                        <div class="following-post-content">${this.escapeHtml(post.content)}</div>
                        ${tagsHtml}
                        ${mediaHtml}
                        <div class="following-post-stats">
                            <div class="following-post-stat">
                                <span>${post.stats.likes}</span>
                                <span>likes</span>
                            </div>
                            <div class="following-post-stat">
                                <span>${post.stats.comments}</span>
                                <span>comments</span>
                            </div>
                            <div class="following-post-stat">
                                <span>${post.stats.validates}</span>
                                <span>validates</span>
                            </div>
                        </div>
                    </div>
                `;
                carouselTrack.appendChild(itemEl);
            });

            // Initialize carousel state
            this.followingCurrentIndex = 0;
            this.followingTotalItems = mockPosts.length;
            this.followingAutoSlideInterval = null;

            // Setup swipe gestures
            this.setupFollowingSwipe(carouselContainer);

            // Start auto-slide
            this.startFollowingAutoSlide();

            // Add click handlers to navigate to stream
            carouselTrack.querySelectorAll('.following-post-preview').forEach(preview => {
                preview.addEventListener('click', () => {
                    // Navigate to stream section
                    this.navigateToSection('stream');
                });
            });

            console.log('Following widget loaded with', mockPosts.length, 'post previews');
        } catch (error) {
            console.error('Error loading following widget:', error);
            if (carouselTrack) {
                carouselTrack.innerHTML = '<div style="padding: 12px; color: var(--text-tertiary); font-size: 12px;">Unable to load</div>';
            }
        }
    }

    setupFollowingSwipe(container) {
        let touchStartX = 0;
        let touchEndX = 0;
        let isDragging = false;

        container.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            isDragging = true;
            this.pauseFollowingAutoSlide();
        }, { passive: true });

        container.addEventListener('touchmove', (e) => {
            if (isDragging) {
                touchEndX = e.touches[0].clientX;
            }
        }, { passive: true });

        container.addEventListener('touchend', () => {
            if (!isDragging) return;

            const swipeDistance = touchStartX - touchEndX;
            const swipeThreshold = 50;

            if (Math.abs(swipeDistance) > swipeThreshold) {
                if (swipeDistance > 0) {
                    // Swipe left - next slide
                    this.nextFollowingSlide();
                } else {
                    // Swipe right - previous slide
                    this.prevFollowingSlide();
                }
            }

            isDragging = false;
            this.startFollowingAutoSlide();
        }, { passive: true });

        // Mouse drag support
        let mouseStartX = 0;
        let mouseIsDown = false;

        container.addEventListener('mousedown', (e) => {
            mouseStartX = e.clientX;
            mouseIsDown = true;
            this.pauseFollowingAutoSlide();
            container.style.cursor = 'grabbing';
        });

        container.addEventListener('mousemove', (e) => {
            if (!mouseIsDown) return;
            e.preventDefault();
        });

        container.addEventListener('mouseup', (e) => {
            if (!mouseIsDown) return;

            const dragDistance = mouseStartX - e.clientX;
            const dragThreshold = 50;

            if (Math.abs(dragDistance) > dragThreshold) {
                if (dragDistance > 0) {
                    this.nextFollowingSlide();
                } else {
                    this.prevFollowingSlide();
                }
            }

            mouseIsDown = false;
            container.style.cursor = 'grab';
            this.startFollowingAutoSlide();
        });

        container.addEventListener('mouseleave', () => {
            if (mouseIsDown) {
                mouseIsDown = false;
                container.style.cursor = 'grab';
                this.startFollowingAutoSlide();
            }
        });
    }

    goToFollowingSlide(index) {
        if (index < 0 || index >= this.followingTotalItems) return;

        this.followingCurrentIndex = index;
        const carouselTrack = document.getElementById('followingCarouselTrack');

        if (carouselTrack) {
            carouselTrack.style.transform = `translateX(-${index * 100}%)`;
        }

        // Reset auto-slide
        this.pauseFollowingAutoSlide();
        this.startFollowingAutoSlide();
    }

    nextFollowingSlide() {
        const nextIndex = (this.followingCurrentIndex + 1) % this.followingTotalItems;
        this.goToFollowingSlide(nextIndex);
    }

    prevFollowingSlide() {
        const prevIndex = (this.followingCurrentIndex - 1 + this.followingTotalItems) % this.followingTotalItems;
        this.goToFollowingSlide(prevIndex);
    }

    startFollowingAutoSlide() {
        this.pauseFollowingAutoSlide();
        this.followingAutoSlideInterval = setInterval(() => {
            this.nextFollowingSlide();
        }, 3000); // Auto-advance every 3 seconds
    }

    pauseFollowingAutoSlide() {
        if (this.followingAutoSlideInterval) {
            clearInterval(this.followingAutoSlideInterval);
            this.followingAutoSlideInterval = null;
        }
    }

    async loadActivityWidget() {
        const activityList = document.getElementById('activityList');
        if (!activityList) {
            console.warn('activityList not found');
            return;
        }

        try {
            console.log('Loading activity widget...');
            // Mock activity data - resonates, refines, reposts
            const activities = [
                { type: 'resonate', content: 'Resonated with "Exploring Internal Arts" in Streams', time: '2h ago' },
                { type: 'refine', content: 'Refined answer in Forums: "Martial Arts & Combative"', time: '5h ago' },
                { type: 'repost', content: 'Reposted from @user_3 in Streams', time: '1d ago' },
                { type: 'resonate', content: 'Resonated with "Visual Design Principles"', time: '2d ago' }
            ];

            activityList.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <div class="activity-content">
                        <span class="activity-type">${this.escapeHtml(activity.type)}:</span>
                        <span class="activity-text">${this.escapeHtml(activity.content)}</span>
                        <span class="activity-time">${this.escapeHtml(activity.time)}</span>
                    </div>
                </div>
            `).join('');

            console.log('Activity widget loaded:', activities.length, 'activities');
        } catch (error) {
            console.error('Error loading activity widget:', error);
            if (activityList) {
                activityList.innerHTML = '<div style="padding: 12px; color: var(--text-tertiary); font-size: 12px;">Unable to load activity</div>';
            }
        }
    }

    async loadMindfulTipsWidget() {
        const dailyTipsList = document.getElementById('dailyTipsList');
        const weeklyTipsList = document.getElementById('weeklyTipsList');

        if (!dailyTipsList && !weeklyTipsList) {
            console.warn('Tip lists not found');
            return;
        }

        try {
            console.log('Loading mindful tips widget...');
            // Daily tips - actionable items for today
            const dailyTips = [
                {
                    title: 'Post a thought',
                    description: 'Share something you learned today',
                    action: 'Post',
                    actionType: 'post'
                },
                {
                    title: 'Meditate for 10 minutes',
                    description: 'Take a mindful break',
                    action: 'Start',
                    actionType: 'meditate'
                },
                {
                    title: 'Learn a new system',
                    description: 'Explore a category you haven\'t visited',
                    action: 'Explore',
                    actionType: 'learn'
                }
            ];

            // Weekly tips - engagement goals
            const weeklyTips = [
                {
                    title: 'Engage with 5 posts this week',
                    description: 'Comment or resonate with community content',
                    action: 'View',
                    actionType: 'engage',
                    badge: 'weekly'
                },
                {
                    title: 'Write a detailed post',
                    description: 'Share your insights on a topic you care about',
                    action: 'Write',
                    actionType: 'write',
                    badge: 'weekly'
                },
                {
                    title: 'Connect with 3 new people',
                    description: 'Follow and engage with community members',
                    action: 'Connect',
                    actionType: 'connect',
                    badge: 'weekly'
                }
            ];

            if (dailyTipsList) {
                dailyTipsList.innerHTML = dailyTips.map(tip => `
                    <div class="tip-item" data-action-type="${tip.actionType}">
                        <div class="tip-content">
                            <div class="tip-title">${this.escapeHtml(tip.title)}</div>
                            <div class="tip-description">${this.escapeHtml(tip.description)}</div>
                        </div>
                        <button class="tip-action" data-action="${tip.actionType}">${this.escapeHtml(tip.action)}</button>
                    </div>
                `).join('');
                console.log('Daily tips loaded:', dailyTips.length);
            }

            if (weeklyTipsList) {
                weeklyTipsList.innerHTML = weeklyTips.map(tip => `
                    <div class="tip-item" data-action-type="${tip.actionType}">
                        <div class="tip-content">
                            <div class="tip-title">
                                ${this.escapeHtml(tip.title)}
                                ${tip.badge ? `<span class="tip-badge">${tip.badge}</span>` : ''}
                            </div>
                            <div class="tip-description">${this.escapeHtml(tip.description)}</div>
                        </div>
                        <button class="tip-action" data-action="${tip.actionType}">${this.escapeHtml(tip.action)}</button>
                    </div>
                `).join('');
                console.log('Weekly tips loaded:', weeklyTips.length);
            }

            // Add click handlers for tip actions
            setTimeout(() => {
                document.querySelectorAll('.tip-action').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const actionType = btn.dataset.action;
                        this.handleTipAction(actionType);
                    });
                });
            }, 100);
        } catch (error) {
            console.error('Error loading mindful tips:', error);
            if (dailyTipsList) dailyTipsList.innerHTML = '<div style="padding: 12px; color: var(--text-tertiary); font-size: 12px;">Unable to load tips</div>';
            if (weeklyTipsList) weeklyTipsList.innerHTML = '<div style="padding: 12px; color: var(--text-tertiary); font-size: 12px;">Unable to load goals</div>';
        }
    }

    handleTipAction(actionType) {
        switch (actionType) {
            case 'post':
                // Open post creation modal
                if (window.streamPage && typeof window.streamPage.openPostModal === 'function') {
                    window.streamPage.openPostModal();
                } else {
                    // Navigate to stream page to post
                    this.navigateToSection('stream');
                }
                break;
            case 'meditate':
                // Could navigate to a meditation/wellness section or open a timer
                console.log('Start meditation');
                // Future: Open meditation timer or navigate to wellness section
                break;
            case 'learn':
                // Navigate to circles/forums to explore
                this.navigateToSection('circles');
                break;
            case 'engage':
                // Navigate to stream to engage with posts
                this.navigateToSection('stream');
                break;
            case 'write':
                // Open post creation with focus on longer form
                if (window.streamPage && typeof window.streamPage.openPostModal === 'function') {
                    window.streamPage.openPostModal();
                } else {
                    this.navigateToSection('stream');
                }
                break;
            case 'connect':
                // Navigate to profiles or stream to find people
                this.navigateToSection('stream');
                break;
            default:
                console.log('Unknown action:', actionType);
        }
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

