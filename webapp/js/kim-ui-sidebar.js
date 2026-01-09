/**
 * KIM Sidebar UI Logic - Modular Right Sidebar
 * Wrapped in IIFE to prevent global namespace pollution
 */

(function() {
    'use strict';
    
    // Check if required dependencies are available
    if (typeof io === 'undefined') {
        console.error('KIM: Socket.IO not loaded');
        return;
    }
    
    if (typeof KIMCrypto === 'undefined') {
        console.error('KIM: KIMCrypto not loaded');
        return;
    }
    
    // Initialize KIM variables in local scope
    const socket = io('/kim');
    const crypto = new KIMCrypto();
    let myUserId = null;
    let currentRoom = 'global-relay';
    let knownUsers = {};
    let currentState = 'login'; // 'login' or 'main'
    let heartbeatInterval = null;
    let katanxAuth = null; // Will store Katanx auth info if available
    
    // DOM Elements - check for existence
    const kimPanel = document.getElementById('kimSidebarPanel');
    const kimToggleBtn = document.getElementById('kimToggleBtn');
    const kimPanelClose = document.getElementById('kimPanelClose');
    const kimLoginState = document.getElementById('kim-login-state');
    const kimMainState = document.getElementById('kim-main-state');
    const kimConnectBtn = document.getElementById('kim-connect-btn');
    const kimNicknameInput = document.getElementById('kim-nickname-input');
    const kimMessageInput = document.getElementById('kim-message-input');
    const kimSendBtn = document.getElementById('kim-send-btn');
    const kimMessagesFeed = document.getElementById('kimMessagesFeed');
    const kimUsersList = document.getElementById('kimUsersList');
    const kimCurrentRoomName = document.getElementById('kim-current-room-name');
    const kimConversationsList = document.getElementById('kimConversationsList');
    
    // Early return if essential elements don't exist
    if (!kimPanel) {
        console.log('KIM: Panel element not found, KIM disabled');
        return;
    }
    
    // State Management
function setState(state) {
    if (!kimLoginState || !kimMainState) {
        console.error('State elements not found');
        return;
    }
    
    if (state === 'login') {
        kimLoginState.classList.add('active');
        kimLoginState.classList.remove('hidden');
        kimMainState.classList.remove('active');
        kimMainState.classList.add('hidden');
        currentState = 'login';
    } else if (state === 'main') {
        kimLoginState.classList.remove('active');
        kimLoginState.classList.add('hidden');
        kimMainState.classList.add('active');
        kimMainState.classList.remove('hidden');
        currentState = 'main';
    }
}

// Panel Toggle - Use safe integration wrapper if available
function togglePanel() {
    if (window.KIMIntegration && window.KIMIntegration.toggle) {
        window.KIMIntegration.toggle();
    } else {
        // Fallback to direct manipulation
        if (kimPanel) {
            kimPanel.classList.toggle('open');
        }
        if (kimToggleBtn) {
            kimToggleBtn.classList.toggle('active');
        }
    }
}

function closePanel() {
    if (window.KIMIntegration && window.KIMIntegration.close) {
        window.KIMIntegration.close();
    } else {
        // Fallback to direct manipulation
        if (kimPanel) {
            kimPanel.classList.remove('open');
        }
        if (kimToggleBtn) {
            kimToggleBtn.classList.remove('active');
        }
    }
}

// Initialize - panel starts closed (wait for DOM)
// Use safe integration if available, otherwise initialize directly
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (kimPanel && !window.KIMIntegration) {
            kimPanel.classList.remove('open');
            kimPanel.style.visibility = 'hidden';
        }
    });
} else {
    if (kimPanel && !window.KIMIntegration) {
        kimPanel.classList.remove('open');
        kimPanel.style.visibility = 'hidden';
    }
}

// Only set up direct handlers if safe integration wrapper is not available
if (!window.KIMIntegration) {
    if (kimToggleBtn) {
        kimToggleBtn.addEventListener('click', togglePanel);
    }
    
    if (kimPanelClose) {
        kimPanelClose.addEventListener('click', closePanel);
    }
    
    // Close on Escape (only if safe wrapper doesn't handle it)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && kimPanel && kimPanel.classList.contains('open')) {
            closePanel();
        }
    });
}

// Try to load Katanx auth info if available
window.addEventListener('DOMContentLoaded', async () => {
    // Check for Katanx auth in localStorage
    try {
        const authData = localStorage.getItem('katanx_auth');
        if (authData) {
            katanxAuth = JSON.parse(authData);
            console.log("Katanx auth found:", katanxAuth);
        }
    } catch (e) {
        console.log("No Katanx auth available");
    }
    
    const savedKey = await crypto.loadKeyPair();
    if (savedKey) {
        console.log("Loaded persisted keys from IndexedDB");
    }
});

// Connection
if (kimConnectBtn) {
    kimConnectBtn.addEventListener('click', async () => {
        const nickname = kimNicknameInput.value.trim();
        if (!nickname) {
            alert("Please enter your name");
            return;
        }

        kimConnectBtn.innerText = "Connecting...";
        kimConnectBtn.disabled = true;

        try {
            let publicKey = await crypto.loadKeyPair();
            if (!publicKey) {
                publicKey = await crypto.generateKeyPair();
                console.log("Keys Generated");
            } else {
                console.log("Keys Loaded from IndexedDB");
            }

            // Prepare registration data with optional Katanx auth
            const registrationData = {
                nickname: nickname,
                publicKey: publicKey
            };
            
            // Add Katanx auth if available
            if (katanxAuth) {
                registrationData.katanxToken = katanxAuth.token;
                registrationData.katanxUserId = katanxAuth.user_id;
            }

            const res = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(registrationData)
            });

            if (!res.ok) {
                const errorText = await res.text();
                throw new Error(`Registration failed: ${res.status} ${errorText}`);
            }

            const data = await res.json();
            console.log("Registration response:", data);
            
            if (data.status === 'registered') {
                myUserId = data.userId;
                console.log("User registered successfully:", myUserId);
                
                // Reset button state
                kimConnectBtn.innerText = "Connect";
                kimConnectBtn.disabled = false;
                
                // Switch to main state
                setState('main');
                
                // Initialize enhanced features
                initializeEnhancedFeatures();

                // Start presence system
                startPresenceSystem();
                
                // Join global room and load history
                socket.emit('join', { room: 'global-relay' });
                loadMessageHistory('global-relay');
                loadUsers();
            } else {
                throw new Error(`Registration failed: ${data.error || 'Unknown error'}`);
            }

        } catch (e) {
            console.error("KIM Init Error:", e);
            alert("Connection failed: " + (e.message || "Please try again."));
            kimConnectBtn.innerText = "Connect";
            kimConnectBtn.disabled = false;
        }
    });
}

