"""智能体基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

from src.data.models.agent import Agent, AgentResponse
from src.utils.logger import setup_logger


class BaseAgent(ABC):
    """智能体基类"""

    def __init__(self, config: Agent):
        self.config = config
        self.logger = setup_logger(f"agent_{config.name}")
        self.conversation_history: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {}

    @abstractmethod
    async def process_message(self, message: str, 
                            context: Dict[str, Any] = None) -> AgentResponse:
        """处理用户消息并返回响应"""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass

    def add_to_history(self, role: str, content: str, 
                      metadata: Dict[str, Any] = None):
        """添加对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        })

    def get_personality_trait(self, trait: str) -> int:
        """获取性格特征"""
        return getattr(self.config.personality, trait, 5)

    async def _create_response(self, content: str, confidence: float = 0.8, 
                             metadata: Dict[str, Any] = None) -> AgentResponse:
        """创建标准响应"""
        return AgentResponse(
            agent_id=self.config.id,
            content=content,
            confidence=confidence,
            metadata=metadata or {}
        )
