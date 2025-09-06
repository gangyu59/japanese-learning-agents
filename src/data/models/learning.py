# src/data/models/learning.py
"""
学习进度数据模型
实现学习进度追踪的核心数据结构
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func
from .base import Base


class LearningProgress(Base):
    """学习进度记录表"""
    __tablename__ = 'learning_progress'

    id = Column(String, primary_key=True)
    user_id = Column(String, default='demo_user')
    grammar_point = Column(String, nullable=False)  # 语法点名称
    mastery_level = Column(Float, default=0.0)  # 掌握程度 0.0-1.0
    practice_count = Column(Integer, default=0)  # 练习次数
    correct_answers = Column(Integer, default=0)  # 正确次数
    last_reviewed = Column(DateTime, default=func.now())
    next_review = Column(DateTime)
    difficulty_rating = Column(Float, default=0.5)  # 用户感知难度
    agent_source = Column(String)  # 来源智能体
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<LearningProgress({self.grammar_point}: {self.mastery_level:.1%})>"


class VocabularyProgress(Base):
    """词汇学习进度表"""
    __tablename__ = 'vocabulary_progress'

    id = Column(String, primary_key=True)
    user_id = Column(String, default='demo_user')
    word = Column(String, nullable=False)  # 日语单词
    reading = Column(String)  # 读音
    meaning = Column(Text, nullable=False)  # 中文含义
    example_sentence = Column(Text)  # 例句
    difficulty_level = Column(Integer, default=1)  # 难度等级 1-5
    review_interval = Column(Integer, default=1)  # 复习间隔（天）
    next_review = Column(DateTime, default=func.now())
    mastery_score = Column(Float, default=0.0)  # 记忆强度
    times_reviewed = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    jlpt_level = Column(String)  # N5, N4, N3, N2, N1
    agent_source = Column(String)  # 来源智能体
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<VocabularyProgress({self.word}: {self.mastery_score:.1%})>"


class ConversationLearning(Base):
    """对话学习记录表"""
    __tablename__ = 'conversation_learning'

    id = Column(String, primary_key=True)
    user_id = Column(String, default='demo_user')
    session_id = Column(String, nullable=False)
    user_input = Column(Text)
    agent_responses = Column(JSON)  # 智能体回复JSON
    learning_points = Column(JSON)  # 提取的学习点
    corrections_made = Column(JSON)  # 语法纠正记录
    participating_agents = Column(JSON)  # 参与的智能体
    scene_context = Column(String, default='general')
    timestamp = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<ConversationLearning({self.session_id}: {len(self.learning_points or [])} points)>"


class UserStats(Base):
    """用户学习统计表"""
    __tablename__ = 'user_stats'

    id = Column(String, primary_key=True)
    user_id = Column(String, default='demo_user')
    total_conversations = Column(Integer, default=0)
    total_vocabulary = Column(Integer, default=0)
    total_grammar_points = Column(Integer, default=0)
    current_level = Column(String, default='beginner')  # beginner, intermediate, advanced
    target_jlpt = Column(String, default='N5')  # N5, N4, N3, N2, N1
    streak_days = Column(Integer, default=0)  # 连续学习天数
    total_xp = Column(Integer, default=0)  # 总经验值
    level = Column(Integer, default=1)  # 用户等级
    last_active = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserStats({self.user_id}: Level {self.level}, {self.total_xp} XP)>"


class CulturalKnowledge(Base):
    """文化知识学习记录"""
    __tablename__ = 'cultural_knowledge'

    id = Column(String, primary_key=True)
    user_id = Column(String, default='demo_user')
    topic = Column(String, nullable=False)  # 文化主题
    subtopic = Column(String)  # 子主题
    content_summary = Column(Text)  # 内容摘要
    learned_from_agent = Column(String)  # 学习来源智能体
    understanding_level = Column(Float, default=0.0)  # 理解程度
    interest_rating = Column(Float)  # 兴趣评分
    notes = Column(Text)  # 用户笔记
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<CulturalKnowledge({self.topic}: {self.understanding_level:.1%})>"