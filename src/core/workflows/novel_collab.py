# -*- coding: utf-8 -*-
from typing import Dict, Any
import asyncio
from .collaboration import MultiAgentOrchestrator, CollaborationMode

# 兼容你此前写过的“也许返回协程/也许同步”的 agent 接口工具（简化版）
async def _maybe_await(x):
    if asyncio.iscoroutine(x):
        return await x
    return x

async def brainstorm_meeting(agents: Dict[str, object], topic: str, session_id: str) -> Dict[str, Any]:
    orch = MultiAgentOrchestrator()
    res = await orch.orchestrate_collaboration(
        user_input=f"就主题「{topic}」进行创意头脑风暴。",
        active_agents=list(agents.keys()) if agents else ["koumi", "yamada", "ai"],
        mode=CollaborationMode.DISCUSSION,
        session_context={"session_id": session_id, "workflow_type": "novel_brainstorm"},
    )
    return {"ideas": [r.content for r in res.responses], "session_id": session_id}

async def co_write_novel(agents: Dict[str, object], outline: str, session_id: str) -> Dict[str, Any]:
    orch = MultiAgentOrchestrator()
    res = await orch.orchestrate_collaboration(
        user_input=f"按大纲协同创作：{outline}",
        active_agents=list(agents.keys()) if agents else ["koumi", "yamada", "tanaka"],
        mode=CollaborationMode.CREATION,
        session_context={"session_id": session_id, "workflow_type": "novel_cowrite"},
    )
    return {"fragments": [r.content for r in res.responses], "session_id": session_id}

async def review_and_edit(agents: Dict[str, object], draft: str, session_id: str) -> Dict[str, Any]:
    orch = MultiAgentOrchestrator()
    res = await orch.orchestrate_collaboration(
        user_input=f"请审阅并编辑这段草稿：{draft}",
        active_agents=list(agents.keys()) if agents else ["tanaka", "koumi", "ai"],
        mode=CollaborationMode.ANALYSIS,
        session_context={"session_id": session_id, "workflow_type": "novel_review"},
    )
    return {"reviews": [r.content for r in res.responses], "session_id": session_id}
