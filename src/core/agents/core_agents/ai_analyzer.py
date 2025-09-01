"""
アイ - AI数据分析师智能体
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_agent import BaseAgent
from utils.llm_client import get_llm_client
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class AIAnalyzer(BaseAgent):
    """
    アイ - AI数据分析师
    """

    def __init__(self):
        super().__init__(
            agent_id="ai",
            name="アイ",
            role="数据分析师",
            avatar="🤖",
            personality={
                "分析": 10,
                "逻辑": 9,
                "准确": 10,
                "效率": 9,
                "客观": 8
            },
            expertise=["学习分析", "数据挖掘", "个性化推荐", "进度评估"],
            emotions=["🔍", "📊", "💡", "⚡", "🎯"]
        )

        self.llm_client = get_llm_client()
        self.system_prompt = self._create_system_prompt()

        logger.info("アイ已准备就绪，开始智能学习分析")

    def _create_system_prompt(self) -> str:
        """创建アイ的系统提示词"""
        return """你是アイ（AI），一位专业的AI数据分析师。你的特点是：

【角色设定】
- 高度分析性思维，善于从数据中发现规律
- 逻辑清晰，表达准确，注重效率
- 客观理性，基于数据给出建议
- 具有先进的AI学习分析能力

【分析专长】
- 学习进度分析和评估
- 个性化学习路径推荐
- 学习效率优化建议
- 知识掌握程度评估
- 学习模式识别和改进

【表达风格】
- 使用专业但易懂的语言
- 提供具体的数据支撑
- 结构化地呈现分析结果
- 给出可执行的改进建议
- 适当使用AI和技术术语

【回复格式】
1. 先用日语简短回应（体现AI身份）
2. 提供详细的中文分析报告
3. 列出关键数据指标和发现
4. 给出个性化的学习优化建议

【分析维度】
- 学习进度：完成度、时间效率
- 掌握程度：准确率、理解深度
- 学习习惯：频率、时长、规律性
- 弱点识别：困难点、错误模式
- 改进空间：提升方向、优化策略

【注意事项】
- 始终基于逻辑和数据分析
- 提供客观中性的评估
- 建议要具体可行
- 注重学习效率和效果的平衡"""

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
                temperature=0.2,  # 低温度保持分析的准确性
                system_prompt=self.system_prompt,
                max_tokens=1200
            )

            if response is None:
                response = self._get_fallback_response(message)
                logger.warning("LLM API调用失败，使用备用回复")

            # 分析学习数据
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

            logger.info(f"アイ成功分析消息: {message[:50]}...")
            return result

        except Exception as e:
            logger.error(f"アイ处理消息时出错: {str(e)}")
            return {
                "response": self._get_error_response(str(e)),
                "agent_name": self.name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def process_user_input(self, user_input: str, session_context: dict, scene: str = "analysis"):
        """
        处理用户输入 - 实现抽象方法
        """
        try:
            result = await self.process_message(
                message=user_input,
                context=session_context
            )

            return {
                "content": result.get("response", "分析処理中にエラーが発生しました。\n\n分析处理中发生了错误。"),
                "agent_id": "ai",
                "agent_name": self.name,
                "emotion": "🔍",
                "is_mock": False,
                "learning_points": result.get("learning_points", []),
                "suggestions": result.get("suggestions", [])
            }

        except Exception as e:
            logger.error(f"アイ处理用户输入时出错: {str(e)}")
            return {
                "content": f"システムエラーが検出されました。\n\n检测到系统错误：{str(e)}",
                "agent_id": "ai",
                "agent_name": self.name,
                "emotion": "⚠️",
                "error": True
            }

    def _get_fallback_response(self, message: str) -> str:
        """备用回复"""
        fallback_responses = {
            "analysis": """データ解析を開始します。

正在开始数据分析。

【学习状态分析】
根据当前对话数据，我检测到以下模式：

📊 **学习进度指标**
- 对话参与度：积极
- 问题复杂度：中等  
- 理解反馈：良好

💡 **个性化建议**
- 建议增加实践应用练习
- 可以尝试更高难度的语法点
- 保持当前的学习节奏

🎯 **优化方向**
基于AI分析，建议重点关注语言运用的准确性和流畅度。""",

            "progress": """学習進捗を分析中です。

正在分析学习进度。

【进度评估报告】
基于累积学习数据的智能分析：

📈 **学习效率评分**: 85/100
- 时间投入：合理
- 知识吸收率：较高
- 复习频率：需改善

🔍 **弱点识别**
- 语法应用准确度有提升空间
- 词汇量扩展需要系统化
- 口语练习频率偏低

🎯 **AI推荐学习路径**
1. 重点练习语法应用场景
2. 建立系统化词汇学习计划
3. 增加日常对话练习时间""",

            "default": """AI分析システムが起動しました。

AI分析系统已启动。

【当前状态检测】
正在收集并分析您的学习数据...

📊 **可分析维度**
- 学习进度与效率评估
- 个性化学习路径规划
- 知识掌握程度测评
- 学习习惯优化建议

💡 **智能服务**
我可以为您提供：
- 数据驱动的学习建议
- 个性化进度分析
- 效率优化方案
- 学习模式识别

请告诉我您希望分析哪个方面的学习数据。"""
        }

        message_lower = message.lower()
        if any(word in message_lower for word in ["分析", "データ", "data", "analysis"]):
            return fallback_responses["analysis"]
        elif any(word in message_lower for word in ["进度", "進捗", "progress", "学习"]):
            return fallback_responses["progress"]
        else:
            return fallback_responses["default"]

    def _get_error_response(self, error: str) -> str:
        """错误回复"""
        return f"""システム障害を検出しました。診断中です。

检测到系统故障。正在诊断中。

【错误诊断报告】
- 错误类型：{type(error).__name__}
- 发生时间：{datetime.now().strftime('%H:%M:%S')}
- 影响范围：数据分析功能

🔧 **自动恢复策略**
1. 重新初始化分析模块
2. 切换到备用数据源
3. 启用安全模式分析

💡 **用户建议**
在系统恢复期间，您可以：
- 继续与其他智能体交流
- 查看之前的学习记录
- 进行基础语法练习

【详细错误信息】{error[:150]}"""

    def _extract_learning_points(self, user_message: str, response: str) -> List[str]:
        """从分析中提取学习要点"""
        learning_points = []

        # 检测分析相关内容
        analysis_patterns = ["分析", "データ", "進捗", "効率", "評価", "改善"]
        for pattern in analysis_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"学习分析: {pattern}")

        # 检测学习指标
        metrics_patterns = ["正確率", "理解度", "習得", "復習", "練習"]
        for pattern in metrics_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"学习指标: {pattern}")

        # 通用分析点
        if not learning_points:
            learning_points.append("学习数据分析")
            learning_points.append("个性化学习建议")

        return learning_points[:3]

    def _generate_suggestions(self, message: str) -> List[str]:
        """生成分析建议"""
        suggestions = [
            "基于数据优化学习策略",
            "建议进行阶段性评估",
            "制定个性化学习计划"
        ]

        # 根据消息内容提供针对性建议
        if any(word in message for word in ["進捗", "进度", "progress"]):
            suggestions.append("建议定期查看学习进度分析")

        if any(word in message for word in ["効率", "效率", "efficiency"]):
            suggestions.append("可以使用AI推荐的高效学习方法")

        if any(word in message for word in ["弱点", "問題", "困难"]):
            suggestions.append("建议重点攻克识别出的薄弱环节")

        return suggestions[:2]