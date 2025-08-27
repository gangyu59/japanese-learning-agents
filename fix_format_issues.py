#!/usr/bin/env python3
"""
一键格式修复脚本 - 解决所有缩进和换行问题
"""


def fix_base_agent():
    """修复 base_agent.py"""
    content = '''"""智能体基类"""
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
'''

    with open("src/core/agents/base_agent.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 修复了 base_agent.py")


def fix_tanaka():
    """修复 tanaka.py 的缩进问题"""
    # 读取现有内容
    with open("src/core/agents/core_agents/tanaka.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 修复特定行的缩进问题
    lines = content.split('\n')

    # 找到并修复 process_message 方法的缩进
    for i, line in enumerate(lines):
        if "async def process_message(self, message: str," in line:
            lines[i + 1] = "                            context: Dict[str, Any] = None) -> AgentResponse:"
        elif "response_content = self._create_correction_response(" in line:
            lines[i + 1] = "                    message, grammar_issues)"
        elif "return f\"素晴らしい文章ですね！「{message}」という表現は正確で自然です。この調子で頑張ってください！\"" in line:
            lines[i] = "            return f\"素晴らしい文章ですね！「{message}」という表現は正確で自然です。この調子で頑張ってください！\""

    # 确保文件以换行符结尾
    content = '\n'.join(lines)
    if not content.endswith('\n'):
        content += '\n'

    with open("src/core/agents/core_agents/tanaka.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 修复了 tanaka.py")


def fix_models():
    """修复数据模型文件"""

    # 修复 base.py
    base_content = '''"""基础数据模型"""
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
'''

    with open("src/data/models/base.py", "w", encoding="utf-8") as f:
        f.write(base_content)
    print("✅ 修复了 base.py")

    # 修复 agent.py
    agent_content = '''"""智能体数据模型"""
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
'''

    with open("src/data/models/agent.py", "w", encoding="utf-8") as f:
        f.write(agent_content)
    print("✅ 修复了 agent.py")


def fix_config():
    """修复 config.py"""
    content = '''"""应用程序配置管理"""
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import os


@dataclass  
class Settings:
    """应用程序设置"""
    app_name: str = "Japanese Learning Multi-Agent System"
    debug: bool = False
    version: str = "0.1.0"
    database_url: str = "sqlite:///./japanese_learning.db"
    openai_api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    data_dir: Path = Path("./data")
    logs_dir: Path = Path("./logs")

    def __post_init__(self):
        """初始化后处理"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)


settings = Settings()
'''

    with open("src/utils/config.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 修复了 config.py")


def fix_logger():
    """修复 logger.py"""
    content = '''"""日志管理模块"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "japanese_learning", 
                level: str = "INFO") -> logging.Logger:
    """设置日志器"""

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # 文件处理器
    log_file = Path("logs") / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    log_file.parent.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 默认日志器
logger = setup_logger()
'''

    with open("src/utils/logger.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 修复了 logger.py")


def main():
    """执行所有修复"""
    print("🔧 开始修复所有格式问题...")

    fix_base_agent()
    fix_tanaka()
    fix_models()
    fix_config()
    fix_logger()

    print("\n✅ 所有格式问题修复完成！")
    print("现在运行检查:")
    print("python -m flake8 src/ --max-line-length=100 --ignore=E203,W503")


if __name__ == "__main__":
    main()