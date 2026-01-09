# KIM (Killer Instant Messaging) Documentation

**Status:** Prototype Complete, Production Features Pending  
**Last Updated:** 2025-01-XX

## Overview

KIM is an end-to-end encrypted messaging system built for the Katanx platform. It provides secure direct messaging (DMs) and chat room functionality using ECDH key exchange and AES-GCM encryption.

## Quick Links

- [Implementation Review](IMPLEMENTATION_REVIEW.md) - What's implemented, what differs from plan, fixes applied
- [Integration Points](INTEGRATION_POINTS.md) - How to integrate KIM into main Katanx platform
- [Missing Features](MISSING_FEATURES.md) - Comprehensive list of features needed for production

## Current Status

### ✅ Implemented
- End-to-end encryption (ECDH-P256 + AES-GCM)
- Direct messaging between users
- Global chat room (prototype, cleartext)
- Real-time messaging via SocketIO
- Key persistence (IndexedDB)
- Standalone server on port 5001
- Dark mode UI matching Katanx aesthetic

### ⚠️ Needs Work
- Message persistence (database storage)
- User authentication integration
- Group encryption (Sender Keys protocol)
- Embedded mode for stream.html

### ❌ Not Implemented
- Typing indicators
- Read receipts
- File/media sharing
- Message search
- Notifications
- Integration with Katanx profiles

## Architecture

### Components
- **Backend:** `webapp/kim_server.py` - Flask + SocketIO server
- **Frontend:** `webapp/kim.html` - Standalone UI
- **Crypto:** `webapp/js/kim-crypto.js` - Web Crypto API implementation
- **UI Logic:** `webapp/js/kim-ui.js` - Client-side logic
- **Styling:** `webapp/css/kim.css` - Dark theme styles

### Encryption Flow
1. User generates ECDH key pair (P-256)
2. Public key shared with server
3. Peer discovery and key exchange
4. Shared secret derived via ECDH
5. Messages encrypted with AES-GCM
6. Server relays encrypted blobs (cannot decrypt)

### Key Persistence
- Key pairs stored in IndexedDB
- Peer public keys cached
- Automatic loading on page refresh
- Keys persist across browser sessions

## Testing

### Manual Testing
1. Start server: `python3 webapp/kim_server.py`
2. Open `http://localhost:5001` in two browser windows
3. Register users in both windows
4. Send encrypted DMs
5. Verify encryption (check server logs)
6. Refresh browsers - keys should persist

### Test Checklist
- [x] Server starts successfully
- [x] UI loads correctly
- [x] Key generation works
- [x] User registration works
- [x] User discovery works
- [x] DM encryption works
- [x] Message relay works
- [x] Key persistence works
- [ ] Message history (needs database)
- [ ] Auth integration (not started)

## Next Steps

### Immediate (Phase 1)
1. Implement message persistence (database)
2. Integrate with Katanx authentication
3. Create embedded mode for stream.html
4. Write unit tests

### Short Term (Phase 2)
1. Implement Sender Keys for group encryption
2. Add typing indicators
3. Add read receipts
4. Integrate Katanx profiles

### Long Term (Phase 3)
1. File/media sharing
2. Message search
3. Notifications
4. Offline support

## Files Structure

```
webapp/
├── kim_server.py          # Standalone server
├── kim.html               # Standalone UI
├── js/
│   ├── kim-crypto.js      # Encryption implementation
│   └── kim-ui.js          # UI logic
└── css/
    └── kim.css            # Styling

docs/kim/
├── README.md              # This file
├── IMPLEMENTATION_REVIEW.md
├── INTEGRATION_POINTS.md
└── MISSING_FEATURES.md
```

## Security Notes

- **Encryption:** ECDH-P256 key exchange, AES-GCM encryption
- **Key Storage:** IndexedDB (browser-specific, consider additional encryption)
- **Server Role:** Relay only - cannot decrypt messages
- **Global Room:** Currently cleartext (prototype limitation)
- **Key Rotation:** Not implemented (future feature)

## Dependencies

### Python
- flask
- flask-socketio
- flask-cors
- eventlet

### JavaScript
- Socket.IO client (CDN)
- Web Crypto API (browser native)
- IndexedDB (browser native)

## License

[Add license information]

## Contributing

[Add contribution guidelines]

