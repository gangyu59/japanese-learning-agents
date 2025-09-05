# -*- coding: utf-8 -*-
"""
Compatibility re-exports for workflows.

目标：
- 统一从此包导出 CollaborationWorkflow（别名自 GrammarCollaborationWorkflows）
- 同时导出 MultiAgentOrchestrator / CollaborationMode
- 透传 novel_collab 模块
- 既支持 "from src.core.workflows ..." 也支持 "from core.workflows ..."
"""

from .grammar_workflows import (
    GrammarCollaborationWorkflows as CollaborationWorkflow,
)
from .collaboration import (
    MultiAgentOrchestrator,
    CollaborationMode,
)
# 让 main.py 能用： from src.core.workflows import novel_collab as flow
from . import novel_collab  # noqa: F401

__all__ = [
    "CollaborationWorkflow",
    "MultiAgentOrchestrator",
    "CollaborationMode",
    "novel_collab",
]
