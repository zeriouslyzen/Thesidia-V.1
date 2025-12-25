# Supabase Phase 2: Database Schema

## Overview

This phase creates the complete database schema in Supabase with:
- 6 core tables with Row Level Security (RLS)
- Helper functions for common queries
- Indexes for performance
- Triggers for automatic timestamps

---

## Quick Start

### 1. Run the Schema

```bash
# 1. Open Supabase Dashboard
# → https://supabase.com/dashboard/project/YOUR_PROJECT/sql

# 2. Click "SQL Editor" → "New Query"

# 3. Copy entire contents of scripts/supabase_schema.sql

# 4. Paste and click "Run"
```

**Expected output**: `Schema created successfully!`

### 2. Verify Schema

```bash
python scripts/verify_supabase_schema.py
```

**Expected output**: All tables ✅

---

## Schema Details

### Tables Created

| Table | Purpose | RLS Enabled |
|-------|---------|-------------|
| `user_profiles` | User settings, preferences | ✅ |
| `conversations` | Chat sessions | ✅ |
| `messages` | Individual messages | ✅ |
| `memory_snapshots` | Sophia gnostic maps | ✅ |
| `user_interests` | Topic tracking | ✅ |
| `system_state` | Thesidia state backups | ✅ (admin only) |

### Helper Functions

**`search_conversations(user_id, query, limit)`**
- Full-text search across user's conversations
- Returns ranked results

**`get_user_stats(user_id)`**
- Returns conversation/message counts
- Tracks reasoning method usage (ToT, Beam Search)

**`get_latest_memory(user_id)`**
- Gets most recent memory snapshot
- Used for Sophia memory loading

### Row Level Security (RLS)

All tables enforce user isolation:
```sql
-- Users can only access their own data
WHERE auth.uid() = user_id
```

**System state** table restricted to service role only (admin).

---

## Testing the Schema

### Create Test User

1. Go to **Authentication** → **Users** in Supabase
2. Click "Add User" → "Create new user"
3. Email: `test@example.com`, Password: `testpass123`
4. Copy the **User ID** (UUID)

### Insert Test Data

```sql
-- Replace YOUR_USER_ID with copied UUID

-- Test profile
INSERT INTO user_profiles (id, operator_name)
VALUES ('YOUR_USER_ID', 'Test User');

-- Test conversation
INSERT INTO conversations (user_id, title, preview, reasoning_method)
VALUES (
    'YOUR_USER_ID',
    'First Conversation',
    'Testing the schema',
    'tree_of_thoughts'
);

-- Test message
INSERT INTO messages (conversation_id, role, content)
SELECT id, 'user', 'Hello Thesidia!'
FROM conversations
WHERE user_id = 'YOUR_USER_ID'
LIMIT 1;
```

### Test RLS Policies

```sql
-- This should only return data for the current user
SELECT * FROM conversations;

-- This should work (own data)
UPDATE user_profiles 
SET operator_name = 'Updated Name'
WHERE id = auth.uid();

-- This should FAIL (different user's data)
UPDATE user_profiles 
SET operator_name = 'Hacker'
WHERE id != auth.uid();
```

---

## Performance Notes

### Indexes Created

```sql
-- Conversations sorted by recent activity
idx_conversations_user_updated (user_id, updated_at DESC)

-- Messages in conversation order
idx_messages_conversation (conversation_id, created_at ASC)

-- Full-text search on message content
idx_messages_content_search (content_vector GIN)

-- Memory version lookup
idx_memory_user_version (user_id, version DESC)

-- User interests by weight
idx_interests_user_weight (user_id, weight DESC)
```

### Query Performance

Expected query times (100K rows):
- List conversations: **< 50ms**
- Search messages: **< 100ms**
- Get latest memory: **< 10ms**
- Get user stats: **< 200ms**

---

## Troubleshooting

**Error: "permission denied for schema public"**
- You're not using service key
- Update `.env` with `SUPABASE_SERVICE_KEY`

**Error: "relation already exists"**
- Schema already created
- Either drop tables or use migration tool

**Error: "function does not exist"**
- Check SQL executed completely
- Look for errors in SQL output

**RLS blocking queries**
- Use service key for admin operations
- Check user is authenticated (`auth.uid()` not null)

---

## Next Steps

After schema verification passes:

1. ✅ **Phase 2 Complete**
2. **Proceed to Phase 3**: Supabase Client Integration
   - Create `SupabaseConversationStore` adapter
   - Update `build_store()` factory
   - Test with live data

See `supabase_readiness.md` Phase 3 for details.

---

## Rollback

If you need to start over:

```sql
-- ⚠️ WARNING: This deletes ALL data!

DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS memory_snapshots CASCADE;
DROP TABLE IF EXISTS user_interests CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS system_state CASCADE;

DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
DROP FUNCTION IF EXISTS search_conversations CASCADE;
DROP FUNCTION IF EXISTS get_user_stats CASCADE;
DROP FUNCTION IF EXISTS get_latest_memory CASCADE;
```

Then re-run `supabase_schema.sql`.
