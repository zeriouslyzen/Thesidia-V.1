# Settings Guide

## Overview

Thesidia provides comprehensive settings management across 6 categories: Account, Security, Privacy, Notifications, Content, and Advanced.

## Settings Pages

### Account Settings (`/settings/account.html`)

**Features**:
- Profile picture upload
- Username management
- Display name
- Bio (500 character limit)
- Location
- Website URL

**Validation**:
- Username: 3-30 characters, alphanumeric + underscore/hyphen
- Bio: Max 500 characters
- Website: Valid URL format

### Security Settings (`/settings/security.html`)

**Features**:
- Password change (requires current password)
- Two-factor authentication toggle
- Active sessions list
- Login history

**Password Requirements** (Production):
- Minimum 12 characters
- Must contain letters and numbers
- Password strength indicator

### Privacy Settings (`/settings/privacy.html`)

**Features**:
- Profile visibility (public, followers, private)
- Show online status toggle
- Direct messages toggle
- Blocked users list
- Muted users list

### Notification Settings (`/settings/notifications.html`)

**Features**:
- Email notifications toggle
- Push notifications toggle
- In-app notifications:
  - Mentions
  - New followers
  - Likes
  - Comments
  - Reposts

### Content Settings (`/settings/content.html`)

**Features**:
- Auto-play videos toggle
- Content filter level (none, moderate, strict)
- Language selection
- Timezone selection

### Advanced Settings (`/settings/advanced.html`)

**Features**:
- API key management
- Data export (JSON download)
- Account deletion

## Settings Storage

Settings are stored in `data/users/{user_id}/settings.json`:

```json
{
  "user_id": "user_xyz",
  "account": {...},
  "privacy": {...},
  "notifications": {...},
  "content": {...},
  "security": {...},
  "created_at": "2025-01-26T00:00:00Z",
  "updated_at": "2025-01-26T00:00:00Z"
}
```

## Settings API

All settings can be accessed via REST API:

- `GET /api/settings` - Get all settings
- `POST /api/settings/{section}` - Update specific section

## Settings Migration

Settings automatically migrate to new schema versions when loaded. Missing fields are populated with defaults.

## Default Settings

New users receive default settings:
- Profile visibility: Public
- DM enabled: True
- Show online status: True
- Push notifications: Enabled
- Content filter: Moderate
- Language: English
- Timezone: UTC

