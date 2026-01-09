# Onboarding System Documentation

## Overview

The onboarding system is a **completely isolated module** that provides contextual tutorials, profile customization, and progressive guidance for new users. It's designed to be non-breaking and can be enabled/disabled without affecting the main application.

## Architecture

### Isolation Strategy

- **Separate Directory**: All onboarding code lives in `webapp/js/onboarding/`
- **Isolated CSS**: Styles in `webapp/css/onboarding.css` (won't conflict)
- **Feature Flags**: Can be enabled/disabled via localStorage or URL params
- **Progressive Enhancement**: App works perfectly without onboarding
- **Error Handling**: All errors are caught and logged, never break the app

### File Structure

```
webapp/
├── js/
│   └── onboarding/
│       ├── utils.js                    # Helper functions
│       ├── onboarding-manager.js       # Core orchestrator
│       ├── tutorials.js                # Tutorial definitions
│       ├── profile-customization.js   # Profile view differences
│       └── integration.js             # App integration
├── css/
│   └── onboarding.css                  # Isolated styles
└── onboarding.html                     # Standalone test page
```

## Features

### 1. Progressive Tutorials

Tutorials appear contextually based on user actions:

- **Welcome**: First visit introduction
- **Profile Setup**: When viewing profile page
- **Stream Navigation**: When on stream page
- **Explore**: When on explore/search page
- **KIM Chat**: When accessing messaging
- **Posting**: When creating first post
- **Profile Customization**: When editing profile

### 2. Profile Customization

**Own Profile View:**
- Edit buttons visible
- Private sections: Drafts, Analytics, Saved Posts, Settings
- Customization panel for layout control
- Preview toggle to see public view

**Others' Profile View:**
- Follow/Message buttons
- Public sections only
- Custom layout (if user customized it)
- No edit controls

### 3. Feature Flags

**Enable/Disable Methods:**

1. **URL Parameter**: `?onboarding=false`
2. **LocalStorage**: `localStorage.setItem('onboarding_enabled', 'false')`
3. **Environment Variable**: `ONBOARDING_ENABLED=false` (server-side)

**Default**: Enabled in dev mode (localhost), disabled in production

## Integration

### Minimal Integration Points

The system is integrated into existing pages with **single script tags**:

**profile.html:**
```html
<link rel="stylesheet" href="css/onboarding.css">
<script type="module" src="js/onboarding/integration.js"></script>
```

**stream.html:**
```html
<link rel="stylesheet" href="css/onboarding.css">
<script type="module" src="js/onboarding/integration.js"></script>
```

### Safe Integration

The integration script:
1. Checks if onboarding is enabled
2. Loads onboarding manager if enabled
3. Catches all errors (doesn't break app)
4. Can be removed without impact

## Testing

### Standalone Test Page

Visit `http://localhost:5002/onboarding.html` to test all features:

- Enable/disable onboarding
- Test individual tutorials
- Test profile customization
- View system status
- Reset progress

### Testing Checklist

- [ ] Onboarding can be enabled/disabled
- [ ] Tutorials appear contextually
- [ ] Profile customization works (own vs others)
- [ ] App works when onboarding is disabled
- [ ] No console errors when onboarding disabled
- [ ] Can remove onboarding files without breaking app

## API Endpoints

### Get Onboarding Status
```
GET /api/onboarding/status
Response: { "enabled": true, "configurable": true }
```

### Test Endpoint
```
GET /api/onboarding/test
Response: { "status": "ok", "message": "Onboarding system is accessible" }
```

## Usage

### For Developers

**Enable Onboarding:**
```javascript
import { OnboardingUtils } from './js/onboarding/utils.js';
OnboardingUtils.setEnabled(true);
```

**Disable Onboarding:**
```javascript
OnboardingUtils.setEnabled(false);
```

**Check Status:**
```javascript
const enabled = OnboardingUtils.isEnabled();
```

**Reset Progress:**
```javascript
localStorage.removeItem('onboarding_progress');
localStorage.removeItem('tutorials_completed');
```

### For Users

**Skip Tutorial:**
- Click "Skip" button on any tutorial

**Disable Onboarding:**
- Add `?onboarding=false` to URL
- Or set in browser console: `localStorage.setItem('onboarding_enabled', 'false')`

## Data Storage

All onboarding data is stored in localStorage:

- `onboarding_enabled`: Enable/disable flag
- `onboarding_progress`: User progress tracking
- `tutorials_completed`: List of completed tutorial IDs
- `profile_customization`: Profile layout settings

## Customization

### Adding New Tutorials

Edit `webapp/js/onboarding/tutorials.js`:

```javascript
this.register({
    id: 'my-tutorial',
    title: 'My Tutorial',
    content: ['Step 1', 'Step 2'],
    target: '.my-element', // Optional: element to highlight
    skippable: true,
    nextText: 'Got it'
});
```

### Customizing Profile Views

Edit `webapp/js/onboarding/profile-customization.js`:

- Modify `showOwnProfileView()` for own profile
- Modify `showOthersProfileView()` for others' profiles
- Add new private sections in `showPrivateSections()`

## Troubleshooting

### Onboarding Not Appearing

1. Check if enabled: `OnboardingUtils.isEnabled()`
2. Check console for errors
3. Verify script is loaded: Check Network tab
4. Check if tutorials already completed

### Tutorials Not Triggering

1. Reset progress: `localStorage.removeItem('tutorials_completed')`
2. Check page detection: `OnboardingUtils.getCurrentPage()`
3. Verify target elements exist

### Profile Customization Not Working

1. Verify on profile page: `OnboardingUtils.getCurrentPage() === 'profile'`
2. Check user ID: `OnboardingUtils.getCurrentUserId()`
3. Verify profile elements exist

## Removal

To completely remove onboarding:

1. Remove script tags from `profile.html` and `stream.html`
2. Remove CSS links
3. Delete `webapp/js/onboarding/` directory
4. Delete `webapp/css/onboarding.css`
5. Delete `webapp/onboarding.html` (test page)

**The app will continue to work normally.**

## Future Enhancements

- [ ] Analytics tracking for tutorial completion
- [ ] A/B testing different tutorial flows
- [ ] User feedback collection
- [ ] Advanced profile customization options
- [ ] Multi-language support
- [ ] Video tutorials

## Support

For issues or questions:
1. Check `onboarding.html` test page
2. Review browser console logs
3. Check `ONBOARDING_SYSTEM.md` (this file)
4. Verify feature flags are set correctly

