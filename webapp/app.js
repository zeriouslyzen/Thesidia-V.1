// Thesidia Web App - Security-First, High-End Mobile Interface

class ThesidiaApp {
    constructor() {
        // Load API configuration (supports local and remote endpoints)
        let apiConfig = { API_ENDPOINT: '/api/thesidia', STATUS_ENDPOINT: '/api/status' };
        try {
            // Try to load from api-config.js if available
            if (typeof window !== 'undefined' && window.API_CONFIG) {
                apiConfig = window.API_CONFIG;
            }
        } catch (e) {
            // Fallback to default local endpoints
        }
        
        this.apiEndpoint = apiConfig.API_ENDPOINT || '/api/thesidia'; // Backend API endpoint
        this.statusEndpoint = apiConfig.STATUS_ENDPOINT || '/api/status'; // Status endpoint
        this.conversations = [];
        this.currentConversationId = null;
        this.isProcessing = false;
        this.showThinking = false;
        this.currentFormat = 'natural'; // 'natural' or 'structured'
        this.researchDepth = 2; // 1=Quick, 2=Deep, 3=Forensic
        this.attachedFiles = []; // Store attached files
        
        // User session management
        this.userId = null;
        this.sessionId = null;
        
        this.init();
    }
    
    init() {
        this.setupUserSession();
        this.setupEventListeners();
        this.loadConversations();
        this.setupAutoResize();
        this.setupKeyboardShortcuts();
        this.checkStatus();
        this.startStatusPolling();
    }
    
