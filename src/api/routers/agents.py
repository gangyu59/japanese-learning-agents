#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎌 智能体API路由
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from utils.config import settings

router = APIRouter()


class CustomAgentCreate(BaseModel):
    name: str
    role: str
    expertise: List[str]
    personality: Dict[str, int]
    speaking_style: str = "casual"
    avatar: str = "🤖"


@router.get("/list")
async def get_agents_list():
    """获取智能体列表"""
    agents = []
    for agent_id, config in settings.CORE_AGENTS.items():
        agents.append({
            "agent_id": agent_id,
            "name": config["name"],
            "role": config["role"],
            "avatar": config["avatar"],
            "is_core": True
        })

    return {
        "agents": agents,
        "total_count": len(agents)
    }


@router.post("/custom")
async def create_custom_agent(agent_data: CustomAgentCreate):
    """创建自定义智能体"""
    try:
        # 这里实现自定义智能体创建逻辑
        return {
            "success": True,
            "message": f"自定义智能体 {agent_data.name} 创建成功",
            "agent_id": f"custom_{agent_data.name.lower()}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """获取智能体状态"""
    if agent_id not in settings.CORE_AGENTS:
        raise HTTPException(status_code=404, detail="智能体不存在")

    config = settings.CORE_AGENTS[agent_id]
    return {
        "agent_id": agent_id,
        "name": config["name"],
        "role": config["role"],
        "avatar": config["avatar"],
        "is_active": False,
        "current_emotion": "😊"
    }