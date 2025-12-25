/**
 * Katanx Event Collector
 * Client-side engagement tracking for Algorithmic Growth Engine
 * 
 * Captures: views, clicks, dwell time, scroll depth, saves, shares
 * Sends events to /api/events endpoint
 */

class KatanxEventCollector {
    constructor(options = {}) {
        this.apiEndpoint = options.apiEndpoint || '/api/events';
        this.userId = options.userId || null;
        this.sessionId = options.sessionId || this.getOrCreateSessionId();
        this.batchSize = options.batchSize || 10;
        this.flushInterval = options.flushInterval || 5000; // 5 seconds

        // Event queue
        this.eventQueue = [];
        this.sequencePosition = 0;
        this.sessionStartAt = new Date().toISOString();

        // Dwell time tracking
        this.dwellTimers = new Map();
        this.scrollDepths = new Map();

        // Device detection
        this.deviceType = this.detectDeviceType();

        // Bind methods
        this.trackView = this.trackView.bind(this);
        this.trackClick = this.trackClick.bind(this);
        this.trackDwell = this.trackDwell.bind(this);
        this.flush = this.flush.bind(this);

        // Auto-flush
        this.flushTimer = setInterval(this.flush, this.flushInterval);

        // Flush on page unload
        window.addEventListener('beforeunload', this.flush);

        console.log('🎯 Katanx Event Collector initialized');
    }

    // =========================================================================
    // Session Management
    // =========================================================================

    getOrCreateSessionId() {
        let sessionId = sessionStorage.getItem('katanx_session_id');
        if (!sessionId) {
            sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('katanx_session_id', sessionId);
        }
        return sessionId;
    }

    setUserId(userId) {
        this.userId = userId;
    }

    detectDeviceType() {
        const ua = navigator.userAgent;
        if (/tablet|ipad|playbook|silk/i.test(ua)) return 'tablet';
        if (/mobile|android|iphone/i.test(ua)) return 'mobile';
        return 'desktop';
    }

    // =========================================================================
    // Event Tracking Methods
    // =========================================================================

    /**
     * Track content view
     * @param {string} contentId - Unique content identifier
     * @param {string} contentType - 'conversation', 'post', 'bot', 'asset'
     * @param {string} sourcePage - Where the view occurred
     */
    trackView(contentId, contentType = 'unknown', sourcePage = 'unknown') {
        this.queueEvent({
            content_id: contentId,
            content_type: contentType,
            action_type: 'view',
            action_value: null,
            source_page: sourcePage
        });

        // Start dwell timer
        this.startDwellTimer(contentId, contentType, sourcePage);
    }

    /**
     * Track click on content
     */
    trackClick(contentId, contentType = 'unknown', sourcePage = 'unknown') {
        this.queueEvent({
            content_id: contentId,
            content_type: contentType,
            action_type: 'click',
            action_value: null,
            source_page: sourcePage
        });
    }

    /**
     * Track like/unlike
     */
    trackLike(contentId, contentType = 'unknown', isUnlike = false) {
        this.queueEvent({
            content_id: contentId,
            content_type: contentType,
            action_type: isUnlike ? 'unlike' : 'like',
            action_value: null,
            source_page: this.getCurrentPage()
        });
    }

    /**
     * Track share
     */
    trackShare(contentId, contentType = 'unknown', shareTarget = null) {
        this.queueEvent({
            content_id: contentId,
            content_type: contentType,
            action_type: 'share',
            action_value: null,
            source_page: this.getCurrentPage()
        });
    }

    /**
     * Track save/bookmark
     */
    trackSave(contentId, contentType = 'unknown') {
        this.queueEvent({
            content_id: contentId,
            content_type: contentType,
            action_type: 'save',
            action_value: null,
            source_page: this.getCurrentPage()
        });
    }

    /**
     * Track comment/reply
     */
    trackComment(contentId, contentType = 'unknown', isReply = false) {
        this.queueEvent({
            content_id: contentId,
            content_type: contentType,
            action_type: isReply ? 'reply' : 'comment',
            action_value: null,
            source_page: this.getCurrentPage()
        });
    }

    /**
     * Track scroll depth
     * @param {string} contentId - Content being scrolled
     * @param {number} depth - Scroll depth percentage (0-100)
     */
    trackScroll(contentId, contentType = 'unknown', depth) {
        // Only track at thresholds: 25%, 50%, 75%, 100%
        const thresholds = [25, 50, 75, 100];
        const currentMax = this.scrollDepths.get(contentId) || 0;

        for (const threshold of thresholds) {
            if (depth >= threshold && currentMax < threshold) {
                this.queueEvent({
                    content_id: contentId,
                    content_type: contentType,
                    action_type: 'scroll',
                    action_value: threshold,
                    source_page: this.getCurrentPage()
                });
                this.scrollDepths.set(contentId, threshold);
            }
        }
    }

