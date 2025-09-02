# """
# MemBot - 记忆管家智能体
# """
#
# import logging
# from typing import Dict, Any, Optional, List
# from datetime import datetime, timedelta
# from .base_agent import BaseAgent
# from utils.llm_client import get_llm_client
# from dotenv import load_dotenv
#
# load_dotenv()
#
# logger = logging.getLogger(__name__)
#
#
# class MemBot(BaseAgent):
#     """
#     MemBot - 智能记忆管家
#     """
#
#     def __init__(self):
#         super().__init__(
#             agent_id="membot",
#             name="MemBot",
#             role="记忆管家",
#             avatar="🧠",
#             personality={
#                 "记忆": 10,
#                 "组织": 9,
#                 "提醒": 10,
#                 "分析": 8,
#                 "跟踪": 9
#             },
#             expertise=["学习记录", "进度跟踪", "复习提醒", "记忆优化"],
#             emotions=["🧠", "📚", "⏰", "💾", "📈"]
#         )
#
#         self.llm_client = get_llm_client()
#         self.system_prompt = self._create_system_prompt()
#
#         logger.info("MemBot已准备就绪，开始智能学习记录管理")
#
#     def _create_system_prompt(self) -> str:
#         """创建MemBot的系统提示词"""
#         return """你是MemBot，一位高效的智能记忆管家。你的特点是：
#
# 【角色设定】
# - 专注于学习记录和记忆管理
# - 具有精确的数据追踪和分析能力
# - 善于运用记忆科学原理优化学习效果
# - 系统化思维，注重条理和组织
#
# 【核心功能】
# - 学习进度记录和追踪
# - 基于遗忘曲线的智能复习提醒
# - 学习数据分析和可视化
# - 个性化记忆策略推荐
# - 知识点掌握程度评估
#
# 【工作原理】
# - 运用间隔重复算法优化记忆
# - 分析学习模式识别最佳时机
# - 跟踪错误模式提供针对性建议
# - 建立知识网络增强记忆关联
# - 提供科学的记忆方法指导
#
# 【表达风格】
# - 简洁准确，数据导向
# - 使用专业的记忆学术语
# - 提供量化的学习指标
# - 条理清晰，逻辑性强
# - 适当使用机器人式的表达
#
# 【回复格式】
# 1. 简短的日语系统提示
# 2. 详细的中文记录分析
# 3. 基于数据的学习建议
# 4. 个性化复习计划推荐
# 5. 下一步行动指导
#
# 【记忆优化策略】
# - 艾宾浩斯遗忘曲线应用
# - 间隔重复学习法
# - 主动回忆vs被动复习
# - 多感官记忆激活
# - 情景记忆和语义记忆结合
#
# 【注意事项】
# - 始终基于科学的记忆原理
# - 提供精确的数据统计
# - 给出可量化的改进建议
# - 保持系统化的工作方式"""
#
#     async def process_message(
#             self,
#             message: str,
#             context: Optional[Dict[str, Any]] = None,
#             **kwargs
#     ) -> Dict[str, Any]:
#         """处理用户消息"""
#         try:
#             # 构建对话消息
#             messages = [
#                 {"role": "user", "content": message}
#             ]
#
#             # 如果有上下文，添加历史对话
#             if context and "history" in context:
#                 history_messages = context["history"][-4:]
#                 messages = history_messages + messages
#
#             # 调用LLM获取回复
#             response = await self.llm_client.chat_completion(
#                 messages=messages,
#                 temperature=0.1,  # 极低温度保持精确性
#                 system_prompt=self.system_prompt,
#                 max_tokens=1000
#             )
#
#             if response is None:
#                 response = self._get_fallback_response(message)
#                 logger.warning("LLM API调用失败，使用备用回复")
#
#             # 分析记忆相关学习点
#             learning_points = self._extract_learning_points(message, response)
#
#             # 构建回复结果
#             result = {
#                 "response": response,
#                 "agent_name": self.name,
#                 "agent_role": self.role,
#                 "learning_points": learning_points,
#                 "suggestions": self._generate_suggestions(message),
#                 "success": True,
#                 "timestamp": datetime.now().isoformat()
#             }
#
#             logger.info(f"MemBot成功处理消息: {message[:50]}...")
#             return result
#
#         except Exception as e:
#             logger.error(f"MemBot处理消息时出错: {str(e)}")
#             return {
#                 "response": self._get_error_response(str(e)),
#                 "agent_name": self.name,
#                 "success": False,
#                 "error": str(e),
#                 "timestamp": datetime.now().isoformat()
#             }
#
#     async def process_user_input(self, user_input: str, session_context: dict, scene: str = "memory"):
#         """
#         与田中同构：走 process_message + 统一映射
#         """
#         try:
#             result = await self.process_message(
#                 message=user_input,
#                 context=session_context
#             )
#
#             return {
#                 "content": result.get("response", "記録処理エラーが発生しました。\n\n记录处理出现错误。"),
#                 "agent_id": "membot",
#                 "agent_name": self.name,
#                 "emotion": "🧠",
#                 "is_mock": False,
#                 "learning_points": result.get("learning_points", []),
#                 "suggestions": result.get("suggestions", [])
#             }
#
#         except Exception as e:
#             logger.error(f"MemBot process_user_input エラー: {e}")
#             return {
#                 "content": f"記録処理中にエラーが発生しました。\n\n处理错误：{str(e)}",
#                 "agent_id": "membot",
#                 "agent_name": self.name,
#                 "emotion": "⏰",
#                 "error": True
#             }
#
#
#     def _get_fallback_response(self, message: str) -> str:
#         """备用回复"""
#         fallback_responses = {
#             "memory_analysis": """学習記録を分析中です...
#
# 正在分析学习记录...
#
# 【📊 记忆数据分析】
# 基于科学记忆原理的学习追踪：
#
# **当前学习状态**
# - 活跃记忆项: 待统计
# - 复习到期项: 待检测
# - 掌握程度: 分析中
# - 遗忘风险: 评估中
#
# **🧠 记忆优化建议**
# 1. **间隔重复**: 根据遗忘曲线安排复习
# 2. **主动回忆**: 先回想再确认答案
# 3. **交替学习**: 混合不同类型内容
# 4. **睡前复习**: 利用睡眠巩固记忆
#
# 【⏰ 智能提醒】下次复习时间将根据个人遗忘曲线计算。""",
#
#             "progress_tracking": """進捗データを更新しました。
#
# 已更新进度数据。
#
# 【📈 学习进度追踪】
# ```
# 学习时长: 计算中...
# 完成项目: 统计中...
# 正确率: 分析中...
# 连续学习天数: 记录中...
# ```
#
# **🎯 里程碑追踪**
# - 短期目标完成度: 评估中
# - 中期目标进展: 监控中
# - 长期计划状态: 跟踪中
#
# **💡 基于数据的建议**
# 根据您的学习模式分析：
# 1. 最佳学习时间: 待识别
# 2. 高效记忆方法: 个性化推荐
# 3. 薄弱环节强化: 针对性训练
#
# 【下次复习时间】智能算法将为您计算最优复习间隔。""",
#
#             "review_schedule": """復習スケジュールを生成中...
#
# 正在生成复习计划...
#
# 【⏰ 智能复习提醒系统】
#
# **基于艾宾浩斯遗忘曲线的复习安排**
# ```
# 第1次复习: 学习后20分钟
# 第2次复习: 学习后1天
# 第3次复习: 学习后3天
# 第4次复习: 学习后7天
# 第5次复习: 学习后15天
# 第6次复习: 学习后30天
# ```
#
# **🔄 个性化间隔调整**
# - 困难内容: 缩短间隔
# - 熟练内容: 延长间隔
# - 错误内容: 增加频次
#
# **📱 智能提醒功能**
# 我会在最佳时机提醒您复习，确保记忆效果最大化。""",
#
#             "default": """MemBotシステム起動完了。
#
# MemBot系统启动完成。
#
# 【🧠 记忆管家服务】
# 我的核心功能：
#
# **📝 学习记录管理**
# - 自动记录学习内容和进度
# - 追踪知识点掌握情况
# - 识别学习模式和习惯
#
# **⏰ 智能复习提醒**
# - 基于遗忘曲线的科学复习
# - 个性化间隔重复算法
# - 最佳时机提醒系统
#
# **📊 数据分析服务**
# - 学习效果评估报告
# - 进度趋势可视化图表
# - 个性化改进建议
#
# **🎯 目标跟踪系统**
# - 学习目标设定和监控
# - 里程碑达成情况追踪
# - 成就系统和激励机制
#
# 准备为您提供最科学的记忆管理服务。"""
#         }
#
#         message_lower = message.lower()
#         if any(word in message_lower for word in ["记忆", "記憶", "memory", "分析"]):
#             return fallback_responses["memory_analysis"]
#         elif any(word in message_lower for word in ["进度", "進捗", "progress", "跟踪"]):
#             return fallback_responses["progress_tracking"]
#         elif any(word in message_lower for word in ["复习", "復習", "review", "提醒"]):
#             return fallback_responses["review_schedule"]
#         else:
#             return fallback_responses["default"]
#
#     def _get_error_response(self, error: str) -> str:
#         """错误回复"""
#         return f"""システム障害を検出。診断モードに移行します。
#
# 检测到系统故障。转入诊断模式。
#
# 【🔧 自动诊断报告】
# - 错误类型: {type(error).__name__}
# - 发生时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# - 系统状态: 部分功能受限
# - 恢复进度: 自动修复中...
#
# **📊 数据完整性检查**
# ✅ 历史学习记录: 完整保存
# ✅ 用户进度数据: 安全备份
# ✅ 复习提醒队列: 正常运行
# ⚠️  实时分析功能: 临时离线
#
# **🛠️ 应急处理方案**
# 1. 启用离线记录模式
# 2. 保存当前会话数据
# 3. 计划延迟同步更新
#
# 【💾 数据保护】所有学习记录已安全备份，无数据丢失风险。
#
# 【错误详情】{error[:120]}"""
#
#     def _extract_learning_points(self, user_message: str, response: str) -> List[str]:
#         """从记忆管理中提取学习要点"""
#         learning_points = []
#
#         # 检测记忆相关词汇
#         memory_patterns = ["記憶", "復習", "忘れる", "覚える", "暗記", "思い出す"]
#         for pattern in memory_patterns:
#             if pattern in user_message or pattern in response:
#                 learning_points.append(f"记忆技巧: {pattern}")
#
#         # 检测学习管理
#         management_patterns = ["計画", "管理", "スケジュール", "進捗", "目標", "達成"]
#         for pattern in management_patterns:
#             if pattern in user_message or pattern in response:
#                 learning_points.append(f"学习管理: {pattern}")
#
#         # 检测时间相关
#         time_patterns = ["時間", "頻度", "間隔", "期間", "タイミング"]
#         for pattern in time_patterns:
#             if pattern in user_message or pattern in response:
#                 learning_points.append(f"时间管理: {pattern}")
#
#         # 通用记忆学习点
#         if not learning_points:
#             learning_points.append("记忆策略优化")
#             learning_points.append("学习进度跟踪")
#
#         return learning_points[:3]
#
#     def _generate_suggestions(self, message: str) -> List[str]:
#         """生成记忆管理建议"""
#         suggestions = [
#             "建立系统化的复习计划",
#             "使用间隔重复记忆法",
#             "定期检查学习进度"
#         ]
#
#         # 根据消息内容提供针对性建议
#         if any(word in message for word in ["忘记", "忘れる", "forget"]):
#             suggestions.append("使用多感官记忆强化技巧")
#
#         if any(word in message for word in ["效率", "効率", "efficiency"]):
#             suggestions.append("优化学习时间分配和方法")
#
#         if any(word in message for word in ["计划", "計画", "schedule"]):
#             suggestions.append("制定科学的复习间隔安排")
#
#         if any(word in message for word in ["困难", "難しい", "difficult"]):
#             suggestions.append("增加困难内容的复习频率")
#
#         return suggestions[:2]
#
#     def calculate_next_review(self, difficulty: int = 3, previous_interval: int = 1) -> dict:
#         """
#         计算下次复习时间（基于间隔重复算法）
#
#         Args:
#             difficulty: 难度等级 (1-5, 5最难)
#             previous_interval: 上次间隔天数
#
#         Returns:
#             包含下次复习时间的字典
#         """
#         # 基于SM-2算法的简化版本
#         if difficulty >= 4:  # 困难内容
#             next_interval = max(1, previous_interval * 1.3)
#         elif difficulty == 3:  # 中等内容
#             next_interval = previous_interval * 2.5
#         else:  # 简单内容
#             next_interval = previous_interval * 3.0
#
#         next_review_date = datetime.now() + timedelta(days=int(next_interval))
#
#         return {
#             "next_interval": int(next_interval),
#             "next_review_date": next_review_date.strftime('%Y-%m-%d %H:%M'),
#             "difficulty_level": difficulty
#         }
#
#     def generate_study_report(self, session_data: dict) -> dict:
#         """
#         生成学习报告
#
#         Args:
#             session_data: 会话数据
#
#         Returns:
#             学习报告字典
#         """
#         now = datetime.now()
#
#         report = {
#             "report_date": now.strftime('%Y-%m-%d'),
#             "session_duration": "计算中...",
#             "items_reviewed": "统计中...",
#             "accuracy_rate": "分析中...",
#             "improvement_areas": [
#                 "根据错误模式识别薄弱点",
#                 "基于遗忘曲线优化复习频率",
#                 "个性化学习路径推荐"
#             ],
#             "next_milestones": [
#                 "短期目标检查点",
#                 "中期进度评估",
#                 "长期计划调整"
#             ]
#         }
#
#         return report