// User Management
async function loadUsers() {
    const res = await fetch('/api/users');
    const users = await res.json();
    kimUsersList.innerHTML = '';

    if (users.length === 0 || users.filter(u => u.userId !== myUserId).length === 0) {
        kimUsersList.innerHTML = '<div class="kim-empty-state">No one online yet</div>';
        return;
    }

    for (const u of users) {
        if (u.userId === myUserId) continue;

        knownUsers[u.userId] = u;

        let peerKeyJWK = await crypto.loadPeerPublicKey(u.userId);
        if (!peerKeyJWK) {
            peerKeyJWK = u.publicKey;
        }
        
        try {
            const peerKey = await crypto.importPeerPublicKey(peerKeyJWK);
            await crypto.deriveSecretKey(peerKey, u.userId);

            // Remove empty state if it exists
            const emptyState = kimUsersList.querySelector('.kim-empty-state');
            if (emptyState) {
                emptyState.remove();
            }
            
            const userItem = document.createElement('div');
            userItem.className = 'kim-user-item';
            userItem.dataset.userId = u.userId;
            
            // Get status for status dot
            const status = u.status || 'online';
            const statusClass = `status-${status}`;
            
            userItem.innerHTML = `
                <div class="kim-user-status-dot ${statusClass}"></div>
                <span class="kim-user-name">${escapeHtml(u.displayName || u.nickname)}</span>
            `;
            userItem.addEventListener('click', () => {
                // Update active states
                document.querySelectorAll('.kim-conversation-item').forEach(item => item.classList.remove('active'));
                document.querySelectorAll('.kim-user-item').forEach(item => item.classList.remove('active'));
                userItem.classList.add('active');
                startDirectMessage(u.userId, u.displayName || u.nickname);
            });
            kimUsersList.appendChild(userItem);

        } catch (e) {
            console.error(`Failed to handshake with ${u.nickname}`, e);
        }
    }
}

// Messaging
function startDirectMessage(userId, nickname) {
    const roomName = [myUserId, userId].sort().join('_');
    currentRoom = roomName;
    kimCurrentRoomName.innerText = nickname;
    kimMessagesFeed.innerHTML = `<div class="kim-system-message">Loading conversation...</div>`;
    socket.emit('join', { room: roomName });
    loadMessageHistory(roomName);
}

// Load message history for a room
async function loadMessageHistory(roomId) {
    try {
        const res = await fetch(`/api/kim/messages/${roomId}?limit=50&offset=0`);
        if (!res.ok) {
            console.error("Failed to load message history");
            return;
        }
        
        const data = await res.json();
        const messages = data.messages || [];
        
        // Clear current feed
        kimMessagesFeed.innerHTML = '';
        
        if (messages.length === 0) {
            kimMessagesFeed.innerHTML = `<div class="kim-system-message">No messages yet</div>`;
            return;
        }
        
        // Decrypt and display messages
        for (const msg of messages) {
            let decText = "[Message]";
            try {
                if (msg.mode === 'CLEAR') {
                    decText = atob(msg.encrypted_content);
                } else {
                    decText = await crypto.decryptMessage({
                        iv: msg.iv,
                        ciphertext: msg.encrypted_content,
                        mode: msg.mode
                    }, msg.sender_id);
                }
            } catch (e) {
                console.error("Decrypt error for history:", e);
                decText = "[Unable to read message]";
            }
            
            const isSelf = msg.sender_id === myUserId;
            let senderName = "Unknown";
            if (knownUsers[msg.sender_id]) {
                senderName = knownUsers[msg.sender_id].nickname;
            } else if (isSelf) {
                senderName = "You";
            }
            
            // Load read receipts and reactions
            const readReceipts = await loadReadReceipts(msg.message_id);
            const reactions = await loadReactions(msg.message_id);
            
            addMessageToFeedHelper(decText, isSelf, senderName, msg.message_id, readReceipts, reactions, msg.parent_message_id, msg.edited);
        }
        
        // Scroll to bottom
        kimMessagesFeed.scrollTop = kimMessagesFeed.scrollHeight;
    } catch (e) {
        console.error("Error loading message history:", e);
    }
}

// Presence System
function startPresenceSystem() {
    // Send heartbeat every 30 seconds
    heartbeatInterval = setInterval(() => {
        if (myUserId) {
            socket.emit('heartbeat', { userId: myUserId });
        }
    }, 30000);
    
    // Listen for presence updates
    socket.on('presence_update', (data) => {
        const userId = data.userId;
        if (knownUsers[userId]) {
            knownUsers[userId].status = data.status;
            knownUsers[userId].statusMessage = data.statusMessage;
            knownUsers[userId].lastSeen = data.lastSeen;
            
            // Update UI if user is in buddy list
            const userItem = document.querySelector(`[data-userId="${userId}"]`);
            if (userItem) {
                const statusDot = userItem.querySelector('.kim-user-status-dot');
                if (statusDot) {
                    statusDot.className = 'kim-user-status-dot';
                    statusDot.classList.add(`status-${data.status}`);
                }
            }
        }
    });
}

// Update user status
function updateUserStatus(status, statusMessage = null) {
    if (!myUserId) return;
    
    socket.emit('presence_update', {
        userId: myUserId,
        status: status,
        statusMessage: statusMessage
    });
}

// Status message editor
const kimStatusEditor = document.getElementById('kim-status-editor');
const kimStatusPresets = document.querySelectorAll('.kim-status-preset');
const kimStatusMessageInput = document.getElementById('kim-status-message-input');
const kimStatusSaveBtn = document.getElementById('kim-status-save-btn');

if (kimStatusPresets.length > 0) {
    kimStatusPresets.forEach(preset => {
        preset.addEventListener('click', () => {
            kimStatusPresets.forEach(p => p.classList.remove('active'));
            preset.classList.add('active');
        });
    });
}

if (kimStatusSaveBtn) {
    kimStatusSaveBtn.addEventListener('click', () => {
        const activePreset = document.querySelector('.kim-status-preset.active');
        const status = activePreset ? activePreset.dataset.status : 'online';
        const statusMessage = kimStatusMessageInput.value.trim() || null;
        
        updateUserStatus(status, statusMessage);
        
        if (kimStatusEditor) {
            kimStatusEditor.classList.add('hidden');
        }
    });
}

// Global chat handler
const globalItem = kimConversationsList.querySelector('[data-room="global"]');
if (globalItem) {
    globalItem.addEventListener('click', () => {
        // Update active states
        document.querySelectorAll('.kim-conversation-item').forEach(item => item.classList.remove('active'));
        document.querySelectorAll('.kim-user-item').forEach(item => item.classList.remove('active'));
        globalItem.classList.add('active');
        
        currentRoom = 'global-relay';
        kimCurrentRoomName.innerText = "General";
        kimMessagesFeed.innerHTML = `<div class="kim-system-message">Loading...</div>`;
        socket.emit('join', { room: 'global-relay' });
        loadMessageHistory('global-relay');
    });
}