    /**
     * Track video/media events
     */
    trackMediaEvent(contentId, contentType, event, value = null) {
        // event: 'play', 'pause', 'complete', 'skip'
        this.queueEvent({
            content_id: contentId,
            content_type: contentType,
            action_type: event,
            action_value: value, // e.g., percentage watched
            source_page: this.getCurrentPage()
        });
    }

    /**
     * Track negative signals
     */
    trackHide(contentId, contentType = 'unknown') {
        this.queueEvent({
            content_id: contentId,
            content_type: contentType,
            action_type: 'hide',
            action_value: null,
            source_page: this.getCurrentPage()
        });
    }

    // =========================================================================
    // Dwell Time Tracking
    // =========================================================================

    startDwellTimer(contentId, contentType, sourcePage) {
        if (this.dwellTimers.has(contentId)) return;

        this.dwellTimers.set(contentId, {
            startTime: Date.now(),
            contentType,
            sourcePage
        });
    }

    stopDwellTimer(contentId) {
        const timer = this.dwellTimers.get(contentId);
        if (!timer) return;

        const dwellTime = (Date.now() - timer.startTime) / 1000; // seconds

        // Only track if dwell time > 1 second
        if (dwellTime > 1) {
            this.queueEvent({
                content_id: contentId,
                content_type: timer.contentType,
                action_type: 'dwell',
                action_value: Math.round(dwellTime * 10) / 10, // 1 decimal place
                source_page: timer.sourcePage
            });
        }

        this.dwellTimers.delete(contentId);
    }

    /**
     * Call when user navigates away from content
     */
    trackDwell(contentId) {
        this.stopDwellTimer(contentId);
    }

    // =========================================================================
    // Event Queue Management
    // =========================================================================

    queueEvent(eventData) {
        this.sequencePosition++;

        const event = {
            ...eventData,
            user_id: this.userId,
            session_id: this.sessionId,
            sequence_position: this.sequencePosition,
            session_start_at: this.sessionStartAt,
            device_type: this.deviceType,
            timestamp: new Date().toISOString()
        };

        this.eventQueue.push(event);

        // Auto-flush if batch size reached
        if (this.eventQueue.length >= this.batchSize) {
            this.flush();
        }
    }

    async flush() {
        if (this.eventQueue.length === 0) return;

        // Stop all active dwell timers before flush
        for (const contentId of this.dwellTimers.keys()) {
            this.stopDwellTimer(contentId);
        }

        const eventsToSend = [...this.eventQueue];
        this.eventQueue = [];

        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ events: eventsToSend }),
                keepalive: true // Important for beforeunload
            });

            if (!response.ok) {
                console.error('Failed to send events:', response.status);
                // Re-queue failed events
                this.eventQueue = [...eventsToSend, ...this.eventQueue];
            }
        } catch (error) {
            console.error('Error sending events:', error);
            // Re-queue on error
            this.eventQueue = [...eventsToSend, ...this.eventQueue];
        }
    }

    getCurrentPage() {
        return window.location.pathname;
    }

    // =========================================================================
    // Cleanup
    // =========================================================================

    destroy() {
        this.flush();
        clearInterval(this.flushTimer);
        window.removeEventListener('beforeunload', this.flush);
    }
}

// =========================================================================
// Auto-tracking utilities
// =========================================================================

/**
 * Setup automatic view tracking with Intersection Observer
 */
function setupAutoViewTracking(collector, options = {}) {
    const {
        selector = '[data-track-view]',
        threshold = 0.5 // 50% visible
    } = options;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const contentId = element.dataset.contentId;
                const contentType = element.dataset.contentType || 'unknown';

                if (contentId && !element.dataset.viewed) {
                    collector.trackView(contentId, contentType, collector.getCurrentPage());
                    element.dataset.viewed = 'true';
                }
            } else {
                // When leaving view, track dwell time
                const contentId = entry.target.dataset.contentId;
                if (contentId) {
                    collector.trackDwell(contentId);
                }
            }
        });
    }, { threshold });

    // Observe all trackable elements
    document.querySelectorAll(selector).forEach(el => observer.observe(el));

    // Return observer for cleanup
    return observer;
}

/**
 * Setup automatic scroll tracking
 */
function setupAutoScrollTracking(collector, contentId, contentType = 'page') {
    let ticking = false;

    const handleScroll = () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const scrollTop = window.scrollY;
                const docHeight = document.documentElement.scrollHeight - window.innerHeight;
                const scrollPercent = Math.round((scrollTop / docHeight) * 100);

                collector.trackScroll(contentId, contentType, scrollPercent);
                ticking = false;
            });
            ticking = true;
        }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => window.removeEventListener('scroll', handleScroll);
}

// =========================================================================
// Export for use
// =========================================================================

// Make globally available
window.KatanxEventCollector = KatanxEventCollector;
window.setupAutoViewTracking = setupAutoViewTracking;
window.setupAutoScrollTracking = setupAutoScrollTracking;

// Create default instance
window.katanxEvents = new KatanxEventCollector();

console.log('🎯 Katanx Event Collector loaded. Access via window.katanxEvents');
