/**
 * KIM UI Logic
 */

const socket = io();
const crypto = new KIMCrypto();
let myUserId = null;
let currentRoom = 'global'; // default room
let knownUsers = {}; // cache of user info

// DOM Elements
const loginOverlay = document.getElementById('kim-login-overlay');
const mainInterface = document.getElementById('kim-main-interface');
const connectBtn = document.getElementById('connect-btn');
const nicknameInput = document.getElementById('nickname-input');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const messagesFeed = document.getElementById('messages-feed');
const userList = document.getElementById('user-list');
const chatArea = document.getElementById('kimChatArea');
const currentRoomName = document.getElementById('current-room-name');
const typingIndicator = document.getElementById('typing-indicator');

// --- Initialization ---

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
            const roomItem = document.createElement('li');
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
                switchToRoom(roomId, roomName, selectedIcon, roomDesc);
            });

            // Add to appropriate category
            const categoryContainer = document.getElementById(category + '-rooms');
            if (categoryContainer) {
                categoryContainer.appendChild(roomItem);
            } else {
                // Fallback to general
                document.getElementById('general-rooms').appendChild(roomItem);
            }

            // Set up click handler for new room
            roomItem.addEventListener('click', function() {
                // Update active states
                document.querySelectorAll('.kim-conversation-item').forEach(item => item.classList.remove('active'));
                roomItem.classList.add('active');
                switchToRoom(roomId, roomName, selectedIcon, roomDesc);
            });

            closeModal();
        });
    }
}

// Room switching function
function switchToRoom(roomId, displayName, icon = '💫', description = '') {
    currentRoom = roomId;
    if (currentRoomName) {
        currentRoomName.textContent = displayName;

        // Update room icon and description
        const roomIcon = document.querySelector('.kim-room-icon');
        const roomSubtitle = document.querySelector('.kim-room-subtitle');
        if (roomIcon) roomIcon.textContent = icon;
        if (roomSubtitle) roomSubtitle.textContent = description || getRoomSubtitle(roomId);
    }

    // Apply room theme
    applyRoomTheme(roomId);

    // Clear messages and load new room
    messagesFeed.innerHTML = `<div class="kim-system-message">Welcome to ${displayName}! 🎉</div>`;
    socket.emit('join', { room: roomId });
}

// Room Theme Application
function applyRoomTheme(roomId) {
    if (chatArea) {
        // Remove existing room theme
        chatArea.removeAttribute('data-room');
        // Apply new theme
        chatArea.setAttribute('data-room', roomId);

        // Add room-specific animations
        chatArea.style.animation = 'none';
        setTimeout(() => {
            chatArea.style.animation = 'room-transition 0.5s ease';
        }, 10);
    }
}

// Get room subtitle
function getRoomSubtitle(roomId) {
    const subtitles = {
        'global': 'New beginnings',
        'inspiration': 'Creative sparks',
        'mindfulness': 'Peace & presence',
        'connections': 'Building bridges',
        'art': 'Express yourself',
        'writing': 'Words & wisdom',
        'music': 'Harmonious vibes',
        'learning': 'Knowledge journey',
        'goals': 'Goals & aspirations',
        'reflection': 'Inner peace'
    };
    return subtitles[roomId] || 'A special place';
}

// Initialize enhanced features
function initializeEnhancedFeatures() {
    initializeRoomCategories();
    initializeRoomCreation();
}

// Try to load existing keys on page load
window.addEventListener('DOMContentLoaded', async () => {
    const savedKey = await crypto.loadKeyPair();
    if (savedKey) {
        // Keys found - check if we can auto-connect
        // For now, still require nickname entry, but keys are loaded
        console.log("Loaded persisted keys from IndexedDB");
    }

    // Initialize enhanced features
    initializeEnhancedFeatures();
});

connectBtn.addEventListener('click', async () => {
    const nickname = nicknameInput.value.trim();
    if (!nickname) {
        alert("Please enter your name");
        return;
    }

    connectBtn.innerText = "Connecting...";
    connectBtn.disabled = true;

    try {
        // 1. Try to load existing keys, otherwise generate new ones
        let publicKey = await crypto.loadKeyPair();
        if (!publicKey) {
            publicKey = await crypto.generateKeyPair();
            console.log("Keys Generated");
        } else {
            console.log("Keys Loaded from IndexedDB");
        }

        // 2. Register with Server
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nickname: nickname,
                publicKey: publicKey
            })
        });

        if (!res.ok) {
            const errorText = await res.text();
            throw new Error(`Registration failed: ${res.status} ${errorText}`);
        }

        const data = await res.json();
        console.log("Registration response:", data);
        
        if (data.status === 'registered') {
            myUserId = data.userId;
            const nicknameEl = document.getElementById('my-nickname');
            if (nicknameEl) {
                nicknameEl.innerText = nickname.toUpperCase();
            }

            // 3. Enter App
            if (loginOverlay) loginOverlay.classList.add('hidden');
            if (mainInterface) mainInterface.classList.remove('hidden');

            // 4. Join Default Room
            // Set up initial room
            switchToRoom('global', 'Welcome', '💫', 'New beginnings');

            // 5. Load online users
            loadUsers();
        } else {
            throw new Error(`Registration failed: ${data.error || 'Unknown error'}`);
        }

    } catch (e) {
        console.error("KIM Init Error:", e);
        alert("Connection failed: " + (e.message || "Please try again."));
        connectBtn.innerText = "Connect";
        connectBtn.disabled = false;
    }
});

