"""智能体数据模型"""
from dataclasses import dataclass, field
from typing import List, Dict, Any
from .base import BaseEntity, AgentPersonality


@dataclass
class Agent(BaseEntity):
    """智能体模型"""
    name: str = ""
    description: str = ""
    personality: AgentPersonality = field(default_factory=AgentPersonality)
    expertise_areas: List[str] = field(default_factory=list)
    system_prompt: str = ""
    is_active: bool = True
    custom_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse(BaseEntity):
    """智能体响应模型"""
    agent_id: str = ""
    content: str = ""
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)
