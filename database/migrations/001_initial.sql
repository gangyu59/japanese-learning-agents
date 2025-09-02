-- database/migrations/001_initial_schema.sql
-- 初始化数据库架构

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    learning_level VARCHAR(20) DEFAULT 'beginner',
    target_jlpt_level VARCHAR(5),
    daily_goal INTEGER DEFAULT 30,
    timezone VARCHAR(50) DEFAULT 'UTC'
);

-- 学习进度表
CREATE TABLE IF NOT EXISTS learning_progress (
    progress_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    grammar_point VARCHAR(100) NOT NULL,
    mastery_level FLOAT DEFAULT 0.0 CHECK (mastery_level >= 0.0 AND mastery_level <= 1.0),
    practice_count INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_review TIMESTAMP,
    difficulty_rating FLOAT CHECK (difficulty_rating >= 1.0 AND difficulty_rating <= 5.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 词汇学习记录表
CREATE TABLE IF NOT EXISTS vocabulary_progress (
    vocab_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    word VARCHAR(100) NOT NULL,
    reading VARCHAR(100),
    meaning TEXT NOT NULL,
    example_sentence TEXT,
    difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level >= 1 AND difficulty_level <= 5),
    review_interval INTEGER DEFAULT 1,
    next_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mastery_score FLOAT DEFAULT 0.0 CHECK (mastery_score >= 0.0 AND mastery_score <= 1.0),
    times_reviewed INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ease_factor FLOAT DEFAULT 2.5,
    repetition_count INTEGER DEFAULT 0
);

-- 自定义智能体配置表
CREATE TABLE IF NOT EXISTS custom_agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by UUID REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    personality_config JSONB,
    expertise_areas TEXT[],
    speaking_style JSONB,
    behavioral_patterns JSONB,
    avatar_config JSONB,
    is_public BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    rating FLOAT DEFAULT 0.0 CHECK (rating >= 0.0 AND rating <= 5.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 自定义场景配置表
CREATE TABLE IF NOT EXISTS custom_scenes (
    scene_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by UUID REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    setting TEXT,
    rules JSONB,
    constraints JSONB,
    learning_objectives TEXT[],
    difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level >= 1 AND difficulty_level <= 5),
    estimated_duration INTEGER,
    is_public BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    rating FLOAT DEFAULT 0.0 CHECK (rating >= 0.0 AND rating <= 5.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 对话历史表
CREATE TABLE IF NOT EXISTS conversation_history (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    user_input TEXT,
    agent_responses JSONB,
    scene_id UUID REFERENCES custom_scenes(scene_id) ON DELETE SET NULL,
    participating_agents TEXT[],
    collaboration_mode VARCHAR(50),
    learning_points_identified TEXT[],
    corrections_made JSONB,
    grammar_points_practiced TEXT[],
    new_vocabulary_encountered TEXT[],
    user_satisfaction_rating INTEGER CHECK (user_satisfaction_rating >= 1 AND user_satisfaction_rating <= 5),
    user_feedback TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学习会话表
CREATE TABLE IF NOT EXISTS learning_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    session_type VARCHAR(50),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    learning_points_covered TEXT[],
    grammar_points_practiced TEXT[],
    vocabulary_learned TEXT[],
    agents_used TEXT[],
    collaboration_modes_used TEXT[],
    performance_metrics JSONB,
    satisfaction_score INTEGER CHECK (satisfaction_score >= 1 AND satisfaction_score <= 5),
    notes TEXT
);

-- 智能体使用统计表
CREATE TABLE IF NOT EXISTS agent_usage_stats (
    stat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(50) NOT NULL,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    usage_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    interaction_count INTEGER DEFAULT 0,
    total_duration_minutes INTEGER DEFAULT 0,
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    learning_effectiveness FLOAT CHECK (learning_effectiveness >= 0.0 AND learning_effectiveness <= 1.0),
    collaboration_count INTEGER DEFAULT 0,
    conflict_count INTEGER DEFAULT 0,
    consensus_contribution FLOAT DEFAULT 0.0
);

-- 记忆卡片表
CREATE TABLE IF NOT EXISTS memory_cards (
    card_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    card_type VARCHAR(50),
    ease_factor FLOAT DEFAULT 2.5,
    interval INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    next_review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_reviews INTEGER DEFAULT 0,
    correct_reviews INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    difficulty INTEGER DEFAULT 3 CHECK (difficulty >= 1 AND difficulty <= 5),
    priority INTEGER DEFAULT 1 CHECK (priority >= 1 AND priority <= 3),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_reviewed TIMESTAMP,
    related_grammar VARCHAR(100),
    related_vocab TEXT[]
);

-- 学习计划表
CREATE TABLE IF NOT EXISTS study_plans (
    plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    plan_name VARCHAR(100) NOT NULL,
    description TEXT,
    target_date TIMESTAMP,
    daily_goals JSONB,
    weekly_goals JSONB,
    learning_path JSONB,
    progress_percentage FLOAT DEFAULT 0.0 CHECK (progress_percentage >= 0.0 AND progress_percentage <= 100.0),
    completed_milestones TEXT[],
    current_milestone VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    adjustment_history JSONB
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_learning_progress_user_id ON learning_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_progress_next_review ON learning_progress(next_review);
CREATE INDEX IF NOT EXISTS idx_vocabulary_progress_user_id ON vocabulary_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_vocabulary_next_review ON vocabulary_progress(next_review);
CREATE INDEX IF NOT EXISTS idx_conversation_history_user_session ON conversation_history(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_history_timestamp ON conversation_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_agent_usage_stats_date ON agent_usage_stats(usage_date);
CREATE INDEX IF NOT EXISTS idx_agent_usage_stats_user ON agent_usage_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_cards_user_review ON memory_cards(user_id, next_review_date);
CREATE INDEX IF NOT EXISTS idx_memory_cards_type ON memory_cards(card_type);
CREATE INDEX IF NOT EXISTS idx_study_plans_user_active ON study_plans(user_id, is_active);

-- 创建触发器自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_custom_agents_updated_at
    BEFORE UPDATE ON custom_agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_study_plans_updated_at
    BEFORE UPDATE ON study_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入默认数据
INSERT INTO users (user_id, username, email, password_hash, learning_level, target_jlpt_level, daily_goal)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'demo_user', 'demo@example.com', 'demo_hash', 'beginner', 'N5', 30)
ON CONFLICT (username) DO NOTHING;

-- 插入一些示例记忆卡片
INSERT INTO memory_cards (user_id, front, back, card_type, difficulty, tags)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'こんにちは', '你好 (konnichiwa)', 'vocabulary', 1, ARRAY['greeting', 'basic']),
    ('00000000-0000-0000-0000-000000000001', 'ありがとう', '谢谢 (arigatou)', 'vocabulary', 1, ARRAY['greeting', 'basic']),
    ('00000000-0000-0000-0000-000000000001', 'て形的用法', '表示进行时态、连接动词等', 'grammar', 3, ARRAY['grammar', 'verb_form'])
ON CONFLICT DO NOTHING;