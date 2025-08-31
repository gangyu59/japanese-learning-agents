#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎌 智能体基类 - 所有智能体的通用功能
提供统一的接口和基础功能
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
    智能体基类

    提供所有智能体共有的基础功能：
    - 记忆系统
    - 情绪状态管理
    - 响应生成
    - 协作协议
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
        """初始化智能体"""
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.avatar = avatar

        # 性格配置
        self.personality = personality or {
            "strictness": 5,
            "patience": 7,
            "humor": 5,
            "formality": 5,
            "friendliness": 7
        }

        # 专业领域和技能
        self.expertise = expertise or ["general"]

        # 情绪系统
        self.emotions = emotions or ["😊", "🤔", "😐", "👍", "😟"]
        self.current_emotion = self.emotions[0]
        self.emotional_state = "neutral"

        # 记忆系统
        self.short_term_memory = []
        self.conversation_context = []
        self.user_profile = {}

        # 状态管理
        self.is_active = False
        self.last_interaction_time = None
        self.total_interactions = 0
        self.response_delay_range = [0.5, 2.0]

        # 学习数据
        self.learning_topics_covered = set()
        self.user_progress_observations = {}

        logger.info(f"🤖 智能体 {self.name} 初始化完成")

    @abstractmethod
    async def process_user_input(
            self,
            user_input: str,
            session_context: Dict[str, Any],
            scene: str = "conversation"
    ) -> Dict[str, Any]:
        """处理用户输入 - 子类必须实现"""
        pass

    async def generate_response(
            self,
            user_input: str,
            context: Optional[Dict[str, Any]] = None,
            scene: str = "conversation"
    ) -> str:
        """生成响应内容 - 核心方法"""
        try:
            # 构建完整的提示信息
            prompt = await self._build_prompt(user_input, context, scene)

            # 调用LLM生成响应
            response = await self._call_llm(prompt)

            # 后处理响应
            processed_response = await self._postprocess_response(response, scene)

            return processed_response

        except Exception as e:
            logger.error(f"❌ {self.name} 生成响应失败: {e}")
            return await self._get_fallback_response(user_input)

    async def _build_prompt(self, user_input: str, context: Dict = None, scene: str = "conversation") -> str:
        """构建完整的提示词"""

        # 基础角色设定
        role_prompt = f"""你是{self.name}，一个{self.role}。

## 角色特征
- 姓名：{self.name}
- 角色：{self.role}  
- 专业领域：{', '.join(self.expertise)}
- 性格特点：{self._format_personality()}
- 当前情绪：{self.current_emotion}

## 对话规则
1. 始终保持角色一致性，体现专业特长
2. 根据性格特征调整语言风格和态度
3. 提供日语内容，并附上中文解释
4. 回应长度控制在200字以内
5. 根据用户水平调整难度

"""

        # 添加场景上下文
        if scene and scene != "conversation":
            scene_info = self._get_scene_info(scene)
            role_prompt += f"\n## 当前场景\n{scene_info}\n"

        # 添加对话记忆
        if self.conversation_context:
            recent_context = self.conversation_context[-3:]
            context_text = "\n".join([
                f"用户: {ctx['user']}\n{self.name}: {ctx['agent']}"
                for ctx in recent_context
            ])
            role_prompt += f"\n## 对话历史\n{context_text}\n"

        # 用户当前输入
        role_prompt += f"\n## 用户输入\n{user_input}\n\n请以{self.name}的身份回应："

        return role_prompt

    def _format_personality(self) -> str:
        """格式化性格特征描述"""
        traits = []
        for trait, level in self.personality.items():
            if level >= 8:
                intensity = "非常"
            elif level >= 6:
                intensity = "比较"
            elif level >= 4:
                intensity = "适度"
            else:
                intensity = "不太"

            trait_names = {
                "strictness": "严格",
                "patience": "耐心",
                "humor": "幽默",
                "formality": "正式",
                "friendliness": "友好",
                "analytical": "分析性",
                "creativity": "创造性"
            }

            trait_name = trait_names.get(trait, trait)
            traits.append(f"{intensity}{trait_name}")

        return "、".join(traits)

    def _get_scene_info(self, scene: str) -> str:
        """获取场景信息"""
        scene_descriptions = {
            "grammar": "语法学习场景 - 重点关注日语语法规则的教学和纠正",
            "conversation": "日常对话场景 - 练习自然的日语交流",
            "restaurant": "餐厅场景 - 日式餐厅的点餐和用餐对话",
            "shopping": "购物场景 - 在商店购物时的日语表达",
            "interview": "面试场景 - 商务日语和面试技巧",
            "culture": "文化探索场景 - 了解日本文化和历史背景",
            "jlpt": "JLPT考试场景 - 针对日语能力考试的训练"
        }
        return scene_descriptions.get(scene, f"{scene}场景")

    async def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        try:
            # 尝试导入LLM客户端
            from utils.llm_client import get_llm_client

            llm_client = await get_llm_client()
            response = await llm_client.generate_response(
                prompt=prompt,
                max_tokens=300,
                temperature=0.7
            )

            return response.strip()

        except ImportError:
            # 如果LLM客户端不可用，使用智能模拟响应
            logger.warning(f"{self.name} LLM客户端不可用，使用模拟响应")
            return await self._generate_smart_mock_response(prompt)
        except Exception as e:
            logger.error(f"❌ LLM调用失败: {e}")
            return await self._generate_smart_mock_response(prompt)

    async def _generate_smart_mock_response(self, prompt: str) -> str:
        """生成智能模拟响应"""
        user_input = self._extract_user_input_from_prompt(prompt)

        # 基于用户输入和智能体特征生成响应
        if self._contains_japanese(user_input):
            return await self._handle_japanese_input_mock(user_input)
        elif self._is_question(user_input):
            return await self._handle_question_mock(user_input)
        else:
            return await self._handle_general_input_mock(user_input)

    def _extract_user_input_from_prompt(self, prompt: str) -> str:
        """从提示词中提取用户输入"""
        lines = prompt.split('\n')
        for line in lines:
            if line.startswith('用户输入') or line.startswith('## 用户输入'):
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    return lines[idx + 1].strip()
        return ""

    def _contains_japanese(self, text: str) -> bool:
        """检查是否包含日文"""
        return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))

    def _is_question(self, text: str) -> bool:
        """检查是否是问题"""
        return any(marker in text for marker in ["？", "?", "什么", "怎么", "为什么", "如何", "吗"])

    async def _handle_japanese_input_mock(self, japanese_input: str) -> str:
        """处理日语输入的模拟响应"""
        responses = {
            "tanaka": f"「{japanese_input}」の文法を分析しますと、{self._analyze_grammar_mock(japanese_input)}\n\n**中文解释：** 让我来分析这个句子的语法结构...",
            "koumi": f"「{japanese_input}」って言うんだね！{self._generate_casual_response_mock()}\n\n**中文提示：** 这个表达很有趣呢！",
            "ai": f"输入分析：文本长度{len(japanese_input)}字符，{self._analyze_complexity_mock(japanese_input)}\n\n**学习建议：** 基于分析结果的个性化建议...",
            "yamada": f"「{japanese_input}」には深い文化的意味がありますね。{self._explain_culture_mock()}\n\n**文化背景：** 这个表达背后的日本文化含义...",
            "sato": f"「{japanese_input}」はJLPT{self._assess_jlpt_level_mock()}レベルです！{self._give_test_advice_mock()}\n\n**考试要点：** 这是考试中的重要表达！",
            "membot": f"「{japanese_input}」を学習記録に追加しました。{self._update_memory_mock()}\n\n**进度更新：** 已更新您的学习记录..."
        }

        base_response = responses.get(self.agent_id, f"「{japanese_input}」について考えています...")
        return base_response

    async def _handle_question_mock(self, question: str) -> str:
        """处理问题的模拟响应"""
        if "语法" in question or "文法" in question:
            return f"语法问题ですね。{self._explain_grammar_mock()}\n\n**详细解释：** 关于这个语法点的详细说明..."
        elif "单词" in question or "词汇" in question:
            return f"词汇について説明します。{self._explain_vocabulary_mock()}\n\n**词汇扩展：** 相关词汇和用法..."
        elif "文化" in question:
            return f"日本文化について興味がおありですね。{self._explain_culture_mock()}\n\n**文化解读：** 日本文化的深层含义..."
        else:
            return f"面白い質問ですね。{self._give_general_advice_mock()}\n\n**回答：** 关于您问题的详细回答..."

    async def _handle_general_input_mock(self, input_text: str) -> str:
        """处理一般输入的模拟响应"""
        return f"「{input_text}」について一緒に学習しましょう。\n\n**学习建议：** 让我们一起深入学习这个内容..."

    # 模拟分析方法
    def _analyze_grammar_mock(self, text: str) -> str:
        patterns = ["基本的な文型です", "複雑な構造ですね", "助詞に注意が必要です"]
        return random.choice(patterns)

    def _generate_casual_response_mock(self) -> str:
        responses = ["よく使う表現だよ～", "覚えておくと便利！", "自然な日本語だね"]
        return random.choice(responses)

    def _analyze_complexity_mock(self, text: str) -> str:
        levels = ["初級レベル", "中級レベル", "上級レベル"]
        return random.choice(levels)

    def _explain_culture_mock(self) -> str:
        explanations = ["伝統的な表現です", "現代でもよく使われます", "地域による違いがあります"]
        return random.choice(explanations)

    def _assess_jlpt_level_mock(self) -> str:
        levels = ["N5", "N4", "N3", "N2", "N1"]
        return random.choice(levels)

    def _give_test_advice_mock(self) -> str:
        advice = ["しっかり覚えましょう", "練習が重要です", "応用問題も解いてみて"]
        return random.choice(advice)

    def _update_memory_mock(self) -> str:
        updates = ["進歩が見られます", "復習をお勧めします", "新しい分野ですね"]
        return random.choice(updates)

    def _explain_grammar_mock(self) -> str:
        explanations = ["基本的な文法規則から説明します", "例文を使って説明しましょう", "段階的に学習していきましょう"]
        return random.choice(explanations)

    def _explain_vocabulary_mock(self) -> str:
        explanations = ["関連する単語も一緒に覚えましょう", "使用場面を考えてみましょう", "例文で確認しましょう"]
        return random.choice(explanations)

    def _give_general_advice_mock(self) -> str:
        advice = ["継続的な学習が大切です", "実践的に使ってみましょう", "楽しく学習していきましょう"]
        return random.choice(advice)

    async def _postprocess_response(self, response: str, scene: str) -> str:
        """后处理响应内容"""
        # 确保响应长度合适
        if len(response) > 400:
            response = response[:397] + "..."

        # 根据性格调整语言风格
        if self.personality.get("formality", 5) >= 8:
            response = response.replace("だよ", "です").replace("だね", "ですね")

        # 确保包含中文提示
        if "**中文" not in response and "**学习" not in response and "**文化" not in response:
            response += "\n\n**中文提示：** 希望这个回答对您有帮助。"

        return response

    async def _get_fallback_response(self, user_input: str) -> str:
        """获取备用响应"""
        fallback_responses = {
            "tanaka": "申し訳ありません。もう一度確認させてください。\n\n**中文提示：** 抱歉，让我重新确认一下。",
            "koumi": "あれ？ちょっとわからなかった。もう一回言ってくれる？\n\n**中文提示：** 咦？我没太明白，能再说一遍吗？",
            "ai": "システムエラーが発生しました。分析を再実行します。\n\n**中文提示：** 系统出错了，正在重新分析。",
            "yamada": "少し考えさせてください。深い質問ですね。\n\n**中文提示：** 让我想想，这是个很深刻的问题。",
            "sato": "集中して取り組みましょう。もう一度チャレンジ！\n\n**中文提示：** 让我们集中精力，再试一次！",
            "membot": "データを整理中です。しばらくお待ちください。\n\n**中文提示：** 正在整理数据，请稍候。"
        }

        fallback = fallback_responses.get(self.agent_id, "少々お待ちください。\n\n**中文提示：** 请稍等片刻。")
        return fallback

    # =================== 记忆和学习系统 ===================

    def add_to_memory(self, user_input: str, agent_response: str, context: Dict = None):
        """添加到记忆系统"""
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "agent": agent_response,
            "context": context or {},
            "emotion": self.current_emotion
        }

        self.short_term_memory.append(memory_entry)
        self.conversation_context.append({
            "user": user_input,
            "agent": agent_response
        })

        # 保持记忆数量限制
        if len(self.short_term_memory) > 50:
            self.short_term_memory.pop(0)

        if len(self.conversation_context) > 10:
            self.conversation_context.pop(0)

    def update_user_profile(self, observations: Dict[str, Any]):
        """更新用户画像"""
        for key, value in observations.items():
            if key in ["level", "interests", "weak_points", "learning_style"]:
                self.user_profile[key] = value

        logger.debug(f"{self.name} 更新用户画像: {observations}")

    # =================== 情绪系统 ===================

    async def update_emotion(self, trigger: str, context: Dict = None):
        """更新情绪状态"""
        emotion_map = {
            "user_progress": ("pleased", ["😊", "👍", "🎉"]),
            "user_mistake": ("concerned", ["😟", "🤔", "😐"]),
            "complex_question": ("thinking", ["🤔", "💭", "🧐"]),
            "praise_received": ("happy", ["😊", "😄", "🥰"]),
            "collaboration": ("cooperative", ["🤝", "😊", "👍"]),
            "teaching_moment": ("focused", ["📝", "👨‍🏫", "💡"])
        }

        if trigger in emotion_map:
            state, possible_emotions = emotion_map[trigger]
            self.emotional_state = state

            # 根据性格特征选择合适的情绪
            if self.personality.get("strictness", 5) >= 8 and trigger == "user_mistake":
                self.current_emotion = random.choice(["😤", "😟", "😐"])
            elif self.personality.get("friendliness", 5) >= 8:
                self.current_emotion = random.choice(["😊", "😄", "🤗"])
            else:
                self.current_emotion = random.choice(possible_emotions)

    # =================== 状态管理 ===================

    def get_status(self) -> Dict[str, Any]:
        """获取智能体完整状态"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "avatar": self.avatar,
            "current_emotion": self.current_emotion,
            "emotional_state": self.emotional_state,
            "is_active": self.is_active,
            "expertise": self.expertise,
            "personality": self.personality,
            "total_interactions": self.total_interactions,
            "memory_count": len(self.short_term_memory),
            "last_interaction": self.last_interaction_time,
            "learning_topics_covered": list(self.learning_topics_covered),
            "user_profile": self.user_profile
        }

    def activate(self):
        """激活智能体"""
        self.is_active = True
        logger.info(f"✅ {self.name} 已激活")

    def deactivate(self):
        """停用智能体"""
        self.is_active = False
        logger.info(f"⏸️ {self.name} 已停用")

    async def reset_session(self):
        """重置会话状态"""
        self.conversation_context.clear()
        self.current_emotion = self.emotions[0]
        self.emotional_state = "neutral"
        self.last_interaction_time = None

        logger.info(f"🔄 {self.name} 会话状态已重置")

    def __str__(self):
        return f"{self.name}({self.role}) - {self.current_emotion}"

    def __repr__(self):
        return f"BaseAgent(id={self.agent_id}, name={self.name}, role={self.role}, active={self.is_active})"