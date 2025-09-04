# -*- coding: utf-8 -*-
"""
Package exports for the core module.
只做“相对导入”，避免运行方式不同导致找不到 core 包。
"""

# 适配层：你工程里提供了 src/core/grammar_workflows.py 的转发
from .grammar_workflows import GrammarCollaborationWorkflows  # noqa: F401

# 让外部可以 “from core.workflows import CollaborationWorkflow”
from .workflows import CollaborationWorkflow  # noqa: F401

# collaboration 相关（如果没有真实 orchestrator，也不会报错）
try:
    from .collaboration import (  # noqa: F401
        MultiAgentOrchestrator,
        CollaborationMode,
    )
except Exception:
    pass

__all__ = [
    "GrammarCollaborationWorkflows",
    "CollaborationWorkflow",
    "MultiAgentOrchestrator",
    "CollaborationMode",
]
