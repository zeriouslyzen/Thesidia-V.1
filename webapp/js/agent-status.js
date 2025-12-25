/**
 * Agent Status Component
 * Shows user's agent name and online/offline status in Nexus header
 */

class AgentStatus {
    constructor() {
        this.nameElement = document.getElementById('agent-name');
        this.indicatorElement = document.getElementById('status-indicator');
        this.updateInterval = 10000; // 10 seconds
        this.updateTimer = null;

        this.init();
    }

    async init() {
        await this.loadUserProfile();
        await this.checkStatus();
        this.startAutoUpdate();
    }

    async loadUserProfile() {
        try {
            // Try to get user profile from localStorage or API
            const savedProfile = localStorage.getItem('userProfile');
            if (savedProfile) {
                const profile = JSON.parse(savedProfile);
                this.updateName(profile.name || profile.username || 'Agent');
                return;
            }

            // Fallback: try to fetch from API
            const response = await fetch('/api/user/profile');
            if (response.ok) {
                const profile = await response.json();
                this.updateName(profile.name || profile.username || 'Agent');
                localStorage.setItem('userProfile', JSON.stringify(profile));
            } else {
                this.updateName('Agent');
            }
        } catch (error) {
            console.warn('Failed to load user profile:', error);
            this.updateName('Agent');
        }
    }

    async checkStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            if (data.ollama_status && data.thesidia_ready) {
                this.updateStatus('online');
            } else if (data.thesidia_ready) {
                this.updateStatus('api-mode');
            } else {
                this.updateStatus('offline');
            }
        } catch (error) {
            console.error('Failed to check status:', error);
            this.updateStatus('offline');
        }
    }

    updateName(name) {
        if (this.nameElement) {
            this.nameElement.textContent = name;
        }
    }

    updateStatus(status) {
        if (!this.indicatorElement) return;

        // Remove all status classes
        this.indicatorElement.classList.remove('online', 'api-mode', 'offline');

        // Add new status class
        this.indicatorElement.classList.add(status);

        // Update title for tooltip
        const statusText = {
            'online': 'Online - Ollama Connected',
            'api-mode': 'API Mode - Using Fallback',
            'offline': 'Offline'
        };
        this.indicatorElement.title = statusText[status] || 'Unknown';
    }

    startAutoUpdate() {
        this.updateTimer = setInterval(() => {
            this.checkStatus();
        }, this.updateInterval);
    }

    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    destroy() {
        this.stopAutoUpdate();
    }
}

// Initialize on page load
let agentStatus;
document.addEventListener('DOMContentLoaded', () => {
    agentStatus = new AgentStatus();
});
