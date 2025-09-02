# database/models.py
"""
Database Models for Japanese Learning Multi-Agent System
日语学习多智能体系统的数据模型
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, date
import uuid

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # 学习配置
    learning_level = Column(String(20), default='beginner')  # beginner, intermediate, advanced
    target_jlpt_level = Column(String(5))  # N5, N4, N3, N2, N1
    daily_goal = Column(Integer, default=30)  # minutes per day
    timezone = Column(String(50), default='UTC')

    # 关联关系
    learning_progress = relationship("LearningProgress", back_populates="user", cascade="all, delete-orphan")
    vocabulary_progress = relationship("VocabularyProgress", back_populates="user", cascade="all, delete-orphan")
    learning_sessions = relationship("LearningSession", back_populates="user", cascade="all, delete-orphan")
    conversation_history = relationship("ConversationHistory", back_populates="user", cascade="all, delete-orphan")
    custom_agents = relationship("CustomAgent", back_populates="creator", cascade="all, delete-orphan")


class LearningProgress(Base):
    """学习进度表"""
    __tablename__ = 'learning_progress'

    progress_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    grammar_point = Column(String(100), nullable=False)
    mastery_level = Column(Float, default=0.0)  # 0.0 to 1.0
    practice_count = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    last_reviewed = Column(DateTime, default=datetime.utcnow)
    next_review = Column(DateTime)
    difficulty_rating = Column(Float)  # user's perceived difficulty 1-5
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="learning_progress")


class VocabularyProgress(Base):
    """词汇学习记录表"""
    __tablename__ = 'vocabulary_progress'

    vocab_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    word = Column(String(100), nullable=False)
    reading = Column(String(100))  # hiragana/katakana reading
    meaning = Column(Text, nullable=False)
    example_sentence = Column(Text)
    difficulty_level = Column(Integer, default=1)  # 1-5 scale
    review_interval = Column(Integer, default=1)  # days
    next_review = Column(DateTime, default=datetime.utcnow)
    mastery_score = Column(Float, default=0.0)  # 0.0-1.0
    times_reviewed = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 记忆曲线相关
    ease_factor = Column(Float, default=2.5)  # Anki-style ease factor
    repetition_count = Column(Integer, default=0)

    # 关联关系
    user = relationship("User", back_populates="vocabulary_progress")


class CustomAgent(Base):
    """自定义智能体配置表"""
    __tablename__ = 'custom_agents'

    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # 性格配置 (JSON格式)
    personality_config = Column(JSON)  # {"strictness": 8, "humor": 3, "patience": 9}
    expertise_areas = Column(ARRAY(String))  # ["grammar", "culture", "conversation"]
    speaking_style = Column(JSON)  # {"formality": 7, "speed": 5, "catchphrases": []}
    behavioral_patterns = Column(JSON)  # {"interrupts_often": false, "uses_examples": true}

    # 外观配置
    avatar_config = Column(JSON)  # {"image_url": "", "emoji": "👨‍🏫", "color": "#blue"}

    # 使用统计
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    creator = relationship("User", back_populates="custom_agents")


class CustomScene(Base):
    """自定义场景配置表"""
    __tablename__ = 'custom_scenes'

    scene_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    setting = Column(Text)  # detailed scene description

    # 场景规则和约束 (JSON格式)
    rules = Column(JSON)  # ["只能使用敬语", "不能使用英语", "必须包含文化元素"]
    constraints = Column(JSON)  # {"max_response_length": 100, "required_grammar": ["て形"]}
    learning_objectives = Column(ARRAY(String))  # ["practice_keigo", "learn_business_terms"]

    difficulty_level = Column(Integer, default=1)  # 1-5
    estimated_duration = Column(Integer)  # minutes

    # 公开和使用统计
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationHistory(Base):
    """对话历史表"""
    __tablename__ = 'conversation_history'

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)

    # 对话内容
    user_input = Column(Text)
    agent_responses = Column(JSON)  # [{"agent_id": "tanaka", "content": "...", "emotion": "😊"}]

    # 协作相关
    scene_id = Column(UUID(as_uuid=True), ForeignKey('custom_scenes.scene_id'))
    participating_agents = Column(ARRAY(String))  # ["tanaka", "koumi", "yamada"]
    collaboration_mode = Column(String(50))  # "discussion", "correction", etc.

    # 学习分析
    learning_points_identified = Column(ARRAY(String))
    corrections_made = Column(JSON)  # [{"type": "grammar", "correction": "...", "agent": "tanaka"}]
    grammar_points_practiced = Column(ARRAY(String))
    new_vocabulary_encountered = Column(ARRAY(String))

    # 用户反馈
    user_satisfaction_rating = Column(Integer)  # 1-5 scale
    user_feedback = Column(Text)

    timestamp = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="conversation_history")


class LearningSession(Base):
    """学习会话表"""
    __tablename__ = 'learning_sessions'

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)

    session_type = Column(String(50))  # "chat", "study", "quiz", "creation", "collaboration"
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)

    # 学习内容
    learning_points_covered = Column(ARRAY(String))
    grammar_points_practiced = Column(ARRAY(String))
    vocabulary_learned = Column(ARRAY(String))

    # 协作相关
    agents_used = Column(ARRAY(String))  # 使用的智能体
    collaboration_modes_used = Column(ARRAY(String))  # 使用的协作模式

    # 性能指标 (JSON格式)
    performance_metrics = Column(JSON)  # {"accuracy": 0.85, "response_time": 1.2, "engagement": 0.9}

    satisfaction_score = Column(Integer)  # 1-5 scale
    notes = Column(Text)  # 用户笔记

    # 关联关系
    user = relationship("User", back_populates="learning_sessions")


class AgentUsageStats(Base):
    """智能体使用统计表"""
    __tablename__ = 'agent_usage_stats'

    stat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(50), nullable=False)  # "tanaka", "koumi", etc.
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)

    usage_date = Column(DateTime, default=datetime.utcnow)
    interaction_count = Column(Integer, default=0)
    total_duration_minutes = Column(Integer, default=0)

    # 用户评价
    user_rating = Column(Integer)  # 1-5 scale for this session
    learning_effectiveness = Column(Float)  # calculated effectiveness score 0-1

    # 协作统计
    collaboration_count = Column(Integer, default=0)  # 参与协作次数
    conflict_count = Column(Integer, default=0)  # 产生冲突次数
    consensus_contribution = Column(Float, default=0.0)  # 对共识的贡献度


class MemoryCard(Base):
    """记忆卡片表 - MemBot使用"""
    __tablename__ = 'memory_cards'

    card_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)

    # 卡片内容
    front = Column(Text, nullable=False)  # 正面内容（问题）
    back = Column(Text, nullable=False)  # 背面内容（答案）
    card_type = Column(String(50))  # "vocabulary", "grammar", "kanji", "culture"

    # 间隔重复算法参数
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=1)  # days until next review
    repetitions = Column(Integer, default=0)
    next_review_date = Column(DateTime, default=datetime.utcnow)

    # 学习统计
    total_reviews = Column(Integer, default=0)
    correct_reviews = Column(Integer, default=0)
    streak = Column(Integer, default=0)  # 连续正确次数

    # 元数据
    difficulty = Column(Integer, default=3)  # 1-5, user perceived difficulty
    priority = Column(Integer, default=1)  # 1-3, 1=high priority
    tags = Column(ARRAY(String))  # ["JLPT-N3", "business", "formal"]

    created_at = Column(DateTime, default=datetime.utcnow)
    last_reviewed = Column(DateTime)

    # 关联数据
    related_grammar = Column(String(100))  # 相关语法点
    related_vocab = Column(ARRAY(String))  # 相关词汇


class StudyPlan(Base):
    """学习计划表 - MemBot生成的个性化学习计划"""
    __tablename__ = 'study_plans'

    plan_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)

    plan_name = Column(String(100), nullable=False)
    description = Column(Text)
    target_date = Column(DateTime)  # 目标完成时间

    # 计划内容 (JSON格式)
    daily_goals = Column(JSON)  # {"vocabulary": 10, "grammar": 2, "conversation": 15}
    weekly_goals = Column(JSON)  # {"new_kanji": 50, "jlpt_practice": 3}
    learning_path = Column(JSON)  # 学习路径和里程碑

    # 进度跟踪
    progress_percentage = Column(Float, default=0.0)
    completed_milestones = Column(ARRAY(String))
    current_milestone = Column(String(100))

    # 计划状态
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # MemBot调整记录
    adjustment_history = Column(JSON)  # MemBot对计划的调整历史


# 数据库连接和会话管理

class DatabaseManager:
    """数据库管理器"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()

    def drop_tables(self):
        """删除所有表 - 仅用于开发环境"""
        Base.metadata.drop_all(bind=self.engine)


# 导出
__all__ = [
    'Base',
    'User', 'LearningProgress', 'VocabularyProgress', 'CustomAgent', 'CustomScene',
    'ConversationHistory', 'LearningSession', 'AgentUsageStats',
    'MemoryCard', 'StudyPlan',
    'DatabaseManager'
]