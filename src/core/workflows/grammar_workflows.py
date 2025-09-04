# -*- coding: utf-8 -*-
"""
语法协作工作流（与 orchestrator 对齐）
"""
import logging
from typing import Dict, Any, List
from .collaboration import MultiAgentOrchestrator, CollaborationMode

class GrammarCollaborationWorkflows:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.orch = MultiAgentOrchestrator()

    async def collaborative_grammar_correction(self, user_input: str, session_context: Dict[str, Any]) -> Dict[str, Any]:
        agents = ["tanaka", "yamada", "koumi", "ai"]
        result = await self.orch.orchestrate_collaboration(
            user_input=user_input,
            active_agents=agents,
            mode=CollaborationMode.CORRECTION,
            session_context={**session_context, "workflow_type": "grammar_correction"},
        )
        return {
            "type": "collaborative_grammar_correction",
            "original_input": user_input,
            "agents_participated": agents,
            "final_recommendation": result.final_recommendation,
            "learning_points": _collect_learning_points(result.responses),
            "session_id": session_context.get("session_id"),
        }

    async def grammar_explanation_discussion(self, grammar_point: str, user_question: str, session_context: Dict[str, Any]) -> Dict[str, Any]:
        q = f"请从不同角度解释语法「{grammar_point}」并回答：{user_question}"
        agents = ["tanaka", "yamada", "koumi", "sato"]
        result = await self.orch.orchestrate_collaboration(
            user_input=q,
            active_agents=agents,
            mode=CollaborationMode.ANALYSIS,
            session_context={**session_context, "workflow_type": "grammar_explanation", "grammar_point": grammar_point},
        )
        return {
            "type": "grammar_explanation_discussion",
            "grammar_point": grammar_point,
            "explanations": [r.content for r in result.responses],
            "summary": result.final_recommendation,
            "agents_participated": agents,
        }

    async def sentence_building_collaboration(self, target_grammar: str, context_hint: str, session_context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"请帮助用户使用语法「{target_grammar}」写例句。上下文提示：{context_hint}"
        agents = ["tanaka", "koumi", "yamada"]
        result = await self.orch.orchestrate_collaboration(
            user_input=prompt,
            active_agents=agents,
            mode=CollaborationMode.CREATION,
            session_context={**session_context, "workflow_type": "sentence_building", "target_grammar": target_grammar},
        )
        return {
            "type": "sentence_building_collaboration",
            "target_grammar": target_grammar,
            "examples": [r.content for r in result.responses],
            "agents_participated": agents,
        }

def _collect_learning_points(responses) -> List[str]:
    pts: List[str] = []
    for r in responses:
        pts.extend(r.learning_points or [])
    # 去重
    seen = set()
    uniq = []
    for x in pts:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq
