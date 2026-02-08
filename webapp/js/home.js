/**
 * Katanx - Modular Home with News
 */

class KatanxModular {
    constructor() {
        this.newsTiles = document.getElementById('news-tiles');
        this.liveFeed = document.getElementById('live-scroll');
        this.feedList = document.getElementById('feed-list');

        this.init();
    }

    async init() {
        await this.loadNews();
        await this.loadLiveActivity();
        await this.loadFeed();

        // Auto-refresh
        setInterval(() => {
            this.loadLiveActivity();
        }, 30000);
    }

    /**
     * Load curated news articles
     */
    async loadNews() {
        // Mock data with images matching Katanx news articles
        const newsArticles = [
            {
                title: "The Science of Neuroplasticity",
                category: "Neuroscience",
                description: "Your brain can rewire itself at any age. New research reveals how deliberate practice, focused attention, and novel experiences reshape neural pathways.",
                curated: false,
                image: "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=400&h=300&fit=crop"
            },
            {
                title: "The Rise of Local AI Models",
                category: "AI Research",
                description: "Local AI models are transforming how we work with artificial intelligence, offering privacy, speed, and customization.",
                curated: true,
                image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=300&fit=crop"
            },
            {
                title: "Mastery Through Deliberate Practice",
                category: "Personal Growth",
                description: "True mastery requires intentional, focused practice that pushes beyond comfort zones.",
                curated: true,
                image: "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=400&h=300&fit=crop"
            },
            {
                title: "The Philosophy of Flow States",
                category: "Philosophy",
                description: "Exploring the mental state where peak performance meets deep satisfaction.",
                curated: true,
                image: "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400&h=300&fit=crop"
            },
            {
                title: "Building Sustainable Ventures",
                category: "Business",
                description: "Long-term thinking and ethical practices in modern entrepreneurship.",
                curated: false,
                image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop"
            }
        ];

        this.renderNews(newsArticles);
    }

    renderNews(articles) {
        if (!this.newsTiles) return;

        this.newsTiles.innerHTML = articles.map(article => `
            <div class="news-card ${article.curated ? 'curated' : ''}">
                <div class="news-image" style="background-image: url('${article.image || '/assets/placeholder-signal.webp'}');"></div>
                <div class="news-content">
                    <div class="news-category">${article.category}</div>
                    <div class="news-title">${article.title}</div>
                    ${article.description ? `<div class="news-description">${article.description}</div>` : ''}
                </div>
            </div>
        `).join('');
    }

    /**
     * Load live activity
     */
    async loadLiveActivity() {
        // Mock live stats
        const stats = [
            `<div class="card-small"><div class="live-dot"></div><p>@kai training</p></div>`,
            `<div class="card-small"><p><strong>103</strong> online</p></div>`,
            `<div class="card-small"><p><strong>14</strong> posts</p></div>`,
            `<div class="card-small"><p><strong>5</strong> signals</p></div>`
        ];

        if (this.liveFeed) {
            // Keep existing cards, just update if needed
        }
    }

    /**
     * Load feed
     */
    async loadFeed() {
        try {
            const response = await fetch('/api/stream/feed?limit=3');
            if (response.ok) {
                const data = await response.json();
                if (data.posts && data.posts.length > 0) {
                    this.renderFeed(data.posts);
                }
            }
        } catch (error) {
            // Keep mock data
        }
    }

    renderFeed(posts) {
        if (!this.feedList) return;

        const feedHTML = posts.slice(0, 2).map(post => `
            <div class="feed-card">
                <p class="feed-user">@${post.username || 'user'}</p>
                <p class="feed-content">${this.truncate(post.content || '', 120)}</p>
                <div class="feed-meta">
                    <span>${this.getTimeAgo(post.created_at)}</span>
                    <span>${post.comments || 0} comments</span>
                </div>
            </div>
        `).join('');

        this.feedList.innerHTML = feedHTML + `
            <a href="/stream" class="view-all">View All →</a>
        `;
    }

    truncate(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    getTimeAgo(timestamp) {
        if (!timestamp) return 'just now';
        const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
        const intervals = {
            year: 31536000,
            month: 2592000,
            week: 604800,
            day: 86400,
            hour: 3600,
            minute: 60
        };

        for (const [unit, secondsInUnit] of Object.entries(intervals)) {
            const interval = Math.floor(seconds / secondsInUnit);
            if (interval >= 1) {
                return `${interval}${unit[0]} ago`;
            }
        }
        return 'just now';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    new KatanxModular();
});