// --- User Management ---

async function loadUsers() {
    const res = await fetch('/api/users');
    const users = await res.json();
    userList.innerHTML = '';

    for (const u of users) {
        if (u.userId === myUserId) continue; // skip self

        knownUsers[u.userId] = u;

        // Import their public key & derive shared secret
        // Check if we already have this peer's key cached
        let peerKeyJWK = await crypto.loadPeerPublicKey(u.userId);
        if (!peerKeyJWK) {
            peerKeyJWK = u.publicKey;
        }
        
        try {
            const peerKey = await crypto.importPeerPublicKey(peerKeyJWK);
            await crypto.deriveSecretKey(peerKey, u.userId);

            // Render in Sidebar
            const li = document.createElement('li');
            li.className = 'contact-item';
            li.dataset.userId = u.userId;
            li.innerHTML = `
                <span class="contact-name">${u.nickname}</span>
                <span class="user-status-dot online"></span>
            `;
            li.addEventListener('click', () => startDirectMessage(u.userId, u.nickname));
            userList.appendChild(li);

        } catch (e) {
            console.error(`Failed to handshake with ${u.nickname}`, e);
        }
    }
}

// --- Messaging Logic ---

function startDirectMessage(userId, nickname) {
    // Switch UI context to direct message
    const roomName = [myUserId, userId].sort().join('_');
    switchToRoom(roomName, nickname, '👤', `Direct message with ${nickname}`);
}

// Set up room click handlers
function setupRoomHandlers() {
    document.querySelectorAll('.kim-conversation-item').forEach(item => {
        item.addEventListener('click', function() {
            const roomId = this.dataset.room;
            const roomName = this.querySelector('.kim-conversation-name').textContent;
            const roomIcon = this.querySelector('.kim-conversation-icon').textContent;
            const roomDesc = this.querySelector('.kim-room-desc')?.textContent || '';

            // Update active states
            document.querySelectorAll('.kim-conversation-item').forEach(item => item.classList.remove('active'));
            this.classList.add('active');

            switchToRoom(roomId, roomName, roomIcon, roomDesc);
        });
    });
}

// Initialize room handlers on page load
window.addEventListener('DOMContentLoaded', function() {
    setupRoomHandlers();
});


// Sending
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    // Determine target encryption
    // If global room, peerId = 'global'
    // If DM room (userId_userId), need to know WHO we are talking to.

    let targetPeerId = 'global';

    if (currentRoom !== 'global-relay') {
        // Extract the OTHER userId from the room string
        const parts = currentRoom.split('_');
        targetPeerId = parts.find(id => id !== myUserId);
    }

    try {
        const encrypted = await crypto.encryptMessage(text, targetPeerId);

        const payload = {
            room: currentRoom,
            encryptedContent: encrypted.ciphertext,
            iv: encrypted.iv,
            mode: encrypted.mode,
            senderId: myUserId,
            timestamp: new Date().toISOString()
        };

        socket.emit('encrypted_message', payload);
        messageInput.value = '';

        // Optimistic UI update? Or wait for relay?
        // Let's add it ourselves immediately as decrypted
        addMessageToFeed(text, true, 'You');

    } catch (e) {
        console.error("Encryption Error", e);
        alert("Unable to send message: " + e.message);
    }
}

// Incoming
socket.on('new_encrypted_message', async (data) => {
    if (data.senderId === myUserId) return; // We already showed ours

    // Decrypt
    let decText = "[Message]";
    try {
        // We know who sent it, do we have a shared secret established with SENDER?
        // Wait, for DM: we derived secret with Peer.
        // For Global: cleartext/mock.

        if (data.mode === 'CLEAR') {
            decText = atob(data.encryptedContent);
        } else {
            // It's a DM using our pairwise shared key
            // The key is stored under the peer's ID (which is the senderId here)
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

    // Identify Sender Nickname
    let senderName = "UNKNOWN";
    if (knownUsers[data.senderId]) senderName = knownUsers[data.senderId].nickname;

    addMessageToFeed(decText, false, senderName);
});

function addMessageToFeed(text, isSelf, senderName) {
    const div = document.createElement('div');
    div.className = `msg ${isSelf ? 'self' : 'peer'}`;

    div.innerHTML = `
        <div class="msg-meta">${senderName}</div>
        <div class="msg-bubble">${escapeHtml(text)}</div>
    `;

    messagesFeed.appendChild(div);
    messagesFeed.scrollTop = messagesFeed.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;
}
