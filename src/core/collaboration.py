# -*- coding: utf-8 -*-
"""
Compatibility layer so both:
  - from core.collaboration import MultiAgentOrchestrator, CollaborationMode
  - from src.core.collaboration import ...
work in your current tree.
优先从 “src/core/workflows/collaboration.py” 导入；若不存在，给到占位对象。
"""
from __future__ import annotations

# 全部使用包内相对导入，避免 “No module named 'core'”
try:
    from .workflows.collaboration import (  # type: ignore
        MultiAgentOrchestrator,
        CollaborationMode,
    )
except Exception:
    # 没有真正的 orchestrator 文件也不致命 —— 给出占位，防止 import 失败
    MultiAgentOrchestrator = None  # type: ignore

    class CollaborationMode:  # type: ignore
        pass

__all__ = ["MultiAgentOrchestrator", "CollaborationMode"]