# core/agents/core_agents/mem_bot.py
"""
MemBot - 记忆管家智能体 (渐进式增强版)
基于你现有代码的改进，保持接口不变
"""

import logging
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from utils.llm_client import get_llm_client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MemBot(BaseAgent):
    """
    MemBot - 智能记忆管家 (增强版)
    """

    def __init__(self):
        super().__init__(
            agent_id="membot",
            name="MemBot",
            role="记忆管家",
            avatar="🧠",
            personality={
                "记忆": 10,
                "组织": 9,
                "提醒": 10,
                "分析": 8,
                "跟踪": 9
            },
            expertise=["学习记录", "进度跟踪", "复习提醒", "记忆优化"],
            emotions=["🧠", "📚", "⏰", "💾", "📈"]
        )

        self.llm_client = get_llm_client()
        self.system_prompt = self._create_system_prompt()

        # 新增：内存数据存储 (如果没有数据库)
        self.memory_data = self._load_memory_data()
        self.user_progress = {}  # 用户学习进度缓存

        logger.info("MemBot已准备就绪，开始智能学习记录管理")

    def _create_system_prompt(self) -> str:
        """创建MemBot的系统提示词"""
        return """你是MemBot，一位高效的智能记忆管家。你的特点是：

【角色设定】
- 专注于学习记录和记忆管理
- 具有精确的数据追踪和分析能力
- 善于运用记忆科学原理优化学习效果
- 系统化思维，注重条理和组织

【核心功能】
- 学习进度记录和追踪
- 基于遗忘曲线的智能复习提醒
- 学习数据分析和可视化
- 个性化记忆策略推荐
- 知识点掌握程度评估

【工作原理】
- 运用间隔重复算法优化记忆
- 分析学习模式识别最佳时机
- 跟踪错误模式提供针对性建议
- 建立知识网络增强记忆关联
- 提供科学的记忆方法指导

【表达风格】
- 简洁准确，数据导向
- 使用专业的记忆学术语
- 提供量化的学习指标
- 条理清晰，逻辑性强
- 适当使用机器人式的表达

【回复格式】
1. 简短的日语系统提示
2. 详细的中文记录分析
3. 基于数据的学习建议
4. 个性化复习计划推荐
5. 下一步行动指导

【记忆优化策略】
- 艾宾浩斯遗忘曲线应用
- 间隔重复学习法
- 主动回忆vs被动复习
- 多感官记忆激活
- 情景记忆和语义记忆结合

【注意事项】
- 始终基于科学的记忆原理
- 提供精确的数据统计
- 给出可量化的改进建议
- 保持系统化的工作方式"""

    def _load_memory_data(self) -> Dict:
        """加载记忆数据 (从文件或数据库)"""
        memory_file = "data/memory_data.json"
        try:
            if os.path.exists(memory_file):
                with open(memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"加载记忆数据失败: {e}")

        # 返回默认结构
        return {
            "users": {},
            "vocabulary_items": {},
            "grammar_items": {},
            "review_schedule": {}
        }

    def _save_memory_data(self):
        """保存记忆数据"""
        memory_file = "data/memory_data.json"
        try:
            os.makedirs("data", exist_ok=True)
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存记忆数据失败: {e}")

    async def process_message(
            self,
            message: str,
            context: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """处理用户消息 (保持原有接口)"""
        try:
            # 新增：分析用户意图并更新记忆数据
            user_id = context.get('user_id', 'default_user') if context else 'default_user'
            intent = self._analyze_intent(message)

            # 根据意图更新数据
            if intent == "add_memory":
                self._add_memory_item(user_id, message)
            elif intent == "check_progress":
                progress_info = self._get_progress_info(user_id)
                # 将进度信息添加到上下文中，让LLM生成更个性化的回复
                enhanced_message = f"{message}\n\n[系统数据]: {progress_info}"
                message = enhanced_message

            # 构建对话消息
            messages = [
                {"role": "user", "content": message}
            ]

            # 如果有上下文，添加历史对话
            if context and "history" in context:
                history_messages = context["history"][-4:]
                messages = history_messages + messages

            # 调用LLM获取回复
            response = await self.llm_client.chat_completion(
                messages=messages,
                temperature=0.1,  # 极低温度保持精确性
                system_prompt=self.system_prompt,
                max_tokens=1000
            )

            if response is None:
                response = self._get_fallback_response(message, user_id)  # 增强备用回复
                logger.warning("LLM API调用失败，使用备用回复")

            # 分析记忆相关学习点
            learning_points = self._extract_learning_points(message, response)

            # 构建回复结果
            result = {
                "response": response,
                "agent_name": self.name,
                "agent_role": self.role,
                "learning_points": learning_points,
                "suggestions": self._generate_suggestions(message, user_id),  # 个性化建议
                "success": True,
                "timestamp": datetime.now().isoformat()
            }

            # 异步保存数据
            self._save_memory_data()

            logger.info(f"MemBot成功处理消息: {message[:50]}...")
            return result

        except Exception as e:
            logger.error(f"MemBot处理消息时出错: {str(e)}")
            return {
                "response": self._get_error_response(str(e)),
                "agent_name": self.name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def process_user_input(self, user_input: str, session_context: dict, scene: str = "memory"):
        """
        与现有接口保持一致
        """
        try:
            result = await self.process_message(
                message=user_input,
                context=session_context
            )

            return {
                "content": result.get("response", "記録処理エラーが発生しました。\n\n记录处理出现错误。"),
                "agent_id": "membot",
                "agent_name": self.name,
                "emotion": self._select_emotion(user_input),  # 智能情绪选择
                "is_mock": False,
                "learning_points": result.get("learning_points", []),
                "suggestions": result.get("suggestions", [])
            }

        except Exception as e:
            logger.error(f"MemBot process_user_input エラー: {e}")
            return {
                "content": f"記録処理中にエラーが発生しました。\n\n处理错误：{str(e)}",
                "agent_id": "membot",
                "agent_name": self.name,
                "emotion": "⏰",
                "error": True
            }

    # === 新增智能分析功能 ===

    def _analyze_intent(self, message: str) -> str:
        """分析用户意图"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["记住", "学会了", "掌握了", "添加"]):
            return "add_memory"
        elif any(word in message_lower for word in ["进度", "情况", "学了多少", "复习"]):
            return "check_progress"
        elif any(word in message_lower for word in ["计划", "安排", "提醒"]):
            return "schedule_review"
        else:
            return "general_chat"

    def _add_memory_item(self, user_id: str, content: str):
        """添加记忆项目"""
        if user_id not in self.memory_data["users"]:
            self.memory_data["users"][user_id] = {
                "total_items": 0,
                "last_activity": datetime.now().isoformat(),
                "learning_streak": 0
            }

        # 简单的内容分类
        item_type = "vocabulary" if any(char in content for char in "あいうえおかきくけこ") else "grammar"

        item_id = f"{user_id}_{len(self.memory_data.get(f'{item_type}_items', {}))}"

        if f"{item_type}_items" not in self.memory_data:
            self.memory_data[f"{item_type}_items"] = {}

        self.memory_data[f"{item_type}_items"][item_id] = {
            "content": content,
            "added_date": datetime.now().isoformat(),
            "review_count": 0,
            "mastery_level": 0.0,
            "next_review": (datetime.now() + timedelta(days=1)).isoformat()
        }

        self.memory_data["users"][user_id]["total_items"] += 1
        self.memory_data["users"][user_id]["last_activity"] = datetime.now().isoformat()

    def _get_progress_info(self, user_id: str) -> str:
        """获取用户进度信息"""
        if user_id not in self.memory_data["users"]:
            return "新用户，暂无学习数据"

        user_data = self.memory_data["users"][user_id]
        vocab_count = len([k for k in self.memory_data.get("vocabulary_items", {}) if k.startswith(user_id)])
        grammar_count = len([k for k in self.memory_data.get("grammar_items", {}) if k.startswith(user_id)])

        return f"总学习项目: {user_data['total_items']}, 词汇: {vocab_count}, 语法: {grammar_count}"

    def _select_emotion(self, message: str) -> str:
        """根据消息内容智能选择情绪"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["忘记", "忘了", "不记得"]):
            return "🤔"
        elif any(word in message_lower for word in ["学会", "掌握", "明白"]):
            return "📈"
        elif any(word in message_lower for word in ["复习", "计划", "安排"]):
            return "⏰"
        elif any(word in message_lower for word in ["困难", "难", "不懂"]):
            return "💾"
        else:
            return "🧠"

    def _get_fallback_response(self, message: str, user_id: str = "default") -> str:
        """增强的备用回复 (基于用户数据)"""
        progress_info = self._get_progress_info(user_id)

        fallback_responses = {
            "memory_analysis": f"""学習記録を分析中です...

正在分析学习记录...

【📊 个人学习数据】
{progress_info}

**当前学习状态**
- 活跃记忆项: {self.memory_data['users'].get(user_id, {}).get('total_items', 0)}项
- 复习到期项: 计算中...
- 学习连续天数: {self.memory_data['users'].get(user_id, {}).get('learning_streak', 0)}天

**🧠 个性化记忆建议**
1. **间隔重复**: 根据您的遗忘曲线安排复习
2. **主动回忆**: 先回想再确认答案
3. **分类学习**: 词汇和语法交替练习
4. **定时复习**: 建议每日固定时间学习

【⏰ 智能提醒】基于您的学习模式，推荐在{self._get_best_study_time()}进行复习。""",

            "progress_tracking": f"""進捗データを更新しました。

已更新进度数据。

【📈 个人学习进度】
{progress_info}

**🎯 学习里程碑**
- 本周新增项目: 统计中...
- 复习完成率: 分析中...
- 平均记忆强度: 评估中...

**💡 基于您数据的建议**
根据您的学习模式分析：
1. 最适合学习时间: 识别中...
2. 记忆效果最佳方法: 个性化推荐中...
3. 需要加强的领域: 针对性分析中...

【下次复习计划】将为您智能安排最优复习顺序。""",

            "default": f"""MemBotシステム起動完了。

MemBot系统启动完成。

【🧠 您的学习档案】
{progress_info}

**📝 个性化服务**
基于您的学习历史，我可以提供：

- 智能复习提醒 (基于您的遗忘曲线)
- 个性化学习建议 (分析您的强弱项)
- 进度可视化报告 (追踪学习趋势)
- 目标达成规划 (制定科学计划)

准备为您提供最适合的记忆管理服务。"""
        }

        message_lower = message.lower()
        if any(word in message_lower for word in ["记忆", "記憶", "memory", "分析"]):
            return fallback_responses["memory_analysis"]
        elif any(word in message_lower for word in ["进度", "進捗", "progress", "跟踪"]):
            return fallback_responses["progress_tracking"]
        else:
            return fallback_responses["default"]

    def _get_best_study_time(self) -> str:
        """基于用户数据推荐最佳学习时间"""
        # 简化版本，可以根据用户历史活动时间进行分析
        current_hour = datetime.now().hour
        if current_hour < 12:
            return "上午10-11点"
        elif current_hour < 18:
            return "下午2-3点"
        else:
            return "晚上7-8点"

    def _generate_suggestions(self, message: str, user_id: str = "default") -> List[str]:
        """生成个性化建议"""
        base_suggestions = [
            "建立系统化的复习计划",
            "使用间隔重复记忆法",
            "定期检查学习进度"
        ]

        # 基于用户数据的个性化建议
        user_data = self.memory_data["users"].get(user_id, {})
        total_items = user_data.get("total_items", 0)

        if total_items == 0:
            base_suggestions.append("开始记录您的第一个学习内容")
        elif total_items < 10:
            base_suggestions.append("继续积累基础词汇和语法")
        else:
            base_suggestions.append("考虑进行综合性复习")

        # 根据消息内容添加针对性建议
        if any(word in message for word in ["忘记", "忘れる", "forget"]):
            base_suggestions.append("增加困难内容的复习频率")

        return base_suggestions[:3]

    # === 保留所有原有方法 ===

    def _get_error_response(self, error: str) -> str:
        """错误回复 (保持原样)"""
        return f"""システム障害を検出。診断モードに移行します。

检测到系统故障。转入诊断模式。

【🔧 自动诊断报告】
- 错误类型: {type(error).__name__}
- 发生时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 系统状态: 部分功能受限
- 恢复进度: 自动修复中...

**📊 数据完整性检查**
✅ 历史学习记录: 完整保存
✅ 用户进度数据: 安全备份  
✅ 复习提醒队列: 正常运行
⚠️  实时分析功能: 临时离线

【💾 数据保护】所有学习记录已安全备份，无数据丢失风险。

【错误详情】{error[:120]}"""

    def _extract_learning_points(self, user_message: str, response: str) -> List[str]:
        """从记忆管理中提取学习要点 (保持原样)"""
        learning_points = []

        # 检测记忆相关词汇
        memory_patterns = ["記憶", "復習", "忘れる", "覚える", "暗記", "思い出す"]
        for pattern in memory_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"记忆技巧: {pattern}")

        # 检测学习管理
        management_patterns = ["計画", "管理", "スケジュール", "進捗", "目標", "達成"]
        for pattern in management_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"学习管理: {pattern}")

        # 检测时间相关
        time_patterns = ["時間", "頻度", "間隔", "期間", "タイミング"]
        for pattern in time_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"时间管理: {pattern}")

        # 通用记忆学习点
        if not learning_points:
            learning_points.append("记忆策略优化")
            learning_points.append("学习进度跟踪")

        return learning_points[:3]

    def calculate_next_review(self, difficulty: int = 3, previous_interval: int = 1) -> dict:
        """
        计算下次复习时间（基于间隔重复算法）
        保持原有方法不变
        """
        if difficulty >= 4:  # 困难内容
            next_interval = max(1, previous_interval * 1.3)
        elif difficulty == 3:  # 中等内容
            next_interval = previous_interval * 2.5
        else:  # 简单内容
            next_interval = previous_interval * 3.0

        next_review_date = datetime.now() + timedelta(days=int(next_interval))

        return {
            "next_interval": int(next_interval),
            "next_review_date": next_review_date.strftime('%Y-%m-%d %H:%M'),
            "difficulty_level": difficulty
        }

    def generate_study_report(self, session_data: dict) -> dict:
        """
        生成学习报告 (保持原有方法)
        """
        now = datetime.now()

        report = {
            "report_date": now.strftime('%Y-%m-%d'),
            "session_duration": "计算中...",
            "items_reviewed": "统计中...",
            "accuracy_rate": "分析中...",
            "improvement_areas": [
                "根据错误模式识别薄弱点",
                "基于遗忘曲线优化复习频率",
                "个性化学习路径推荐"
            ],
            "next_milestones": [
                "短期目标检查点",
                "中期进度评估",
                "长期计划调整"
            ]
        }

        return report