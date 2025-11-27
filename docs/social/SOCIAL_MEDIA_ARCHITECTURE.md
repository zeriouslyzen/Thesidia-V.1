# Social Media Architecture

## Overview

Thesidia's social media platform is built as a lightweight, AI-first system with JSON-based storage, comprehensive security infrastructure, and quality-focused content curation.

## Architecture Components

### 1. Security Infrastructure

**Location**: `webapp/config/`, `webapp/auth/`, `webapp/middleware/`

- **Security Configuration** (`config/security.py`): Environment-based security flags (DEV_MODE, PROD_MODE)
- **Authentication** (`auth/auth_manager.py`, `auth/session_manager.py`): JWT tokens, password hashing, session management (disabled in dev)
- **Security Middleware** (`middleware/security.py`, `middleware/rate_limiter.py`): CSRF protection, input sanitization, rate limiting

### 2. Database Schema

**Location**: `data/social/`, `webapp/social/schema.py`

- **Posts**: `data/social/posts/{post_id}.json`
- **User Profiles**: `data/users/{user_id}/profile.json`
- **Social Graph**: `data/users/{user_id}/social.json`
- **Settings**: `data/users/{user_id}/settings.json`
- **Indexes**: `data/social/indexes/` (posts_by_user, posts_by_date, posts_by_score, users_by_username)

### 3. Social Features

**Location**: `webapp/social/`

- **Post Manager** (`post_manager.py`): Create, update, delete posts with content sanitization
- **Feed Manager** (`feed_manager.py`): Chronological, quality, and personalized feeds
- **Feed Ranker** (`feed_ranker.py`): AI-powered feed ranking (quality, relevance, recency, diversity)
- **Social Graph** (`social_graph.py`): Follow/unfollow, blocking, muting
- **Interaction Manager** (`interaction_manager.py`): Likes, comments, reposts, views
- **AI Quality Scorer** (`ai_quality_scorer.py`): Multi-factor quality scoring
- **Bot Detector** (`bot_detector.py`): Multi-signal bot detection
- **Moderation Manager** (`moderation_manager.py`): Content moderation, user reporting

### 4. Settings System

**Location**: `webapp/settings/`

- **Settings Pages**: Account, Security, Privacy, Notifications, Content, Advanced
- **Settings Manager** (`settings_manager.py`): Load/save settings with validation
- **Settings API**: RESTful endpoints for all settings sections

### 5. API Endpoints

**Location**: `webapp/server.py`

**Social Endpoints**:
- `POST /api/posts` - Create post
- `GET /api/posts/{post_id}` - Get post
- `DELETE /api/posts/{post_id}` - Delete post
- `GET /api/feed` - Get feed (chronological, quality, personalized)
- `POST /api/posts/{post_id}/like` - Like/unlike post
- `POST /api/posts/{post_id}/comment` - Comment on post
- `POST /api/users/{user_id}/follow` - Follow/unfollow user
- `GET /api/users/{user_id}/profile` - Get user profile

**Settings Endpoints**:
- `GET /api/settings` - Get all settings
- `POST /api/settings/account` - Update account settings
- `POST /api/settings/security` - Update security settings
- `POST /api/settings/privacy` - Update privacy settings
- `POST /api/settings/notifications` - Update notification settings
- `POST /api/settings/content` - Update content settings

## Data Flow

### Post Creation Flow

1. User submits post via `/api/posts`
2. Content sanitized (XSS prevention)
3. Post created and saved to `data/social/posts/{post_id}.json`
4. Indexes updated (posts_by_user, posts_by_date, posts_by_score)
5. AI quality scoring applied
6. Bot detection run
7. Moderation status determined
8. Feed cache invalidated
9. Post returned to client

### Feed Generation Flow

1. User requests feed via `/api/feed`
2. Check feed cache (5-minute TTL)
3. If cache miss:
   - Get posts based on feed type (chronological/quality/personalized)
   - Filter blocked/muted users
   - Rank posts (if personalized)
   - Cache results
4. Add interactions to each post
5. Return feed to client

### AI Quality Scoring

1. Content length analysis (optimal: 100-500 chars)
2. Spam detection (keywords, links, capitalization)
3. Content uniqueness check
4. Engagement quality ratio
5. User reputation score
6. Sentiment balance
7. Weighted average (0-1 score)

### Bot Detection

1. Post frequency analysis
2. Content repetition check
3. Engagement pattern analysis
4. Network anomaly detection (follower ratios)
5. Account age verification
6. Weighted bot probability (0-1)

## Security Model

### Development Mode (Default)

- Authentication: Disabled
- CSRF Protection: Disabled
- Rate Limiting: Enabled (relaxed: 1000/min)
- Input Validation: Basic
- Security Headers: Disabled

### Production Mode

- Authentication: Required (JWT tokens)
- CSRF Protection: Enabled
- Rate Limiting: Strict (100/min, 1000/hour)
- Input Validation: Strict
- Security Headers: Enabled (CSP, HSTS, etc.)

## Performance Optimizations

1. **Feed Caching**: 5-minute TTL per user/feed type
2. **Index Files**: Fast lookups for posts by user, date, score
3. **Lazy Loading**: Frontend uses Intersection Observer
4. **Incremental Updates**: Only fetch new posts since last check
5. **JSON Storage**: Lightweight, no database overhead

## Vibecode Compliance

All AI interactions maintain Vibecode compliance:
- Prompt sanitization (Vibecode #5, #7)
- Context management (Vibecode #2, #9)
- Memory reinsertion protocol (Vibecode #6)
- Mode switching (Vibecode #8)
- Race condition protection (Vibecode #3)

## Future Enhancements

1. Media upload handling (images, videos)
2. Real-time updates (WebSocket or Server-Sent Events)
3. Advanced AI scoring (embeddings, semantic similarity)
4. Redis backend for caching (production)
5. Database migration path (if needed for scale)

