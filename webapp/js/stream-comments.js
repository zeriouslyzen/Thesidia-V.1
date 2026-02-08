/**
 * Katanx Stream Comments
 * 
 * Real-time comment system with threading, reactions, and moderation integration.
 * 
 * @author Katanx Team
 */

const KatanxComments = (function () {
    'use strict';

    // ═══════════════════════════════════════════════════════════════
    // CONFIGURATION
    // ═══════════════════════════════════════════════════════════════

    const Config = {
        MAX_COMMENT_LENGTH: 280,
        MAX_REPLY_DEPTH: 2,
        POLL_INTERVAL_MS: 3000,
        ANIMATION_DURATION_MS: 300,
        LOAD_BATCH_SIZE: 20
    };

    // ═══════════════════════════════════════════════════════════════
    // STATE
    // ═══════════════════════════════════════════════════════════════

    let state = {
        streamId: null,
        comments: [],
        currentUser: null,
        container: null,
        inputField: null,
        pollInterval: null,
        isLoading: false
    };

    // ═══════════════════════════════════════════════════════════════
    // INITIALIZATION
    // ═══════════════════════════════════════════════════════════════

    /**
     * Initialize the comments system
     * @param {Object} options - { streamId, container, inputField, currentUser }
     */
    function init(options) {
        state.streamId = options.streamId;
        state.container = typeof options.container === 'string'
            ? document.querySelector(options.container)
            : options.container;
        state.inputField = typeof options.inputField === 'string'
            ? document.querySelector(options.inputField)
            : options.inputField;
        state.currentUser = options.currentUser || getStoredUser();

        if (!state.container) {
            console.error('[KatanxComments] Container not found');
            return;
        }

        setupEventListeners();
        loadComments();
        startPolling();

        console.log('[KatanxComments] Initialized for stream:', state.streamId);
    }

    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // Submit on enter
        if (state.inputField) {
            state.inputField.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    submitComment();
                }
            });

            // Character counter
            state.inputField.addEventListener('input', updateCharCounter);
        }

        // Delegated event listeners for comment actions
        state.container.addEventListener('click', handleCommentAction);
    }

    // ═══════════════════════════════════════════════════════════════
    // COMMENT LOADING & RENDERING
    // ═══════════════════════════════════════════════════════════════

    /**
     * Load comments from storage/API
     */
    async function loadComments() {
        if (state.isLoading) return;
        state.isLoading = true;

        try {
            // For now, load from localStorage (will be replaced with API)
            const stored = localStorage.getItem(`kx_comments_${state.streamId}`);
            state.comments = stored ? JSON.parse(stored) : [];
            renderComments();
        } catch (error) {
            console.error('[KatanxComments] Failed to load comments:', error);
        } finally {
            state.isLoading = false;
        }
    }

    /**
     * Render all comments
     */
    function renderComments() {
        const fragment = document.createDocumentFragment();

        // Sort by timestamp (newest first for streams)
        const sorted = [...state.comments].sort((a, b) =>
            new Date(b.created_at) - new Date(a.created_at)
        );

        sorted.forEach(comment => {
            if (!comment.parent_id) {
                fragment.appendChild(createCommentElement(comment));
            }
        });

        state.container.innerHTML = '';
        state.container.appendChild(fragment);
    }

    /**
     * Create a comment DOM element
     */
    function createCommentElement(comment, depth = 0) {
        const el = document.createElement('div');
        el.className = 'kx-comment';
        el.dataset.commentId = comment.id;
        if (depth > 0) el.classList.add('kx-comment--reply');
        if (comment.is_cut) el.classList.add('kx-comment--cut');

        const timeAgo = formatTimeAgo(comment.created_at);
        const avatarUrl = comment.user.avatar_url || 'data:image/svg+xml,...';

        el.innerHTML = `
            <div class="kx-comment__avatar">
                <img src="${escapeHtml(avatarUrl)}" alt="${escapeHtml(comment.user.display_name)}" 
                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 40 40%22%3E%3Ccircle cx=%2220%22 cy=%2220%22 r=%2220%22 fill=%22%23333%22/%3E%3C/svg%3E'">
            </div>
            <div class="kx-comment__body">
                <div class="kx-comment__header">
                    <span class="kx-comment__name">${escapeHtml(comment.user.display_name)}</span>
                    <span class="kx-comment__handle">@${escapeHtml(comment.user.username)}</span>
                    <span class="kx-comment__time">${timeAgo}</span>
                    ${comment.is_cut ? '<span class="kx-comment__cut-badge">🗡️ CUT</span>' : ''}
                </div>
                <div class="kx-comment__content">${formatContent(comment.content)}</div>
                <div class="kx-comment__actions">
                    <button class="kx-comment__action" data-action="reply" title="Reply">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                        </svg>
                        <span>${comment.replies?.length || 0}</span>
                    </button>
                    <button class="kx-comment__action" data-action="like" title="Like">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                        </svg>
                        <span>${comment.likes || 0}</span>
                    </button>
                    <button class="kx-comment__action" data-action="challenge" title="Issue Challenge">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <line x1="12" y1="18" x2="12" y2="12"/>
                            <line x1="9" y1="15" x2="15" y2="15"/>
                        </svg>
                    </button>
                    <button class="kx-comment__action kx-comment__action--danger" data-action="report" title="Report">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
                            <line x1="4" y1="22" x2="4" y2="15"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        // Add replies if within depth limit
        if (comment.replies && depth < Config.MAX_REPLY_DEPTH) {
            const repliesContainer = document.createElement('div');
            repliesContainer.className = 'kx-comment__replies';
            comment.replies.forEach(reply => {
                repliesContainer.appendChild(createCommentElement(reply, depth + 1));
            });
            el.appendChild(repliesContainer);
        }

        return el;
    }

    // ═══════════════════════════════════════════════════════════════
    // COMMENT SUBMISSION
    // ═══════════════════════════════════════════════════════════════

    /**
     * Submit a new comment
     */
    async function submitComment(parentId = null) {
        if (!state.inputField || !state.currentUser) return;

        const content = state.inputField.value.trim();
        if (!content || content.length > Config.MAX_COMMENT_LENGTH) return;

        // Run through moderation
        if (typeof KatanxModeration !== 'undefined') {
            const modResult = KatanxModeration.moderate(content, state.currentUser.id);

            if (modResult.action !== KatanxModeration.Action.ALLOW) {
                handleModerationAction(modResult);
                if (modResult.action === KatanxModeration.Action.SHADOW_BLOCK) {
                    // Fake success for shadow blocks
                    showShadowComment(content);
                }
                return;
            }
        }

        const comment = {
            id: generateId(),
            stream_id: state.streamId,
            parent_id: parentId,
            user: state.currentUser,
            content: content,
            created_at: new Date().toISOString(),
            likes: 0,
            replies: [],
            is_cut: false
        };

        // Add to state
        if (parentId) {
            const parent = findComment(parentId);
            if (parent) {
                parent.replies = parent.replies || [];
                parent.replies.push(comment);
            }
        } else {
            state.comments.unshift(comment);
        }

        // Save and render
        saveComments();
        renderComments();

        // Clear input
        state.inputField.value = '';
        updateCharCounter();

        // Animate new comment
        setTimeout(() => {
            const newEl = state.container.querySelector(`[data-comment-id="${comment.id}"]`);
            if (newEl) {
                newEl.classList.add('kx-comment--new');
                setTimeout(() => newEl.classList.remove('kx-comment--new'), Config.ANIMATION_DURATION_MS);
            }
        }, 10);
    }

    /**
     * Handle moderation action
     */
    function handleModerationAction(result) {
        switch (result.action) {
            case 'warn':
                showWarning(result.reason);
                break;
            case 'temp_mute':
                showMuteNotice(result.muteRemaining || 600);
                break;
            case 'ban':
                showBanNotice();
                break;
            case 'flag_review':
                showFlaggedNotice();
                break;
        }
    }

    /**
     * Show inline warning
     */
    function showWarning(reason) {
        const warning = document.createElement('div');
        warning.className = 'kx-comment-warning';
        warning.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <span>${escapeHtml(reason)}</span>
        `;

        state.inputField.parentElement.appendChild(warning);
        setTimeout(() => warning.remove(), 5000);
    }

    // ═══════════════════════════════════════════════════════════════
    // COMMENT ACTIONS
    // ═══════════════════════════════════════════════════════════════

    /**
     * Handle click actions on comments
     */
    function handleCommentAction(e) {
        const actionBtn = e.target.closest('[data-action]');
        if (!actionBtn) return;

        const commentEl = actionBtn.closest('.kx-comment');
        const commentId = commentEl?.dataset.commentId;
        const action = actionBtn.dataset.action;

        switch (action) {
            case 'reply':
                openReplyInput(commentId);
                break;
            case 'like':
                toggleLike(commentId);
                break;
            case 'challenge':
                issueChallenge(commentId);
                break;
            case 'report':
                reportComment(commentId);
                break;
        }
    }

    /**
     * Toggle like on a comment
     */
    function toggleLike(commentId) {
        const comment = findComment(commentId);
        if (!comment) return;

        const likedKey = `kx_liked_${commentId}`;
        const isLiked = localStorage.getItem(likedKey);

        if (isLiked) {
            comment.likes = Math.max(0, (comment.likes || 0) - 1);
            localStorage.removeItem(likedKey);
        } else {
            comment.likes = (comment.likes || 0) + 1;
            localStorage.setItem(likedKey, '1');
        }

        saveComments();
        renderComments();
    }

    /**
     * Issue a challenge (Katanx Cut)
     */
    function issueChallenge(commentId) {
        const comment = findComment(commentId);
        if (!comment) return;

        // Dispatch event for Katanx Cuts system to handle
        const event = new CustomEvent('katanx:challenge', {
            detail: {
                targetComment: comment,
                challenger: state.currentUser,
                streamId: state.streamId
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Report a comment
     */
    function reportComment(commentId) {
        const comment = findComment(commentId);
        if (!comment) return;

        // Add to report queue
        const reports = JSON.parse(localStorage.getItem('kx_reports') || '[]');
        reports.push({
            id: generateId(),
            comment_id: commentId,
            comment_content: comment.content,
            reported_by: state.currentUser?.id,
            reported_at: new Date().toISOString(),
            status: 'pending'
        });
        localStorage.setItem('kx_reports', JSON.stringify(reports));

        // Show confirmation
        showToast('Comment reported. Our team will review it.');
    }

    // ═══════════════════════════════════════════════════════════════
    // UTILITIES
    // ═══════════════════════════════════════════════════════════════

    function findComment(id, comments = state.comments) {
        for (const comment of comments) {
            if (comment.id === id) return comment;
            if (comment.replies) {
                const found = findComment(id, comment.replies);
                if (found) return found;
            }
        }
        return null;
    }

    function saveComments() {
        localStorage.setItem(`kx_comments_${state.streamId}`, JSON.stringify(state.comments));
    }

    function startPolling() {
        if (state.pollInterval) clearInterval(state.pollInterval);
        state.pollInterval = setInterval(loadComments, Config.POLL_INTERVAL_MS);
    }

    function stopPolling() {
        if (state.pollInterval) {
            clearInterval(state.pollInterval);
            state.pollInterval = null;
        }
    }

    function updateCharCounter() {
        const counter = document.querySelector('.kx-comment-counter');
        if (!counter || !state.inputField) return;

        const remaining = Config.MAX_COMMENT_LENGTH - state.inputField.value.length;
        counter.textContent = remaining;
        counter.classList.toggle('kx-comment-counter--warning', remaining < 30);
        counter.classList.toggle('kx-comment-counter--error', remaining < 0);
    }

    function formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        if (seconds < 60) return 'now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d`;
        return date.toLocaleDateString();
    }

    function formatContent(content) {
        // Escape HTML first
        let formatted = escapeHtml(content);

        // Convert @mentions to links
        formatted = formatted.replace(/@(\w+)/g, '<a href="/profile.html?user=$1" class="kx-mention">@$1</a>');

        // Convert #hashtags
        formatted = formatted.replace(/#(\w+)/g, '<a href="/explore.html?tag=$1" class="kx-hashtag">#$1</a>');

        return formatted;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function generateId() {
        return 'kx_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
    }

    function getStoredUser() {
        const stored = localStorage.getItem('kx_current_user');
        return stored ? JSON.parse(stored) : null;
    }

    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'kx-toast';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    function showShadowComment(content) {
        // User sees their comment but it's not actually posted
        const fakeComment = {
            id: 'shadow_' + generateId(),
            user: state.currentUser,
            content: content,
            created_at: new Date().toISOString(),
            likes: 0,
            replies: [],
            is_shadow: true
        };

        const el = createCommentElement(fakeComment);
        el.classList.add('kx-comment--shadow');
        state.container.prepend(el);
        state.inputField.value = '';
    }

    // ═══════════════════════════════════════════════════════════════
    // PUBLIC API
    // ═══════════════════════════════════════════════════════════════

    return {
        init,
        submitComment,
        loadComments,
        stopPolling,
        getComments: () => [...state.comments],
        setUser: (user) => { state.currentUser = user; },
        Config
    };

})();

// Export for Node.js / testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KatanxComments;
}
