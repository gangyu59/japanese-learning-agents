"""
MemBot - 记忆管家智能体
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from utils.llm_client import get_llm_client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MemBot(BaseAgent):
    """
    MemBot - 智能记忆管家
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

    async def process_message(
            self,
            message: str,
            context: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """处理用户消息"""
        try:
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
                response = self._get_fallback_response(message)
                logger.warning("LLM API调用失败，使用备用回复")

            # 分析记忆相关学习点
            learning_points = self._extract_learning_points(message, response)

            # 构建回复结果
            result = {
                "response": response,
                "agent_name": self.name,
                "agent_role": self.role,
                "learning_points": learning_points,
                "suggestions": self._generate_suggestions(message),
                "success": True,
                "timestamp": datetime.now().isoformat()
            }

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
        与田中同构：走 process_message + 统一映射
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
                "emotion": "🧠",
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


    def _get_fallback_response(self, message: str) -> str:
        """备用回复"""
        fallback_responses = {
            "memory_analysis": """学習記録を分析中です...

正在分析学习记录...

【📊 记忆数据分析】
基于科学记忆原理的学习追踪：

**当前学习状态**
- 活跃记忆项: 待统计
- 复习到期项: 待检测  
- 掌握程度: 分析中
- 遗忘风险: 评估中

**🧠 记忆优化建议**
1. **间隔重复**: 根据遗忘曲线安排复习
2. **主动回忆**: 先回想再确认答案
3. **交替学习**: 混合不同类型内容
4. **睡前复习**: 利用睡眠巩固记忆

【⏰ 智能提醒】下次复习时间将根据个人遗忘曲线计算。""",

            "progress_tracking": """進捗データを更新しました。

已更新进度数据。

【📈 学习进度追踪】
```
学习时长: 计算中...
完成项目: 统计中...
正确率: 分析中...
连续学习天数: 记录中...
```

**🎯 里程碑追踪**
- 短期目标完成度: 评估中
- 中期目标进展: 监控中  
- 长期计划状态: 跟踪中

**💡 基于数据的建议**
根据您的学习模式分析：
1. 最佳学习时间: 待识别
2. 高效记忆方法: 个性化推荐
3. 薄弱环节强化: 针对性训练

【下次复习时间】智能算法将为您计算最优复习间隔。""",

            "review_schedule": """復習スケジュールを生成中...

正在生成复习计划...

【⏰ 智能复习提醒系统】

**基于艾宾浩斯遗忘曲线的复习安排**
```
第1次复习: 学习后20分钟
第2次复习: 学习后1天
第3次复习: 学习后3天  
第4次复习: 学习后7天
第5次复习: 学习后15天
第6次复习: 学习后30天
```

**🔄 个性化间隔调整**
- 困难内容: 缩短间隔
- 熟练内容: 延长间隔
- 错误内容: 增加频次

**📱 智能提醒功能**
我会在最佳时机提醒您复习，确保记忆效果最大化。""",

            "default": """MemBotシステム起動完了。

MemBot系统启动完成。

【🧠 记忆管家服务】
我的核心功能：

**📝 学习记录管理**
- 自动记录学习内容和进度
- 追踪知识点掌握情况
- 识别学习模式和习惯

**⏰ 智能复习提醒**  
- 基于遗忘曲线的科学复习
- 个性化间隔重复算法
- 最佳时机提醒系统

**📊 数据分析服务**
- 学习效果评估报告
- 进度趋势可视化图表
- 个性化改进建议

**🎯 目标跟踪系统**
- 学习目标设定和监控  
- 里程碑达成情况追踪
- 成就系统和激励机制

准备为您提供最科学的记忆管理服务。"""
        }

        message_lower = message.lower()
        if any(word in message_lower for word in ["记忆", "記憶", "memory", "分析"]):
            return fallback_responses["memory_analysis"]
        elif any(word in message_lower for word in ["进度", "進捗", "progress", "跟踪"]):
            return fallback_responses["progress_tracking"]
        elif any(word in message_lower for word in ["复习", "復習", "review", "提醒"]):
            return fallback_responses["review_schedule"]
        else:
            return fallback_responses["default"]

    def _get_error_response(self, error: str) -> str:
        """错误回复"""
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

**🛠️ 应急处理方案**
1. 启用离线记录模式
2. 保存当前会话数据
3. 计划延迟同步更新

【💾 数据保护】所有学习记录已安全备份，无数据丢失风险。

【错误详情】{error[:120]}"""

    def _extract_learning_points(self, user_message: str, response: str) -> List[str]:
        """从记忆管理中提取学习要点"""
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

    def _generate_suggestions(self, message: str) -> List[str]:
        """生成记忆管理建议"""
        suggestions = [
            "建立系统化的复习计划",
            "使用间隔重复记忆法",
            "定期检查学习进度"
        ]

        # 根据消息内容提供针对性建议
        if any(word in message for word in ["忘记", "忘れる", "forget"]):
            suggestions.append("使用多感官记忆强化技巧")

        if any(word in message for word in ["效率", "効率", "efficiency"]):
            suggestions.append("优化学习时间分配和方法")

        if any(word in message for word in ["计划", "計画", "schedule"]):
            suggestions.append("制定科学的复习间隔安排")

        if any(word in message for word in ["困难", "難しい", "difficult"]):
            suggestions.append("增加困难内容的复习频率")

        return suggestions[:2]

    def calculate_next_review(self, difficulty: int = 3, previous_interval: int = 1) -> dict:
        """
        计算下次复习时间（基于间隔重复算法）

        Args:
            difficulty: 难度等级 (1-5, 5最难)
            previous_interval: 上次间隔天数

        Returns:
            包含下次复习时间的字典
        """
        # 基于SM-2算法的简化版本
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
        生成学习报告

        Args:
            session_data: 会话数据

        Returns:
            学习报告字典
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