# core/workflows/collaboration.py
"""
Enhanced Multi-Agent Collaboration Orchestrator
基于现有架构扩展的智能体协作编排系统
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

# 导入现有的智能体
from ..agents.core_agents.tanaka_sensei import TanakaSensei
from ..agents.core_agents.koumi import KoumiAgent  # 用户更正：是KoumiAgent
from ..agents.core_agents.ai_analyzer import AIAnalyzer
from ..agents.core_agents.yamada_sensei import YamadaSensei
from ..agents.core_agents.sato_coach import SatoCoach
from ..agents.core_agents.mem_bot import MemBot


class CollaborationMode(Enum):
    """协作模式枚举"""
    DISCUSSION = "discussion"  # 讨论模式：智能体们自由讨论
    CORRECTION = "correction"  # 纠错模式：协作纠正用户错误
    CREATION = "creation"  # 创作模式：协作创作内容
    ANALYSIS = "analysis"  # 分析模式：多角度分析问题


@dataclass
class AgentResponse:
    """智能体响应数据结构"""
    agent_id: str
    agent_name: str
    content: str
    confidence: float  # 0.0-1.0 confidence score
    emotion: str
    learning_points: List[str]
    suggestions: List[str]
    timestamp: datetime
    agrees_with: List[str] = None  # 同意哪些其他智能体
    disagrees_with: List[str] = None  # 不同意哪些其他智能体


@dataclass
class CollaborationResult:
    """协作结果数据结构"""
    responses: List[AgentResponse]
    consensus: Optional[str]  # 达成的共识
    conflicts: List[Tuple[str, str, str]]  # (agent1, agent2, conflict_point)
    final_recommendation: str
    user_arbitration_needed: bool
    session_id: str


class MultiAgentOrchestrator:
    """多智能体协作编排器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 初始化所有智能体
        self.agents = {
            "tanaka": TanakaSensei(),
            "koumi": KoumiAgent(),  # 修正名称
            "ai": AIAnalyzer(),
            "yamada": YamadaSensei(),
            "sato": SatoCoach(),
            "membot": MemBot()
        }

        # 智能体专长领域定义
        self.agent_expertise = {
            "tanaka": ["grammar", "syntax", "formal_language"],
            "koumi": ["conversation", "casual_language", "youth_culture"],
            "ai": ["analysis", "statistics", "learning_optimization"],
            "yamada": ["culture", "history", "traditional_knowledge"],
            "sato": ["jlpt", "exam_strategy", "goal_setting"],
            "membot": ["memory", "spaced_repetition", "progress_tracking"]
        }

        # 协作历史记录
        self.collaboration_history = []

    async def orchestrate_collaboration(
            self,
            user_input: str,
            active_agents: List[str],
            mode: CollaborationMode,
            session_context: Dict[str, Any]
    ) -> CollaborationResult:
        """
        编排多智能体协作

        Args:
            user_input: 用户输入
            active_agents: 参与的智能体列表
            mode: 协作模式
            session_context: 会话上下文
        """
        session_id = session_context.get('session_id', f"session_{datetime.now().timestamp()}")

        self.logger.info(f"开始多智能体协作: {mode.value}, 参与者: {active_agents}")

        # 根据协作模式选择不同的协作策略
        if mode == CollaborationMode.DISCUSSION:
            return await self._handle_discussion_mode(user_input, active_agents, session_context)
        elif mode == CollaborationMode.CORRECTION:
            return await self._handle_correction_mode(user_input, active_agents, session_context)
        elif mode == CollaborationMode.CREATION:
            return await self._handle_creation_mode(user_input, active_agents, session_context)
        elif mode == CollaborationMode.ANALYSIS:
            return await self._handle_analysis_mode(user_input, active_agents, session_context)
        else:
            # 默认讨论模式
            return await self._handle_discussion_mode(user_input, active_agents, session_context)

    async def _handle_discussion_mode(
            self,
            user_input: str,
            active_agents: List[str],
            session_context: Dict[str, Any]
    ) -> CollaborationResult:
        """处理讨论模式的协作"""

        responses = []

        # 第一轮：各智能体独立回应
        first_round_tasks = []
        for agent_id in active_agents:
            if agent_id in self.agents:
                task = self._get_agent_response(agent_id, user_input, session_context)
                first_round_tasks.append(task)

        first_round_responses = await asyncio.gather(*first_round_tasks)
        responses.extend(first_round_responses)

        # 检测冲突和分歧
        conflicts = self._detect_conflicts(first_round_responses)

        # 如果有分歧，进行第二轮讨论
        if conflicts:
            second_round_responses = await self._handle_conflicts(
                conflicts, active_agents, session_context
            )
            responses.extend(second_round_responses)

        # 尝试达成共识
        consensus = self._attempt_consensus(responses)
        final_recommendation = self._generate_final_recommendation(responses)

        return CollaborationResult(
            responses=responses,
            consensus=consensus,
            conflicts=conflicts,
            final_recommendation=final_recommendation,
            user_arbitration_needed=len(conflicts) > 0 and consensus is None,
            session_id=session_context.get('session_id')
        )

    async def _handle_correction_mode(
            self,
            user_input: str,
            active_agents: List[str],
            session_context: Dict[str, Any]
    ) -> CollaborationResult:
        """处理纠错模式的协作 - 多智能体协作纠正用户错误"""

        responses = []

        # 按专长顺序进行协作纠错
        correction_sequence = self._optimize_correction_sequence(active_agents)

        accumulated_analysis = {"original_input": user_input, "corrections": []}

        for agent_id in correction_sequence:
            if agent_id in self.agents:
                # 传递之前智能体的分析结果
                enhanced_context = {
                    **session_context,
                    "previous_analysis": accumulated_analysis,
                    "collaboration_mode": "correction"
                }

                response = await self._get_agent_response(agent_id, user_input, enhanced_context)
                responses.append(response)

                # 累积分析结果
                accumulated_analysis["corrections"].append({
                    "agent": agent_id,
                    "corrections": response.suggestions,
                    "confidence": response.confidence
                })

        # 生成最终的纠错建议
        final_recommendation = self._synthesize_corrections(responses)

        return CollaborationResult(
            responses=responses,
            consensus=None,  # 纠错模式不需要共识
            conflicts=[],  # 纠错模式冲突较少
            final_recommendation=final_recommendation,
            user_arbitration_needed=False,
            session_id=session_context.get('session_id')
        )

    async def _handle_creation_mode(
            self,
            user_input: str,
            active_agents: List[str],
            session_context: Dict[str, Any]
    ) -> CollaborationResult:
        """处理创作模式的协作 - 多智能体协作创作"""

        responses = []

        # 创作模式的协作流程
        creation_phases = ["brainstorm", "structure", "create", "refine"]

        for phase in creation_phases:
            phase_context = {
                **session_context,
                "creation_phase": phase,
                "previous_contributions": responses
            }

            # 每个阶段让智能体们轮流贡献
            for agent_id in active_agents:
                if agent_id in self.agents:
                    response = await self._get_agent_response(agent_id, user_input, phase_context)
                    response.content = f"[{phase.upper()}] {response.content}"
                    responses.append(response)

        # 整合创作成果
        final_recommendation = self._integrate_creative_output(responses)

        return CollaborationResult(
            responses=responses,
            consensus=None,  # 创作模式更重视多样性
            conflicts=[],
            final_recommendation=final_recommendation,
            user_arbitration_needed=False,
            session_id=session_context.get('session_id')
        )

    async def _handle_analysis_mode(
            self,
            user_input: str,
            active_agents: List[str],
            session_context: Dict[str, Any]
    ) -> CollaborationResult:
        """处理分析模式的协作 - 多角度深度分析"""

        responses = []

        # 为每个智能体分配特定的分析角度
        analysis_assignments = self._assign_analysis_perspectives(active_agents)

        analysis_tasks = []
        for agent_id, perspective in analysis_assignments.items():
            if agent_id in self.agents:
                enhanced_context = {
                    **session_context,
                    "analysis_perspective": perspective,
                    "collaboration_mode": "analysis"
                }
                task = self._get_agent_response(agent_id, user_input, enhanced_context)
                analysis_tasks.append(task)

        responses = await asyncio.gather(*analysis_tasks)

        # 综合分析结果
        final_recommendation = self._synthesize_analysis(responses)

        return CollaborationResult(
            responses=responses,
            consensus=None,  # 分析模式重视多元观点
            conflicts=[],
            final_recommendation=final_recommendation,
            user_arbitration_needed=False,
            session_id=session_context.get('session_id')
        )

    async def _get_agent_response(
            self,
            agent_id: str,
            user_input: str,
            session_context: Dict[str, Any]
    ) -> AgentResponse:
        """获取单个智能体的响应"""

        try:
            agent = self.agents[agent_id]

            # 调用智能体的现有方法
            result = await agent.process_user_input(
                user_input=user_input,
                session_context=session_context,
                scene=session_context.get('scene', 'general')
            )

            return AgentResponse(
                agent_id=agent_id,
                agent_name=getattr(agent, 'name', agent_id),
                content=result.get('content', ''),
                confidence=result.get('confidence', 0.8),
                emotion=result.get('emotion', '😊'),
                learning_points=result.get('learning_points', []),
                suggestions=result.get('suggestions', []),
                timestamp=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"Agent {agent_id} 响应错误: {str(e)}")
            return AgentResponse(
                agent_id=agent_id,
                agent_name=agent_id,
                content=f"抱歉，我暂时无法回应：{str(e)}",
                confidence=0.0,
                emotion="😅",
                learning_points=[],
                suggestions=[],
                timestamp=datetime.now()
            )

    def _detect_conflicts(self, responses: List[AgentResponse]) -> List[Tuple[str, str, str]]:
        """检测智能体间的冲突和分歧"""
        conflicts = []

        # 简化的冲突检测逻辑
        # 实际应用中可以使用更复杂的语义分析

        for i, resp1 in enumerate(responses):
            for j, resp2 in enumerate(responses[i + 1:], i + 1):
                # 检测关键词冲突
                conflict_indicators = [
                    ("错误", "正确"),
                    ("不对", "对的"),
                    ("应该", "不应该"),
                    ("必须", "不必"),
                ]

                for indicator1, indicator2 in conflict_indicators:
                    if indicator1 in resp1.content and indicator2 in resp2.content:
                        conflicts.append((
                            resp1.agent_id,
                            resp2.agent_id,
                            f"关于 '{user_input}' 的观点存在分歧"
                        ))
                        break

        return conflicts

    async def _handle_conflicts(
            self,
            conflicts: List[Tuple[str, str, str]],
            active_agents: List[str],
            session_context: Dict[str, Any]
    ) -> List[AgentResponse]:
        """处理智能体间的冲突"""

        resolution_responses = []

        for agent1, agent2, conflict_point in conflicts:
            # 让冲突双方进一步解释自己的观点
            resolution_context = {
                **session_context,
                "conflict_resolution": True,
                "conflict_with": agent2 if agent1 in self.agents else agent1,
                "conflict_point": conflict_point
            }

            if agent1 in self.agents:
                prompt = f"请进一步解释你对 '{conflict_point}' 的观点，并考虑其他可能性。"
                response = await self._get_agent_response(agent1, prompt, resolution_context)
                response.content = f"[解释观点] {response.content}"
                resolution_responses.append(response)

            if agent2 in self.agents:
                prompt = f"请进一步解释你对 '{conflict_point}' 的观点，并考虑其他可能性。"
                response = await self._get_agent_response(agent2, prompt, resolution_context)
                response.content = f"[解释观点] {response.content}"
                resolution_responses.append(response)

        return resolution_responses

    def _optimize_correction_sequence(self, active_agents: List[str]) -> List[str]:
        """优化纠错协作的智能体顺序"""
        # 按专业领域优化顺序：语法 -> 文化 -> 口语 -> 分析
        preferred_order = ["tanaka", "yamada", "koumi", "ai", "sato", "membot"]

        # 保持活跃智能体中符合优先顺序的排列
        optimized = []
        for agent_id in preferred_order:
            if agent_id in active_agents:
                optimized.append(agent_id)

        # 添加剩余的智能体
        for agent_id in active_agents:
            if agent_id not in optimized:
                optimized.append(agent_id)

        return optimized

    def _assign_analysis_perspectives(self, active_agents: List[str]) -> Dict[str, str]:
        """为分析模式分配不同的分析角度"""
        perspectives = {
            "tanaka": "语法和语言结构分析",
            "koumi": "实际应用和交流效果分析",
            "ai": "数据和学习效果分析",
            "yamada": "文化背景和深层含义分析",
            "sato": "考试应用和目标达成分析",
            "membot": "记忆和长期学习效果分析"
        }

        return {agent_id: perspectives.get(agent_id, "综合分析")
                for agent_id in active_agents if agent_id in self.agents}

    def _attempt_consensus(self, responses: List[AgentResponse]) -> Optional[str]:
        """尝试在智能体间达成共识"""
        if len(responses) < 2:
            return None

        # 简化的共识算法
        # 实际应用中可以使用更复杂的语义相似度计算

        common_points = []
        for resp in responses:
            if resp.confidence > 0.7:  # 高置信度的回应
                common_points.extend(resp.learning_points)

        if common_points:
            return f"智能体们达成共识：{', '.join(set(common_points))}"

        return None

    def _generate_final_recommendation(self, responses: List[AgentResponse]) -> str:
        """生成最终建议"""
        if not responses:
            return "暂时无法生成建议。"

        # 收集所有建议
        all_suggestions = []
        high_confidence_content = []

        for resp in responses:
            all_suggestions.extend(resp.suggestions)
            if resp.confidence > 0.7:
                high_confidence_content.append(f"{resp.agent_name}: {resp.content[:100]}...")

        # 构建最终建议
        final_rec = "📋 协作总结:\n\n"

        if high_confidence_content:
            final_rec += "🎯 关键观点:\n"
            for content in high_confidence_content[:3]:  # 最多3个关键观点
                final_rec += f"• {content}\n"
            final_rec += "\n"

        if all_suggestions:
            unique_suggestions = list(set(all_suggestions))
            final_rec += "💡 建议:\n"
            for suggestion in unique_suggestions[:5]:  # 最多5个建议
                final_rec += f"• {suggestion}\n"

        return final_rec

    def _synthesize_corrections(self, responses: List[AgentResponse]) -> str:
        """综合纠错建议"""
        corrections = []
        for resp in responses:
            if resp.suggestions:
                corrections.extend(resp.suggestions)

        if not corrections:
            return "没有发现需要纠正的问题。"

        return f"📝 协作纠错建议:\n" + "\n".join([f"• {c}" for c in corrections[:10]])

    def _integrate_creative_output(self, responses: List[AgentResponse]) -> str:
        """整合创作输出"""
        phases = {"brainstorm": [], "structure": [], "create": [], "refine": []}

        for resp in responses:
            for phase in phases.keys():
                if f"[{phase.upper()}]" in resp.content:
                    phases[phase].append(resp.content)

        integrated = "🎨 协作创作成果:\n\n"
        for phase, contents in phases.items():
            if contents:
                integrated += f"## {phase.title()} 阶段:\n"
                for content in contents[:2]:  # 每阶段最多2个贡献
                    integrated += f"• {content.replace(f'[{phase.upper()}]', '').strip()}\n"
                integrated += "\n"

        return integrated

    def _synthesize_analysis(self, responses: List[AgentResponse]) -> str:
        """综合分析结果"""
        analysis = "🔍 多角度分析结果:\n\n"

        for resp in responses:
            if resp.content.strip():
                analysis += f"**{resp.agent_name}的分析:**\n"
                analysis += f"{resp.content[:200]}...\n\n"

        # 收集共同学习点
        all_learning_points = []
        for resp in responses:
            all_learning_points.extend(resp.learning_points)

        if all_learning_points:
            unique_points = list(set(all_learning_points))
            analysis += "📚 关键学习点:\n"
            for point in unique_points[:5]:
                analysis += f"• {point}\n"

        return analysis


# 导出主要类
__all__ = ['MultiAgentOrchestrator', 'CollaborationMode', 'CollaborationResult', 'AgentResponse']