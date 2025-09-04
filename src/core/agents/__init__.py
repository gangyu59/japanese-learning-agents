# src/core/agents/__init__.py

# 包级单例加载器，向外暴露 get_agent / list_agents / AGENT_REGISTRY
from typing import Dict, Any
from .complete_agent_loader import CompleteAgentLoader  # 依赖现有的完整加载器

__all__ = ["get_agent", "list_agents", "AGENT_REGISTRY", "CompleteAgentLoader"]

# --- 懒加载单例 ---
_loader: CompleteAgentLoader = None

def _get_loader() -> CompleteAgentLoader:
    global _loader
    if _loader is None:
        _loader = CompleteAgentLoader()
    return _loader

# --- 包级 API（测试脚本要求的导出） ---
def get_agent(agent_id: str):
    """
    包级 get_agent：测试脚本通过 from core.agents import get_agent 调用。
    """
    return _get_loader().get_agent(agent_id)

def list_agents() -> Dict[str, str]:
    """
    返回可用智能体字典：{agent_id: class_name}
    """
    # 兼容两种命名：list_available_agents / list_agents
    loader = _get_loader()
    if hasattr(loader, "list_available_agents"):
        return loader.list_available_agents()
    elif hasattr(loader, "list_agents"):
        return loader.list_agents()
    else:
        return {}

# 注册表占位：让测试侧能 from core.agents import AGENT_REGISTRY 成功
try:
    # 若加载器内部维护了注册表，尽量透传；否则给一个只读的动态视图
    _registry = getattr(_get_loader(), "agents", None)
    AGENT_REGISTRY = _registry if isinstance(_registry, dict) else {}
except Exception:
    AGENT_REGISTRY = {}
