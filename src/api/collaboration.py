# src/api/collaboration.py
"""
Multi-Agent Collaboration API
多智能体协作API端点
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

# 导入协作编排器
from ..workflows.collaboration import MultiAgentOrchestrator, CollaborationMode, CollaborationResult

router = APIRouter()
logger = logging.getLogger(__name__)

# 全局协作编排器实例
orchestrator = MultiAgentOrchestrator()


class MultiAgentChatRequest(BaseModel):
    """多智能体聊天请求"""
    message: str = Field(..., description="用户消息")
    user_id: str = Field(..., description="用户ID")
    session_id: str = Field(..., description="会话ID")
    active_agents: List[str] = Field(..., description="参与的智能体列表")
    collaboration_mode: str = Field(default="discussion", description="协作模式")
    scene_context: str = Field(default="general", description="场景上下文")
    additional_context: Dict[str, Any] = Field(default_factory=dict, description="额外上下文")


class MultiAgentChatResponse(BaseModel):
    """多智能体聊天响应"""
    success: bool
    session_id: str
    collaboration_mode: str
    agents_participated: List[str]
    responses: List[Dict[str, Any]]  # 各智能体的响应
    consensus: Optional[str]  # 达成的共识
    conflicts: List[Dict[str, Any]]  # 冲突信息
    final_recommendation: str  # 最终建议
    user_arbitration_needed: bool  # 是否需要用户仲裁
    timestamp: datetime


class ConflictResolutionRequest(BaseModel):
    """冲突解决请求"""
    session_id: str
    user_choice: str  # 用户的选择
    conflict_id: str  # 冲突标识
    additional_feedback: Optional[str] = None


@router.post("/multi-agent-chat", response_model=MultiAgentChatResponse)
async def multi_agent_chat(request: MultiAgentChatRequest):
    """
    多智能体协作聊天端点

    支持多个智能体同时参与对话，自动检测和处理分歧
    """
    try:
        logger.info(f"多智能体协作开始: 用户 {request.user_id}, 智能体 {request.active_agents}")

        # 验证协作模式
        try:
            mode = CollaborationMode(request.collaboration_mode)
        except ValueError:
            mode = CollaborationMode.DISCUSSION

        # 验证智能体ID
        available_agents = ["tanaka", "koumi", "ai", "yamada", "sato", "membot"]
        valid_agents = [agent for agent in request.active_agents if agent in available_agents]

        if not valid_agents:
            raise HTTPException(status_code=400, detail="没有有效的智能体被选中")

        if len(valid_agents) < 2:
            # 如果只有一个智能体，回退到单智能体模式
            return await _single_agent_fallback(request, valid_agents[0])

        # 构建会话上下文
        session_context = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "scene": request.scene_context,
            "timestamp": datetime.now().isoformat(),
            **request.additional_context
        }

        # 执行多智能体协作
        result: CollaborationResult = await orchestrator.orchestrate_collaboration(
            user_input=request.message,
            active_agents=valid_agents,
            mode=mode,
            session_context=session_context
        )

        # 格式化响应
        formatted_responses = []
        for response in result.responses:
            formatted_responses.append({
                "agent_id": response.agent_id,
                "agent_name": response.agent_name,
                "content": response.content,
                "confidence": response.confidence,
                "emotion": response.emotion,
                "learning_points": response.learning_points,
                "suggestions": response.suggestions,
                "timestamp": response.timestamp.isoformat()
            })

        # 格式化冲突信息
        formatted_conflicts = []
        for conflict in result.conflicts:
            formatted_conflicts.append({
                "agent1": conflict[0],
                "agent2": conflict[1],
                "conflict_point": conflict[2],
                "conflict_id": f"{conflict[0]}_{conflict[1]}_{len(formatted_conflicts)}"
            })

        return MultiAgentChatResponse(
            success=True,
            session_id=request.session_id,
            collaboration_mode=request.collaboration_mode,
            agents_participated=valid_agents,
            responses=formatted_responses,
            consensus=result.consensus,
            conflicts=formatted_conflicts,
            final_recommendation=result.final_recommendation,
            user_arbitration_needed=result.user_arbitration_needed,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"多智能体协作错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"协作处理失败: {str(e)}")


@router.post("/resolve-conflict")
async def resolve_conflict(request: ConflictResolutionRequest):
    """
    用户仲裁冲突端点

    当智能体产生分歧时，用户可以通过此端点进行仲裁
    """
    try:
        logger.info(f"用户仲裁冲突: {request.conflict_id}, 选择: {request.user_choice}")

        # 这里可以记录用户的仲裁选择，用于后续学习
        # TODO: 将用户选择保存到数据库，用于改善协作算法

        return {
            "success": True,
            "message": "仲裁结果已记录，智能体们会学习您的偏好",
            "conflict_id": request.conflict_id,
            "user_choice": request.user_choice
        }

    except Exception as e:
        logger.error(f"冲突解决错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"冲突解决失败: {str(e)}")


@router.get("/collaboration-modes")
async def get_collaboration_modes():
    """获取支持的协作模式列表"""
    return {
        "modes": [
            {
                "id": "discussion",
                "name": "自由讨论",
                "description": "智能体们就话题进行自由讨论，展现不同观点"
            },
            {
                "id": "correction",
                "name": "协作纠错",
                "description": "多个智能体协作纠正语法、用法等问题"
            },
            {
                "id": "creation",
                "name": "协作创作",
                "description": "智能体们协作进行内容创作，如小说、对话等"
            },
            {
                "id": "analysis",
                "name": "深度分析",
                "description": "从多个角度深入分析问题或内容"
            }
        ]
    }


@router.get("/active-agents")
async def get_active_agents():
    """获取可用的智能体列表"""
    return {
        "agents": [
            {
                "id": "tanaka",
                "name": "田中先生",
                "role": "语法专家",
                "expertise": ["grammar", "syntax", "formal_language"],
                "personality": "严谨、专业、注重准确性"
            },
            {
                "id": "koumi",
                "name": "小美",
                "role": "对话伙伴",
                "expertise": ["conversation", "casual_language", "youth_culture"],
                "personality": "活泼、友善、年轻化用语"
            },
            {
                "id": "ai",
                "name": "アイ",
                "role": "数据分析师",
                "expertise": ["analysis", "statistics", "learning_optimization"],
                "personality": "逻辑、准确、数据驱动"
            },
            {
                "id": "yamada",
                "name": "山田先生",
                "role": "文化专家",
                "expertise": ["culture", "history", "traditional_knowledge"],
                "personality": "博学、风趣、传统智慧"
            },
            {
                "id": "sato",
                "name": "佐藤教练",
                "role": "考试专家",
                "expertise": ["jlpt", "exam_strategy", "goal_setting"],
                "personality": "目标导向、激励、高效"
            },
            {
                "id": "membot",
                "name": "MemBot",
                "role": "记忆管家",
                "expertise": ["memory", "spaced_repetition", "progress_tracking"],
                "personality": "系统化、精确、科学记忆"
            }
        ]
    }


async def _single_agent_fallback(request: MultiAgentChatRequest, agent_id: str):
    """单智能体回退模式"""
    try:
        # 使用现有的单智能体API逻辑
        agent = orchestrator.agents[agent_id]

        session_context = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "scene": request.scene_context,
        }

        result = await agent.process_user_input(
            user_input=request.message,
            session_context=session_context,
            scene=request.scene_context
        )

        # 格式化为多智能体响应格式
        return MultiAgentChatResponse(
            success=True,
            session_id=request.session_id,
            collaboration_mode="single_agent_fallback",
            agents_participated=[agent_id],
            responses=[{
                "agent_id": agent_id,
                "agent_name": result.get("agent_name", agent_id),
                "content": result.get("content", ""),
                "confidence": result.get("confidence", 0.8),
                "emotion": result.get("emotion", "😊"),
                "learning_points": result.get("learning_points", []),
                "suggestions": result.get("suggestions", []),
                "timestamp": datetime.now().isoformat()
            }],
            consensus=None,
            conflicts=[],
            final_recommendation=result.get("content", ""),
            user_arbitration_needed=False,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"单智能体回退错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"单智能体回退失败: {str(e)}")


# WebSocket支持（可选）
@router.websocket("/ws/collaboration/{session_id}")
async def collaboration_websocket(websocket, session_id: str):
    """
    WebSocket端点支持实时协作

    可以实时显示智能体的思考过程和协作流程
    """
    await websocket.accept()

    try:
        while True:
            # 接收前端消息
            data = await websocket.receive_json()

            # 处理协作请求
            # TODO: 实现实时协作逻辑

            # 发送响应
            await websocket.send_json({
                "type": "collaboration_update",
                "session_id": session_id,
                "data": data
            })

    except Exception as e:
        logger.error(f"WebSocket协作错误: {str(e)}")
        await websocket.close()


# 导出路由
__all__ = ['router']