# Authentication & Onboarding Implementation

## Overview

This document outlines the new authentication system that replaces hardcoded user data with proper onboarding, social login, and phone authentication.

## What's Been Implemented

### 1. OAuth Providers (`webapp/auth/oauth_providers.py`)
- **Google OAuth** - Full integration with Google Sign-In
- **Twitter/X OAuth** - OAuth 2.0 integration
- **GitHub OAuth** - GitHub authentication
- **Apple Sign In** - Apple authentication (requires JWT signing in production)

### 2. Phone Authentication (`webapp/auth/phone_auth.py`)
- SMS verification via Twilio (production) or dev mode (console logging)
- 6-digit verification codes
- 10-minute expiration
- Rate limiting (5 attempts max)
- Phone number normalization (E.164 format)

### 3. Onboarding UI (`public/auth.html`)
- Modern, clean authentication page
- Social login buttons (Google, Twitter, GitHub, Apple)
- Phone number authentication with SMS verification
- Email/password fallback
- Tab-based interface (Phone/Email)
- Error and success messaging
- Loading states

### 4. Server Endpoints (`webapp/server.py`)
- `/auth.html` - Authentication page
- `/api/auth/phone/send` - Send SMS verification code
- `/api/auth/phone/verify` - Verify code and create/login user
- `/api/auth/login` - Email/password login
- `/api/auth/<provider>` - Initiate OAuth flow
- `/api/auth/<provider>/callback` - Handle OAuth callback

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `pyjwt>=2.8.0` - JWT token handling
- `bcrypt>=4.0.0` - Password hashing
- `twilio>=8.0.0` - SMS service (optional, for production)

### 2. Environment Variables

Create a `.env` file or set environment variables:

```bash
# OAuth Providers (optional - only set what you want to use)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

APPLE_CLIENT_ID=your_apple_client_id
APPLE_CLIENT_SECRET=your_apple_client_secret

# OAuth Redirect Base URL
OAUTH_REDIRECT_BASE=https://yourdomain.com  # or http://localhost:5002 for dev

# SMS Service (Twilio - optional, works in dev mode without)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Flask Session Secret
FLASK_SECRET_KEY=your_random_secret_key_here
```

### 3. OAuth Provider Setup

#### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `https://yourdomain.com/api/auth/google/callback`

#### Twitter/X OAuth
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app
3. Set callback URL: `https://yourdomain.com/api/auth/twitter/callback`
4. Get Client ID and Client Secret

#### GitHub OAuth
1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create new OAuth App
3. Set Authorization callback URL: `https://yourdomain.com/api/auth/github/callback`

#### Apple Sign In
1. Go to [Apple Developer Portal](https://developer.apple.com/)
2. Create App ID and Service ID
3. Configure Sign in with Apple
4. Requires JWT signing (more complex setup)

### 4. Twilio Setup (Optional - for SMS)
1. Sign up at [Twilio](https://www.twilio.com/)
2. Get Account SID and Auth Token
3. Get a phone number
4. Set environment variables

**Note**: In development mode, SMS codes are logged to console instead of actually sent.

## What Still Needs to Be Done

### 1. Remove Hardcoded User Data
The following files still have hardcoded "Jack Danger" and "jacksonadanger":
- `public/index.html` - Sidebar profile
- `public/stream.html` - Sidebar profile  
- `public/profile.html` - Profile page
- `public/profile.js` - Profile JavaScript

**Fix**: These should load from user session/profile data instead.

### 2. Update Frontend to Check Auth
- Add auth check on app load
- Redirect to `/auth.html` if not authenticated
- Load user profile data from API instead of hardcoded values

### 3. User Profile Initialization
- Create default profile on first login
- Generate username from email/phone if not provided
- Set default display name

### 4. Session Management
- Add session expiration handling
- Add "Remember me" option
- Add logout functionality

### 5. Registration Flow
- Add signup option (currently only login)
- Email verification for email signup
- Username availability checking

## Usage Flow

### Phone Authentication
1. User enters phone number
2. System sends 6-digit SMS code
3. User enters code
4. System verifies and creates/logs in user
5. User redirected to main app

### OAuth Flow
1. User clicks "Continue with [Provider]"
2. Redirected to provider's login page
3. User authorizes
4. Provider redirects back with code
5. Server exchanges code for token
6. Server gets user info from provider
7. System creates/logs in user
8. User redirected to main app

### Email/Password
1. User enters email and password
2. System authenticates
3. User redirected to main app

## Security Considerations

1. **CSRF Protection**: OAuth uses state tokens
2. **Password Hashing**: bcrypt with salt
3. **JWT Tokens**: For session management (optional)
4. **Rate Limiting**: SMS verification has attempt limits
5. **Session Security**: Flask sessions with secret key

## Testing

### Development Mode
- Phone auth works without Twilio (logs to console)
- OAuth can be tested with local redirect URLs
- Email/password works immediately

### Production Mode
- Requires all OAuth credentials
- Requires Twilio for SMS (or alternative service)
- Requires HTTPS for OAuth callbacks

## Next Steps

1. **Remove hardcoded data** from frontend templates
2. **Add auth middleware** to protect routes
3. **Create user profile API** endpoints
4. **Add logout functionality**
5. **Add registration flow** for email signup
6. **Add password reset** functionality
7. **Add email verification** for email signups

