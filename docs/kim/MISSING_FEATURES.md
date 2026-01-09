# KIM Missing Features for Production

**Date:** 2025-01-XX  
**Purpose:** Comprehensive list of features needed to bring KIM from prototype to production

## Critical Features (Must Have)

### 1. Message Persistence
**Status:** ❌ Not Implemented  
**Priority:** CRITICAL  
**Description:** Messages are currently stored in-memory on server. Lost on server restart.

**Requirements:**
- Database storage for messages (SQLite, PostgreSQL, or Supabase)
- Message history retrieval on reconnect
- Message pagination for long conversations
- Message deletion/archival

**Implementation:**
- Add database schema for messages table
- Store encrypted message blobs (server can't decrypt)
- Store metadata: room_id, sender_id, timestamp, message_id
- Add API endpoint: `GET /api/kim/messages/:roomId?limit=50&offset=0`
- Load message history when joining room

**Files to Create/Modify:**
- `webapp/kim/storage.py` - Database models and queries
- `webapp/kim_server.py` - Add message persistence
- `webapp/js/kim-ui.js` - Load message history on room join

### 2. User Authentication Integration
**Status:** ❌ Not Implemented  
**Priority:** CRITICAL  
**Description:** Currently uses nickname-only registration. No integration with Katanx auth.

**Requirements:**
- Link KIM users to Katanx user accounts
- Use Katanx user IDs instead of public key hashes
- Authenticate via Katanx session/auth system
- Map Katanx user profiles to KIM identities

**Implementation:**
- Modify registration to require Katanx auth token
- Store Katanx user ID with KIM identity
- Use Katanx user display names/avatars
- Link to Katanx user profiles from KIM

**Files to Create/Modify:**
- `webapp/kim_server.py` - Add auth middleware
- `webapp/js/kim-ui.js` - Use Katanx auth session
- `webapp/middleware/user_auth.py` - Extend for KIM

### 3. Group Encryption (Sender Keys Protocol)
**Status:** ❌ Not Implemented  
**Priority:** HIGH  
**Description:** Global room uses cleartext. Need proper group encryption.

**Requirements:**
- Implement Sender Keys protocol (Signal-style)
- Encrypt group messages properly
- Handle key rotation
- Support for multiple group rooms

**Implementation:**
- Research and implement Sender Keys protocol
- Store group keys in IndexedDB
- Handle key distribution on room join
- Rotate keys periodically

**Files to Create/Modify:**
- `webapp/js/kim-crypto.js` - Add Sender Keys methods
- `webapp/js/kim-ui.js` - Handle group key exchange

## Important Features (Should Have)

### 4. Typing Indicators
**Status:** ❌ Not Implemented  
**Priority:** MEDIUM  
**Description:** Show when other users are typing.

**Requirements:**
- SocketIO event: `typing_start`, `typing_stop`
- UI indicator in chat area
- Timeout after inactivity

**Implementation:**
- Add typing events to `kim_server.py`
- Add typing UI to `kim.html`
- Debounce typing detection in `kim-ui.js`

### 5. Read Receipts
**Status:** ❌ Not Implemented  
**Priority:** MEDIUM  
**Description:** Show when messages have been read.

**Requirements:**
- Track message read status
- Store read receipts (encrypted)
- Display read indicators

**Implementation:**
- Add read receipt events
- Store in database
- Update UI with read status

### 6. File/Media Sharing
**Status:** ❌ Not Implemented  
**Priority:** MEDIUM  
**Description:** Support for sharing images, files, etc.

**Requirements:**
- File upload endpoint
- Encrypted file storage
- File download/decryption
- Image preview in chat

**Implementation:**
- Add file upload to server
- Encrypt files before storage
- Add file message type
- UI for file sharing

### 7. Message Search
**Status:** ❌ Not Implemented  
**Priority:** MEDIUM  
**Description:** Search through message history.

**Requirements:**
- Client-side search (decrypt then search)
- Search within room/conversation
- Highlight search results

**Implementation:**
- Load message history
- Decrypt messages
- Client-side search
- UI search interface

### 8. Notifications
**Status:** ❌ Not Implemented  
**Priority:** MEDIUM  
**Description:** Browser notifications for new messages.

**Requirements:**
- Request notification permission
- Show notifications for new messages
- Notification settings
- Do Not Disturb mode

**Implementation:**
- Use Web Notifications API
- Add notification settings
- Respect user preferences

## Nice to Have Features

### 9. Message Reactions
**Status:** ❌ Not Implemented  
**Priority:** LOW  
**Description:** React to messages with emoji (or text reactions).

**Requirements:**
- Store reactions (encrypted)
- Display reactions on messages
- Multiple reactions per message

### 10. Message Editing
**Status:** ❌ Not Implemented  
**Priority:** LOW  
**Description:** Edit sent messages.

**Requirements:**
- Mark messages as edited
- Store edit history
- UI for editing

### 11. Message Threading
**Status:** ❌ Not Implemented  
**Priority:** LOW  
**Description:** Reply to specific messages, create threads.

**Requirements:**
- Link messages to parent
- Display threaded conversations
- Thread navigation

### 12. Voice Messages
**Status:** ❌ Not Implemented  
**Priority:** LOW  
**Description:** Record and send voice messages.

**Requirements:**
- Audio recording API
- Audio encryption
- Audio playback

### 13. Video Calls
**Status:** ❌ Not Implemented  
**Priority:** LOW  
**Description:** Video calling capability.

**Requirements:**
- WebRTC integration
- Signaling via SocketIO
- Video encryption

### 14. Message Status Indicators
**Status:** ❌ Not Implemented  
**Priority:** LOW  
**Description:** Show sent, delivered, read status.

**Requirements:**
- Track message delivery
- Visual indicators
- Status updates

## Technical Improvements

### 15. Key Rotation
**Status:** ❌ Not Implemented  
**Priority:** MEDIUM  
**Description:** Periodically rotate encryption keys.

**Requirements:**
- Key rotation protocol
- Re-encrypt messages (optional)
- Handle key rotation gracefully

### 16. Offline Support
**Status:** ❌ Not Implemented  
**Priority:** MEDIUM  
**Description:** Queue messages when offline, send when online.

**Requirements:**
- Service Worker for offline detection
- Message queue in IndexedDB
- Sync on reconnect

### 17. Multi-Device Support
**Status:** ❌ Not Implemented  
**Priority:** LOW  
**Description:** Sync keys and messages across devices.

**Requirements:**
- Key sync protocol
- Message sync
- Device management

### 18. Message Encryption Audit
**Status:** ⚠️ Partial  
**Priority:** HIGH  
**Description:** Audit and verify encryption implementation.

**Requirements:**
- Security audit
- Penetration testing
- Encryption verification
- Document security model

### 19. Performance Optimization
**Status:** ⚠️ Needs Work  
**Priority:** MEDIUM  
**Description:** Optimize for large message histories.

**Requirements:**
- Virtual scrolling for messages
- Lazy loading
- Message pagination
- Efficient encryption/decryption

### 20. Error Handling
**Status:** ⚠️ Basic  
**Priority:** MEDIUM  
**Description:** Comprehensive error handling and recovery.

**Requirements:**
- Network error handling
- Decryption failure recovery
- Connection retry logic
- User-friendly error messages

## Integration Features

### 21. Katanx Profile Integration
**Status:** ❌ Not Implemented  
**Priority:** HIGH  
**Description:** Show Katanx user profiles in KIM.

**Requirements:**
- Link KIM users to Katanx profiles
- Display profile pictures
- Show profile information
- Link to full profile

### 22. Katanx Feed Integration
**Status:** ❌ Not Implemented  
**Priority:** LOW  
**Description:** Share Katanx posts in KIM.

**Requirements:**
- Share post links
- Preview posts
- Link to original post

### 23. Embedded Mode
**Status:** ❌ Not Implemented  
**Priority:** HIGH  
**Description:** KIM as embedded panel in stream.html.

**Requirements:**
- Simplified UI for panel
- Remove login overlay
- Compact layout
- Panel animations

## Testing & Quality

### 24. Unit Tests
**Status:** ❌ Not Implemented  
**Priority:** HIGH  
**Description:** Automated tests for crypto and UI.

**Requirements:**
- Test encryption/decryption
- Test key exchange
- Test UI functions
- Test error cases

**Files to Create:**
- `tests/test_kim_crypto.js`
- `tests/test_kim_ui.js`
- `tests/test_kim_server.py`

### 25. Integration Tests
**Status:** ❌ Not Implemented  
**Priority:** MEDIUM  
**Description:** End-to-end testing.

**Requirements:**
- Multi-user scenarios
- Message flow testing
- Error recovery testing
- Performance testing

### 26. Documentation
**Status:** ⚠️ Partial  
**Priority:** MEDIUM  
**Description:** Complete user and developer documentation.

**Requirements:**
- User guide
- Developer API docs
- Security documentation
- Architecture diagrams

## Priority Summary

### Phase 1 (Critical - Launch Blockers)
1. Message Persistence
2. User Authentication Integration
3. Embedded Mode
4. Unit Tests

### Phase 2 (Important - Post-Launch)
5. Group Encryption (Sender Keys)
6. Typing Indicators
7. Read Receipts
8. Katanx Profile Integration
9. Performance Optimization

### Phase 3 (Enhancements)
10. File/Media Sharing
11. Message Search
12. Notifications
13. Message Reactions
14. Offline Support

### Phase 4 (Future)
15. Voice Messages
16. Video Calls
17. Multi-Device Support
18. Message Threading
19. Message Editing

## Implementation Estimates

- **Message Persistence:** 2-3 days
- **Auth Integration:** 1-2 days
- **Embedded Mode:** 2-3 days
- **Group Encryption:** 5-7 days (complex)
- **Typing Indicators:** 1 day
- **Read Receipts:** 2 days
- **File Sharing:** 3-4 days
- **Unit Tests:** 2-3 days

**Total Phase 1:** ~8-11 days  
**Total Phase 2:** ~15-20 days  
**Total All Phases:** ~40-50 days

## Notes

- Some features may be simplified for MVP
- Security features (encryption audit) should be prioritized
- User experience features (typing, read receipts) improve engagement
- Integration features enable seamless Katanx experience

