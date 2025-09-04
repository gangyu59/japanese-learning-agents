# -*- coding: utf-8 -*-
"""
Expose workflow symbols for legacy imports used by tests:
- from core.workflows import CollaborationWorkflow
- keep optional orchestrator symbols if present
"""

# 先把“语法协作工作流”作为 CollaborationWorkflow 暴露出来
from .grammar_workflows import (  # noqa: F401
    GrammarCollaborationWorkflows as CollaborationWorkflow,
)

# 可选地把编排器相关符号也透出（不存在就给到 None，占位）
try:
    from .collaboration import (  # type: ignore
        MultiAgentOrchestrator,  # noqa: F401
        CollaborationMode,       # noqa: F401
    )
except Exception:
    MultiAgentOrchestrator = None  # type: ignore
    class CollaborationMode:       # type: ignore
        pass

__all__ = ["CollaborationWorkflow", "MultiAgentOrchestrator", "CollaborationMode"]
