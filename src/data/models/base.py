# src/data/models/base.py
"""基础数据模型 - 扩展支持SQLAlchemy"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager


# 保持原有的dataclass模型
@dataclass
class BaseEntity:
    """基础实体模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class AgentPersonality:
    """智能体性格配置"""
    strictness: int = 5  # 1-10
    humor: int = 5       # 1-10
    patience: int = 5    # 1-10
    creativity: int = 5  # 1-10
    formality: int = 5   # 1-10


@dataclass
class MessageMetadata:
    """消息元数据"""
    confidence: float = 0.8
    processing_time: float = 0.0
    token_count: int = 0
    cost: Optional[float] = None


# === 新增 SQLAlchemy 支持 ===

# 数据库配置
DATABASE_URL = "sqlite:///C:/Users/1/Desktop/日语学习智能体/japanese-learning-agents/database/japanese_learning.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # 设置为True可以看到SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy声明基类
Base = declarative_base()


def get_db_session() -> Session:
    """获取数据库会话"""
    return SessionLocal()


@contextmanager
def get_db_session_context():
    """使用上下文管理器的数据库会话"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_database():
    """初始化数据库表"""
    print("🗄️  正在初始化数据库...")
    
    # 确保数据库目录存在
    import os
    os.makedirs(os.path.dirname(DATABASE_URL.replace('sqlite:///', '')), exist_ok=True)
    
    # 导入所有模型以确保表被创建
    try:
        from .learning import (
            LearningProgress, VocabularyProgress, ConversationLearning,
            UserStats, CulturalKnowledge
        )
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        print("✅ 数据库初始化完成")
        print(f"📍 数据库位置: {DATABASE_URL}")
        
        # 检查表是否创建成功
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📊 已创建的表: {tables}")
        
        return tables
        
    except ImportError as e:
        print(f"⚠️  无法导入学习模型: {e}")
        print("请确保 learning.py 文件存在且正确")
        return []
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return []


if __name__ == "__main__":
    init_database()