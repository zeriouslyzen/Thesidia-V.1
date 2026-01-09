# Authentication Mock Testing Guide

## Overview

Mock testing mode is enabled for local development, allowing you to test the complete authentication flow without requiring external services (OAuth providers, SMS services, etc.).

## Features Enabled in Mock Mode

### ✅ Phone Authentication (SMS)
- **Status**: Fully functional
- **How it works**: 
  - Enter any phone number
  - Click "Send Verification Code"
  - The 6-digit code is displayed:
    - In the browser console
    - In the server terminal logs
    - In the success message (if enabled)
- **Example**: Enter `+1 (555) 123-4567`, code will be shown as `123456`

### ✅ Email/Password Authentication
- **Status**: Fully functional
- **How it works**:
  - Enter any email and password
  - Click "Sign In"
  - If account doesn't exist, it auto-creates one
  - If account exists, it logs you in
- **No password requirements** in mock mode (can use any password)

### ✅ OAuth Providers (Google, Twitter/X, GitHub, Apple)
- **Status**: Mock flow enabled
- **How it works**:
  - Click any OAuth button (e.g., "Continue with Google")
  - Shows mock success message
  - Automatically creates a mock user session
  - Redirects to main app after 1.5 seconds

## Testing the Auth Flow

### 1. Access the Auth Page
```
http://localhost:5002/auth.html
```

### 2. Visual Indicators
- **Mock Mode Badge**: Yellow indicator in top-right corner
- **Header Message**: "Mock Testing Mode - No external services required"

### 3. Test Phone Auth
1. Click "Phone" tab
2. Select country code (default: +1)
3. Enter phone number: `5551234567`
4. Click "Send Verification Code"
5. **Check console/terminal for code** (e.g., `123456`)
6. Enter code in verification field
7. Click "Verify & Sign In"
8. Should redirect to main app

### 4. Test Email Auth
1. Click "Email" tab
2. Enter email: `test@example.com`
3. Enter password: `password123` (any password works)
4. Click "Sign In"
5. First time: Creates account
6. Subsequent times: Logs in
7. Should redirect to main app

### 5. Test OAuth
1. Click any OAuth button (e.g., "Continue with Google")
2. See mock success message
3. Wait 1.5 seconds
4. Should redirect to main app with mock session

## Mock Mode Detection

Mock mode is automatically enabled when:
- Running on `localhost` or `127.0.0.1`
- `DEV_MODE=true` (default)

To disable mock mode (use real auth):
```bash
export PROD_MODE=true
export DEV_MODE=false
```

## API Endpoints

### Phone Auth
```bash
# Send code
POST /api/auth/phone/send
Body: {"phone": "+15551234567"}
Response: {"success": true, "verification_id": "...", "mock_code": "123456"}

# Verify code
POST /api/auth/phone/verify
Body: {"verification_id": "...", "code": "123456"}
Response: {"success": true, "user_id": "...", "session_id": "..."}
```

### Email Auth
```bash
# Register/Login
POST /api/auth/register
POST /api/auth/login
Body: {"email": "test@example.com", "password": "password123"}
Response: {"user_id": "...", "session_id": "...", "token": "..."}
```

### OAuth
```bash
# Mock OAuth (dev mode)
GET /api/auth/google
GET /api/auth/twitter
GET /api/auth/github
GET /api/auth/apple
```

## Session Storage

After successful authentication, sessions are stored in:
- `localStorage.thesidia_user_id`
- `localStorage.thesidia_session_id`
- `localStorage.thesidia_token` (if JWT enabled)
- `localStorage.thesidia_oauth_provider` (if OAuth)

## Troubleshooting

### Auth page redirects immediately
- **Issue**: Old code still has dev bypass
- **Fix**: Clear browser cache or hard refresh (Cmd+Shift+R)

### SMS code not showing
- **Check**: Server terminal logs
- **Check**: Browser console (F12)
- **Verify**: Phone auth manager is initialized

### OAuth buttons don't work
- **Check**: Mock mode indicator is visible
- **Check**: Browser console for errors
- **Verify**: OAuth mock handler is loaded

## Production Deployment

To enable real authentication in production:

1. **Set environment variables**:
   ```bash
   export PROD_MODE=true
   export DEV_MODE=false
   ```

2. **Configure OAuth providers** (at least one):
   ```bash
   export GOOGLE_CLIENT_ID=your_id
   export GOOGLE_CLIENT_SECRET=your_secret
   # ... etc for other providers
   ```

3. **Configure SMS provider** (for phone auth):
   ```bash
   export TWILIO_ACCOUNT_SID=your_sid
   export TWILIO_AUTH_TOKEN=your_token
   export TWILIO_PHONE_NUMBER=+1234567890
   ```

4. **Restart server**

## Notes

- Mock mode is **safe for development** - no real SMS sent, no real OAuth calls
- All user data is stored locally in `data/auth/` directory
- Passwords are hashed even in mock mode (using bcrypt)
- Sessions persist across server restarts (stored in localStorage + server files)

