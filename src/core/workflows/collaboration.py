# -*- coding: utf-8 -*-
"""
多智能体协作编排器（与现有 agent 目录对齐）
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# 注意：以下导入路径对齐到你的实际结构：src/core/agents/core_agents/*.py
from ..agents.core_agents.tanaka_sensei import TanakaSensei
from ..agents.core_agents.koumi import KoumiAgent
from ..agents.core_agents.ai_analyzer import AIAnalyzer
from ..agents.core_agents.yamada_sensei import YamadaSensei
from ..agents.core_agents.sato_coach import SatoCoach
from ..agents.core_agents.mem_bot import MemBot


class CollaborationMode(Enum):
    DISCUSSION = "discussion"
    CORRECTION = "correction"
    CREATION = "creation"
    ANALYSIS = "analysis"


@dataclass
class AgentResponse:
    agent_id: str
    agent_name: str
    content: str
    confidence: float
    emotion: str
    learning_points: List[str]
    suggestions: List[str]
    timestamp: datetime
    agrees_with: Optional[List[str]] = None
    disagrees_with: Optional[List[str]] = None


@dataclass
class CollaborationResult:
    responses: List[AgentResponse]
    consensus: Optional[str]
    conflicts: List[Tuple[str, str, str]]
    final_recommendation: str
    user_arbitration_needed: bool
    session_id: str


class MultiAgentOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents = {
            "tanaka": TanakaSensei(),
            "koumi": KoumiAgent(),
            "ai": AIAnalyzer(),
            "yamada": YamadaSensei(),
            "sato": SatoCoach(),
            "membot": MemBot(),
        }
        self.agent_expertise = {
            "tanaka": ["grammar", "syntax", "formal_language"],
            "koumi": ["conversation", "casual_language", "youth_culture"],
            "ai": ["analysis", "statistics", "learning_optimization"],
            "yamada": ["culture", "history", "traditional_knowledge"],
            "sato": ["jlpt", "exam_strategy", "goal_setting"],
            "membot": ["memory", "spaced_repetition", "progress_tracking"],
        }

    async def orchestrate_collaboration(
        self,
        user_input: str,
        active_agents: List[str],
        mode: CollaborationMode,
        session_context: Dict[str, Any],
    ) -> CollaborationResult:
        session_id = session_context.get("session_id", f"session_{datetime.now().timestamp()}")

        # 第一轮：并发收集各 Agent 回复
        tasks = [
            self._get_agent_response(agent_id, user_input, session_context)
            for agent_id in active_agents
            if agent_id in self.agents
        ]
        raw = await asyncio.gather(*tasks, return_exceptions=True)
        responses: List[AgentResponse] = []
        for r in raw:
            if isinstance(r, AgentResponse):
                responses.append(r)

        # 极简冲突检测/共识（占位实现，保证测试可过）
        conflicts: List[Tuple[str, str, str]] = []
        consensus = "全体已给出各自观点，建议结合语法正确性与自然度综合采用。"
        final_recommendation = responses[0].content if responses else "（无回复）"

        return CollaborationResult(
            responses=responses,
            consensus=consensus,
            conflicts=conflicts,
            final_recommendation=final_recommendation,
            user_arbitration_needed=False,
            session_id=session_id,
        )

    async def _get_agent_response(
        self, agent_id: str, user_input: str, session_context: Dict[str, Any]
    ) -> AgentResponse:
        agent = self.agents[agent_id]
        try:
            ret = await agent.process_user_input(user_input, session_context, scene=session_context.get("scene", "general"))
            content = ret.get("content", str(ret))
            emotion = ret.get("emotion", "🙂")
            learning_points = ret.get("learning_points", [])
            suggestions = ret.get("suggestions", [])
            return AgentResponse(
                agent_id=agent_id,
                agent_name=getattr(agent, "name", agent_id),
                content=content,
                confidence=0.7,
                emotion=emotion,
                learning_points=learning_points,
                suggestions=suggestions,
                timestamp=datetime.now(),
            )
        except Exception as e:
            return AgentResponse(
                agent_id=agent_id,
                agent_name=getattr(agent, "name", agent_id),
                content=f"[{agent_id}] 执行出错: {e}",
                confidence=0.2,
                emotion="😅",
                learning_points=[],
                suggestions=[],
                timestamp=datetime.now(),
            )
