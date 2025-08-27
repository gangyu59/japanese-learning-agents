"""基础数据模型"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


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
