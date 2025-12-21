/**
 * Chat Module
 * Handles messaging, typing animations, and conversation history.
 */

export class Chat {
    constructor(appInstance) {
        this.app = appInstance;
        this.messagesContainer = document.getElementById('messages');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.promptInput = document.getElementById('promptInput');
        this.sendBtn = document.getElementById('sendBtn');
    }

    init() {
        if (!this.promptInput || !this.sendBtn || !this.messagesContainer) {
            console.log('Chat elements not found, skipping chat init');
            return;
        }

        this.sendBtn.addEventListener('click', () => this.handleSendMessage());
        this.promptInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });

        this.setupAutoResize();
    }

    async handleSendMessage() {
        const message = this.promptInput.value.trim();
        if (!message || this.app.isProcessing) return;

        this.addMessage('user', message);
        this.promptInput.value = '';
        this.autoResizeTextarea();

        await this.app.callThesidiaAPI(message);
    }

    addMessage(type, content) {
        if (!this.messagesContainer) return;

        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}-message`;
        msgDiv.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(content)}</p>
            </div>
        `;
        this.messagesContainer.appendChild(msgDiv);
        this.scrollToBottom();
    }

    showTyping() {
        if (this.typingIndicator) this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTyping() {
        if (this.typingIndicator) this.typingIndicator.style.display = 'none';
    }

    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }

    setupAutoResize() {
        this.promptInput.addEventListener('input', () => this.autoResizeTextarea());
    }

    autoResizeTextarea() {
        this.promptInput.style.height = 'auto';
        this.promptInput.style.height = Math.min(this.promptInput.scrollHeight, 200) + 'px';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
