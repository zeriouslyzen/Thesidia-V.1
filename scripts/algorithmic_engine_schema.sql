-- ============================================================================
-- Katanx Algorithmic Growth Engine - Phase 1 Schema
-- Engagement Tracking + Content Scoring + Interest Clustering
-- ============================================================================
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ============================================================================

-- ============================================================================
-- Table 1: User Interactions (Event Stream)
-- ============================================================================
-- Captures all user actions for sequence learning (Meta-style)

CREATE TABLE user_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id TEXT, -- For anonymous tracking
    
    -- Content reference
    content_id TEXT NOT NULL, -- Can be conversation_id, post_id, etc.
    content_type TEXT NOT NULL, -- 'conversation', 'post', 'bot', 'asset'
    
    -- Action details
    action_type TEXT NOT NULL CHECK (action_type IN (
        'view', 'click', 'like', 'unlike', 'share', 'save', 'bookmark',
        'comment', 'reply', 'scroll', 'dwell', 'hover', 'expand',
        'play', 'pause', 'complete', 'skip', 'hide', 'report'
    )),
    action_value FLOAT, -- dwell_time seconds, scroll_depth %, etc.
    
    -- Sequence tracking (for pattern learning)
    sequence_position INTEGER, -- Order in session (1, 2, 3...)
    session_start_at TIMESTAMP WITH TIME ZONE, -- Session grouping
    
    -- Context
    source_page TEXT, -- 'feed', 'profile', 'search', 'direct'
    device_type TEXT, -- 'desktop', 'mobile', 'tablet'
    
    -- Timing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS: Users see own interactions, service role sees all
ALTER TABLE user_interactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own interactions"
    ON user_interactions FOR SELECT
    USING (auth.uid() = user_id OR session_id IS NOT NULL);

CREATE POLICY "Users can create interactions"
    ON user_interactions FOR INSERT
    WITH CHECK (true); -- Allow anonymous tracking via session_id

-- Indexes for fast lookups
CREATE INDEX idx_interactions_user_time ON user_interactions(user_id, created_at DESC);
CREATE INDEX idx_interactions_content ON user_interactions(content_id, content_type);
CREATE INDEX idx_interactions_session ON user_interactions(session_id, sequence_position);
CREATE INDEX idx_interactions_action ON user_interactions(action_type, created_at DESC);

-- ============================================================================
-- Table 2: Content Scores (Quality Metrics)
-- ============================================================================
-- Wilson score + engagement velocity + Gnostic relevance

CREATE TABLE content_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id TEXT NOT NULL UNIQUE,
    content_type TEXT NOT NULL,
    
    -- Engagement counts
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    unlike_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    save_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    
    -- Detailed metrics
    total_dwell_time FLOAT DEFAULT 0, -- Sum of all dwell times
    avg_dwell_time FLOAT DEFAULT 0,
    unique_viewers INTEGER DEFAULT 0,
    
    -- Calculated scores (updated by trigger/function)
    wilson_score FLOAT DEFAULT 0, -- Reddit-style confidence score
    engagement_velocity FLOAT DEFAULT 0, -- Engagements per hour in first 24h
    viral_probability FLOAT DEFAULT 0, -- Cascade prediction score
    gnostic_relevance FLOAT DEFAULT 0, -- Thesidia pattern match score
    creator_reputation FLOAT DEFAULT 0, -- Author credibility
    
    -- Final ranking score
    total_score FLOAT DEFAULT 0,
    hot_score FLOAT DEFAULT 0, -- For "Hot" feed ranking
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    first_interaction_at TIMESTAMP WITH TIME ZONE
);

-- RLS: Public read, service role write
ALTER TABLE content_scores ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view content scores"
    ON content_scores FOR SELECT
    USING (true);

CREATE POLICY "Service role can manage scores"
    ON content_scores FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- Indexes
CREATE INDEX idx_content_scores_total ON content_scores(total_score DESC);
CREATE INDEX idx_content_scores_hot ON content_scores(hot_score DESC);
CREATE INDEX idx_content_scores_viral ON content_scores(viral_probability DESC);

-- ============================================================================
-- Table 3: Interest Clusters (Community Detection)
-- ============================================================================
-- SimCluster-style community groupings

