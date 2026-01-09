# KIM Integration Points

**Date:** 2025-01-XX  
**Purpose:** Document where and how to integrate KIM into the main Katanx platform

## Current Notes Section Location

### HTML Structure
**File:** `webapp/stream.html`  
**Lines:** 758-774

```html
<!-- Star Notepad Button - Far Right -->
<button class="star-notepad-btn" id="starNotepadBtn" aria-label="Notes">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
    </svg>
</button>

<!-- Star Notepad Panel -->
<div class="notepad-panel" id="starNotepadPanel">
    <div class="notepad-header">
        <h3>Notes</h3>
        <button class="notepad-close" id="notepadClose" aria-label="Close">×</button>
    </div>
    <textarea class="notepad-textarea" id="notepadTextarea"
        placeholder="Your notes here... They persist across pages."></textarea>
</div>
```

### JavaScript Initialization
**Files with Notes initialization:**
- `webapp/app.js` - Lines 3563-3605: `initStarNotepad()` function
- `webapp/js/modules/effects.js` - Lines 94-103: `initStarNotepad()` method
- `webapp/js/app-modular.js` - Line 57: Calls `Effects.initStarNotepad()`
- `webapp/js/base.js` - Line 16: Calls `Effects.initStarNotepad()`

### CSS Styling
**File:** `webapp/styles.css`
- Lines 897-923: `.star-notepad-btn` styles
- Lines 930-997: `.notepad-panel` styles
- Line 6862: Mobile responsive styles

### Other Files with Notes
- `webapp/index.html` - Lines 174-190
- `webapp/app.html` - Lines 175-190
- `webapp/contexts.html` - Lines 107-121
- `webapp/components/header.html` - Lines 38-52

## Integration Strategy

### Option 1: Direct Replacement (Recommended)
Replace the Notes panel with KIM panel in the same location.

**Steps:**
1. Remove Notes HTML from `stream.html` (lines 758-774)
2. Add KIM panel HTML in same location
3. Update button ID and classes to KIM-specific
4. Remove Notes initialization from JavaScript files
5. Add KIM initialization
6. Update CSS to use KIM styles (or merge with existing)

### Option 2: Toggle Between Notes and KIM
Keep both, allow users to switch between Notes and KIM.

**Steps:**
1. Add toggle button/selector
2. Keep both panels in DOM
3. Show/hide based on selection
4. Initialize both systems

### Option 3: Separate Button
Add KIM as separate button next to Notes button.

**Steps:**
1. Add new KIM button next to Notes button
2. Add KIM panel as separate slide-out
3. Both systems coexist
4. Different button icons/colors

## Recommended Approach: Option 1 (Direct Replacement)

### Rationale
- KIM provides encrypted messaging (more valuable than simple notes)
- Reduces UI clutter
- Notes functionality can be achieved via KIM DMs to self
- Maintains same UX pattern (slide-out panel)

### Implementation Plan

#### Step 1: HTML Replacement
**File:** `webapp/stream.html`

**Remove:**
```html
<button class="star-notepad-btn" id="starNotepadBtn" aria-label="Notes">
    <!-- SVG icon -->
</button>
<div class="notepad-panel" id="starNotepadPanel">
    <!-- Notes content -->
</div>
```

**Replace with:**
```html
<button class="kim-toggle-btn" id="kimToggleBtn" aria-label="KIM Messages">
    <!-- KIM icon (similar to current, or use lock/chat icon) -->
</button>
<div class="kim-panel" id="kimPanel">
    <!-- KIM interface (sidebar + chat area, or simplified version) -->
</div>
```

#### Step 2: JavaScript Updates

**Files to modify:**
1. `webapp/app.js` - Remove `initStarNotepad()` call, add KIM init
2. `webapp/js/modules/effects.js` - Remove `initStarNotepad()`, add KIM init
3. `webapp/js/app-modular.js` - Update initialization
4. `webapp/js/base.js` - Update initialization

