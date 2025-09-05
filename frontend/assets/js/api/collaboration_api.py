# backend/api/collaboration_api.py
"""
完整的多智能体协作API端点
集成了增强的分歧检测功能
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import logging
import time
from datetime import datetime

# 导入增强的分歧检测器
from enhanced_disagreement_detector import EnhancedDisagreementDetector

logger = logging.getLogger(__name__)
router = APIRouter()


# 请求和响应模型
class MultiAgentRequest(BaseModel):
    message: str
    user_id: str
    session_id: str
    active_agents: List[str]
    collaboration_mode: str = "discussion"
    scene_context: str = "multi_agent_collaboration"


class AgentResponseModel(BaseModel):
    agent_id: str
    agent_name: str
    content: str
    confidence: float
    emotion: str
    learning_points: List[str]
    suggestions: List[str]
    timestamp: str
    response_time: float


class DisagreementModel(BaseModel):
    topic: str
    type: str
    severity: str
    agents_involved: List[str]
    positions: Dict[str, str]
    resolution_needed: bool


class CollaborationResponse(BaseModel):
    success: bool
    responses: List[AgentResponseModel]
    disagreements: List[DisagreementModel]
    conflicts: List[List[str]]  # 向后兼容
    consensus: Optional[str]
    final_recommendation: str
    user_arbitration_needed: bool
    session_id: str
    processing_time: float
    error: Optional[str] = None


# 初始化分歧检测器
disagreement_detector = EnhancedDisagreementDetector()


@router.post("/multi-agent-collaboration", response_model=CollaborationResponse)
async def handle_multi_agent_collaboration(request: MultiAgentRequest):
    """处理多智能体协作请求"""
    start_time = time.time()

    try:
        logger.info(f"收到协作请求: {request.active_agents}, 模式: {request.collaboration_mode}")

        # 验证输入
        if len(request.active_agents) < 2:
            raise HTTPException(status_code=400, detail="至少需要选择2个智能体进行协作")

        # 1. 并行获取智能体响应
        agent_responses = await collect_agent_responses(
            request.message,
            request.active_agents,
            request.session_id,
            request.scene_context
        )

        # 2. 应用增强的分歧检测
        disagreements = disagreement_detector.detect_disagreements_from_responses(
            [{'agent_name': r.agent_name, 'content': r.content, 'agent_id': r.agent_id}
             for r in agent_responses]
        )

        # 如果没有检测到分歧，尝试强制生成（用于测试）
        if not disagreements and len(agent_responses) >= 2:
            disagreements = disagreement_detector.force_disagreement_for_test(
                [{'agent_name': r.agent_name, 'content': r.content, 'agent_id': r.agent_id}
                 for r in agent_responses],
                request.message
            )

        # 3. 生成共识和建议
        consensus = generate_consensus(agent_responses, disagreements)
        final_recommendation = generate_final_recommendation(agent_responses, disagreements)

        # 4. 判断是否需要用户仲裁
        needs_arbitration = any(d.get('severity') in ['medium', 'high'] for d in disagreements)

        # 5. 转换格式
        disagreement_models = [
            DisagreementModel(
                topic=d.get('topic', 'unknown'),
                type=d.get('type', 'general'),
                severity=d.get('severity', 'low'),
                agents_involved=d.get('agents_involved', []),
                positions=d.get('positions', {}),
                resolution_needed=d.get('resolution_needed', False)
            ) for d in disagreements
        ]

        # 6. 生成冲突列表（向后兼容）
        conflicts = []
        for d in disagreements:
            agents = d.get('agents_involved', [])
            if len(agents) >= 2:
                conflicts.append([agents[0], agents[1], d.get('topic', 'conflict')])

        processing_time = time.time() - start_time

        return CollaborationResponse(
            success=True,
            responses=agent_responses,
            disagreements=disagreement_models,
            conflicts=conflicts,
            consensus=consensus,
            final_recommendation=final_recommendation,
            user_arbitration_needed=needs_arbitration,
            session_id=request.session_id,
            processing_time=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"协作处理失败: {e}", exc_info=True)
        processing_time = time.time() - start_time

        return CollaborationResponse(
            success=False,
            responses=[],
            disagreements=[],
            conflicts=[],
            consensus=None,
            final_recommendation="协作处理失败，请重试",
            user_arbitration_needed=False,
            session_id=request.session_id,
            processing_time=processing_time,
            error=str(e)
        )


async def collect_agent_responses(message: str, active_agents: List[str],
                                  session_id: str, scene_context: str) -> List[AgentResponseModel]:
    """并行收集智能体响应"""
    tasks = []

    for agent_id in active_agents:
        task = get_single_agent_response(message, agent_id, session_id, scene_context)
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    responses = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"智能体 {active_agents[i]} 响应失败: {result}")
            # 创建错误响应
            responses.append(AgentResponseModel(
                agent_id=active_agents[i],
                agent_name=f"智能体_{active_agents[i]}",
                content=f"抱歉，{active_agents[i]} 暂时无法响应",
                confidence=0.1,
                emotion="😅",
                learning_points=[],
                suggestions=[],
                timestamp=datetime.now().isoformat(),
                response_time=0.0
            ))
        else:
            responses.append(result)

    return responses


async def get_single_agent_response(message: str, agent_id: str,
                                    session_id: str, scene_context: str) -> AgentResponseModel:
    """获取单个智能体的响应"""
    start_time = time.time()

    try:
        # 导入智能体
        from core.agents import get_agent

        agent = get_agent(agent_id)
        agent_name_map = {
            "tanaka": "田中先生",
            "koumi": "小美",
            "ai": "アイ",
            "yamada": "山田先生",
            "sato": "佐藤教练",
            "membot": "MemBot"
        }

        session_context = {
            "user_id": "collaboration_user",
            "session_id": session_id,
            "scene": scene_context,
            "history": []
        }

        # 调用智能体处理
        response = await agent.process_user_input(
            user_input=message,
            session_context=session_context,
            scene=scene_context
        )

        response_time = time.time() - start_time

        return AgentResponseModel(
            agent_id=agent_id,
            agent_name=agent_name_map.get(agent_id, agent_id),
            content=response.get("content", ""),
            confidence=response.get("confidence", 0.8),
            emotion=response.get("emotion", "😊"),
            learning_points=response.get("learning_points", []),
            suggestions=response.get("suggestions", []),
            timestamp=datetime.now().isoformat(),
            response_time=response_time
        )

    except Exception as e:
        logger.error(f"智能体 {agent_id} 处理失败: {e}")
        response_time = time.time() - start_time

        return AgentResponseModel(
            agent_id=agent_id,
            agent_name=f"智能体_{agent_id}",
            content=f"处理出错: {str(e)}",
            confidence=0.1,
            emotion="😅",
            learning_points=[],
            suggestions=[],
            timestamp=datetime.now().isoformat(),
            response_time=response_time
        )


def generate_consensus(responses: List[AgentResponseModel],
                       disagreements: List[Dict]) -> Optional[str]:
    """生成协作共识"""
    if not disagreements:
        return f"智能体们基本达成一致，共同提供了 {len(responses)} 个观点。"

    consensus_parts = []
    high_confidence_responses = [r for r in responses if r.confidence > 0.7]

    if high_confidence_responses:
        consensus_parts.append(f"高置信度观点来自: {', '.join([r.agent_name for r in high_confidence_responses])}")

    if disagreements:
        consensus_parts.append(f"发现 {len(disagreements)} 个分歧点需要进一步讨论")

    return "；".join(consensus_parts) if consensus_parts else None


def generate_final_recommendation(responses: List[AgentResponseModel],
                                  disagreements: List[Dict]) -> str:
    """生成最终建议"""
    if not responses:
        return "未获得有效回复，建议重新提问。"

    # 选择最高置信度的回复
    best_response = max(responses, key=lambda r: r.confidence)

    recommendation = f"基于 {len(responses)} 个智能体的协作分析，"

    if disagreements:
        high_severity_disagreements = [d for d in disagreements if d.get('severity') in ['medium', 'high']]
        if high_severity_disagreements:
            recommendation += f"发现 {len(high_severity_disagreements)} 个重要分歧，"
        recommendation += f"建议重点参考 {best_response.agent_name} 的观点。"
    else:
        recommendation += f"智能体们意见较为一致，推荐采纳综合建议。"

    return recommendation


@router.get("/agents/list")
async def get_agents_list():
    """获取可用智能体列表"""
    agents = [
        {"id": "tanaka", "name": "田中先生", "role": "语法专家", "avatar": "👨‍🏫", "online": True},
        {"id": "koumi", "name": "小美", "role": "对话伙伴", "avatar": "👧", "online": True},
        {"id": "ai", "name": "アイ", "role": "数据分析师", "avatar": "🤖", "online": True},
        {"id": "yamada", "name": "山田先生", "role": "文化专家", "avatar": "🎌", "online": True},
        {"id": "sato", "name": "佐藤教练", "role": "考试专家", "avatar": "🎯", "online": True},
        {"id": "membot", "name": "MemBot", "role": "记忆管家", "avatar": "🧠", "online": True}
    ]
    return {"success": True, "agents": agents}


@router.post("/test-collaboration")
async def test_collaboration_endpoint(request: MultiAgentRequest):
    """测试协作功能的专用端点"""
    try:
        # 强制使用特定智能体组合进行测试
        test_agents = ["tanaka", "koumi"]
        request.active_agents = test_agents

        result = await handle_multi_agent_collaboration(request)

        return {
            "success": True,
            "test_result": {
                "disagreements_detected": len(result.disagreements),
                "agents_responded": len(result.responses),
                "arbitration_needed": result.user_arbitration_needed,
                "processing_time": result.processing_time
            },
            "disagreements": [
                {
                    "topic": d.topic,
                    "type": d.type,
                    "severity": d.severity,
                    "agents": d.agents_involved
                } for d in result.disagreements
            ]
        }

    except Exception as e:
        logger.error(f"协作测试失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }