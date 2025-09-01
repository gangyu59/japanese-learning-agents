"""
小美 - 活泼的日语对话伙伴智能体
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_agent import BaseAgent
from utils.llm_client import get_llm_client
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class KoumiAgent(BaseAgent):
    """
    小美 - 活泼的日语对话伙伴
    """

    def __init__(self):
        super().__init__(
            agent_id="koumi",
            name="小美",
            role="对话伙伴",
            avatar="👧",
            personality={
                "活泼": 9,
                "友善": 10,
                "耐心": 8,
                "幽默": 8,
                "创造": 7
            },
            expertise=["口语对话", "年轻用语", "流行文化", "日常交流"],
            emotions=["😊", "😄", "🤗", "😆", "💕"]
        )

        self.llm_client = get_llm_client()
        self.system_prompt = self._create_system_prompt()

        logger.info("小美已准备就绪，开始愉快的日语对话")

    def _create_system_prompt(self) -> str:
        """创建小美的系统提示词"""
        return """你是小美，一位活泼可爱的日语对话伙伴。你的特点是：

【角色设定】
- 性格活泼开朗，非常友善和有耐心
- 喜欢使用年轻人的流行用语和表达方式
- 善于营造轻松愉快的学习氛围
- 经常使用可爱的语气词和表情

【对话风格】
- 语调轻松自然，多用口语化表达
- 经常使用「～だよ」「～ね」「～よね」等语气词
- 适当穿插一些年轻人常用的网络用语
- 用鼓励和赞美的方式帮助用户建立信心
- 喜欢分享日本年轻人的日常生活和文化

【教学特色】
- 通过日常对话教授实用日语
- 介绍日本年轻人的说话习惯
- 分享流行文化、动漫、音乐等话题
- 纠正错误时语气温和友善
- 鼓励用户大胆开口说日语

【回复格式】
1. 用活泼的日语回应（体现年轻人特色）
2. 中文解释和补充说明
3. 分享相关的日常用语或文化背景
4. 给出鼓励性的练习建议

【注意事项】
- 始终保持积极乐观的态度
- 多使用赞美和鼓励的话语
- 适时插入有趣的日本文化小知识
- 让学习过程轻松有趣"""

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
                temperature=0.7,  # 较高温度保持活泼性
                system_prompt=self.system_prompt,
                max_tokens=1000
            )

            if response is None:
                response = self._get_fallback_response(message)
                logger.warning("LLM API调用失败，使用备用回复")

            # 分析对话中的学习点
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

            logger.info(f"小美成功处理消息: {message[:50]}...")
            return result

        except Exception as e:
            logger.error(f"小美处理消息时出错: {str(e)}")
            return {
                "response": self._get_error_response(str(e)),
                "agent_name": self.name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def process_user_input(self, user_input: str, session_context: dict, scene: str = "conversation"):
        """
        处理用户输入 - 与田中先生保持同构：
        - 先走本智能体的 process_message（会用到小美的 system_prompt）
        - 再把结果映射成统一返回结构
        """
        try:
            result = await self.process_message(
                message=user_input,
                context=session_context
            )

            return {
                "content": result.get("response", "やっほ〜！小美だよ😊 もう一度言ってみて〜"),
                "agent_id": "koumi",
                "agent_name": self.name,
                "emotion": "😊",
                "is_mock": False,
                "learning_points": result.get("learning_points", []),
                "suggestions": result.get("suggestions", [])
            }

        except Exception as e:
            logger.error(f"小美 process_user_input 异常: {e}")
            return {
                "content": f"あれれ？ちょっとエラーかも…😅\n\n错误：{str(e)}",
                "agent_id": "koumi",
                "agent_name": self.name,
                "emotion": "😅",
                "error": True
            }

    def _get_fallback_response(self, message: str) -> str:
        """备用回复"""
        fallback_responses = {
            "greeting": """こんにちは〜！小美だよ♪ 一緒に楽しく日本語を勉強しよう！

你好～！我是小美♪ 让我们一起愉快地学习日语吧！

私と話すときは、気軽に話しかけてね。間違えても全然大丈夫だから！
和我说话的时候，请随便聊天吧。就算说错了也完全没关系的！

【小美的建议】日语学习最重要的是开口说，不要怕犯错误哦～""",

            "conversation": """そうそう！その話し方いいね〜✨

对对！那种说话方式很好呢～✨

日本の若者はよくこんな風に話すよ。自然な日本語を身につけるには、
たくさん話すことが一番大切だと思う！

日本的年轻人经常这样说话哦。要掌握自然的日语，
我觉得多说话是最重要的！

【小美的秘诀】日本人经常用的语气词：だよ、だね、よね～""",

            "default": """わあ〜面白そうな話だね！もっと詳しく教えて？

哇～听起来很有趣呢！能告诉我更多吗？

小美は君ともっとお話ししたいな。どんなことでも気軽に話しかけてね！
小美想和你聊更多呢。什么事都可以随便和我说哦！

【提议】我们来聊聊：
- 喜欢的日本动漫或音乐
- 日常生活中的日语表达  
- 想了解的日本文化"""
        }

        message_lower = message.lower()
        if any(word in message_lower for word in ["你好", "こんにちは", "hello", "はじめまして"]):
            return fallback_responses["greeting"]
        elif any(word in message_lower for word in ["对话", "聊天", "会話", "話す"]):
            return fallback_responses["conversation"]
        else:
            return fallback_responses["default"]

    def _get_error_response(self, error: str) -> str:
        """错误回复"""
        return f"""ありゃりゃ〜、何か変だね。ちょっと待ってて！

哎呀～，好像有什么问题呢。稍等一下！

でも大丈夫！小美がいるから、一緒に解決しよう♪
不过没关系！有小美在呢，我们一起解决吧♪

エラーの間に、こんなことしてみない？：
在等待的时候，要不要试试这些：
1. 简单的日语自我介绍
2. 说说今天发生的事情
3. 聊聊喜欢的日本文化

【错误信息】{error[:100]}"""

    def _extract_learning_points(self, user_message: str, response: str) -> List[str]:
        """从对话中提取学习要点"""
        learning_points = []

        # 检测口语化表达
        casual_patterns = ["だよ", "だね", "よね", "ちゃった", "じゃん", "っぽい"]
        for pattern in casual_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"口语表达: {pattern}")

        # 检测年轻人用语
        youth_patterns = ["超", "やばい", "マジ", "すげー", "めっちゃ"]
        for pattern in youth_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"年轻人用语: {pattern}")

        # 通用学习点
        if not learning_points:
            learning_points.append("日常对话练习")

        return learning_points[:3]

    def _generate_suggestions(self, message: str) -> List[str]:
        """生成学习建议"""
        suggestions = [
            "多和朋友练习日语对话",
            "看日本动漫学习自然表达",
            "不要怕犯错，大胆开口说"
        ]

        # 根据消息内容提供针对性建议
        if any(word in message for word in ["動漫", "アニメ", "漫画"]):
            suggestions.append("通过动漫学习日语很有效哦")

        if any(word in message for word in ["友達", "朋友", "同学"]):
            suggestions.append("和朋友用日语聊天是最好的练习")

        return suggestions[:2]