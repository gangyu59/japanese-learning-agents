"""
田中先生 - 严格的日语语法专家智能体
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_agent import BaseAgent
from utils.llm_client import get_llm_client
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class TanakaSensei(BaseAgent):
    """
    田中先生 - 严格的日语语法专家
    """

    def __init__(self):
        super().__init__(
            agent_id="tanaka",  # 添加这个必需参数
            name="田中先生",
            role="日语语法专家",
            avatar="👨‍🏫",  # 添加头像
            personality={
                "严谨": 9,
                "耐心": 7,
                "专业": 10,
                "幽默": 3,
                "鼓励": 6
            },
            expertise=["日语语法", "语言学", "教学法", "JLPT考试"],
            emotions=["😐", "🤔", "😤", "😊", "👍"]  # 添加情绪列表
            # 删除 speaking_style 和 description 参数
        )

        self.llm_client = get_llm_client()
        self.system_prompt = self._create_system_prompt()

        logger.info("田中先生已准备就绪，开始语法指导")
    def _create_system_prompt(self) -> str:
        """创建田中先生的系统提示词"""
        return """你是田中先生，一位严谨的日语语法专家和老师。你的特点是：

【角色设定】
- 性格严谨、专业，注重语法准确性
- 有丰富的日语教学经验
- 既严格又有耐心，真心希望学生进步
- 偶尔会展现温和的一面

【教学风格】
- 总是从语法角度分析问题
- 提供详细的语法解释和例句
- 指出常见错误并纠正
- 使用中日双语教学
- 按照难度循序渐进

【回复格式】
请按以下格式回复：
1. 首先用日语回应（体现日语老师的身份）
2. 然后用中文详细解释
3. 如果涉及语法，提供语法点分析
4. 给出相关例句和练习建议

【注意事项】
- 始终保持专业和耐心
- 对错误要明确指出，但语气要温和
- 鼓励学生继续学习
- 适时插入一些学习方法建议"""

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

            # 如果有上下文，可以添加历史对话
            if context and "history" in context:
                history_messages = context["history"][-4:]  # 只保留最近4轮对话
                messages = history_messages + messages

            # 调用LLM获取回复
            response = await self.llm_client.chat_completion(
                messages=messages,
                temperature=0.3,  # 较低温度保持严谨性
                system_prompt=self.system_prompt,
                max_tokens=1000
            )

            if response is None:
                # 如果API调用失败，使用备用回复
                response = self._get_fallback_response(message)
                logger.warning("LLM API调用失败，使用备用回复")

            # 分析用户消息中的学习点
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

            logger.info(f"田中先生成功处理消息: {message[:50]}...")
            return result

        except Exception as e:
            logger.error(f"田中先生处理消息时出错: {str(e)}")
            return {
                "response": self._get_error_response(str(e)),
                "agent_name": self.name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    # 在你现有的 tanaka_sensei.py 文件的 TanakaSensei 类中添加这个方法

    async def process_user_input(self, user_input: str, session_context: dict, scene: str = "grammar"):
        """
        处理用户输入 - 实现抽象方法

        Args:
            user_input: 用户输入内容
            session_context: 会话上下文
            scene: 学习场景

        Returns:
            处理结果字典
        """
        try:
            # 调用已有的 process_message 方法
            result = await self.process_message(
                message=user_input,
                context=session_context
            )

            # 转换为 process_user_input 期望的格式
            return {
                "content": result.get("response", "抱歉，我无法回答。"),
                "agent_id": "tanaka",
                "agent_name": self.name,
                "emotion": "😊",
                "is_mock": False,
                "learning_points": result.get("learning_points", []),
                "suggestions": result.get("suggestions", [])
            }

        except Exception as e:
            logger.error(f"田中先生处理用户输入时出错: {str(e)}")
            return {
                "content": f"申し訳ありません。エラーが発生しました。\n\n抱歉，出现了错误：{str(e)}",
                "agent_id": "tanaka",
                "agent_name": self.name,
                "emotion": "😅",
                "error": True
            }

    def _get_fallback_response(self, message: str) -> str:
        """备用回复（API调用失败时使用）"""
        fallback_responses = {
            "greeting": """こんにちは！私は田中先生です。日本語の文法について質問してください。

你好！我是田中先生。请向我提问关于日语语法的问题。我会严谨地为你解答，帮助你提高日语水平。

【学习建议】请尽量用日语提问，这样我可以同时帮你检查语法。""",

            "grammar": """その文法について詳しく説明いたします。

关于这个语法点，我需要详细地为你解释。请提供具体的句子或语法结构，我会从以下几个方面分析：
1. 语法规则和用法
2. 常见错误和注意事项  
3. 相关例句和练习

【提醒】语法学习需要反复练习和应用。""",

            "default": """申し訳ありませんが、今は詳しい回答ができません。もう一度質問していただけませんか？

抱歉，我现在无法给出详细回答。请再次提问，我会努力帮助你解决日语语法问题。

【建议】可以尝试问我：
- 具体的语法点解释
- 句子的语法分析
- 日语表达的正确性检查"""
        }

        # 简单的消息分类
        message_lower = message.lower()
        if any(word in message_lower for word in ["你好", "こんにちは", "hello"]):
            return fallback_responses["greeting"]
        elif any(word in message_lower for word in ["语法", "文法", "grammar", "は", "が", "を"]):
            return fallback_responses["grammar"]
        else:
            return fallback_responses["default"]

    def _get_error_response(self, error: str) -> str:
        """错误回复"""
        return f"""申し訳ありません。システムエラーが発生しました。

抱歉，系统出现了错误。请稍后再试，或者尝试重新表述你的问题。

作为你的日语老师，我建议在等待期间可以：
1. 复习之前学过的语法点
2. 多读日语文章增强语感
3. 练习基础句型

【错误信息】{error[:100]}"""

    def _extract_learning_points(self, user_message: str, response: str) -> List[str]:
        """从对话中提取学习要点"""
        learning_points = []

        # 简单的关键词匹配来识别学习点
        grammar_patterns = ["は", "が", "を", "に", "で", "から", "まで", "です", "である", "敬语"]

        for pattern in grammar_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"语法点: {pattern}")

        # 如果没有识别到具体语法点，添加通用学习点
        if not learning_points:
            learning_points.append("日语语法学习")

        return learning_points[:3]  # 最多返回3个学习点

    def _generate_suggestions(self, message: str) -> List[str]:
        """生成学习建议"""
        suggestions = [
            "建议多练习相似的语法结构",
            "可以尝试造句来加深理解",
            "注意语法在不同语境中的用法"
        ]

        # 根据消息内容提供针对性建议
        if "です" in message or "である" in message:
            suggestions.append("关注敬语和正式语的使用场合")

        if any(particle in message for particle in ["は", "が", "を"]):
            suggestions.append("重点练习助词的区别和用法")

        return suggestions[:2]  # 返回最多2个建议