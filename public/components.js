/**
 * Katanx // Shared Components
 * Reusable UI components for all pages
 */

class Components {
    /**
     * Create a stream item card
     */
    static createStreamItem(item) {
        const div = document.createElement('div');
        div.className = 'stream-item';
        div.dataset.id = item.id;
        
        const relevance = (item.relevance_score || 0).toFixed(2);
        const timestamp = item.timestamp ? new Date(item.timestamp).toLocaleDateString() : '';
        
        div.innerHTML = `
            <div class="stream-item-header">
                <div>
                    <div class="stream-item-title">${this.escapeHtml(item.title || 'Untitled')}</div>
                    <div class="stream-item-meta">
                        ${item.type || 'pattern'} • ${timestamp}
                        ${item.relevance_score ? `<span class="relevance-score"> • relevance: ${relevance}</span>` : ''}
                    </div>
                </div>
            </div>
            <div class="stream-item-content">
                ${this.escapeHtml(item.content || '')}
            </div>
            ${item.facts_count !== undefined || item.connections_count !== undefined ? `
                <div class="stream-item-stats">
                    ${item.facts_count !== undefined ? `<span>${item.facts_count} facts</span>` : ''}
                    ${item.connections_count !== undefined ? `<span>${item.connections_count} connections</span>` : ''}
                </div>
            ` : ''}
        `;
        
        // Add click handler
        div.addEventListener('click', () => {
            if (item.id) {
                this.handleItemClick(item);
            }
        });
        
        return div;
    }
    
    /**
     * Create a pattern card for Atlas
     */
    static createPatternCard(pattern) {
        const div = document.createElement('div');
        div.className = 'pattern-card';
        div.dataset.id = pattern.id;
        
        div.innerHTML = `
            <div class="pattern-card-header">
                <h3 class="pattern-name">${this.escapeHtml(pattern.name || pattern.id)}</h3>
                <div class="pattern-meta">
                    ${pattern.facts_count || 0} facts • ${pattern.connections_count || 0} connections
                </div>
            </div>
            ${pattern.last_updated ? `
                <div class="pattern-date">
                    Updated: ${new Date(pattern.last_updated).toLocaleDateString()}
                </div>
            ` : ''}
        `;
        
        div.addEventListener('click', () => {
            if (pattern.id) {
                this.handlePatternClick(pattern.id);
            }
        });
        
        return div;
    }
    
    /**
     * Create a research thread card
     */
    static createThreadCard(thread) {
        const div = document.createElement('div');
        div.className = 'thread-card';
        div.dataset.id = thread.id;
        
        const statusClass = thread.status === 'active' ? 'status-active' : 'status-completed';
        
        div.innerHTML = `
            <div class="thread-header">
                <h3 class="thread-title">${this.escapeHtml(thread.title)}</h3>
                <span class="thread-status ${statusClass}">${thread.status}</span>
            </div>
            <div class="thread-meta">
                <span>${thread.interaction_count || 0} interactions</span>
                ${thread.source_count ? `<span>${thread.source_count} sources</span>` : ''}
                ${thread.updated_at ? `<span>${new Date(thread.updated_at).toLocaleDateString()}</span>` : ''}
            </div>
            ${thread.connections && thread.connections.length > 0 ? `
                <div class="thread-connections">
                    ${thread.connections.map(c => `<span class="connection-tag">${this.escapeHtml(c)}</span>`).join('')}
                </div>
            ` : ''}
        `;
        
        div.addEventListener('click', () => {
            if (thread.id) {
                this.handleThreadClick(thread.id);
            }
        });
        
        return div;
    }
    
    /**
     * Create an insight card
     */
    static createInsightCard(insight) {
        const div = document.createElement('div');
        div.className = 'insight-card';
        div.dataset.id = insight.id;
        
        const priorityClass = `priority-${insight.priority || 'medium'}`;
        
        div.innerHTML = `
            <div class="insight-header">
                <h3 class="insight-title">${this.escapeHtml(insight.title)}</h3>
                <span class="insight-priority ${priorityClass}">${insight.priority || 'medium'}</span>
            </div>
            <div class="insight-description">
                ${this.escapeHtml(insight.description || '')}
            </div>
            ${insight.action ? `
                <div class="insight-action">
                    <strong>Action:</strong> ${this.escapeHtml(insight.action)}
                </div>
            ` : ''}
            ${insight.facts_count ? `
                <div class="insight-stats">
                    ${insight.facts_count} facts documented
                </div>
            ` : ''}
        `;
        
        div.addEventListener('click', () => {
            if (insight.id) {
                this.handleInsightClick(insight);
            }
        });
        
        return div;
    }
    
    /**
     * Create loading indicator
     */
    static createLoadingIndicator(message = 'Loading...') {
        const div = document.createElement('div');
        div.className = 'loading-indicator';
        div.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-message">${this.escapeHtml(message)}</div>
        `;
        return div;
    }
    
    /**
     * Create empty state
     */
    static createEmptyState(message = 'No data available') {
        const div = document.createElement('div');
        div.className = 'empty-state';
        div.innerHTML = `
            <div class="empty-icon">▦</div>
            <div class="empty-message">${this.escapeHtml(message)}</div>
        `;
        return div;
    }
    
    /**
     * Create error state
     */
    static createErrorState(message = 'An error occurred', retryCallback = null) {
        const div = document.createElement('div');
        div.className = 'error-state';
        div.innerHTML = `
            <div class="error-icon">⚠</div>
            <div class="error-message">${this.escapeHtml(message)}</div>
            ${retryCallback ? `
                <button class="retry-button" onclick="(${retryCallback})()">Retry</button>
            ` : ''}
        `;
        return div;
    }
    
    /**
     * Handle item click events
     */
    static handleItemClick(item) {
        // Track interaction
        if (window.State) {
            State.trackInteraction('stream', item.id, 'click');
        }
        
        // Navigate or show details
        if (item.type === 'pattern' && item.id) {
            window.location.href = `/atlas.html?pattern=${encodeURIComponent(item.id)}`;
        }
    }
    
    /**
     * Handle pattern click
     */
    static handlePatternClick(patternId) {
        window.location.href = `/atlas.html?pattern=${encodeURIComponent(patternId)}`;
    }
    
    /**
     * Handle thread click
     */
    static handleThreadClick(threadId) {
        window.location.href = `/reactor.html?thread=${encodeURIComponent(threadId)}`;
    }
    
    /**
     * Handle insight click
     */
    static handleInsightClick(insight) {
        if (insight.actionable && insight.id) {
            // Could open application layer or show details
            console.log('Insight clicked:', insight);
        }
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    static escapeHtml(text) {
        if (text == null) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Format date
     */
    static formatDate(dateString) {
        if (!dateString) return '';
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch {
            return dateString;
        }
    }
    
    /**
     * Format relative time
     */
    static formatRelativeTime(dateString) {
        if (!dateString) return '';
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diff = now - date;
            const seconds = Math.floor(diff / 1000);
            const minutes = Math.floor(seconds / 60);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);
            
            if (days > 0) return `${days}d ago`;
            if (hours > 0) return `${hours}h ago`;
            if (minutes > 0) return `${minutes}m ago`;
            return 'just now';
        } catch {
            return dateString;
        }
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Components;
}

