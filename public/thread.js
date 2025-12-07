/**
 * Thread Detail Page Component
 * Reddit-style post detail page with comment threading, voting, and sorting
 */

class ThreadDetailPage {
    constructor() {
        this.threadId = null;
        this.thread = null;
        this.comments = [];
        this.currentSort = 'best';
        this.collapsedComments = new Set();
        this.userId = localStorage.getItem('thesidia_user_id');
        this.sessionId = localStorage.getItem('thesidia_session_id');
        
        this.init();
    }
    
    async ensureSession() {
        // Create session if doesn't exist
        if (!this.sessionId) {
            try {
                const sessionResponse = await fetch('/api/user/session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                const sessionData = await sessionResponse.json();
                this.userId = sessionData.user_id;
                this.sessionId = sessionData.session_id;
                localStorage.setItem('thesidia_user_id', this.userId);
                localStorage.setItem('thesidia_session_id', this.sessionId);
            } catch (e) {
                console.warn('Could not create session:', e);
            }
        }
    }
    
    async init() {
        // Ensure session exists
        await this.ensureSession();
        
        // Get thread ID from URL - try multiple methods
        let threadId = null;
        
        // Method 1: Router (if available)
        if (window.Router) {
            const route = window.Router.getCurrentRoute();
            threadId = route?.params?.threadId || route?.params?.id;
        }
        
        // Method 2: Extract from URL path
        if (!threadId) {
            const path = window.location.pathname;
            const match = path.match(/\/(?:thread|circles\/[^\/]+)\/([^\/]+)/);
            if (match) {
                threadId = match[1];
            }
        }
        
        // Method 3: URL hash or query param
        if (!threadId) {
            const hash = window.location.hash.replace('#', '');
            const params = new URLSearchParams(window.location.search);
            threadId = hash || params.get('thread') || params.get('id');
        }
        
        // Method 4: Check if we're on thread.html and extract from current URL
        if (!threadId && window.location.pathname.includes('thread.html')) {
            // Try to get from hash
            threadId = window.location.hash.replace('#', '');
            
            // Also try query params
            if (!threadId) {
                const params = new URLSearchParams(window.location.search);
                threadId = params.get('id') || params.get('thread');
            }
        }
        
        this.threadId = threadId;
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load thread if ID is available
        if (this.threadId) {
            this.loadThread(this.threadId);
        } else {
            // Show error if no thread ID found
            const container = document.getElementById('threadPost');
            if (container) {
                container.innerHTML = `
                    <div class="thread-error">
                        <h3>Thread Not Found</h3>
                        <p>No thread ID found in URL. Please navigate from the circles page.</p>
                        <button class="retry-btn" onclick="window.location.href='/stream.html'">
                            Go to Circles
                        </button>
                    </div>
                `;
            }
        }
    }
    
    setupEventListeners() {
        // Back button
        const backBtn = document.getElementById('threadBackBtn');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                this.handleBack();
            });
        }
        
        // Comment form submit
        const submitBtn = document.getElementById('commentSubmit');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitComment());
        }
        
        // Enter key in comment input
        const commentInput = document.getElementById('commentInput');
        if (commentInput) {
            commentInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault();
                    this.submitComment();
                }
                // Escape to clear
                if (e.key === 'Escape') {
                    commentInput.value = '';
                    delete commentInput.dataset.parentId;
                    commentInput.placeholder = 'Add a comment...';
                }
            });
            
            // Auto-resize textarea
            commentInput.addEventListener('input', () => {
                commentInput.style.height = 'auto';
                commentInput.style.height = Math.min(commentInput.scrollHeight, 200) + 'px';
            });
        }
        
        // Sort buttons
        const sortButtons = document.querySelectorAll('.sort-btn');
        sortButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const sort = btn.dataset.sort;
                this.changeSort(sort);
            });
        });
    }
    
    async loadThread(threadId, retryCount = 0) {
        this.threadId = threadId;
        const maxRetries = 2;
        
        const postContainer = document.getElementById('threadPost');
        if (postContainer) {
            postContainer.innerHTML = '<div class="thread-loading">Loading thread...</div>';
        }
        
        try {
            // Load thread data
            const threadResponse = await fetch(`/api/threads/${threadId}?user_id=${this.userId || ''}&session_id=${this.sessionId || ''}`);
            
            if (!threadResponse.ok) {
                // Retry on 404 or 500 errors
                if ((threadResponse.status === 404 || threadResponse.status === 500) && retryCount < maxRetries) {
                    console.log(`Retrying thread load (attempt ${retryCount + 1}/${maxRetries})...`);
                    await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1))); // Exponential backoff
                    return this.loadThread(threadId, retryCount + 1);
                }
                
                const errorData = await threadResponse.json().catch(() => ({}));
                throw new Error(errorData.error || `Failed to load thread: ${threadResponse.status}`);
            }
            
            this.thread = await threadResponse.json();
            
            // Validate thread data
            if (!this.thread || !this.thread.id) {
                throw new Error('Invalid thread data received');
            }
            
            this.renderThread(this.thread);
            
            // Load comments
            await this.loadComments(threadId, this.currentSort);
        } catch (error) {
            console.error('Error loading thread:', error);
            if (postContainer) {
                const errorHtml = `
                    <div class="thread-error">
                        <h3>Unable to load thread</h3>
                        <p>${this.escapeHtml(error.message)}</p>
                        <button class="retry-btn" onclick="window.ThreadDetailPage.loadThread('${threadId}')">
                            Retry
                        </button>
                    </div>
                `;
                postContainer.innerHTML = errorHtml;
            }
        }
    }
    
    renderThread(thread) {
        const container = document.getElementById('threadPost');
        if (!container) return;
        
        const author = thread.author || {};
        const avatarUrl = this.getAvatarUrl(thread.circle || '', author.user_id, author.avatar_url);
        const fallbackAvatarUrl = this.getFallbackAvatarUrl(thread.circle || '', author.user_id);
        const timeAgo = this.formatTime(thread.created_at);
        const score = thread.score || (thread.upvotes || 0) - (thread.downvotes || 0);
        const userVote = thread.user_vote;
        
        container.innerHTML = `
            <div class="thread-vote-section">
                <button class="vote-btn vote-up ${userVote === 'up' ? 'active' : ''}" 
                        data-thread-id="${thread.id}" 
                        data-direction="up"
                        aria-label="Upvote">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 15l-6-6-6 6"/>
                    </svg>
                </button>
                <div class="vote-score ${score > 0 ? 'positive' : score < 0 ? 'negative' : ''}">${score}</div>
                <button class="vote-btn vote-down ${userVote === 'down' ? 'active' : ''}" 
                        data-thread-id="${thread.id}" 
                        data-direction="down"
                        aria-label="Downvote">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M6 9l6 6 6-6"/>
                    </svg>
                </button>
            </div>
            <div class="thread-content-section">
                <div class="thread-header-content">
                    <div class="thread-category-badge">${this.escapeHtml(thread.circle || 'General')}</div>
                    <div class="thread-author-info">
                        <img src="${avatarUrl}" 
                             alt="${this.escapeHtml(author.display_name || author.username || 'User')}" 
                             class="thread-author-avatar"
                             onerror="this.onerror=null; this.src='${fallbackAvatarUrl}';"
                             loading="lazy">
                        <div class="thread-author-details">
                            <span class="thread-author-name">${this.escapeHtml(author.display_name || author.username || 'User')}</span>
                            <span class="thread-time">${timeAgo}</span>
                        </div>
                    </div>
                </div>
                <h1 class="thread-title">${this.escapeHtml(thread.title || '')}</h1>
                <div class="thread-body">${this.escapeHtml(thread.body || '').replace(/\n/g, '<br>')}</div>
                <div class="thread-footer-actions">
                    <button class="thread-action-btn" data-action="comment">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                        </svg>
                        <span>${thread.comment_count || 0} comments</span>
                    </button>
                </div>
            </div>
        `;
        
        // Update header
        const categoryEl = document.getElementById('threadCategory');
        if (categoryEl) {
            categoryEl.textContent = thread.circle || 'General';
        }
        
        const metaEl = document.getElementById('threadMetaHeader');
        if (metaEl) {
            metaEl.textContent = `${thread.comment_count || 0} comments`;
        }
        
        // Setup vote handlers
        this.setupVoteHandlers(thread.id);
    }
    
    async loadComments(threadId, sort = 'best', retryCount = 0) {
        this.currentSort = sort;
        const maxRetries = 2;
        
        const container = document.getElementById('commentsTree');
        if (container && retryCount === 0) {
            container.innerHTML = '<div class="comments-loading">Loading comments...</div>';
        }
        
        try {
            const response = await fetch(
                `/api/threads/${threadId}/comments?sort=${sort}&limit=50&user_id=${this.userId || ''}&session_id=${this.sessionId || ''}`
            );
            
            if (!response.ok) {
                // Retry on 404 or 500 errors
                if ((response.status === 404 || response.status === 500) && retryCount < maxRetries) {
                    console.log(`Retrying comments load (attempt ${retryCount + 1}/${maxRetries})...`);
                    await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
                    return this.loadComments(threadId, sort, retryCount + 1);
                }
                
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Failed to load comments: ${response.status}`);
            }
            
            const data = await response.json();
            this.comments = data.comments || [];
            this.renderCommentTree(this.comments);
            
            // Update sort button states
            document.querySelectorAll('.sort-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.sort === sort);
            });
        } catch (error) {
            console.error('Error loading comments:', error);
            if (container) {
                const errorHtml = `
                    <div class="comments-error">
                        <p>${this.escapeHtml(error.message)}</p>
                        <button class="retry-btn" onclick="window.ThreadDetailPage.loadComments('${threadId}', '${sort}')">
                            Retry
                        </button>
                    </div>
                `;
                container.innerHTML = errorHtml;
            }
        }
    }
    
    renderCommentTree(comments, depth = 0) {
        const container = document.getElementById('commentsTree');
        if (!container) return;
        
        if (!comments || comments.length === 0) {
            container.innerHTML = '<div class="comments-empty">No comments yet. Be the first to comment!</div>';
            return;
        }
        
        container.innerHTML = comments.map(comment => this.renderComment(comment, depth)).join('');
        
        // Setup event handlers for all comments
        this.setupCommentHandlers();
    }
    
    renderComment(comment, depth = 0) {
        const isCollapsed = this.collapsedComments.has(comment.id);
        const author = comment.author || {};
        const avatarUrl = this.getAvatarUrl('', author.user_id, author.avatar_url);
        const fallbackAvatarUrl = this.getFallbackAvatarUrl('', author.user_id);
        const timeAgo = this.formatTime(comment.created_at);
        const score = comment.score || (comment.upvotes || 0) - (comment.downvotes || 0);
        const userVote = comment.user_vote;
        const replyCount = this.countReplies(comment);
        
        if (isCollapsed) {
            return `
                <div class="comment collapsed" data-comment-id="${comment.id}" data-depth="${depth}">
                    <div class="comment-collapsed-bar"></div>
                    <button class="comment-expand-btn" data-comment-id="${comment.id}">
                        [+${replyCount + 1} more]
                    </button>
                </div>
            `;
        }
        
        const repliesHtml = comment.replies && comment.replies.length > 0
            ? comment.replies.map(reply => this.renderComment(reply, depth + 1)).join('')
            : '';
        
        return `
            <div class="comment" data-comment-id="${comment.id}" data-depth="${depth}">
                <div class="comment-vote-section">
                    <button class="vote-btn vote-up ${userVote === 'up' ? 'active' : ''}" 
                            data-comment-id="${comment.id}" 
                            data-direction="up"
                            aria-label="Upvote">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 15l-6-6-6 6"/>
                        </svg>
                    </button>
                    <div class="vote-score ${score > 0 ? 'positive' : score < 0 ? 'negative' : ''}">${score}</div>
                    <button class="vote-btn vote-down ${userVote === 'down' ? 'active' : ''}" 
                            data-comment-id="${comment.id}" 
                            data-direction="down"
                            aria-label="Downvote">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M6 9l6 6 6-6"/>
                        </svg>
                    </button>
                </div>
                <div class="comment-content-section">
                    <div class="comment-header">
                        <img src="${avatarUrl}" 
                             alt="${this.escapeHtml(author.display_name || author.username || 'User')}" 
                             class="comment-avatar"
                             onerror="this.onerror=null; this.src='${fallbackAvatarUrl}';"
                             loading="lazy">
                        <span class="comment-author">${this.escapeHtml(author.display_name || author.username || 'User')}</span>
                        <span class="comment-time">${timeAgo}</span>
                        <button class="comment-collapse-btn" data-comment-id="${comment.id}" aria-label="Collapse thread">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 15l-6-6-6 6"/>
                            </svg>
                        </button>
                    </div>
                    <div class="comment-body">${this.escapeHtml(comment.content || '').replace(/\n/g, '<br>')}</div>
                    <div class="comment-actions">
                        <button class="comment-reply-btn" data-comment-id="${comment.id}" data-parent-id="${comment.id}">
                            Reply
                        </button>
                        <button class="comment-award-btn" data-comment-id="${comment.id}">
                            Award
                        </button>
                    </div>
                    ${comment.awards && comment.awards.length > 0 ? `
                        <div class="comment-awards">
                            ${comment.awards.map(award => {
                                const awardTypes = {
                                    'quality': { icon: '★', name: 'Quality' },
                                    'insightful': { icon: '💡', name: 'Insightful' },
                                    'helpful': { icon: '✓', name: 'Helpful' },
                                    'original': { icon: '✨', name: 'Original' },
                                    'well_researched': { icon: '📚', name: 'Well Researched' },
                                    'thoughtful': { icon: '🤔', name: 'Thoughtful' }
                                };
                                const awardInfo = awardTypes[award.type] || { icon: '★', name: award.type || 'Award' };
                                return `
                                    <span class="award-badge" title="${this.escapeHtml(awardInfo.name)}">
                                        <span class="award-badge-icon">${awardInfo.icon}</span>
                                        <span class="award-badge-count">${award.count || 1}</span>
                                    </span>
                                `;
                            }).join('')}
                        </div>
                    ` : ''}
                    ${repliesHtml ? `<div class="comment-replies">${repliesHtml}</div>` : ''}
                </div>
            </div>
        `;
    }
    
    countReplies(comment) {
        let count = 0;
        if (comment.replies) {
            count += comment.replies.length;
            comment.replies.forEach(reply => {
                count += this.countReplies(reply);
            });
        }
        return count;
    }
    
    setupCommentHandlers() {
        // Vote buttons
        document.querySelectorAll('.comment .vote-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const commentId = btn.dataset.commentId;
                const direction = btn.dataset.direction;
                this.handleCommentVote(commentId, direction);
            });
        });
        
        // Collapse buttons
        document.querySelectorAll('.comment-collapse-btn, .comment-expand-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const commentId = btn.dataset.commentId;
                this.toggleCollapse(commentId);
            });
        });
        
        // Reply buttons
        document.querySelectorAll('.comment-reply-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const commentId = btn.dataset.commentId;
                this.showReplyForm(commentId);
            });
        });
        
        // Award buttons
        document.querySelectorAll('.comment-award-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const commentId = btn.dataset.commentId;
                this.showAwardMenu(commentId);
            });
        });
    }
    
    async showAwardMenu(commentId) {
        try {
            // Load award types
            const response = await fetch('/api/awards/types');
            const data = await response.json();
            const awardTypes = data.awards || [];
            
            // Create award modal
            const modal = document.createElement('div');
            modal.className = 'award-modal';
            modal.innerHTML = `
                <div class="award-modal-backdrop"></div>
                <div class="award-modal-content">
                    <div class="award-modal-header">
                        <h3>Give Award</h3>
                        <button class="award-modal-close" aria-label="Close">×</button>
                    </div>
                    <div class="award-modal-body">
                        <p class="award-modal-description">Select an award type:</p>
                        <div class="award-types-list">
                            ${awardTypes.map(award => `
                                <button class="award-type-btn" data-award-type="${award.id}">
                                    <span class="award-icon">${award.icon || '★'}</span>
                                    <span class="award-name">${this.escapeHtml(award.name)}</span>
                                </button>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Close handlers
            const closeModal = () => modal.remove();
            modal.querySelector('.award-modal-backdrop').addEventListener('click', closeModal);
            modal.querySelector('.award-modal-close').addEventListener('click', closeModal);
            
            // Award type selection
            modal.querySelectorAll('.award-type-btn').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const awardType = btn.dataset.awardType;
                    closeModal();
                    await this.giveAward(commentId, awardType);
                });
            });
        } catch (error) {
            console.error('Error showing award menu:', error);
            alert('Error loading awards. Please try again.');
        }
    }
    
    async giveAward(commentId, awardType) {
        try {
            const response = await fetch(`/api/comments/${commentId}/award`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    award_type: awardType,
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });
            
            if (response.ok) {
                // Reload comments to show new award
                await this.loadComments(this.threadId, this.currentSort);
            } else {
                const error = await response.json();
                alert(`Error: ${error.error || 'Failed to give award'}`);
            }
        } catch (error) {
            console.error('Error giving award:', error);
            alert('Error giving award. Please try again.');
        }
    }
    
    setupVoteHandlers(threadId) {
        document.querySelectorAll('.thread-vote-section .vote-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const direction = btn.dataset.direction;
                this.handleVote(threadId, direction);
            });
        });
    }
    
    async handleVote(threadId, direction) {
        // Ensure session exists
        await this.ensureSession();
        
        try {
            const btn = document.querySelector(`.thread-vote-section .vote-btn[data-direction="${direction}"]`);
            const isActive = btn?.classList.contains('active');
            const currentDirection = isActive ? null : direction;
            
            // Optimistic UI update
            if (btn) {
                const container = btn.closest('.thread-vote-section');
                const scoreEl = container?.querySelector('.vote-score');
                const currentScore = parseInt(scoreEl?.textContent || '0');
                
                // Temporarily update score
                if (currentDirection === 'up' && !isActive) {
                    scoreEl.textContent = currentScore + 1;
                } else if (currentDirection === 'down' && !isActive) {
                    scoreEl.textContent = currentScore - 1;
                } else if (isActive) {
                    // Removing vote
                    if (direction === 'up') {
                        scoreEl.textContent = currentScore - 1;
                    } else {
                        scoreEl.textContent = currentScore + 1;
                    }
                }
            }
            
            const response = await fetch(`/api/threads/${threadId}/vote`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    direction: currentDirection,
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateVoteUI('.thread-vote-section', data);
            } else {
                // Revert optimistic update on error
                this.loadThread(threadId);
            }
        } catch (error) {
            console.error('Error voting:', error);
            // Revert on error
            if (this.threadId) {
                this.loadThread(this.threadId);
            }
        }
    }
    
    async handleCommentVote(commentId, direction) {
        // Ensure session exists
        await this.ensureSession();
        
        try {
            const commentEl = document.querySelector(`.comment[data-comment-id="${commentId}"]`);
            if (!commentEl) return;
            
            const btn = commentEl.querySelector(`.vote-btn[data-direction="${direction}"]`);
            const isActive = btn?.classList.contains('active');
            const currentDirection = isActive ? null : direction;
            
            // Optimistic UI update
            const container = commentEl.querySelector('.comment-vote-section');
            const scoreEl = container?.querySelector('.vote-score');
            const currentScore = parseInt(scoreEl?.textContent || '0');
            
            if (currentDirection === 'up' && !isActive) {
                scoreEl.textContent = currentScore + 1;
            } else if (currentDirection === 'down' && !isActive) {
                scoreEl.textContent = currentScore - 1;
            } else if (isActive) {
                if (direction === 'up') {
                    scoreEl.textContent = currentScore - 1;
                } else {
                    scoreEl.textContent = currentScore + 1;
                }
            }
            
            const response = await fetch(`/api/comments/${commentId}/vote`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    direction: currentDirection,
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateVoteUI(container, data);
            } else {
                // Revert optimistic update on error
                await this.loadComments(this.threadId, this.currentSort);
            }
        } catch (error) {
            console.error('Error voting on comment:', error);
            // Revert on error
            await this.loadComments(this.threadId, this.currentSort);
        }
    }
    
    updateVoteUI(container, data) {
        if (!container) return;
        
        const scoreEl = container.querySelector('.vote-score');
        if (scoreEl) {
            scoreEl.textContent = data.score;
            scoreEl.className = `vote-score ${data.score > 0 ? 'positive' : data.score < 0 ? 'negative' : ''}`;
        }
        
        // Update button states
        container.querySelectorAll('.vote-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        if (data.user_vote === 'up') {
            container.querySelector('.vote-up')?.classList.add('active');
        } else if (data.user_vote === 'down') {
            container.querySelector('.vote-down')?.classList.add('active');
        }
    }
    
    toggleCollapse(commentId) {
        if (this.collapsedComments.has(commentId)) {
            this.collapsedComments.delete(commentId);
        } else {
            this.collapsedComments.add(commentId);
        }
        
        // Re-render comments to update UI
        this.renderCommentTree(this.comments);
    }
    
    changeSort(sortType) {
        this.currentSort = sortType;
        this.loadComments(this.threadId, sortType);
    }
    
    showReplyForm(commentId) {
        // Scroll to comment form and set parent ID
        const form = document.getElementById('commentInput');
        if (form) {
            form.dataset.parentId = commentId;
            form.placeholder = 'Write a reply...';
            
            // Highlight the comment being replied to
            const commentEl = document.querySelector(`.comment[data-comment-id="${commentId}"]`);
            if (commentEl) {
                commentEl.style.backgroundColor = 'var(--accent-subtle)';
                commentEl.style.transition = 'background-color 0.3s ease';
                setTimeout(() => {
                    commentEl.style.backgroundColor = '';
                    setTimeout(() => {
                        commentEl.style.transition = '';
                    }, 300);
                }, 2000);
            }
            
            // Scroll to form
            setTimeout(() => {
                form.focus();
                const formSection = document.querySelector('.thread-comment-form');
                if (formSection) {
                    formSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }, 100);
        }
    }
    
    async submitComment() {
        const input = document.getElementById('commentInput');
        if (!input || !input.value.trim()) {
            // Visual feedback for empty comment
            if (input) {
                input.style.borderColor = '#ff4500';
                setTimeout(() => {
                    input.style.borderColor = '';
                }, 1000);
            }
            return;
        }
        
        const submitBtn = document.getElementById('commentSubmit');
        const originalText = submitBtn?.textContent;
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Posting...';
        }
        
        const content = input.value.trim();
        const parentId = input.dataset.parentId;
        input.value = '';
        input.placeholder = 'Add a comment...';
        delete input.dataset.parentId;
        
        try {
            let response;
            if (parentId) {
                // Reply to comment
                response = await fetch(`/api/comments/${parentId}/reply`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content: content,
                        thread_id: this.threadId,
                        user_id: this.userId,
                        session_id: this.sessionId
                    })
                });
            } else {
                // Top-level comment
                response = await fetch(`/api/threads/${this.threadId}/comments`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content: content,
                        user_id: this.userId,
                        session_id: this.sessionId
                    })
                });
            }
            
            if (response.ok) {
                // Reload comments
                await this.loadComments(this.threadId, this.currentSort);
                // Scroll to top of comments
                const commentsSection = document.querySelector('.thread-comments');
                if (commentsSection) {
                    commentsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            } else {
                const error = await response.json();
                alert(`Error: ${error.error || 'Failed to post comment'}`);
                // Restore input
                input.value = content;
                if (parentId) {
                    input.dataset.parentId = parentId;
                    input.placeholder = 'Write a reply...';
                }
            }
        } catch (error) {
            console.error('Error submitting comment:', error);
            alert('Error posting comment. Please try again.');
            // Restore input
            input.value = content;
            if (parentId) {
                input.dataset.parentId = parentId;
                input.placeholder = 'Write a reply...';
            }
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText || 'Post';
            }
        }
    }
    
    // Utility methods
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatTime(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
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
        return `${month}/${day}`;
    }
    
    getAvatarUrl(topic, authorId, authorAvatarUrl) {
        if (authorAvatarUrl && authorAvatarUrl.trim()) {
            return authorAvatarUrl;
        }
        const seed = authorId || topic || 'default';
        let seedHash = 0;
        for (let i = 0; i < seed.length; i++) {
            seedHash = seed.charCodeAt(i) + ((seedHash << 5) - seedHash);
        }
        const numericSeed = Math.abs(seedHash);
        return `https://api.dicebear.com/7.x/personas/svg?seed=${numericSeed}&size=40&radius=50`;
    }
    
    getFallbackAvatarUrl(topic, authorId) {
        const seed = authorId || topic || 'default';
        let seedHash = 0;
        for (let i = 0; i < seed.length; i++) {
            seedHash = seed.charCodeAt(i) + ((seedHash << 5) - seedHash);
        }
        const numericSeed = Math.abs(seedHash);
        return `https://randomuser.me/api/portraits/${numericSeed % 2 === 0 ? 'men' : 'women'}/${numericSeed % 99}.jpg`;
    }
}

// Create global instance
window.ThreadDetailPage = new ThreadDetailPage();


