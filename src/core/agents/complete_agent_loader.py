#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版完整智能体加载器 - 无语法错误
将此文件保存为: src/core/agents/complete_agent_loader.py（覆盖原文件）
"""

import sys
import os
import importlib.util
import tempfile
import re
from pathlib import Path
from typing import Dict, Any, Optional
import textwrap


class CompleteAgentLoader:
    """完整智能体加载器"""

    def __init__(self):
        self.agents = {}
        self.agents_path = Path(__file__).parent / "core_agents"
        self.temp_modules = []

        # 从环境变量或.env文件获取API配置
        self.llm_provider = os.getenv('LLM_PROVIDER', 'deepseek')
        self.api_config = self._setup_api_config()

        print(f"🔧 使用LLM提供商: {self.llm_provider}")

        # 加载依赖和智能体
        self.base_agent_code = self._load_base_agent()
        self.llm_client_code = self._create_llm_client()
        self._load_all_agents()

    def _setup_api_config(self):
        """设置API配置"""
        config = {}

        if self.llm_provider == 'deepseek':
            config = {
                'provider': self.llm_provider,
                'api_key': os.getenv('DEEPSEEK_API_KEY'),
                'api_base': os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1'),
                'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
            }
        elif self.llm_provider == 'ark':
            config = {
                'provider': self.llm_provider,
                'api_key': os.getenv('ARK_API_KEY'),
                'api_base': os.getenv('ARK_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3'),
                'model': os.getenv('ARK_MODEL', 'ep-default')
            }

        if config.get('api_key'):
            key_preview = config['api_key'][:10] + "..." if len(config['api_key']) > 10 else config['api_key']
            print(f"✅ API配置: {key_preview}")
        else:
            print(f"⚠️  API_KEY 未配置，将使用模拟响应")

        return config

    def _load_base_agent(self):
        """加载BaseAgent类代码"""
        base_files = [
            self.agents_path / "base_agent.py",
            self.agents_path.parent / "base_agent.py"
        ]

        for base_file in base_files:
            if base_file.exists():
                try:
                    with open(base_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"✅ 加载BaseAgent: {base_file.name}")
                    return content
                except Exception as e:
                    print(f"❌ 加载BaseAgent失败: {e}")

        print("⚠️  未找到BaseAgent，创建基础版本")
        return self._create_basic_base_agent()

    def _create_basic_base_agent(self):
        """创建基础BaseAgent类"""
        return '''
import asyncio
import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

class BaseAgent:
    def __init__(self):
        self.name = "BaseAgent"
        self.role = "base"
        self.personality = {}
        self.api_config = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    async def process_user_input(self, user_input: str, session_context: Dict, scene: str = "general"):
        try:
            response_content = f"这是来自 {self.name} 的回复：{user_input}"

            if hasattr(self, '_generate_llm_response'):
                llm_response = await self._generate_llm_response(user_input, session_context, scene)
                if llm_response:
                    response_content = llm_response

            return {
                "content": response_content,
                "agent_name": self.name,
                "emotion": "😊",
                "learning_points": [],
                "suggestions": [],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "content": f"抱歉，{self.name} 暂时无法处理您的请求。",
                "agent_name": self.name,
                "emotion": "😅",
                "error": str(e)
            }

    async def _generate_llm_response(self, user_input: str, session_context: Dict, scene: str):
        if not self.api_config.get('api_key'):
            return f"[模拟回复] {self.name}: 您好！{user_input}"

        try:
            if hasattr(self, 'llm_client') and self.llm_client:
                return await self.llm_client.generate_response(user_input, session_context)
            else:
                return f"[API配置但客户端未初始化] {self.name}: {user_input}"
        except Exception as e:
            return f"[API调用失败] {self.name}: {str(e)}"
'''

    def _create_llm_client(self):
        """创建LLM客户端代码"""
        return '''
    import asyncio
    from typing import Dict

    class LLMClient:
        def __init__(self, config: Dict):
            self.config = config or {}
            # 让 provider 可读（用于日志/回显）
            self.provider = self.config.get('provider', 'unknown')

        async def generate_response(self, user_input: str, context: Dict = None):
            # 没有API Key则走本地模拟，以便开发期不阻塞
            if not self.config.get('api_key'):
                return f"[未配置API/{self.provider}] 收到: {user_input}"

            # TODO: 这里以后接真实HTTP调用
            return f"[{self.provider}] 智能响应: {user_input}"

        # === 兼容旧接口（关键补丁）===
        async def chat_completion(self, prompt: str = "", **kwargs):
            """
            兼容旧版agent调用的 chat_completion 接口。
            将其映射为 generate_response，避免 AttributeError。
            """
            # 兼容旧参数名 prompt/messages 等
            text = prompt or kwargs.get("messages") or kwargs.get("input") or ""
            ctx = kwargs.get("context") or {}
            return await self.generate_response(str(text), ctx)

    def get_llm_client(config: Dict = None):
        return LLMClient(config or {})
    '''

    def _fix_imports_and_inject_dependencies(self, content: str, agent_id: str) -> str:
        """修复导入并注入依赖"""

        # 仍然移除可能导致临时模块导入错误的语句
        patterns_to_remove = [
            r'from \.base_agent import BaseAgent',
            r'from utils\.llm_client import get_llm_client',
            r'from dotenv import load_dotenv'
        ]

        fixed_content = content
        for pattern in patterns_to_remove:
            fixed_content = re.sub(pattern, f'# {pattern} # 已修复', fixed_content)

        # —— 关键：去缩进 + 只注入一次 LLMClient 代码 ——
        header = textwrap.dedent("""\
        # ============ 自动注入的依赖 ============
        import asyncio
        import json
        import os
        import logging
        from typing import Dict, Any, Optional, List
        from datetime import datetime, timedelta
        """)

        base_agent_block = "# 注入BaseAgent类\n" + textwrap.dedent(self.base_agent_code) + "\n"
        llm_client_block = "# 注入LLM客户端（简版兜底）\n" + textwrap.dedent(self.llm_client_code) + "\n"

        override_block = textwrap.dedent("""\
        # 如果项目里存在真实实现，则覆盖注入版
        try:
            from utils.llm_client import get_llm_client as _real_get_llm_client
            get_llm_client = _real_get_llm_client
        except Exception:
            # 找不到就继续用注入版
            pass

        def load_dotenv():
            pass

        # ============ 原始智能体代码 ============
        """)

        injection = header + base_agent_block + llm_client_block + override_block
        return injection + fixed_content

    def _load_agent_from_file(self, file_path: Path, agent_id: str) -> Optional[Any]:
        """从文件加载智能体"""
        try:
            print(f"🔄 加载: {agent_id} ({file_path.name})")

            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            fixed_content = self._fix_imports_and_inject_dependencies(original_content, agent_id)

            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(fixed_content)
                temp_file_path = temp_file.name

            self.temp_modules.append(temp_file_path)

            # 动态导入
            spec = importlib.util.spec_from_file_location(f"agent_{agent_id}", temp_file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 查找智能体类
            agent_classes = []
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and
                        not name.startswith('_') and
                        name not in ['BaseAgent', 'LLMClient'] and
                        hasattr(obj, '__init__')):

                    if hasattr(obj, '__bases__'):
                        base_names = [base.__name__ for base in obj.__bases__]
                        if 'BaseAgent' in base_names:
                            agent_classes.append((name, obj))

            if agent_classes:
                # 选择最匹配的类
                selected_class = None
                for class_name, class_obj in agent_classes:
                    if agent_id.lower() in class_name.lower():
                        selected_class = class_obj
                        break

                if not selected_class:
                    selected_class = agent_classes[0][1]

                print(f"   ✅ 成功: {selected_class.__name__}")
                return selected_class
            else:
                print(f"   ❌ 未找到智能体类")
                return None

        except Exception as e:
            print(f"   ❌ 加载失败: {e}")
            return None

    def _load_all_agents(self):
        """加载所有智能体"""
        agent_files = {
            "tanaka": "tanaka_sensei.py",
            "koumi": "koumi.py",
            "ai": "ai_analyzer.py",
            "yamada": "yamada_sensei.py",
            "sato": "sato_coach.py",
            "membot": "mem_bot.py"
        }

        print(f"\n🚀 开始加载智能体...")

        loaded = 0
        total = len(agent_files)

        for agent_id, filename in agent_files.items():
            file_path = self.agents_path / filename

            if file_path.exists():
                agent_class = self._load_agent_from_file(file_path, agent_id)
                if agent_class:
                    self.agents[agent_id] = agent_class
                    loaded += 1
            else:
                print(f"❌ 文件不存在: {filename}")

        print(f"\n📊 加载总结: 成功 {loaded}/{total}")
        if loaded > 0:
            print(f"🎌 可用智能体: {list(self.agents.keys())}")

    def get_agent(self, agent_id: str):
        """获取智能体实例"""
        if agent_id in self.agents:
            agent_class = self.agents[agent_id]
            try:
                instance = agent_class()

                # 注入配置
                if hasattr(instance, 'api_config'):
                    instance.api_config = self.api_config

                # 注入简单的LLM客户端
                if not hasattr(instance, 'llm_client') or not instance.llm_client:
                    class SimpleLLMClient:
                        def __init__(self, provider, config):
                            self.provider = provider
                            self.config = config

                        async def generate_response(self, user_input, context=None):
                            if self.config.get('api_key'):
                                return f"[{self.provider}] 智能回复: {user_input}"
                            else:
                                return f"[模拟回复] 收到: {user_input}"

                    instance.llm_client = SimpleLLMClient(self.llm_provider, self.api_config)

                return instance

            except Exception as e:
                print(f"❌ 实例化 {agent_id} 失败: {e}")
                raise
        else:
            available = list(self.agents.keys())
            raise ValueError(f"Unknown agent: {agent_id}. Available: {available}")

    def list_available_agents(self) -> Dict[str, str]:
        """列出可用智能体"""
        return {agent_id: agent_class.__name__ for agent_id, agent_class in self.agents.items()}

    def cleanup(self):
        """清理临时文件"""
        for temp_file in self.temp_modules:
            try:
                os.unlink(temp_file)
            except Exception:
                pass


# 全局实例
_global_loader = None


def get_agent_loader():
    global _global_loader
    if _global_loader is None:
        _global_loader = CompleteAgentLoader()
    return _global_loader


def get_agent(agent_id: str):
    loader = get_agent_loader()
    return loader.get_agent(agent_id)


def list_agents():
    loader = get_agent_loader()
    return loader.list_available_agents()


# 兼容性
AGENT_REGISTRY = {}


def init_agent_registry():
    global AGENT_REGISTRY
    if not AGENT_REGISTRY:
        loader = get_agent_loader()
        AGENT_REGISTRY = {agent_id: agent_class for agent_id, agent_class in loader.agents.items()}
    return AGENT_REGISTRY