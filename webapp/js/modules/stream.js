/**
 * Stream Module
 * Handles post fetching, rendering, and interactions for the Signal Stream.
 */

export class StreamPage {
    constructor(appInstance) {
        this.app = appInstance;
        this.posts = [];
        this.currentPage = 0;
        this.hasMore = true;
        this.userId = appInstance.userId;
        this.sessionId = appInstance.sessionId;
        this.loading = false;
    }

    async init() {
        console.log('Initializing stream page...');
        if (!document.getElementById('streamFeed')) return;

        // Wait for session if not already set by app-modular.js
        if (!this.userId) {
            this.userId = localStorage.getItem('thesidia_user_id');
            this.sessionId = localStorage.getItem('thesidia_session_id');
        }

        await this.loadPosts();
        this.setupEventListeners();
        this.setupInfiniteScroll();
    }

    setupInfiniteScroll() {
        const feed = document.getElementById('streamFeed');
        if (!feed) return;

        // Intersection Observer for infinite scroll
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && this.hasMore && !this.loading) {
                    this.loadMorePosts();
                }
            });
        }, { rootMargin: '100px' });

        // Create sentinel element if it doesn't exist
        let sentinel = document.getElementById('feedSentinel');
        if (!sentinel) {
            sentinel = document.createElement('div');
            sentinel.id = 'feedSentinel';
            sentinel.style.height = '1px';
            feed.appendChild(sentinel);
        }
        observer.observe(sentinel);
    }

    async loadMorePosts() {
        if (this.loading || !this.hasMore) return;
        this.loading = true;
        this.currentPage++;
        await this.loadPosts(this.currentPage);
        this.loading = false;
    }

    async loadPosts(page = 0, limit = 20) {
        console.log('Loading stream feed...', { page, limit });
        try {
            const feedType = localStorage.getItem('feed_type') || 'chronological';
            const response = await fetch(`/api/feed?user_id=${this.userId}&session_id=${this.sessionId}&type=${feedType}&limit=${limit}&offset=${page * limit}`);
            const data = await response.json();

            if (data.items) {
                if (page === 0) {
                    this.posts = data.items;
                } else {
                    this.posts = [...this.posts, ...data.items];
                }
                this.hasMore = data.has_more || false;
                this.currentPage = page;
                this.renderPosts();
            }
        } catch (error) {
            console.error('Error loading posts:', error);
            const feed = document.getElementById('streamFeed');
            if (feed && page === 0) {
                feed.innerHTML = '<div class="stream-loading">Error loading stream. Please refresh.</div>';
            }
        }
    }

    renderPosts() {
        const feed = document.getElementById('streamFeed');
        if (!feed) return;

        if (this.posts.length === 0) {
            feed.innerHTML = '<div class="stream-loading">No posts yet. Be the first to post!</div>';
            return;
        }

        // Keep sentinel if it exists
        const sentinel = document.getElementById('feedSentinel');
        feed.innerHTML = this.posts.map(post => this.renderPost(post)).join('');
        if (sentinel) feed.appendChild(sentinel);
    }

    renderPost(post) {
        const timeAgo = this.getTimeAgo(post.created_at);
        const interactions = post.interactions || {};
        const likes = interactions.likes || 0;
        const comments = interactions.comments || 0;
        const reposts = interactions.reposts || 0;
        const views = interactions.views || 0;
        const liked = interactions.liked_by && interactions.liked_by.includes(this.userId);
        const reposted = interactions.reposted_by && interactions.reposted_by.includes(this.userId);

        return `
            <div class="stream-post" data-post-id="${post.id}">
                <div class="post-header">
                    <div class="post-author">
                        <img src="${post.author?.avatar_url || '/profile-image.jpg'}" alt="${post.author?.display_name || 'User'}" class="post-avatar" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'40\' height=\'40\'%3E%3Ccircle cx=\'20\' cy=\'20\' r=\'20\' fill=\'%23ffffff\' fill-opacity=\'0.1\'/%3E%3Ccircle cx=\'20\' cy=\'14\' r=\'6\' fill=\'%23ffffff\' fill-opacity=\'0.3\'/%3E%3Cpath d=\'M10 38 Q20 32 30 38\' stroke=\'%23ffffff\' stroke-width=\'2\' fill=\'none\' stroke-opacity=\'0.3\'/%3E%3C/svg%3E'">
                        <div class="post-author-info">
                            <div class="post-author-name">${this.escapeHtml(post.author?.display_name || 'User')}</div>
                            <div class="post-author-handle">${this.escapeHtml(post.author?.username || '@user')}</div>
                        </div>
                    </div>
                    <div class="post-time">${timeAgo}</div>
                </div>
                <div class="post-content">${this.escapeHtml(post.content || '')}</div>
                ${post.media && post.media.length > 0 ? `
                    <div class="post-media">
                        ${post.media.map(mediaItem => {
            if (mediaItem.type === 'gif' || mediaItem.url.includes('.gif')) {
                return `<img src="${mediaItem.url}" alt="Post media" class="post-media-item" style="max-width: 100%; border-radius: 12px; margin-top: 12px;">`;
            } else if (mediaItem.type === 'image') {
                return `<img src="${mediaItem.url}" alt="Post media" class="post-media-item" style="max-width: 100%; border-radius: 12px; margin-top: 12px;" loading="lazy">`;
            } else if (mediaItem.type === 'video') {
                return `<video src="${mediaItem.url}" controls class="post-media-item" style="max-width: 100%; border-radius: 12px; margin-top: 12px;"></video>`;
            }
            return '';
        }).join('')}
                    </div>
                ` : ''}
                <div class="post-actions">
                    <button class="post-action-btn ${liked ? 'active' : ''}" data-action="like" data-post-id="${post.id}">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                        </svg>
                        <span class="like-count">${likes}</span>
                    </button>
                    <button class="post-action-btn" data-action="comment" data-post-id="${post.id}">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                        </svg>
                        <span class="comment-count">${comments}</span>
                    </button>
                    <button class="post-action-btn ${reposted ? 'active' : ''}" data-action="repost" data-post-id="${post.id}">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M17 1l4 4-4 4M21 5H11a4 4 0 0 0-4 4v6"/>
                            <path d="M7 23l-4-4 4-4M3 19h10a4 4 0 0 0 4-4V9"/>
                        </svg>
                        <span class="repost-count">${reposts}</span>
                    </button>
                    <button class="post-action-btn" data-action="views" data-post-id="${post.id}">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                            <circle cx="12" cy="12" r="3"/>
                        </svg>
                        <span class="view-count">${views}</span>
                    </button>
                </div>
            </div>
        `;
    }

    getTimeAgo(timestamp) {
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

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setupEventListeners() {
        const composeTextarea = document.getElementById('composeTextarea');
        const postBtn = document.getElementById('postBtn');

        if (composeTextarea && postBtn) {
            composeTextarea.addEventListener('input', () => {
                postBtn.disabled = !composeTextarea.value.trim();
            });

            postBtn.addEventListener('click', () => this.createPost());
        }

        // Submenu filter items
        const submenuFilters = document.querySelectorAll('.submenu-item[data-filter]');
        submenuFilters.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const filterType = item.dataset.filter;
                submenuFilters.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                localStorage.setItem('feed_type', filterType);
                this.currentPage = 0;
                this.posts = [];
                this.loadPosts(0, 20);
            });
        });

        // Delegate event listeners for post actions
        const feed = document.getElementById('streamFeed');
        if (feed) {
            feed.addEventListener('click', (e) => {
                const btn = e.target.closest('.post-action-btn');
                if (!btn) return;
                const action = btn.dataset.action;
                const postId = btn.dataset.postId;

                if (action === 'like') this.toggleLike(postId, btn);
                else if (action === 'comment') this.showComments(postId);
                else if (action === 'repost') this.toggleRepost(postId, btn);
            });
        }
    }

    async createPost() {
        const composeTextarea = document.getElementById('composeTextarea');
        if (!composeTextarea || !composeTextarea.value.trim()) return;

        const content = composeTextarea.value.trim();
        composeTextarea.value = '';
        const postBtn = document.getElementById('postBtn');
        if (postBtn) postBtn.disabled = true;

        try {
            const response = await fetch('/api/posts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: content,
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });

            if (response.ok) {
                await this.loadPosts(0, 20);
            }
        } catch (error) {
            console.error('Error creating post:', error);
        } finally {
            if (postBtn) postBtn.disabled = false;
        }
    }

    async toggleLike(postId, btn) {
        try {
            const response = await fetch(`/api/posts/${postId}/like`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });

            if (response.ok) {
                const data = await response.json();
                const likeCount = btn.querySelector('.like-count');
                if (likeCount) {
                    likeCount.textContent = data.interactions.likes;
                }
                btn.classList.toggle('active', data.liked);
            }
        } catch (error) {
            console.error('Error toggling like:', error);
        }
    }

    async toggleRepost(postId, btn) { console.log('Repost not yet implemented'); }
    showComments(postId) { console.log('Comments not yet implemented'); }
}
