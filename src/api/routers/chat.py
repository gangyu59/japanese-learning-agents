#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎌 聊天API路由
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter()

class ChatMessage(BaseModel):
    session_id: str
    content: str
    active_agents: List[str] = ["tanaka"]
    scene: str = "grammar"

class ChatResponse(BaseModel):
    success: bool
    message: str
    responses: List[Dict[str, Any]] = []

@router.post("/send", response_model=ChatResponse)
async def send_chat_message(message: ChatMessage):
    """发送聊天消息API端点"""
    try:
        # 这里实现聊天逻辑（暂时返回模拟响应）
        return ChatResponse(
            success=True,
            message="消息已发送",
            responses=[{
                "agent_id": "tanaka",
                "agent_name": "田中先生",
                "content": f"收到您的消息：{message.content}",
                "emotion": "😊"
            }]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """获取聊天历史"""
    return {
        "session_id": session_id,
        "messages": [],
        "total_count": 0
    }