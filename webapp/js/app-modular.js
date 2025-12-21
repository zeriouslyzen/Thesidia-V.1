/**
 * Thesidia App - Refactored Main Entry Point
 */

import { ComponentLoader } from './modules/loader.js';
import { Navigation } from './modules/navigation.js';
import { Chat } from './modules/chat.js';
import { Effects } from './modules/effects.js';
import { StreamPage } from './modules/stream.js';
import { ProfilePage } from './modules/profile.js';

class ThesidiaApp {
    constructor() {
        this.apiEndpoint = '/api/thesidia';
        this.statusEndpoint = '/api/status';
        this.userId = localStorage.getItem('thesidia_user_id');
        this.sessionId = localStorage.getItem('thesidia_session_id');
        this.isProcessing = false;

        this.init();
    }

    async init() {
        // 1. Load Components
        const loaded = await ComponentLoader.loadSharedComponents();
        if (!loaded) console.error('Failed to load shared components');

        // 2. Initialize Core Modules (Navigation is on all pages)
        this.navigation = new Navigation(this);
        this.navigation.init();

        // 3. Initialize Page-Specific Modules
        const path = window.location.pathname;

        // Chat module (Home/Index)
        if (path === '/' || path.includes('index.html')) {
            this.chat = new Chat(this);
            this.chat.init();
        }

        // Stream page
        if (path.includes('stream.html')) {
            this.stream = new StreamPage(this);
            this.stream.init();
        }

        // Profile page
        if (path.includes('profile.html')) {
            this.profile = new ProfilePage(this);
            // ProfilePage.init() is called in its constructor for now, 
            // but we can ensure it has the app instance.
        }

        // 4. Initialize Global Effects
        Effects.initNanoDust();
        Effects.initAstrologicalTime();
        Effects.initStarNotepad();

        // 5. Setup/Sync Session
        await this.setupUserSession();

        console.log('Thesidia App Initialized for path:', path);
    }

    async setupUserSession() {
        try {
            const response = await fetch('/api/user/session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: this.userId, session_id: this.sessionId })
            });
            const data = await response.json();
            this.userId = data.user_id;
            this.sessionId = data.session_id;
            localStorage.setItem('thesidia_user_id', this.userId);
            localStorage.setItem('thesidia_session_id', this.sessionId);
        } catch (error) {
            console.error('Session error:', error);
        }
    }

    async callThesidiaAPI(message) {
        this.isProcessing = true;
        this.chat.showTyping();

        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message,
                    user_id: this.userId,
                    session_id: this.sessionId,
                    stream: false // For simplicity in this refactor step
                })
            });

            const data = await response.json();
            this.chat.hideTyping();
            this.chat.addMessage('thesidia', data.response || 'No response');
        } catch (error) {
            this.chat.hideTyping();
            this.chat.addMessage('system', 'Error connecting to Thesidia.');
        } finally {
            this.isProcessing = false;
        }
    }
}

// Global instance
window.addEventListener('DOMContentLoaded', () => {
    window.thesidiaApp = new ThesidiaApp();
});
