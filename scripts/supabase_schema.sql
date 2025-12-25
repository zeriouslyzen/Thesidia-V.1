-- ============================================================================
-- Thesidia Supabase Database Schema
-- Phase 2: Database Setup
-- ============================================================================
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- ============================================================================
-- Table 1: User Profiles
-- ============================================================================
-- Extends Supabase auth.users with Thesidia-specific data

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    operator_name TEXT,
    coaching_preferences JSONB DEFAULT '{}',
    
    -- Session tracking
    last_session_id TEXT,
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Feature flags
    tree_of_thoughts_enabled BOOLEAN DEFAULT true,
    beam_search_enabled BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON user_profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Indexes
CREATE INDEX idx_user_profiles_last_active ON user_profiles(last_active_at DESC);

-- ============================================================================
-- Table 2: Conversations
-- ============================================================================

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Display info
    title TEXT NOT NULL,
    preview TEXT NOT NULL,
    
    -- Metadata
    reasoning_method TEXT,  -- 'standard', 'tree_of_thoughts', 'beam_search'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own conversations"
    ON conversations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create conversations"
    ON conversations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own conversations"
    ON conversations FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own conversations"
    ON conversations FOR DELETE
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
CREATE INDEX idx_conversations_reasoning ON conversations(reasoning_method);

-- ============================================================================
-- Table 3: Messages
-- ============================================================================

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    
    -- Message content
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Search
    content_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security (inherited from conversation)
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view messages in own conversations"
    ON messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM conversations
            WHERE conversations.id = messages.conversation_id
            AND conversations.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create messages in own conversations"
    ON messages FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversations
            WHERE conversations.id = messages.conversation_id
            AND conversations.user_id = auth.uid()
        )
    );

-- Indexes
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at ASC);
CREATE INDEX idx_messages_content_search ON messages USING GIN(content_vector);

-- ============================================================================
-- Table 4: Memory Snapshots (Sophia Gnostic Maps)
-- ============================================================================

CREATE TABLE memory_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Versioning
    version INTEGER NOT NULL,
    
    -- Memory data
    gnostic_map JSONB NOT NULL,
    
    -- Metadata
    snapshot_type TEXT DEFAULT 'auto',  -- 'auto', 'manual', 'backup'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, version)
);

-- Row Level Security
ALTER TABLE memory_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own memory"
    ON memory_snapshots FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create memory snapshots"
    ON memory_snapshots FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_memory_user_version ON memory_snapshots(user_id, version DESC);
CREATE INDEX idx_memory_created ON memory_snapshots(created_at DESC);

-- Helper function: Get latest memory for user
CREATE OR REPLACE FUNCTION get_latest_memory(p_user_id UUID)
RETURNS TABLE (
    version INTEGER,
    gnostic_map JSONB,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT m.version, m.gnostic_map, m.created_at
    FROM memory_snapshots m
    WHERE m.user_id = p_user_id
    ORDER BY m.version DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Table 5: User Interests
-- ============================================================================

CREATE TABLE user_interests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Interest data
    topic TEXT NOT NULL,
    weight FLOAT NOT NULL CHECK (weight >= 0 AND weight <= 1),
    
    -- Tracking
    first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    interaction_count INTEGER DEFAULT 1,
    
    UNIQUE(user_id, topic)
);

CREATE TRIGGER update_interests_updated_at
    BEFORE UPDATE ON user_interests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security
ALTER TABLE user_interests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own interests"
    ON user_interests FOR ALL
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_interests_user_weight ON user_interests(user_id, weight DESC);
CREATE INDEX idx_interests_topic_search ON user_interests USING GIN(to_tsvector('english', topic));

-- ============================================================================
-- Table 6: System State (Thesidia State Snapshots)
-- ============================================================================

CREATE TABLE system_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- State data (personality, patterns, etc.)
    state_data JSONB NOT NULL,
    
    -- Metadata
    snapshot_reason TEXT,  -- 'scheduled', 'manual', 'before_migration'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS: Admin only (service role)
ALTER TABLE system_state ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage system state"
    ON system_state FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- Index
CREATE INDEX idx_system_state_created ON system_state(created_at DESC);

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function: Search conversations by content
CREATE OR REPLACE FUNCTION search_conversations(
    p_user_id UUID,
    p_query TEXT,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    conversation_id UUID,
    title TEXT,
    preview TEXT,
    rank REAL,
    updated_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (c.id)
        c.id,
        c.title,
        c.preview,
        ts_rank(m.content_vector, plainto_tsquery('english', p_query)) AS rank,
        c.updated_at
    FROM conversations c
    JOIN messages m ON m.conversation_id = c.id
    WHERE c.user_id = p_user_id
      AND m.content_vector @@ plainto_tsquery('english', p_query)
    ORDER BY c.id, rank DESC, c.updated_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get conversation statistics for user
CREATE OR REPLACE FUNCTION get_user_stats(p_user_id UUID)
RETURNS TABLE (
    total_conversations INTEGER,
    total_messages INTEGER,
    avg_messages_per_conversation NUMERIC,
    tree_of_thoughts_count INTEGER,
    beam_search_count INTEGER,
    last_activity TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT c.id)::INTEGER,
        COUNT(m.id)::INTEGER,
        ROUND(COUNT(m.id)::NUMERIC / NULLIF(COUNT(DISTINCT c.id), 0), 2),
        COUNT(DISTINCT CASE WHEN c.reasoning_method = 'tree_of_thoughts' THEN c.id END)::INTEGER,
        COUNT(DISTINCT CASE WHEN c.reasoning_method = 'beam_search' THEN c.id END)::INTEGER,
        MAX(c.updated_at)
    FROM conversations c
    LEFT JOIN messages m ON m.conversation_id = c.id
    WHERE c.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify schema created successfully
DO $$
BEGIN
    RAISE NOTICE 'Schema created successfully!';
    RAISE NOTICE 'Tables: user_profiles, conversations, messages, memory_snapshots, user_interests, system_state';
    RAISE NOTICE 'Functions: get_latest_memory, search_conversations, get_user_stats';
    RAISE NOTICE 'All tables have Row Level Security enabled';
END $$;

-- ============================================================================
-- Test Data (Optional - Remove for Production)
-- ============================================================================

-- Uncomment to insert test data after creating a test user via Supabase Auth

/*
-- Example: Insert test user profile (replace USER_UUID with actual UUID)
INSERT INTO user_profiles (id, operator_name, coaching_preferences)
VALUES (
    'USER_UUID_HERE'::UUID,
    'Test Operator',
    '{"style": "direct", "depth": "comprehensive"}'::JSONB
);

-- Example: Insert test conversation
INSERT INTO conversations (id, user_id, title, preview, reasoning_method)
VALUES (
    uuid_generate_v4(),
    'USER_UUID_HERE'::UUID,
    'Test Conversation',
    'Testing the database schema',
    'tree_of_thoughts'
);
*/

-- ============================================================================
-- End of Schema
-- ============================================================================