// Sending
if (kimSendBtn) {
    kimSendBtn.addEventListener('click', sendMessage);
}

// Typing indicators
let typingTimeout = null;
let isTyping = false;

if (kimMessageInput) {
    kimMessageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
            stopTyping();
        } else {
            startTyping();
        }
    });
    
    kimMessageInput.addEventListener('input', () => {
        if (kimMessageInput.value.trim()) {
            startTyping();
        } else {
            stopTyping();
        }
    });
}

function startTyping() {
    if (!isTyping && currentRoom) {
        isTyping = true;
        socket.emit('typing_start', {
            room: currentRoom,
            userId: myUserId
        });
    }
    
    // Reset timeout
    if (typingTimeout) {
        clearTimeout(typingTimeout);
    }
    
    // Auto-stop after 3 seconds of inactivity
    typingTimeout = setTimeout(() => {
        stopTyping();
    }, 3000);
}

function stopTyping() {
    if (isTyping && currentRoom) {
        isTyping = false;
        socket.emit('typing_stop', {
            room: currentRoom,
            userId: myUserId
        });
    }
    
    if (typingTimeout) {
        clearTimeout(typingTimeout);
        typingTimeout = null;
    }
}

// Listen for typing indicators
socket.on('typing_indicator', (data) => {
    if (data.room !== currentRoom) return;
    if (data.userId === myUserId) return;
    
    const typingIndicator = document.getElementById('kim-typing-indicator');
    if (!typingIndicator) return;
    
    if (data.typing) {
        const userName = knownUsers[data.userId]?.nickname || 'Someone';
        typingIndicator.textContent = `${userName} is typing...`;
        typingIndicator.classList.remove('hidden');
    } else {
        typingIndicator.classList.add('hidden');
    }
});

async function sendMessage() {
    const text = kimMessageInput.value.trim();
    if (!text) return;

    // Check if editing
    const editingMessageId = kimMessageInput.dataset.editingMessageId;
    if (editingMessageId) {
        await saveEditedMessage(editingMessageId, text);
        kimMessageInput.value = '';
        kimMessageInput.dataset.editingMessageId = '';
        kimSendBtn.textContent = 'Send';
        replyingToMessageId = null;
        kimMessageInput.placeholder = 'Type a message...';
        return;
    }

    let targetPeerId = 'global';
    if (currentRoom !== 'global-relay') {
        const parts = currentRoom.split('_');
        targetPeerId = parts.find(id => id !== myUserId);
    }

    try {
        const encrypted = await crypto.encryptMessage(text, targetPeerId);
        const messageId = `${myUserId}_${Date.now()}`;
        const payload = {
            room: currentRoom,
            encryptedContent: encrypted.ciphertext,
            iv: encrypted.iv,
            mode: encrypted.mode,
            senderId: myUserId,
            messageId: messageId,
            timestamp: new Date().toISOString(),
            parentMessageId: replyingToMessageId
        };

        socket.emit('encrypted_message', payload);
        kimMessageInput.value = '';
        addMessageToFeedHelper(text, true, 'You', messageId, [], [], replyingToMessageId, false);
        
        // Clear reply state
        replyingToMessageId = null;
        kimMessageInput.placeholder = 'Type a message...';
    } catch (e) {
        console.error("Encryption Error", e);
        alert("Unable to send message: " + e.message);
    }
}

// Incoming
socket.on('new_encrypted_message', async (data) => {
    if (data.senderId === myUserId) return;

    let decText = "[Message]";
    try {
        if (data.mode === 'CLEAR') {
            decText = atob(data.encryptedContent);
        } else {
            decText = await crypto.decryptMessage({
                iv: data.iv,
                ciphertext: data.encryptedContent,
                mode: data.mode
            }, data.senderId);
        }
    } catch (e) {
        console.error("Decrypt Error", e);
        decText = "[Unable to read message]";
    }

    let senderName = "Unknown";
    if (knownUsers[data.senderId]) senderName = knownUsers[data.senderId].nickname;

    // Load read receipts and reactions for new message
    const messageId = data.messageId;
    const readReceipts = messageId ? await loadReadReceipts(messageId) : [];
    const reactions = messageId ? await loadReactions(messageId) : [];
    
    addMessageToFeedHelper(decText, false, senderName, messageId, readReceipts, reactions);
});

function addMessageToFeed(text, isSelf, senderName, messageId = null, readReceipts = null, reactions = null, parentMessageId = null, edited = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `kim-message ${isSelf ? 'self' : 'peer'}`;
    if (messageId) {
        msgDiv.dataset.messageId = messageId;
    }
    if (parentMessageId) {
        msgDiv.dataset.parentMessageId = parentMessageId;
        msgDiv.classList.add('kim-message-reply');
    }
    
    // Read receipt indicator
    let readIndicator = '';
    if (isSelf && readReceipts) {
        const readCount = readReceipts.length;
        if (readCount > 0) {
            readIndicator = '<span class="kim-read-receipt">✓✓</span>';
        } else {
            readIndicator = '<span class="kim-read-receipt">✓</span>';
        }
    }
    
    // Edited indicator
    let editedIndicator = edited ? '<span class="kim-edited-indicator">(edited)</span>' : '';
    
    // Reply indicator
    let replyIndicator = '';
    if (parentMessageId) {
        const parentMsg = document.querySelector(`[data-message-id="${parentMessageId}"]`);
        if (parentMsg) {
            const parentText = parentMsg.querySelector('.kim-message-bubble')?.textContent || '';
            const preview = parentText.substring(0, 50) + (parentText.length > 50 ? '...' : '');
            replyIndicator = `<div class="kim-reply-preview">Replying to: ${escapeHtml(preview)}</div>`;
        }
    }
    
    // Reactions
    let reactionsHtml = '';
    if (reactions && reactions.length > 0) {
        const reactionGroups = {};
        reactions.forEach(r => {
            if (!reactionGroups[r.reaction_type]) {
                reactionGroups[r.reaction_type] = [];
            }
            reactionGroups[r.reaction_type].push(r);
        });
        
        reactionsHtml = '<div class="kim-message-reactions">';
        for (const [reactionType, reactionList] of Object.entries(reactionGroups)) {
            reactionsHtml += `<span class="kim-reaction" data-reaction="${reactionType}">${reactionType} ${reactionList.length}</span>`;
        }
        reactionsHtml += '</div>';
    }
    
    msgDiv.innerHTML = `
        <div class="kim-message-meta">
            ${escapeHtml(senderName)}
            ${readIndicator}
            ${editedIndicator}
        </div>
        ${replyIndicator}
        <div class="kim-message-bubble">${escapeHtml(text)}</div>
        ${reactionsHtml}
        <div class="kim-message-actions">
            <button class="kim-reply-btn" title="Reply" data-message-id="${messageId || ''}">↩</button>
            ${isSelf ? `<button class="kim-edit-btn" title="Edit" data-message-id="${messageId || ''}">✏</button>` : ''}
            <button class="kim-reaction-btn" title="Add reaction">😊</button>
        </div>
    `;
    
    // Add button handlers
    const reactionBtn = msgDiv.querySelector('.kim-reaction-btn');
    if (reactionBtn && messageId) {
        reactionBtn.addEventListener('click', () => {
            showReactionPicker(messageId, reactionBtn);
        });
    }
    
    const replyBtn = msgDiv.querySelector('.kim-reply-btn');
    if (replyBtn && messageId) {
        replyBtn.addEventListener('click', () => {
            startReply(messageId);
        });
    }
    
    const editBtn = msgDiv.querySelector('.kim-edit-btn');
    if (editBtn && messageId && isSelf) {
        editBtn.addEventListener('click', () => {
            editMessage(messageId, text);
        });
    }
    
    kimMessagesFeed.appendChild(msgDiv);
    kimMessagesFeed.scrollTop = kimMessagesFeed.scrollHeight;
    
    // Mark as read if not self
    if (!isSelf && messageId) {
        markMessageAsRead(messageId);
    }
}