    async setupUserSession() {
        // Get user session from localStorage or create new one
        this.userId = localStorage.getItem('thesidia_user_id');
        this.sessionId = localStorage.getItem('thesidia_session_id');
        
        try {
            const response = await fetch('/api/user/session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });
            
            const userData = await response.json();
            this.userId = userData.user_id;
            this.sessionId = userData.session_id;
            
            // Store in localStorage
            localStorage.setItem('thesidia_user_id', this.userId);
            localStorage.setItem('thesidia_session_id', this.sessionId);
            
            console.log('User session initialized:', { user_id: this.userId, session_id: this.sessionId });
        } catch (error) {
            console.error('Error setting up user session:', error);
        }
    }
    
    async exportConversation() {
        if (!this.userId && !this.sessionId) {
            alert('No user session found. Please refresh the page.');
            return;
        }
        
        try {
            const response = await fetch('/api/user/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });
            
            if (!response.ok) {
                throw new Error('Export failed');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `thesidia_conversation_${this.userId || 'export'}_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting conversation:', error);
            alert('Error exporting conversation. Please try again.');
        }
    }
    
    async checkStatus() {
        try {
            const response = await fetch(this.statusEndpoint);
            const data = await response.json();
            
            this.updateStatusIndicators(data);
        } catch (error) {
            console.error('Status check error:', error);
            this.updateStatusIndicators({
                ollama_status: false,
                thesidia_ready: false
            });
        }
    }
    
    updateStatusIndicators(status) {
        const ollamaStatus = document.getElementById('ollamaStatus');
        const thesidiaStatus = document.getElementById('thesidiaStatus');
        
        if (!ollamaStatus || !thesidiaStatus) {
            console.error('Status indicators not found in DOM');
            return;
        }
        
        // Ollama status
        const ollamaDot = ollamaStatus.querySelector('.status-dot');
        if (ollamaDot) {
            if (status.ollama_status) {
                ollamaDot.classList.add('online');
                ollamaDot.classList.remove('offline');
            } else {
                ollamaDot.classList.add('offline');
                ollamaDot.classList.remove('online');
            }
        }
        
        // Thesidia status
        const thesidiaDot = thesidiaStatus.querySelector('.status-dot');
        if (thesidiaDot) {
            if (status.thesidia_ready && status.ollama_status) {
                thesidiaDot.classList.add('ready');
                thesidiaDot.classList.remove('offline');
            } else {
                thesidiaDot.classList.add('offline');
                thesidiaDot.classList.remove('ready');
            }
        }
    }
    
    startStatusPolling() {
        // Check status every 5 seconds
        setInterval(() => {
            this.checkStatus();
        }, 5000);
    }
    
    setupEventListeners() {
        try {
            // Send button
            const sendBtn = document.getElementById('sendBtn');
            const promptInput = document.getElementById('promptInput');
            
            if (!sendBtn || !promptInput) {
                console.error('Critical elements not found: sendBtn or promptInput');
                return;
            }
            
            sendBtn.addEventListener('click', () => this.sendMessage());
            promptInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            // Menu toggle
            const menuBtn = document.getElementById('menuBtn');
            const closeSidebar = document.getElementById('closeSidebar');
            const overlay = document.getElementById('overlay');
            
            if (menuBtn) menuBtn.addEventListener('click', () => this.toggleSidebar());
            if (closeSidebar) closeSidebar.addEventListener('click', () => this.toggleSidebar());
            if (overlay) overlay.addEventListener('click', () => this.toggleSidebar());
            
            // New chat
            const newChatBtn = document.getElementById('newChatBtn');
            if (newChatBtn) newChatBtn.addEventListener('click', () => this.newConversation());
            
            const exportBtn = document.getElementById('exportBtn');
            if (exportBtn) exportBtn.addEventListener('click', () => this.exportConversation());
        } catch (error) {
            console.error('Error setting up event listeners:', error);
        }
        
        // Thinking toggle
        const thinkingToggle = document.getElementById('showThinkingToggle');
        if (thinkingToggle) {
            thinkingToggle.addEventListener('change', (e) => {
                this.showThinking = e.target.checked;
                const thinkingBtn = document.getElementById('thinkingBtn');
                if (thinkingBtn) {
                    if (this.showThinking) {
                        thinkingBtn.classList.add('active');
                    } else {
                        thinkingBtn.classList.remove('active');
                    }
                }
            });
        }
        
        // Deep research toggle
        const deepResearchToggle = document.getElementById('deepResearchToggle');
        if (deepResearchToggle) {
            deepResearchToggle.addEventListener('change', (e) => {
                this.deepResearchMode = e.target.checked;
                // Disable auto-detect when manual mode is enabled
                if (this.deepResearchMode) {
                    const autoDetectToggle = document.getElementById('autoDetectToggle');
                    if (autoDetectToggle) {
                        autoDetectToggle.checked = false;
                        this.autoDetect = false;
                    }
                }
            });
        }
        
        // Format selector
        const formatNatural = document.getElementById('formatNatural');
        const formatStructured = document.getElementById('formatStructured');
        if (formatNatural) {
            formatNatural.addEventListener('click', () => {
                this.currentFormat = 'natural';
                formatNatural.classList.add('active');
                formatStructured?.classList.remove('active');
            });
        }
        if (formatStructured) {
            formatStructured.addEventListener('click', () => {
                this.currentFormat = 'structured';
                formatStructured.classList.add('active');
                formatNatural?.classList.remove('active');
            });
        }
        
        // Research depth slider
        const researchDepth = document.getElementById('researchDepth');
        if (researchDepth) {
            researchDepth.addEventListener('input', (e) => {
                this.researchDepth = parseInt(e.target.value);
                // Update depth labels (both selectors for compatibility)
                document.querySelectorAll('.depth-labels span, .depth-label-item').forEach((item, index) => {
                    if (index + 1 === this.researchDepth) {
                        item.classList.add('active');
                    } else {
                        item.classList.remove('active');
                    }
                });
            });
        }
        
        // Template chips
        document.querySelectorAll('.template-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                const template = e.target.dataset.template;
                const templates = {
                    'genesis': 'What is the true story of genesis from the bible',
                    'power': 'Analyze the power structures behind modern institutions',
                    'pattern': 'What patterns connect ancient texts to modern systems',
                    'ancient': 'Decode the hidden meanings in ancient texts'
                };
                if (templates[template]) {
                    promptInput.value = templates[template];
                    promptInput.focus();
                    this.autoResizeTextarea(promptInput);
                }
            });
        });
        
        // Toggle thinking display
        const toggleThinking = document.getElementById('toggleThinking');
        if (toggleThinking) {
            toggleThinking.addEventListener('click', () => {
                const thinkingSteps = document.getElementById('thinkingSteps');
                if (thinkingSteps) {
                    if (thinkingSteps.style.display === 'none') {
                        thinkingSteps.style.display = 'block';
                        toggleThinking.textContent = 'Hide';
                    } else {
                        thinkingSteps.style.display = 'none';
                        toggleThinking.textContent = 'Show';
                    }
                }
            });
        }
        
        // Auto-resize textarea
        promptInput.addEventListener('input', () => this.autoResizeTextarea(promptInput));
        
        // Advanced options toggle
        const advancedToggle = document.getElementById('advancedToggle');
        const advancedOptions = document.getElementById('advancedOptions');
        if (advancedToggle && advancedOptions) {
            advancedToggle.addEventListener('click', () => {
                const isVisible = advancedOptions.style.display !== 'none';
                advancedOptions.style.display = isVisible ? 'none' : 'block';
                advancedToggle.classList.toggle('active', !isVisible);
            });
        }
        
        // File upload
        const fileInput = document.getElementById('fileInput');
        const attachBtn = document.getElementById('attachBtn');
        const attachedFiles = document.getElementById('attachedFiles');
        if (attachBtn && fileInput) {
            attachBtn.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', (e) => {
                this.handleFileUpload(e.target.files, attachedFiles);
            });
        }
        
        // Format selector (in advanced options)
        const formatNatural = document.getElementById('formatNatural');
        const formatStructured = document.getElementById('formatStructured');
        if (formatNatural && formatStructured) {
            formatNatural.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.currentFormat = 'natural';
                formatNatural.classList.add('active');
                formatStructured.classList.remove('active');
            });
            formatStructured.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.currentFormat = 'structured';
                formatStructured.classList.add('active');
                formatNatural.classList.remove('active');
            });
        }
        
        // Research depth slider
        const researchDepth = document.getElementById('researchDepth');
        if (researchDepth) {
            researchDepth.addEventListener('input', (e) => {
                this.researchDepth = parseInt(e.target.value);
                document.querySelectorAll('.depth-labels span').forEach((span, index) => {
                    span.classList.toggle('active', index + 1 === this.researchDepth);
                });
            });
        }
    }
    
    handleFileUpload(files, container) {
        if (!files || files.length === 0) return;
        
        container.style.display = 'flex';
        container.innerHTML = '';
        
        Array.from(files).forEach((file, index) => {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'attached-file';
            fileDiv.innerHTML = `
                <span>${file.name}</span>
                <button onclick="this.parentElement.remove(); if(document.getElementById('attachedFiles').children.length === 0) document.getElementById('attachedFiles').style.display = 'none';" aria-label="Remove file">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            `;
            container.appendChild(fileDiv);
        });
        
        // Store files for sending
        this.attachedFiles = Array.from(files);
    }
    
    setupAutoResize() {
        const promptInput = document.getElementById('promptInput');
        promptInput.addEventListener('input', () => {
            promptInput.style.height = 'auto';
            promptInput.style.height = Math.min(promptInput.scrollHeight, 200) + 'px';
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Cmd/Ctrl + K for new chat
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.newConversation();
            }
            
            // Escape to close sidebar
            if (e.key === 'Escape') {
                this.closeSidebar();
            }
        });
    }
    
    async sendMessage() {
        const promptInput = document.getElementById('promptInput');
        const message = promptInput.value.trim();
        
        if (!message || this.isProcessing) return;
        
        // Clear input
        promptInput.value = '';
        promptInput.style.height = 'auto';
        
        // Add user message
        this.addMessage('user', message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Disable send button
        this.isProcessing = true;
        this.updateSendButton();
        
        try {
            // Send to backend (streaming handles UI updates)
            await this.callThesidiaAPI(message);
            
            // Hide typing indicator (streaming will handle this)
            this.hideTypingIndicator();
            
        } catch (error) {
            console.error('Error:', error);
            this.hideTypingIndicator();
            this.addMessage('thesidia', 'Error: Could not process request. Please try again.');
        } finally {
            this.isProcessing = false;
            this.updateSendButton();
        }
    }
    
    async callThesidiaAPI(message) {
        // Security: Sanitize input
        let sanitizedMessage = this.sanitizeInput(message);
        
        // Format and depth are now controlled by UI, not auto-detection
        
        // Use streaming by default
        return new Promise((resolve, reject) => {
            // Create message element for streaming
            const messagesContainer = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message thesidia';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            const textElement = document.createElement('p');
            textElement.textContent = '';
            contentDiv.appendChild(textElement);
            
            messageDiv.appendChild(contentDiv);
            messagesContainer.appendChild(messageDiv);
            
            // Progress indicator - Better styling
            const progressDiv = document.createElement('div');
            progressDiv.className = 'progress-indicator';
            progressDiv.style.display = 'none';
            progressDiv.style.marginTop = '12px';
            messageDiv.appendChild(progressDiv);
            
            // Thinking indicator (if enabled)
            let thinkingDiv = null;
            if (this.showThinking) {
                thinkingDiv = document.createElement('div');
                thinkingDiv.className = 'thinking-indicator';
                thinkingDiv.style.display = 'none';
                thinkingDiv.style.marginTop = '8px';
                messageDiv.appendChild(thinkingDiv);
            }
            
            // Use fetch - handle both streaming and non-streaming
            const useStreaming = true; // Enable streaming for better UX
            fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: sanitizedMessage,
                    conversation_id: this.currentConversationId,
                    show_thinking: this.showThinking,
                    format: this.currentFormat, // 'natural' or 'structured'
                    research_depth: this.researchDepth, // 1=Quick, 2=Deep, 3=Forensic
                    stream: useStreaming,
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            }).then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                // Check content type to determine if streaming or JSON
                const contentType = response.headers.get('content-type') || '';
                
                if (useStreaming && contentType.includes('text/event-stream')) {
                    // Handle streaming response (SSE)
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = '';
                    let fullResponse = '';
                    let currentEvent = null;
                    
                    const readChunk = () => {
                        reader.read().then(({ done, value }) => {
                            if (done) {
                                // Complete
                                this.hideTypingIndicator();
                                if (progressDiv.parentNode) {
                                    progressDiv.style.display = 'none';
                                }
                                this.scrollToBottom();
                                this.saveConversation(sanitizedMessage, fullResponse);
                                resolve(fullResponse);
                                return;
                            }
                            
                            buffer += decoder.decode(value, { stream: true });
                            const lines = buffer.split('\n');
                            buffer = lines.pop() || ''; // Keep incomplete line in buffer
                            
                            for (const line of lines) {
                                if (line.trim() === '') continue;
                                
                                if (line.startsWith('event: ')) {
                                    currentEvent = line.substring(7).trim();
                                    continue;
                                }
                                
                                if (line.startsWith('data: ')) {
                                    try {
                                        const data = JSON.parse(line.substring(6));
                                        
                                        if (data.phase === 'progress' || currentEvent === 'progress') {
                                            // Update progress indicator with better visibility
                                            progressDiv.style.display = 'block';
                                            progressDiv.textContent = `${data.message} (${Math.round(data.progress)}%)`;
                                            progressDiv.className = 'progress-indicator active';
                                            this.scrollToBottom();
                                        } else if (data.text || currentEvent === 'chunk') {
                                            // Stream text chunk - real-time token streaming
                                            const chunk = data.text || '';
                                            textElement.textContent += chunk;
                                            this.scrollToBottom();
                                            fullResponse += chunk;
                                            
                                            // Hide progress when streaming starts
                                            if (chunk.length > 0 && progressDiv.style.display !== 'none') {
                                                progressDiv.style.display = 'none';
                                            }
                                        } else if (currentEvent === 'thinking' || data.thinking) {
                                            // Show thinking steps
                                            if (this.showThinking) {
                                                this.displayThinkingStep(data.step || 'thinking', data.message || data.thinking);
                                                
                                                // Also show inline thinking indicator
                                                if (thinkingDiv) {
                                                    thinkingDiv.style.display = 'block';
                                                    thinkingDiv.textContent = `${data.message || data.thinking}`;
                                                }
                                            }
                                        } else if (data.phase === 'complete' || currentEvent === 'complete') {
                                            // Complete
                                            progressDiv.style.display = 'none';
                                            this.hideTypingIndicator();
                                        } else if (data.error || currentEvent === 'error') {
                                            // Error
                                            throw new Error(data.message || data.error || 'Unknown error');
                                        }
                                    } catch (e) {
                                        console.error('Error parsing SSE data:', e, line);
                                    }
                                    currentEvent = null;
                                }
                            }
                            
                            readChunk();
                        }).catch(err => {
                            console.error('Streaming error:', err);
                            this.hideTypingIndicator();
                            if (progressDiv.parentNode) {
                                progressDiv.style.display = 'none';
                            }
                            reject(err);
                        });
                    };
                    
                    readChunk();
                } else {
                    // Handle non-streaming JSON response
                    return response.json().then(data => {
                        this.hideTypingIndicator();
                        if (progressDiv.parentNode) {
                            progressDiv.style.display = 'none';
                        }
                        
                        const responseText = data.response || data.message || 'No response';
                        textElement.textContent = responseText;
                        this.scrollToBottom();
                        this.saveConversation(sanitizedMessage, responseText);
                        resolve(responseText);
                    });
                }
            }).catch(err => {
                console.error('Fetch error:', err);
                this.hideTypingIndicator();
                if (progressDiv.parentNode) {
                    progressDiv.style.display = 'none';
                }
                textElement.textContent = `Error: ${err.message}`;
                reject(err);
            });
        });
    }
    
    async callThesidiaAPIFallback(message) {
        // Fallback non-streaming method
        const response = await fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_id: this.currentConversationId,
                show_thinking: this.showThinking,
                format: this.currentFormat, // 'natural' or 'structured'
                research_depth: this.researchDepth, // 1=Quick, 2=Deep, 3=Forensic
                stream: false,
                user_id: this.userId,
                session_id: this.sessionId
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display thinking steps if available
        if (data.thinking_steps && data.thinking_steps.length > 0) {
            this.displayThinkingSteps(data.thinking_steps);
        }
        
        return data.response || data.message || 'No response received';
    }
    
    displayThinkingSteps(steps) {
        const thinkingContent = document.getElementById('thinkingContent');
        const thinkingSteps = document.getElementById('thinkingSteps');
        
        if (!thinkingContent || !thinkingSteps) return;
        
        thinkingContent.innerHTML = '';
        
        steps.forEach((step, index) => {
            const stepDiv = document.createElement('div');
            stepDiv.className = 'thinking-step';
            stepDiv.style.animationDelay = `${index * 0.1}s`;
            
            stepDiv.innerHTML = `
                <div class="thinking-step-header">${this.escapeHtml(step.step)}</div>
                <div class="thinking-step-detail">${this.escapeHtml(step.detail)}</div>
                <div class="thinking-step-time">${new Date(step.timestamp).toLocaleTimeString()}</div>
            `;
            
            thinkingContent.appendChild(stepDiv);
        });
        
        thinkingSteps.style.display = 'block';
        this.scrollToBottom();
    }
    
    displayThinkingStep(step, message) {
        // Display real-time thinking step
        const thinkingContent = document.getElementById('thinkingContent');
        const thinkingSteps = document.getElementById('thinkingSteps');
        
        if (!thinkingContent || !thinkingSteps || !this.showThinking) return;
        
        // Show thinking steps container
        thinkingSteps.style.display = 'block';
        
        // Add or update thinking step
        const stepDiv = document.createElement('div');
        stepDiv.className = 'thinking-step';
        stepDiv.innerHTML = `
            <div class="thinking-step-header">${this.escapeHtml(step)}</div>
            <div class="thinking-step-detail">${this.escapeHtml(message)}</div>
            <div class="thinking-step-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        thinkingContent.appendChild(stepDiv);
        this.scrollToBottom();
    }
    
    sanitizeInput(input) {
        // Basic sanitization - remove potentially dangerous characters
        return input
            .replace(/[<>]/g, '') // Remove < and >
            .trim()
            .slice(0, 10000); // Limit length
    }
    
    addMessageWithTyping(type, text, speed = 15) {
        // Create message element
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const textElement = document.createElement('p');
        textElement.textContent = '';
        contentDiv.appendChild(textElement);
        
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Remove system message if exists
        const systemMessage = messagesContainer.querySelector('.system-message');
        if (systemMessage && type !== 'system') {
            systemMessage.remove();
        }
        
        // Type out the text letter by letter
        let index = 0;
        const typingInterval = setInterval(() => {
            if (index < text.length) {
                // Handle special characters and formatting
                if (text[index] === '\n') {
                    textElement.innerHTML += '<br>';
                } else if (text[index] === '*' && index + 1 < text.length && text[index + 1] === '*') {
                    // Handle bold markdown
                    let boldEnd = text.indexOf('**', index + 2);
                    if (boldEnd !== -1) {
                        textElement.innerHTML += '<strong>' + text.substring(index + 2, boldEnd) + '</strong>';
                        index = boldEnd + 1;
                    } else {
                        textElement.textContent += text[index];
                    }
                } else {
                    textElement.textContent += text[index];
                }
                index++;
                // Auto-scroll as text appears
                this.scrollToBottom();
            } else {
                clearInterval(typingInterval);
            }
        }, speed);
    }
    
    addMessage(type, content) {
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Format content (support markdown-like formatting)
        const formattedContent = this.formatMessage(content);
        contentDiv.innerHTML = formattedContent;
        
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Remove system message if exists
        const systemMessage = messagesContainer.querySelector('.system-message');
        if (systemMessage && type !== 'system') {
            systemMessage.remove();
        }
    }
    
    formatMessage(content) {
        // Simple formatting - convert code blocks, preserve line breaks
        return content
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }
    
    showTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        typingIndicator.style.display = 'block';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        typingIndicator.style.display = 'none';
    }
    
    scrollToBottom() {
        const chatContainer = document.getElementById('chatContainer');
        setTimeout(() => {
            chatContainer.scrollTo({
                top: chatContainer.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }
    
    updateSendButton() {
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.disabled = this.isProcessing;
    }
    
    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        
        sidebar.classList.toggle('open');
        overlay.classList.toggle('show');
    }
    
    closeSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        
        sidebar.classList.remove('open');
        overlay.classList.remove('show');
    }
    
    newConversation() {
        this.currentConversationId = null;
        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = `
            <div class="message system-message">
                <div class="message-content">
                    <p>Execute directives directly. Build websites, devices, blueprints, training programs.</p>
                </div>
            </div>
        `;
        this.closeSidebar();
    }
    
    saveConversation(userMessage, thesidiaResponse) {
        if (!this.currentConversationId) {
            this.currentConversationId = Date.now().toString();
        }
        
        const conversation = {
            id: this.currentConversationId,
            title: userMessage.slice(0, 50),
            preview: thesidiaResponse.slice(0, 100),
            timestamp: Date.now(),
            messages: [
                { type: 'user', content: userMessage },
                { type: 'thesidia', content: thesidiaResponse }
            ]
        };
        
        // Save to localStorage (in production, use secure backend)
        this.conversations.unshift(conversation);
        this.conversations = this.conversations.slice(0, 50); // Keep last 50
        localStorage.setItem('thesidia_conversations', JSON.stringify(this.conversations));
        
        this.updateConversationsList();
    }
    
    loadConversations() {
        try {
            const stored = localStorage.getItem('thesidia_conversations');
            if (stored) {
                this.conversations = JSON.parse(stored);
                this.updateConversationsList();
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }
    
    updateConversationsList() {
        const listContainer = document.getElementById('conversationsList');
        listContainer.innerHTML = '';
        
        this.conversations.forEach(conv => {
            const item = document.createElement('div');
            item.className = 'conversation-item';
            if (conv.id === this.currentConversationId) {
                item.classList.add('active');
            }
            
            item.innerHTML = `
                <div class="conversation-title">${this.escapeHtml(conv.title)}</div>
                <div class="conversation-preview">${this.escapeHtml(conv.preview)}</div>
            `;
            
            item.addEventListener('click', () => this.loadConversation(conv.id));
            listContainer.appendChild(item);
        });
    }
    
    loadConversation(conversationId) {
        const conversation = this.conversations.find(c => c.id === conversationId);
        if (!conversation) return;
        
        this.currentConversationId = conversationId;
        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = '';
        
        conversation.messages.forEach(msg => {
            this.addMessage(msg.type, msg.content);
        });
        
        this.updateConversationsList();
        this.closeSidebar();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
}

// Initialize app when DOM is ready
try {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            try {
                window.thesidiaApp = new ThesidiaApp();
                console.log('Thesidia app initialized');
            } catch (error) {
                console.error('Error initializing Thesidia app:', error);
                // Show error message to user
                const app = document.getElementById('app');
                if (app) {
                    app.innerHTML = `
                        <div style="padding: 20px; color: #fff; background: #000;">
                            <h1>Error Loading Thesidia</h1>
                            <p>There was an error initializing the app. Please check the console for details.</p>
                            <p>Error: ${error.message}</p>
                        </div>
                    `;
                }
            }
        });
    } else {
        try {
            window.thesidiaApp = new ThesidiaApp();
            console.log('Thesidia app initialized');
        } catch (error) {
            console.error('Error initializing Thesidia app:', error);
            const app = document.getElementById('app');
            if (app) {
                app.innerHTML = `
                    <div style="padding: 20px; color: #fff; background: #000;">
                        <h1>Error Loading Thesidia</h1>
                        <p>There was an error initializing the app. Please check the console for details.</p>
                        <p>Error: ${error.message}</p>
                    </div>
                `;
            }
        }
    }
} catch (error) {
    console.error('Fatal error:', error);
}

// Service Worker for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Service worker registration can be added here
    });
}

