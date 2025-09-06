from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field


# 进度追踪
def track_learning_async(user_input: str, agent_responses: dict, session_id: str):
    try:
        import requests
        requests.post("http://localhost:8000/api/v1/progress/track",
                     json={
                         "user_input": user_input,
                         "agent_responses": agent_responses,
                         "session_id": session_id
                     }, timeout=1)
    except:
        pass

# === 修改现有的 multi_agent_chat 函数 ===
@router.post("/multi-agent-chat", response_model=MultiAgentChatResponse)
async def multi_agent_chat(request: MultiAgentChatRequest):
    """
    多智能体协作聊天端点 - 已集成学习进度追踪

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
        agent_responses_for_tracking = {}  # 用于进度追踪的响应格式

        for response in result.responses:
            formatted_response = {
                "agent_id": response.agent_id,
                "agent_name": response.agent_name,
                "content": response.content,
                "confidence": response.confidence,
                "emotion": response.emotion,
                "learning_points": response.learning_points,
                "suggestions": response.suggestions,
                "timestamp": response.timestamp.isoformat()
            }
            formatted_responses.append(formatted_response)

            # 为进度追踪准备数据
            agent_responses_for_tracking[response.agent_name] = {
                "content": response.content,
                "agent_name": response.agent_name,
                "learning_points": response.learning_points,
                "suggestions": response.suggestions
            }

         # 追踪学习进度
        track_learning_async(request.message, agent_responses_for_tracking, request.session_id)

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


# === 修改现有的 _single_agent_fallback 函数 ===
async def _single_agent_fallback(request: MultiAgentChatRequest, agent_id: str):
    """单智能体回退模式 - 已集成学习进度追踪"""
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

        # === 新增：追踪单智能体的学习进度 ===
        agent_name = result.get("agent_name", agent_id)
        single_agent_responses = {
            agent_name: {
                "content": result.get("content", ""),
                "agent_name": agent_name,
                "learning_points": result.get("learning_points", []),
                "suggestions": result.get("suggestions", [])
            }
        }

        track_learning_progress(
            user_input=request.message,
            agent_responses=single_agent_responses,
            session_id=request.session_id,
            scene_context=request.scene_context
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


# === 如果你有单独的单智能体API，也需要类似的修改 ===
# 例如，如果有类似这样的端点：

@router.post("/single-agent-chat")
async def single_agent_chat(request: SingleAgentChatRequest):
    """
    单智能体聊天端点 - 已集成学习进度追踪
    """
    try:
        # ... 现有的处理逻辑 ...

        result = await agent.process_user_input(
            user_input=request.message,
            session_context=session_context,
            scene=request.scene_context
        )

        # === 追踪学习进度 ===
        agent_name = result.get("agent_name", request.agent_name)
        agent_responses = {
            agent_name: {
                "content": result.get("content", ""),
                "agent_name": agent_name,
                "learning_points": result.get("learning_points", []),
                "suggestions": result.get("suggestions", [])
            }
        }

        track_learning_progress(
            user_input=request.message,
            agent_responses=agent_responses,
            session_id=request.session_id,
            scene_context=request.scene_context
        )

        # 返回原有格式的响应
        return {
            "response": result.get("content", "抱歉，我无法回答。"),
            "agent_name": result.get("agent_name", request.agent_name),
            "learning_points": result.get("learning_points", []),
            "suggestions": result.get("suggestions", []),
            "emotion": result.get("emotion", "😊"),
            "success": not result.get("error", False)
        }

    except Exception as e:
        return {
            "response": f"系统错误：{str(e)}",
            "success": False,
            "error": str(e)
        }


# === 添加进度追踪状态检查端点 ===
@router.get("/progress-tracking-status")
async def get_progress_tracking_status():
    """检查进度追踪功能状态"""
    return {
        "progress_tracking_enabled": PROGRESS_TRACKER_AVAILABLE,
        "message": "进度追踪功能正常" if PROGRESS_TRACKER_AVAILABLE else "进度追踪功能不可用",
        "database_status": "connected" if PROGRESS_TRACKER_AVAILABLE else "not_available"
    }