let replyingToMessageId = null;

function startReply(messageId) {
    replyingToMessageId = messageId;
    const messageEl = document.querySelector(`[data-message-id="${messageId}"]`);
    if (messageEl) {
        const bubble = messageEl.querySelector('.kim-message-bubble');
        const preview = bubble?.textContent || '';
        kimMessageInput.placeholder = `Replying to: ${preview.substring(0, 30)}...`;
        kimMessageInput.focus();
    }
}

function editMessage(messageId, currentText) {
    kimMessageInput.value = currentText;
    kimMessageInput.focus();
    kimMessageInput.dataset.editingMessageId = messageId;
    kimSendBtn.textContent = 'Save';
}

async function saveEditedMessage(messageId, newText) {
    try {
        // In a full implementation, we'd send an edit event to the server
        // For now, we'll just update the UI
        const messageEl = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageEl) {
            const bubble = messageEl.querySelector('.kim-message-bubble');
            if (bubble) {
                bubble.textContent = newText;
            }
            
            // Add edited indicator
            let editedIndicator = messageEl.querySelector('.kim-edited-indicator');
            if (!editedIndicator) {
                const meta = messageEl.querySelector('.kim-message-meta');
                if (meta) {
                    editedIndicator = document.createElement('span');
                    editedIndicator.className = 'kim-edited-indicator';
                    editedIndicator.textContent = '(edited)';
                    meta.appendChild(editedIndicator);
                }
            }
        }
        
        // Send edit event to server (would update database)
        socket.emit('message_edit', {
            messageId: messageId,
            newContent: newText,
            userId: myUserId
        });
    } catch (e) {
        console.error("Error saving edited message:", e);
    }
}

async function markMessageAsRead(messageId) {
    try {
        await fetch(`/api/kim/messages/${messageId}/read`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userId: myUserId })
        });
    } catch (e) {
        console.error("Error marking message as read:", e);
    }
}

function showReactionPicker(messageId, button) {
    // Simple emoji picker - in production, use a proper emoji picker library
    const reactions = ['👍', '❤️', '😂', '😮', '😢', '🙏'];
    const picker = document.createElement('div');
    picker.className = 'kim-reaction-picker';
    picker.innerHTML = reactions.map(r => `<button class="kim-reaction-option" data-reaction="${r}">${r}</button>`).join('');
    
    // Position picker
    const rect = button.getBoundingClientRect();
    picker.style.position = 'fixed';
    picker.style.left = `${rect.left}px`;
    picker.style.top = `${rect.top - 40}px`;
    picker.style.zIndex = '1000';
    
    document.body.appendChild(picker);
    
    // Handle reaction selection
    picker.querySelectorAll('.kim-reaction-option').forEach(btn => {
        btn.addEventListener('click', async () => {
            const reactionType = btn.dataset.reaction;
            await addReaction(messageId, reactionType);
            document.body.removeChild(picker);
        });
    });
    
    // Close on outside click
    setTimeout(() => {
        const closePicker = (e) => {
            if (!picker.contains(e.target) && e.target !== button) {
                document.body.removeChild(picker);
                document.removeEventListener('click', closePicker);
            }
        };
        document.addEventListener('click', closePicker);
    }, 100);
}

async function addReaction(messageId, reactionType) {
    try {
        await fetch(`/api/kim/messages/${messageId}/reactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                userId: myUserId,
                reactionType: reactionType
            })
        });
    } catch (e) {
        console.error("Error adding reaction:", e);
    }
}

// Listen for read receipts and reactions
socket.on('read_receipt', (data) => {
    const messageEl = document.querySelector(`[data-message-id="${data.messageId}"]`);
    if (messageEl) {
        const readReceipt = messageEl.querySelector('.kim-read-receipt');
        if (readReceipt) {
            readReceipt.textContent = '✓✓';
        }
    }
});

socket.on('reaction_added', (data) => {
    const messageEl = document.querySelector(`[data-message-id="${data.messageId}"]`);
    if (messageEl) {
        // Reload reactions for this message
        loadReactionsForMessage(data.messageId);
    }
});

socket.on('message_edited', (data) => {
    const messageEl = document.querySelector(`[data-message-id="${data.messageId}"]`);
    if (messageEl) {
        const bubble = messageEl.querySelector('.kim-message-bubble');
        if (bubble) {
            bubble.textContent = data.newContent;
        }
        
        // Add edited indicator
        let editedIndicator = messageEl.querySelector('.kim-edited-indicator');
        if (!editedIndicator) {
            const meta = messageEl.querySelector('.kim-message-meta');
            if (meta) {
                editedIndicator = document.createElement('span');
                editedIndicator.className = 'kim-edited-indicator';
                editedIndicator.textContent = '(edited)';
                meta.appendChild(editedIndicator);
            }
        }
    }
});

async function loadReadReceipts(messageId) {
    try {
        const res = await fetch(`/api/kim/messages/${messageId}/read`);
        if (!res.ok) return [];
        const data = await res.json();
        return data.receipts || [];
    } catch (e) {
        console.error("Error loading read receipts:", e);
        return [];
    }
}

async function loadReactions(messageId) {
    try {
        const res = await fetch(`/api/kim/messages/${messageId}/reactions`);
        if (!res.ok) return [];
        const data = await res.json();
        return data.reactions || [];
    } catch (e) {
        console.error("Error loading reactions:", e);
        return [];
    }
}

async function loadReactionsForMessage(messageId) {
    try {
        const reactions = await loadReactions(messageId);
        
        const messageEl = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageEl) {
            let reactionsEl = messageEl.querySelector('.kim-message-reactions');
            if (!reactionsEl) {
                reactionsEl = document.createElement('div');
                reactionsEl.className = 'kim-message-reactions';
                messageEl.querySelector('.kim-message-bubble').after(reactionsEl);
            }
            
            if (reactions.length > 0) {
                const reactionGroups = {};
                reactions.forEach(r => {
                    if (!reactionGroups[r.reaction_type]) {
                        reactionGroups[r.reaction_type] = [];
                    }
                    reactionGroups[r.reaction_type].push(r);
                });
                
                reactionsEl.innerHTML = Object.entries(reactionGroups).map(([type, list]) => 
                    `<span class="kim-reaction" data-reaction="${type}">${type} ${list.length}</span>`
                ).join('');
            } else {
                reactionsEl.innerHTML = '';
            }
        }
    } catch (e) {
        console.error("Error loading reactions:", e);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;
}

// File Upload
const kimFileBtn = document.getElementById('kim-file-btn');
const kimFileInput = document.getElementById('kim-file-input');

if (kimFileBtn && kimFileInput) {
    kimFileBtn.addEventListener('click', () => {
        kimFileInput.click();
    });
    
    kimFileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        try {
            // Process file client-side (compress, optimize)
            const mediaProcessor = new MediaProcessor();
            const processed = await mediaProcessor.processFile(file, {
                compressImages: true,
                maxImageWidth: 1920,
                imageQuality: 0.8,
                generateThumbnails: true
            });
            
            const fileInfo = {
                name: file.name,
                size: processed.processedSize,
                type: file.type,
                originalSize: processed.originalSize,
                saved: processed.saved
            };
            
            // Upload processed file
            const formData = new FormData();
            formData.append('file', processed.file);
            formData.append('userId', myUserId);
            
            if (processed.thumbnail) {
                formData.append('thumbnail', processed.thumbnail, 'thumb_' + file.name);
            }
            
            const res = await fetch('/api/kim/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!res.ok) {
                throw new Error('Upload failed');
            }
            
            const data = await res.json();
            
            // Send file as message
            await sendFileMessage(data, fileInfo);
            
            // Reset input
            kimFileInput.value = '';
        } catch (e) {
            console.error("File upload error:", e);
            alert("Failed to upload file: " + e.message);
        }
    });
}

async function sendFileMessage(fileData, fileInfo) {
    try {
        // Encrypt file metadata
        const fileMessage = `[FILE:${fileData.fileId}:${fileInfo.name}:${fileData.type}]`;
        
        let targetPeerId = 'global';
        if (currentRoom !== 'global-relay') {
            const parts = currentRoom.split('_');
            targetPeerId = parts.find(id => id !== myUserId);
        }
        
        const encrypted = await crypto.encryptMessage(fileMessage, targetPeerId);
        const messageId = `${myUserId}_${Date.now()}`;
        const payload = {
            room: currentRoom,
            encryptedContent: encrypted.ciphertext,
            iv: encrypted.iv,
            mode: encrypted.mode,
            senderId: myUserId,
            messageId: messageId,
            timestamp: new Date().toISOString(),
            fileData: fileData
        };
        
        socket.emit('encrypted_message', payload);
        
        // Display file in feed
        displayFileMessage(fileData, fileInfo, true, 'You', messageId);
    } catch (e) {
        console.error("Error sending file message:", e);
        alert("Failed to send file: " + e.message);
    }
}

function displayFileMessage(fileData, fileInfo, isSelf, senderName, messageId) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `kim-message ${isSelf ? 'self' : 'peer'}`;
    if (messageId) {
        msgDiv.dataset.messageId = messageId;
    }
    
    let fileContent = '';
    if (fileData.type === 'image') {
        fileContent = `<img src="${fileData.url}" alt="${fileInfo.name}" class="kim-file-image">`;
    } else if (fileData.type === 'video') {
        fileContent = `<video src="${fileData.url}" controls class="kim-file-video"></video>`;
    } else {
        fileContent = `
            <div class="kim-file-info">
                <span class="kim-file-icon">📄</span>
                <div class="kim-file-details">
                    <div class="kim-file-name">${escapeHtml(fileInfo.name)}</div>
                    <div class="kim-file-size">${formatFileSize(fileInfo.size)}</div>
                </div>
                <a href="${fileData.url}" download="${fileInfo.name}" class="kim-file-download">Download</a>
            </div>
        `;
    }
    
    msgDiv.innerHTML = `
        <div class="kim-message-meta">${escapeHtml(senderName)}</div>
        <div class="kim-message-bubble">
            <div class="kim-message-file">${fileContent}</div>
        </div>
    `;
    
    kimMessagesFeed.appendChild(msgDiv);
    kimMessagesFeed.scrollTop = kimMessagesFeed.scrollHeight;
    
    // Mark as read if not self
    if (!isSelf && messageId) {
        markMessageAsRead(messageId);
    }
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Handle file messages in incoming messages
function parseFileMessage(text) {
    const match = text.match(/\[FILE:([^:]+):([^:]+):([^\]]+)\]/);
    if (match) {
        return {
            fileId: match[1],
            filename: match[2],
            type: match[3]
        };
    }
    return null;
}

// Helper to add message (handles both text and file messages)
function addMessageToFeedHelper(text, isSelf, senderName, messageId, readReceipts, reactions) {
    const fileData = parseFileMessage(text);
    if (fileData) {
        displayFileMessage(
            { fileId: fileData.fileId, url: `/api/kim/files/${fileData.fileId}`, type: fileData.type },
            { name: fileData.filename, size: 0 },
            isSelf,
            senderName,
            messageId
        );
        return;
    }
    addMessageToFeed(text, isSelf, senderName, messageId, readReceipts, reactions);
}

// Message Search
const kimSearchBtn = document.getElementById('kim-search-btn');
const kimSearchBar = document.getElementById('kim-search-bar');
const kimSearchInput = document.getElementById('kim-search-input');
const kimSearchClose = document.getElementById('kim-search-close');
let searchResults = [];
let currentSearchIndex = -1;

if (kimSearchBtn) {
    kimSearchBtn.addEventListener('click', () => {
        if (kimSearchBar) {
            kimSearchBar.classList.remove('hidden');
            if (kimSearchInput) {
                kimSearchInput.focus();
            }
        }
    });
}

if (kimSearchClose) {
    kimSearchClose.addEventListener('click', () => {
        if (kimSearchBar) {
            kimSearchBar.classList.add('hidden');
        }
        if (kimSearchInput) {
            kimSearchInput.value = '';
        }
        clearSearchHighlights();
    });
}

if (kimSearchInput) {
    let searchTimeout = null;
    kimSearchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        if (query.length < 2) {
            clearSearchHighlights();
            return;
        }
        
        searchTimeout = setTimeout(() => {
            searchMessages(query);
        }, 300);
    });
    
    kimSearchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (e.shiftKey) {
                navigateSearchResults(-1); // Previous
            } else {
                navigateSearchResults(1); // Next
            }
        } else if (e.key === 'Escape') {
            if (kimSearchBar) {
                kimSearchBar.classList.add('hidden');
            }
            clearSearchHighlights();
        }
    });
}

async function searchMessages(query) {
    try {
        // Load all messages for current room
        const res = await fetch(`/api/kim/messages/${currentRoom}?limit=500&offset=0`);
        if (!res.ok) return;
        
        const data = await res.json();
        const messages = data.messages || [];
        
        // Decrypt and search
        searchResults = [];
        const lowerQuery = query.toLowerCase();
        
        for (const msg of messages) {
            let decText = "";
            try {
                if (msg.mode === 'CLEAR') {
                    decText = atob(msg.encrypted_content);
                } else {
                    decText = await crypto.decryptMessage({
                        iv: msg.iv,
                        ciphertext: msg.encrypted_content,
                        mode: msg.mode
                    }, msg.sender_id);
                }
            } catch (e) {
                continue;
            }
            
            if (decText.toLowerCase().includes(lowerQuery)) {
                searchResults.push({
                    messageId: msg.message_id,
                    text: decText,
                    index: searchResults.length
                });
            }
        }
        
        // Highlight results
        highlightSearchResults(query);
        
        if (searchResults.length > 0) {
            currentSearchIndex = 0;
            scrollToSearchResult(searchResults[0].messageId);
        }
    } catch (e) {
        console.error("Search error:", e);
    }
}

function highlightSearchResults(query) {
    clearSearchHighlights();
    
    const messages = kimMessagesFeed.querySelectorAll('.kim-message');
    const lowerQuery = query.toLowerCase();
    
    messages.forEach(msg => {
        const bubble = msg.querySelector('.kim-message-bubble');
        if (!bubble) return;
        
        const text = bubble.textContent || bubble.innerText;
        if (text.toLowerCase().includes(lowerQuery)) {
            msg.classList.add('highlight');
        }
    });
}

function clearSearchHighlights() {
    const messages = kimMessagesFeed.querySelectorAll('.kim-message');
    messages.forEach(msg => msg.classList.remove('highlight'));
    searchResults = [];
    currentSearchIndex = -1;
}

function navigateSearchResults(direction) {
    if (searchResults.length === 0) return;
    
    currentSearchIndex += direction;
    if (currentSearchIndex < 0) {
        currentSearchIndex = searchResults.length - 1;
    } else if (currentSearchIndex >= searchResults.length) {
        currentSearchIndex = 0;
    }
    
    const result = searchResults[currentSearchIndex];
    scrollToSearchResult(result.messageId);
}

function scrollToSearchResult(messageId) {
    const messageEl = document.querySelector(`[data-message-id="${messageId}"]`);
    if (messageEl) {
        messageEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        messageEl.classList.add('highlight');
        setTimeout(() => {
            messageEl.classList.remove('highlight');
            setTimeout(() => messageEl.classList.add('highlight'), 100);
        }, 2000);
    }
}

// Notifications
let notificationPermission = null;

async function requestNotificationPermission() {
    if (!('Notification' in window)) {
        console.log('Notifications not supported');
        return false;
    }
    
    if (Notification.permission === 'granted') {
        notificationPermission = true;
        return true;
    }
    
    if (Notification.permission !== 'denied') {
        const permission = await Notification.requestPermission();
        notificationPermission = permission === 'granted';
        return notificationPermission;
    }
    
    return false;
}

function showNotification(title, body, icon = null) {
    if (!notificationPermission) return;
    
    try {
        const notification = new Notification(title, {
            body: body,
            icon: icon || '/katanx-logo.png',
            badge: '/katanx-logo.png',
            tag: 'kim-message',
            requireInteraction: false
        });
        
        notification.onclick = () => {
            window.focus();
            if (kimPanel) {
                kimPanel.classList.add('open');
            }
            notification.close();
        };
        
        // Auto-close after 5 seconds
        setTimeout(() => {
            notification.close();
        }, 5000);
    } catch (e) {
        console.error("Error showing notification:", e);
    }
}

// Request permission on connect
if (kimConnectBtn) {
    const originalConnect = kimConnectBtn.onclick;
    kimConnectBtn.addEventListener('click', async () => {
        await requestNotificationPermission();
    });
}

// Update notification badge
let unreadCount = 0;

function updateNotificationBadge(count) {
    const badge = document.getElementById('kim-notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count.toString();
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    }
}

// Show notification for new messages (if not focused)
socket.on('new_encrypted_message', async (data) => {
    if (data.senderId === myUserId) return;
    
    const isViewingChat = document.hasFocus() && 
                         kimPanel && 
                         kimPanel.classList.contains('open') &&
                         data.room === currentRoom;
    
    if (!isViewingChat) {
        unreadCount++;
        updateNotificationBadge(unreadCount);
        
        let senderName = "Someone";
        if (knownUsers[data.senderId]) {
            senderName = knownUsers[data.senderId].nickname;
        }
        
        showNotification(
            `New message from ${senderName}`,
            "You have a new message",
            null
        );
    }
});

// Clear badge when panel opens
if (kimToggleBtn) {
    const originalTogglePanel = togglePanel;
    togglePanel = function() {
        originalTogglePanel();
        if (kimPanel && kimPanel.classList.contains('open')) {
            unreadCount = 0;
            updateNotificationBadge(0);
        }
    };
    
    // Re-attach event listener with new function
    kimToggleBtn.removeEventListener('click', originalTogglePanel);
    kimToggleBtn.addEventListener('click', togglePanel);
}

// Room Category Management
function initializeRoomCategories() {
    // Set up category expand/collapse
    document.querySelectorAll('.kim-category-header').forEach(header => {
        header.addEventListener('click', function() {
            const category = this.dataset.category;
            const categoryDiv = this.closest('.kim-room-category');
            const roomsContainer = categoryDiv.querySelector('.kim-category-rooms');

            // Toggle expanded state
            categoryDiv.classList.toggle('collapsed');

            // Update visual state
            if (categoryDiv.classList.contains('collapsed')) {
                this.classList.remove('expanded');
            } else {
                this.classList.add('expanded');
            }
        });
    });

    // Initially collapse creative and growth categories
    document.querySelectorAll('.kim-room-category').forEach((category, index) => {
        if (index > 0) { // Skip first category (General)
            category.classList.add('collapsed');
        } else {
            category.querySelector('.kim-category-header').classList.add('expanded');
        }
    });
}

// Room Creation Modal
function initializeRoomCreation() {
    const addRoomBtn = document.getElementById('kimAddRoomBtn');
    const modal = document.getElementById('kimCreateRoomModal');
    const modalClose = document.getElementById('kimModalClose');
    const cancelBtn = document.getElementById('kimCancelCreate');
    const createBtn = document.getElementById('kimCreateRoom');
    const roomNameInput = document.getElementById('kimRoomName');
    const roomDescInput = document.getElementById('kimRoomDescription');
    const roomCategorySelect = document.getElementById('kimRoomCategory');

    // Icon selector
    let selectedIcon = '💫';
    document.querySelectorAll('.kim-icon-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.kim-icon-option').forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            selectedIcon = this.dataset.icon;
        });
    });

    // Open modal
    if (addRoomBtn) {
        addRoomBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            modal.classList.add('active');
            roomNameInput.focus();
        });
    }

    // Close modal functions
    function closeModal() {
        modal.classList.remove('active');
        // Reset form
        roomNameInput.value = '';
        roomDescInput.value = '';
        roomCategorySelect.value = 'general';
        selectedIcon = '💫';
        document.querySelectorAll('.kim-icon-option').forEach((opt, index) => {
            opt.classList.toggle('selected', index === 0);
        });
    }

    if (modalClose) modalClose.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

    // Click outside to close
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // ESC key to close
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });

    // Create room
    if (createBtn) {
        createBtn.addEventListener('click', function() {
            const roomName = roomNameInput.value.trim();
            if (!roomName) {
                alert('Please enter a room name');
                return;
            }

            const roomId = 'custom_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            const roomDesc = roomDescInput.value.trim();
            const category = roomCategorySelect.value;

            // Create room element
            const roomItem = document.createElement('div');
            roomItem.className = 'kim-conversation-item';
            roomItem.dataset.room = roomId;

            roomItem.innerHTML = `
                <span class="kim-conversation-icon">${selectedIcon}</span>
                <span class="kim-conversation-name">${escapeHtml(roomName)}</span>
                ${roomDesc ? `<span class="kim-room-desc">${escapeHtml(roomDesc)}</span>` : ''}
            `;

            // Add click handler
            roomItem.addEventListener('click', function() {
                // Update active states
                document.querySelectorAll('.kim-conversation-item').forEach(item => item.classList.remove('active'));
                roomItem.classList.add('active');

                // Switch to room
                document.getElementById('kim-current-room-name').textContent = roomName;
                applyRoomTheme(roomId); // Apply room theme
                loadMessageHistory(roomId);

                // Join room
                socket.emit('join', { room: roomId });
            });

            // Add to appropriate category
            const categoryContainer = document.getElementById(category + '-rooms');
            if (categoryContainer) {
                categoryContainer.appendChild(roomItem);
            } else {
                // Fallback to general
                document.getElementById('general-rooms').appendChild(roomItem);
            }

            closeModal();

            // Show success feedback
            showNotification('Room created successfully!', 'success');
        });
    }
}

// Panel Expansion
function initializePanelExpansion() {
    // Add expand button to panel header if not exists
    const panelActions = document.querySelector('.kim-panel-actions');
    if (panelActions && !document.getElementById('kimExpandBtn')) {
        const expandBtn = document.createElement('button');
        expandBtn.id = 'kimExpandBtn';
        expandBtn.className = 'kim-expand-btn';
        expandBtn.title = 'Expand/Collapse Sidebar';
        expandBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M15 3h6v6"></path>
                <path d="M9 21H3v-6"></path>
                <path d="m21 3-7 7"></path>
                <path d="m3 21 7-7"></path>
            </svg>
        `;

        expandBtn.addEventListener('click', function() {
            const panel = document.getElementById('kimSidebarPanel');
            panel.classList.toggle('resizable');

            // Update icon
            const icon = this.querySelector('svg');
            if (panel.classList.contains('resizable')) {
                icon.innerHTML = `
                    <path d="M9 21H3v-6"></path>
                    <path d="M21 3h-6v6"></path>
                    <path d="m3 21 7-7"></path>
                    <path d="m21 3-7 7"></path>
                `;
                this.title = 'Lock Sidebar Size';
            } else {
                icon.innerHTML = `
                    <path d="M15 3h6v6"></path>
                    <path d="M9 21H3v-6"></path>
                    <path d="m21 3-7 7"></path>
                    <path d="m3 21 7-7"></path>
                `;
                this.title = 'Expand/Collapse Sidebar';
            }
        });

        panelActions.insertBefore(expandBtn, panelActions.firstChild);
    }
}

// Notification System
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `kim-notification kim-notification-${type}`;
    notification.innerHTML = `
        <span class="kim-notification-icon">${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
        <span class="kim-notification-text">${message}</span>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => notification.classList.add('active'), 10);

    // Auto remove
    setTimeout(() => {
        notification.classList.remove('active');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Online Count Updates
function updateOnlineCount() {
    const onlineUsers = Object.values(knownUsers).filter(u => u.status === 'online').length;
    const countElement = document.getElementById('kimOnlineCount');
    if (countElement) {
        countElement.textContent = `${onlineUsers} online`;
    }
}

// Room Theme Application
function applyRoomTheme(roomId) {
    const chatView = document.getElementById('kimChatView');
    if (chatView) {
        // Remove existing room theme
        chatView.removeAttribute('data-room');
        // Apply new theme
        chatView.setAttribute('data-room', roomId);

        // Add room-specific animations
        chatView.style.animation = 'none';
        setTimeout(() => {
            chatView.style.animation = 'room-transition 0.5s ease';
        }, 10);
    }
}

// Initialize all new features
function initializeEnhancedFeatures() {
    initializeRoomCategories();
    initializeRoomCreation();
    initializePanelExpansion();

    // Apply initial room theme
    applyRoomTheme('global');

    // Update online count periodically
    setInterval(updateOnlineCount, 5000);
    updateOnlineCount(); // Initial update
}

// Offline Support
let offlineQueue = [];
let isOnline = navigator.onLine;

window.addEventListener('online', () => {
    isOnline = true;
    syncOfflineQueue();
    if (kimPanel) {
        const offlineIndicator = document.querySelector('.kim-offline-indicator');
        if (offlineIndicator) {
            offlineIndicator.remove();
        }
    }
});

window.addEventListener('offline', () => {
    isOnline = false;
    showOfflineIndicator();
});

function showOfflineIndicator() {
    if (!kimPanel) return;
    
    let indicator = document.querySelector('.kim-offline-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'kim-offline-indicator';
        indicator.textContent = 'Offline - messages will be sent when connection is restored';
        kimPanel.querySelector('.kim-panel-content').prepend(indicator);
    }
}

async function syncOfflineQueue() {
    if (offlineQueue.length === 0) return;
    
    const queue = [...offlineQueue];
    offlineQueue = [];
    
    for (const message of queue) {
        try {
            socket.emit('encrypted_message', message);
        } catch (e) {
            console.error("Error syncing queued message:", e);
            offlineQueue.push(message); // Re-queue on error
        }
    }
}

// Store messages in IndexedDB when offline
async function queueMessageForOffline(payload) {
    try {
        const db = await crypto.initDB();
        if (!db) return;
        
        const tx = db.transaction(['offlineMessages'], 'readwrite');
        const store = tx.objectStore('offlineMessages');
        
        await store.add({
            id: Date.now(),
            payload: payload,
            timestamp: new Date().toISOString()
        });
        
        offlineQueue.push(payload);
    } catch (e) {
        console.error("Error queueing message:", e);
    }
}

// Load queued messages from IndexedDB on startup
async function loadOfflineQueue() {
    try {
        const db = await crypto.initDB();
        if (!db) {
            console.log('IndexedDB not available for offline queue');
            return;
        }
        
        // Check if offlineMessages store exists
        if (!db.objectStoreNames.contains('offlineMessages')) {
            console.log('offlineMessages store not found, skipping queue load');
            return;
        }
        
        const tx = db.transaction(['offlineMessages'], 'readonly');
        const store = tx.objectStore('offlineMessages');
        const request = store.getAll();
        
        request.onsuccess = () => {
            const messages = request.result || [];
            offlineQueue = messages.map(m => m.payload);
            
            if (offlineQueue.length > 0 && isOnline) {
                syncOfflineQueue();
            }
        };
        
        request.onerror = () => {
            console.log('Error reading offline queue:', request.error);
        };
    } catch (e) {
        // Silently fail - offline queue is optional
        console.log("Offline queue not available:", e.message);
    }
}

// Offline messages store is created in crypto.initDB() onupgradeneeded
// No need for separate initialization

// Load offline queue on startup
loadOfflineQueue();

// Update sendMessage to queue when offline
async function sendMessageWithOfflineSupport() {
    const text = kimMessageInput.value.trim();
    if (!text) return;

    // Check if editing
    const editingMessageId = kimMessageInput.dataset.editingMessageId;
    if (editingMessageId) {
        await saveEditedMessage(editingMessageId, text);
        kimMessageInput.value = '';
        kimMessageInput.dataset.editingMessageId = '';
        kimSendBtn.textContent = 'Send';
        replyingToMessageId = null;
        kimMessageInput.placeholder = 'Type a message...';
        return;
    }

    let targetPeerId = 'global';
    if (currentRoom !== 'global-relay') {
        const parts = currentRoom.split('_');
        targetPeerId = parts.find(id => id !== myUserId);
    }

    try {
        const encrypted = await crypto.encryptMessage(text, targetPeerId);
        const messageId = `${myUserId}_${Date.now()}`;
        const payload = {
            room: currentRoom,
            encryptedContent: encrypted.ciphertext,
            iv: encrypted.iv,
            mode: encrypted.mode,
            senderId: myUserId,
            messageId: messageId,
            timestamp: new Date().toISOString(),
            parentMessageId: replyingToMessageId
        };

        if (isOnline) {
            socket.emit('encrypted_message', payload);
        } else {
            await queueMessageForOffline(payload);
            showOfflineIndicator();
        }
        
        kimMessageInput.value = '';
        addMessageToFeedHelper(text, true, 'You', messageId, [], [], replyingToMessageId, false);
        
        // Clear reply state
        replyingToMessageId = null;
        kimMessageInput.placeholder = 'Type a message...';
    } catch (e) {
        console.error("Encryption Error", e);
        alert("Unable to send message: " + e.message);
    }
}

// Replace original sendMessage
async function sendMessage() {
    return sendMessageWithOfflineSupport();
}

// Profile Editor
const kimProfileBtn = document.getElementById('kim-profile-btn');
const kimProfileEditor = document.getElementById('kim-profile-editor');
const kimProfileClose = document.getElementById('kim-profile-close');
const kimAvatarInput = document.getElementById('kim-avatar-input');
const kimAvatarUploadBtn = document.getElementById('kim-avatar-upload-btn');
const kimAvatarPreview = document.getElementById('kim-avatar-preview');
const kimProfileDisplayName = document.getElementById('kim-profile-display-name');
const kimProfileBio = document.getElementById('kim-profile-bio');
const kimProfileSaveBtn = document.getElementById('kim-profile-save-btn');

if (kimProfileBtn) {
    kimProfileBtn.addEventListener('click', () => {
        if (kimProfileEditor) {
            kimProfileEditor.classList.toggle('hidden');
        }
    });
}

if (kimAvatarUploadBtn && kimAvatarInput) {
    kimAvatarUploadBtn.addEventListener('click', () => {
        kimAvatarInput.click();
    });
    
    kimAvatarInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                if (kimAvatarPreview) {
                    kimAvatarPreview.innerHTML = `<img src="${e.target.result}" alt="Avatar">`;
                }
            };
            reader.readAsDataURL(file);
        }
    });
}

if (kimProfileClose) {
    kimProfileClose.addEventListener('click', () => {
        if (kimProfileEditor) {
            kimProfileEditor.classList.add('hidden');
        }
    });
}

if (kimProfileSaveBtn) {
    kimProfileSaveBtn.addEventListener('click', async () => {
        const displayName = kimProfileDisplayName?.value.trim() || '';
        const bio = kimProfileBio?.value.trim() || '';
        
        // In a full implementation, save to server
        console.log('Saving profile:', { displayName, bio });
        
        if (kimProfileEditor) {
            kimProfileEditor.classList.add('hidden');
        }
    });
}

// Initialize - only if elements exist
if (kimLoginState && kimMainState) {
    setState('login');
} else {
    console.warn('KIM: Login/main state elements not found');
}

// Expose KIM API for external use (if needed)
window.KIM = {
    getUserId: () => myUserId,
    getCurrentRoom: () => currentRoom,
    isConnected: () => myUserId !== null,
    sendMessage: (text) => {
        if (kimMessageInput) {
            kimMessageInput.value = text;
            sendMessage();
        }
    }
};

})(); // End IIFE wrapper

