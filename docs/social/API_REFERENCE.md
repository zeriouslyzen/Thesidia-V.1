# API Reference

## Base URL

All API endpoints are prefixed with `/api/`

## Authentication

In development mode: No authentication required (uses session IDs)

In production mode: JWT token required in `Authorization` header:
```
Authorization: Bearer <jwt_token>
```

## Social Media Endpoints

### Create Post

**POST** `/api/posts`

**Request Body**:
```json
{
  "user_id": "user_xyz",
  "session_id": "session_abc",
  "content": "Post content",
  "media": [],
  "tags": ["tag1", "tag2"],
  "visibility": "public"
}
```

**Response**:
```json
{
  "id": "post_abc123",
  "author_id": "user_xyz",
  "content": "Post content",
  "created_at": "2025-01-26T10:00:00Z",
  "interactions": {
    "likes": 0,
    "comments": 0,
    "reposts": 0,
    "views": 0
  },
  "ai_score": 0.85,
  "moderation_status": "approved"
}
```

### Get Post

**GET** `/api/posts/{post_id}`

**Response**: Post object with interactions

### Delete Post

**DELETE** `/api/posts/{post_id}`

**Request Body**:
```json
{
  "user_id": "user_xyz",
  "session_id": "session_abc"
}
```

**Response**:
```json
{
  "success": true
}
```

### Get Feed

**GET** `/api/feed`

**Query Parameters**:
- `user_id`: User ID
- `session_id`: Session ID
- `type`: Feed type (`chronological`, `quality`, `personalized`)
- `limit`: Number of posts (default: 20)
- `offset`: Pagination offset (default: 0)

**Response**:
```json
{
  "items": [...posts...],
  "has_more": true,
  "page": 0,
  "limit": 20
}
```

### Like Post

**POST** `/api/posts/{post_id}/like`

**Request Body**:
```json
{
  "user_id": "user_xyz",
  "session_id": "session_abc"
}
```

**Response**:
```json
{
  "liked": true,
  "interactions": {
    "likes": 5,
    "comments": 2,
    "reposts": 1,
    "views": 100
  }
}
```

### Comment on Post

**POST** `/api/posts/{post_id}/comment`

**Request Body**:
```json
{
  "user_id": "user_xyz",
  "session_id": "session_abc",
  "content": "Comment text"
}
```

**Response**:
```json
{
  "comment": {
    "id": "comment_xyz",
    "user_id": "user_xyz",
    "content": "Comment text",
    "created_at": "2025-01-26T10:00:00Z"
  },
  "interactions": {...}
}
```

### Follow User

**POST** `/api/users/{target_user_id}/follow`

**Request Body**:
```json
{
  "user_id": "user_xyz",
  "session_id": "session_abc"
}
```

**Response**:
```json
{
  "following": true,
  "target_user_id": "target_user"
}
```

### Get User Profile

**GET** `/api/users/{user_id}/profile`

**Response**:
```json
{
  "user_id": "user_xyz",
  "username": "@username",
  "display_name": "Display Name",
  "bio": "User bio",
  "avatar_url": "/avatars/user_xyz.jpg",
  "stats": {
    "posts": 42,
    "followers": 150,
    "following": 75
  }
}
```

## Settings Endpoints

### Get Settings

**GET** `/api/settings`

**Query Parameters**: `user_id`, `session_id`

**Response**: Complete settings object

### Update Account Settings

**POST** `/api/settings/account`

**Request Body**:
```json
{
  "user_id": "user_xyz",
  "session_id": "session_abc",
  "username": "@username",
  "display_name": "Display Name",
  "bio": "User bio",
  "location": "City, Country",
  "website": "https://example.com"
}
```

### Update Security Settings

**POST** `/api/settings/security`

**Request Body**:
```json
{
  "user_id": "user_xyz",
  "session_id": "session_abc",
  "current_password": "old_password",
  "new_password": "new_password",
  "two_factor_enabled": false
}
```

### Update Privacy Settings

**POST** `/api/settings/privacy`

**Request Body**:
```json
{
  "user_id": "user_xyz",
  "session_id": "session_abc",
  "profile_visibility": "public",
  "dm_enabled": true,
  "show_online_status": true
}
```

### Update Notification Settings

**POST** `/api/settings/notifications`

**Request Body**:
```json
{
  "user_id": "user_xyz",
  "session_id": "session_abc",
  "email_enabled": false,
  "push_enabled": true,
  "mentions": true,
  "follows": true,
  "likes": true,
  "comments": true,
  "reposts": false
}
```

### Update Content Settings

**POST** `/api/settings/content`

**Request Body**:
```json
{
  "user_id": "user_xyz",
  "session_id": "session_abc",
  "auto_play_videos": false,
  "content_filter": "moderate",
  "language": "en",
  "timezone": "UTC"
}
```

## Error Responses

All errors follow this format:
```json
{
  "error": "Error message"
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad Request (validation error)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (permission denied)
- `404`: Not Found
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error
- `503`: Service Unavailable (feature not available)