**New KIM initialization:**
```javascript
function initKIM() {
    const kimBtn = document.getElementById('kimToggleBtn');
    const kimPanel = document.getElementById('kimPanel');
    const kimClose = document.getElementById('kimClose');
    
    if (!kimBtn || !kimPanel) return;
    
    // Load KIM scripts if not already loaded
    if (!window.KIMCrypto) {
        loadKIMScripts();
    }
    
    // Toggle panel
    kimBtn.addEventListener('click', () => {
        kimPanel.classList.toggle('open');
    });
    
    // Close panel
    kimClose?.addEventListener('click', () => {
        kimPanel.classList.remove('open');
    });
}
```

#### Step 3: CSS Updates

**File:** `webapp/styles.css`

**Option A:** Replace Notes styles with KIM styles
- Remove `.star-notepad-btn` and `.notepad-panel` styles
- Add `.kim-toggle-btn` and `.kim-panel` styles
- Import or copy from `webapp/css/kim.css`

**Option B:** Keep existing panel styles, adapt KIM to use them
- Reuse `.notepad-panel` structure
- Add KIM-specific overrides

#### Step 4: Server Integration

**File:** `webapp/server.py`

**Add KIM routes and SocketIO:**
```python
from flask_socketio import SocketIO, emit, join_room

# Initialize SocketIO (if not already)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Add KIM routes from kim_server.py
@app.route('/api/kim/register', methods=['POST'])
def kim_register():
    # Copy from kim_server.py register_user()
    pass

@app.route('/api/kim/users', methods=['GET'])
def kim_users():
    # Copy from kim_server.py get_users()
    pass

# Add SocketIO events
@socketio.on('kim_join')
def on_kim_join(data):
    # Copy from kim_server.py on_join()
    pass

@socketio.on('kim_encrypted_message')
def handle_kim_message(data):
    # Copy from kim_server.py handle_encrypted_message()
    pass
```

## Integration Points Summary

### Files to Modify

**HTML:**
- `webapp/stream.html` - Replace Notes section with KIM panel
- `webapp/index.html` - Update if Notes present
- `webapp/app.html` - Update if Notes present
- `webapp/contexts.html` - Update if Notes present
- `webapp/components/header.html` - Update if Notes present

**JavaScript:**
- `webapp/app.js` - Remove Notes init, add KIM init
- `webapp/js/modules/effects.js` - Remove Notes method, add KIM method
- `webapp/js/app-modular.js` - Update initialization
- `webapp/js/base.js` - Update initialization
- `webapp/js/kim-ui.js` - Adapt for embedded mode (remove standalone login)
- `webapp/js/kim-crypto.js` - No changes needed

**CSS:**
- `webapp/styles.css` - Replace/update Notes styles
- `webapp/css/kim.css` - May need adjustments for embedded mode

**Python:**
- `webapp/server.py` - Add KIM routes and SocketIO events
- `webapp/kim_server.py` - Can be removed after integration (or kept for standalone testing)

### Key Considerations

1. **Authentication:** KIM currently uses nickname-only. Need to integrate with Katanx user system.
2. **User IDs:** KIM uses public key hash as user ID. Need mapping to Katanx user IDs.
3. **Panel Size:** KIM full interface may be too large for slide-out. Consider simplified version.
4. **SocketIO:** Main server may already have SocketIO. Need to check for conflicts.
5. **Port:** KIM currently runs on 5001. Integration uses main server port.
6. **State Management:** KIM state (current room, users) needs to persist across page navigation.

## Simplified KIM Panel Design

For embedded mode, consider a simplified KIM interface:

**Layout:**
- Compact sidebar (contacts list only)
- Main chat area (messages + input)
- Remove login overlay (use Katanx auth)
- Remove global room (DMs only)

**Features:**
- Show unread message count on button
- Quick access to recent conversations
- Minimal UI to fit slide-out panel

## Testing Plan

1. **Unit Tests:**
   - Test KIM crypto functions in embedded context
   - Test panel open/close
   - Test message sending/receiving

2. **Integration Tests:**
   - Test with Katanx authentication
   - Test message persistence
   - Test multi-user scenarios

3. **UI Tests:**
   - Test panel animation
   - Test responsive design
   - Test keyboard shortcuts

## Migration Path

1. **Phase 1:** Keep both Notes and KIM (toggle)
2. **Phase 2:** Make KIM default, Notes optional
3. **Phase 3:** Remove Notes, KIM only

This allows users to migrate gradually and provides fallback.

