#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎌 智能体基类 - 统一接口 & 公共能力（直连 LLM 版）
"""

import asyncio
import json
import random
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    智能体基类（与田中同构，支持直连 LLM）
    - 记忆系统 / 情绪系统 / 状态管理
    - 提供 generate_response（仍可用，但已直连 LLM）
    - 子类推荐实现：process_message / process_user_input（首选）
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        avatar: str = "🤖",
        personality: Optional[Dict[str, int]] = None,
        expertise: Optional[List[str]] = None,
        emotions: Optional[List[str]] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.avatar = avatar

        self.personality = personality or {
            "strictness": 5, "patience": 7, "humor": 5,
            "formality": 5, "friendliness": 7
        }
        self.expertise = expertise or ["general"]

        self.emotions = emotions or ["😊", "🤔", "😐", "👍", "😟"]
        self.current_emotion = self.emotions[0]
        self.emotional_state = "neutral"

        # 记忆与上下文
        self.short_term_memory: List[Dict[str, Any]] = []
        self.conversation_context: List[Dict[str, str]] = []
        self.user_profile: Dict[str, Any] = {}

        # 状态
        self.is_active = False
        self.last_interaction_time = None
        self.total_interactions = 0

        logger.info(f"🤖 智能体 {self.name} 初始化完成")

    # -------- 子类必须实现 --------
    @abstractmethod
    async def process_user_input(
        self,
        user_input: str,
        session_context: Dict[str, Any],
        scene: str = "conversation"
    ) -> Dict[str, Any]:
        pass

    # -------- 仍保留的公共生成接口（直连 LLM）--------
    async def generate_response(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        scene: str = "conversation"
    ) -> str:
        try:
            prompt = await self._build_prompt(user_input, context or {}, scene)
            response = await self._call_llm(prompt)  # 直连 LLM
            processed = await self._postprocess_response(response, scene)
            return processed
        except Exception as e:
            logger.error(f"❌ {self.name} 生成响应失败: {e}")
            return await self._get_fallback_response(user_input)

    async def _build_prompt(self, user_input: str, context: Dict = None, scene: str = "conversation") -> str:
        role_prompt = f"""你是{self.name}，一个{self.role}。

## 角色特征
- 姓名：{self.name}
- 角色：{self.role}
- 专业领域：{', '.join(self.expertise)}
- 性格特点：{self._format_personality()}
- 当前情绪：{self.current_emotion}

## 对话规则
1. 保持角色一致，体现专业特长
2. 根据性格调整语气
3. 先日文、后中文补充
4. 回应≤200字，简洁可执行
"""

        if scene and scene != "conversation":
            role_prompt += f"\n## 场景\n{self._get_scene_info(scene)}\n"

        if self.conversation_context:
            recent = self.conversation_context[-3:]
            ctx = "\n".join([f"用户: {c['user']}\n{self.name}: {c['agent']}" for c in recent])
            role_prompt += f"\n## 最近对话\n{ctx}\n"

        role_prompt += f"\n## 用户输入\n{user_input}\n\n请以{self.name}的身份回应："
        return role_prompt

    def _format_personality(self) -> str:
        traits = []
        for trait, level in self.personality.items():
            if level >= 8: intensity = "非常"
            elif level >= 6: intensity = "比较"
            elif level >= 4: intensity = "适度"
            else: intensity = "不太"
            mapping = {
                "strictness": "严格", "patience": "耐心", "humor": "幽默",
                "formality": "正式", "friendliness": "友好",
                "analytical": "分析性", "creativity": "创造性"
            }
            name = mapping.get(trait, trait)
            traits.append(f"{intensity}{name}")
        return "、".join(traits)

    def _get_scene_info(self, scene: str) -> str:
        desc = {
            "grammar": "语法学习场景", "conversation": "日常对话场景",
            "restaurant": "餐厅点餐场景", "shopping": "购物场景",
            "interview": "面试场景", "culture": "文化探索场景",
            "jlpt": "JLPT 考试训练场景", "planning": "学习计划场景", "analytics": "数据分析场景"
        }
        return desc.get(scene, f"{scene} 场景")

    async def _call_llm(self, prompt: str) -> str:
        """直连 LLM（与田中同构：chat_completion）"""
        from utils.llm_client import get_llm_client
        llm = get_llm_client()  # 非异步，与田中保持一致
        messages = [{"role": "user", "content": prompt}]
        resp = await llm.chat_completion(
            messages=messages,
            temperature=0.5,
            system_prompt=None,
            max_tokens=800
        )
        return (resp or "").strip()

    # ---- 旧的“智能模拟”方法仍保留（仅真正异常时 fallback 用）----
    async def _get_fallback_response(self, user_input: str) -> str:
        return f"一時停止：うまく応答できませんでした。もう一度お願いします。\n\n（系统提示：请重试或换个说法）"

    async def _postprocess_response(self, response: str, scene: str) -> str:
        # 限长
        if len(response) > 1200:
            response = response[:1197] + "..."
        # 高正式度时，做简单敬体替换
        if self.personality.get("formality", 5) >= 8:
            response = response.replace("だよ", "です").replace("だね", "ですね")
        return response

    # 记忆系统
    def add_to_memory(self, user_input: str, agent_response: str, context: Dict = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input, "agent": agent_response,
            "context": context or {}, "emotion": self.current_emotion
        }
        self.short_term_memory.append(entry)
        self.conversation_context.append({"user": user_input, "agent": agent_response})
        if len(self.short_term_memory) > 50: self.short_term_memory.pop(0)
        if len(self.conversation_context) > 10: self.conversation_context.pop(0)

    def update_user_profile(self, observations: Dict[str, Any]):
        for k, v in observations.items():
            if k in ["level", "interests", "weak_points", "learning_style"]:
                self.user_profile[k] = v

    # 情绪系统
    async def update_emotion(self, trigger: str, context: Dict = None):
        emotion_map = {
            "user_progress": ("pleased", ["😊","👍","🎉"]),
            "user_mistake": ("concerned", ["😟","🤔","😐"]),
            "complex_question": ("thinking", ["🤔","💭","🧐"]),
            "praise_received": ("happy", ["😊","😄","🥰"]),
            "collaboration": ("cooperative", ["🤝","😊","👍"]),
            "teaching_moment": ("focused", ["📝","👨‍🏫","💡"])
        }
        if trigger in emotion_map:
            state, pool = emotion_map[trigger]
            self.emotional_state = state
            self.current_emotion = random.choice(pool)

    # 状态
    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id, "name": self.name, "role": self.role, "avatar": self.avatar,
            "current_emotion": self.current_emotion, "emotional_state": self.emotional_state,
            "is_active": self.is_active, "expertise": self.expertise, "personality": self.personality,
            "total_interactions": self.total_interactions,
            "memory_count": len(self.short_term_memory),
            "last_interaction": self.last_interaction_time,
            "learning_topics_covered": [], "user_profile": self.user_profile
        }

    def activate(self): self.is_active = True
    def deactivate(self): self.is_active = False
    async def reset_session(self):
        self.conversation_context.clear()
        self.current_emotion = self.emotions[0]; self.emotional_state = "neutral"; self.last_interaction_time = None

    def __str__(self): return f"{self.name}({self.role}) - {self.current_emotion}"
    def __repr__(self): return f"BaseAgent(id={self.agent_id}, name={self.name}, role={self.role}, active={self.is_active})"