CREATE TABLE interest_clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Cluster identity
    cluster_name TEXT NOT NULL,
    cluster_description TEXT,
    
    -- Cluster characteristics
    keywords TEXT[], -- Top keywords for this cluster
    topics TEXT[], -- Thesidia-detected topics
    
    -- Statistics
    member_count INTEGER DEFAULT 0,
    active_members_24h INTEGER DEFAULT 0,
    total_interactions INTEGER DEFAULT 0,
    avg_engagement_rate FLOAT DEFAULT 0,
    
    -- Cluster embedding (for similarity)
    -- Note: Supabase pgvector extension needed for full vector support
    embedding_json JSONB, -- Fallback: store as JSON array
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_recalculated_at TIMESTAMP WITH TIME ZONE
);

-- RLS
ALTER TABLE interest_clusters ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view clusters"
    ON interest_clusters FOR SELECT
    USING (true);

-- Indexes
CREATE INDEX idx_clusters_name ON interest_clusters(cluster_name);
CREATE INDEX idx_clusters_members ON interest_clusters(member_count DESC);

-- ============================================================================
-- Table 4: User Cluster Memberships
-- ============================================================================
-- Many-to-many relationship with affinity scores

CREATE TABLE user_clusters (
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    cluster_id UUID REFERENCES interest_clusters(id) ON DELETE CASCADE,
    
    -- Affinity (0.0 to 1.0, higher = stronger membership)
    affinity_score FLOAT NOT NULL DEFAULT 0.5 CHECK (affinity_score >= 0 AND affinity_score <= 1),
    
    -- Tracking
    interactions_in_cluster INTEGER DEFAULT 0,
    last_interaction_at TIMESTAMP WITH TIME ZONE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (user_id, cluster_id)
);

-- RLS
ALTER TABLE user_clusters ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own cluster memberships"
    ON user_clusters FOR SELECT
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_user_clusters_affinity ON user_clusters(user_id, affinity_score DESC);
CREATE INDEX idx_user_clusters_cluster ON user_clusters(cluster_id, affinity_score DESC);

-- ============================================================================
-- Table 5: Model Training Logs
-- ============================================================================
-- Track self-learning loop progress

CREATE TABLE model_training_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Model identity
    model_name TEXT NOT NULL,
    model_version TEXT,
    
    -- Training metrics
    training_samples INTEGER,
    validation_accuracy FLOAT,
    loss FLOAT,
    
    -- Performance comparison
    previous_performance JSONB,
    current_performance JSONB,
    improvement_percentage FLOAT,
    
    -- A/B testing
    experiment_id TEXT,
    variant TEXT, -- 'control', 'treatment_a', 'treatment_b'
    
    -- Metadata
    trained_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    training_duration_seconds INTEGER,
    notes TEXT
);

-- RLS: Admin only
ALTER TABLE model_training_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage training logs"
    ON model_training_logs FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================================================
-- Table 6: Viral Cascade Events
-- ============================================================================
-- Track viral spread for cascade detection

CREATE TABLE viral_cascades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id TEXT NOT NULL,
    
    -- Cascade metrics
    cascade_depth INTEGER DEFAULT 0, -- How many "hops" of sharing
    total_reach INTEGER DEFAULT 0, -- Unique users reached
    velocity_score FLOAT DEFAULT 0, -- Speed of spread
    
    -- Cross-cluster spread (key viral indicator)
    origin_cluster_id UUID REFERENCES interest_clusters(id),
    clusters_reached TEXT[], -- Array of cluster IDs reached
    cross_cluster_spread_ratio FLOAT DEFAULT 0, -- % outside origin
    
    -- Timeline
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    peak_velocity_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Status
    is_viral BOOLEAN DEFAULT FALSE, -- True if crossed viral threshold
    viral_threshold_crossed_at TIMESTAMP WITH TIME ZONE
);

-- RLS
ALTER TABLE viral_cascades ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view viral cascades"
    ON viral_cascades FOR SELECT
    USING (true);

-- Indexes
CREATE INDEX idx_cascades_content ON viral_cascades(content_id);
CREATE INDEX idx_cascades_viral ON viral_cascades(is_viral, velocity_score DESC);

-- ============================================================================
-- Functions: Wilson Score Calculation
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_wilson_score(
    positive INTEGER,
    negative INTEGER,
    confidence FLOAT DEFAULT 0.95
)
RETURNS FLOAT AS $$
DECLARE
    n INTEGER;
    z FLOAT;
    phat FLOAT;
    result FLOAT;
BEGIN
    n := positive + negative;
    IF n = 0 THEN
        RETURN 0;
    END IF;
    
    -- z-score for 95% confidence = 1.96
    z := 1.96;
    phat := positive::FLOAT / n::FLOAT;
    
    -- Wilson score interval lower bound
    result := (phat + z*z/(2*n) - z * sqrt((phat*(1-phat) + z*z/(4*n))/n)) / (1 + z*z/n);
    
    RETURN result;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- Functions: Hot Score Calculation (Reddit-style)
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_hot_score(
    score INTEGER,
    created_at TIMESTAMP WITH TIME ZONE
)
RETURNS FLOAT AS $$
DECLARE
    order_val FLOAT;
    sign_val INTEGER;
    seconds FLOAT;
    result FLOAT;
BEGIN
    -- Order of magnitude
    IF abs(score) >= 1 THEN
        order_val := log(greatest(abs(score), 1));
    ELSE
        order_val := 0;
    END IF;
    
    -- Sign
    IF score > 0 THEN
        sign_val := 1;
    ELSIF score < 0 THEN
        sign_val := -1;
    ELSE
        sign_val := 0;
    END IF;
    
    -- Seconds since epoch (adjusted for recency)
    seconds := EXTRACT(EPOCH FROM created_at) - 1134028003;
    
    -- Hot formula: sign * order + seconds / 45000
    result := sign_val * order_val + seconds / 45000;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- Functions: Update Content Scores
-- ============================================================================

CREATE OR REPLACE FUNCTION update_content_score(p_content_id TEXT)
RETURNS VOID AS $$
DECLARE
    v_view_count INTEGER;
    v_like_count INTEGER;
    v_unlike_count INTEGER;
    v_share_count INTEGER;
    v_wilson FLOAT;
    v_hot FLOAT;
    v_first_interaction TIMESTAMP WITH TIME ZONE;
    v_velocity FLOAT;
BEGIN
    -- Aggregate interaction counts
    SELECT 
        COUNT(*) FILTER (WHERE action_type = 'view'),
        COUNT(*) FILTER (WHERE action_type = 'like'),
        COUNT(*) FILTER (WHERE action_type = 'unlike'),
        COUNT(*) FILTER (WHERE action_type = 'share'),
        MIN(created_at)
    INTO v_view_count, v_like_count, v_unlike_count, v_share_count, v_first_interaction
    FROM user_interactions
    WHERE content_id = p_content_id;
    
    -- Calculate scores
    v_wilson := calculate_wilson_score(v_like_count, v_unlike_count);
    
    -- Calculate velocity (engagements per hour in first 24h)
    IF v_first_interaction IS NOT NULL THEN
        SELECT (v_like_count + v_share_count)::FLOAT / 
               GREATEST(EXTRACT(EPOCH FROM (NOW() - v_first_interaction)) / 3600, 1)
        INTO v_velocity;
    ELSE
        v_velocity := 0;
    END IF;
    
    v_hot := calculate_hot_score(v_like_count - v_unlike_count, COALESCE(v_first_interaction, NOW()));
    
    -- Upsert content score
    INSERT INTO content_scores (content_id, content_type, view_count, like_count, unlike_count, share_count,
                                wilson_score, engagement_velocity, hot_score, total_score, first_interaction_at, updated_at)
    VALUES (p_content_id, 'unknown', v_view_count, v_like_count, v_unlike_count, v_share_count,
            v_wilson, v_velocity, v_hot, v_wilson * 0.4 + v_velocity * 0.3 + (v_hot / 1000) * 0.3, 
            v_first_interaction, NOW())
    ON CONFLICT (content_id) DO UPDATE SET
        view_count = EXCLUDED.view_count,
        like_count = EXCLUDED.like_count,
        unlike_count = EXCLUDED.unlike_count,
        share_count = EXCLUDED.share_count,
        wilson_score = EXCLUDED.wilson_score,
        engagement_velocity = EXCLUDED.engagement_velocity,
        hot_score = EXCLUDED.hot_score,
        total_score = EXCLUDED.total_score,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Trigger: Auto-update scores on new interactions
-- ============================================================================

CREATE OR REPLACE FUNCTION trigger_update_content_score()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM update_content_score(NEW.content_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_interaction_update_score
    AFTER INSERT ON user_interactions
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_content_score();

-- ============================================================================
-- Verification
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Algorithmic Growth Engine Phase 1 Schema Created!';
    RAISE NOTICE 'Tables: user_interactions, content_scores, interest_clusters, user_clusters, model_training_logs, viral_cascades';
    RAISE NOTICE 'Functions: calculate_wilson_score, calculate_hot_score, update_content_score';
    RAISE NOTICE 'Triggers: Auto-update scores on new interactions';
END $$;

-- ============================================================================
-- End of Phase 1 Schema
-- ============================================================================
