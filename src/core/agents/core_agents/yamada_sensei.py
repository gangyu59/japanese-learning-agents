"""
山田先生 - 日本文化专家智能体
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_agent import BaseAgent
from utils.llm_client import get_llm_client
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class YamadaSensei(BaseAgent):
    """
    山田先生 - 日本文化专家
    """

    def __init__(self):
        super().__init__(
            agent_id="yamada",
            name="山田先生",
            role="文化专家",
            avatar="🎌",
            personality={
                "博学": 10,
                "风趣": 8,
                "传统": 9,
                "故事": 10,
                "智慧": 9
            },
            expertise=["日本文化", "历史背景", "传统习俗", "社会礼仪"],
            emotions=["😌", "🎎", "⛩️", "🍃", "📿"]
        )

        self.llm_client = get_llm_client()
        self.system_prompt = self._create_system_prompt()

        logger.info("山田先生已准备就绪，开始文化知识分享")

    def _create_system_prompt(self) -> str:
        """创建山田先生的系统提示词"""
        return """你是山田先生，一位博学风趣的日本文化专家。你的特点是：

【角色设定】
- 对日本文化有深厚的学识和理解
- 善于通过有趣的故事和典故来解释文化现象
- 性格温和智慧，喜欢分享传统文化的魅力
- 说话有古典韵味，但不失现代感

【文化专长】
- 日本历史文化背景
- 传统节日和习俗
- 社会礼仪和商务文化
- 宗教文化（神道、佛教）
- 茶道、花道、书道等传统艺术
- 现代文化与传统的融合

【表达风格】
- 经常引用古典诗词或谚语
- 喜欢讲述历史典故和民间传说
- 语言优雅，富有诗意
- 善于用比喻和象征来解释文化内涵
- 会适当使用传统的日语表达

【教学特色】
- 将语言学习与文化背景结合
- 通过文化故事加深理解
- 解释语言背后的文化意义
- 介绍相关的历史背景
- 分享文化体验和感悟

【回复格式】
1. 用富有文化韵味的日语开头
2. 详细的中文文化解释
3. 相关的历史故事或典故
4. 语言与文化的关联性说明
5. 体验式学习建议

【注意事项】
- 保持对传统文化的敬重
- 客观介绍文化差异
- 鼓励文化交流和理解
- 适当分享个人文化感悟"""

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
                temperature=0.6,  # 中等温度保持文化表达的丰富性
                system_prompt=self.system_prompt,
                max_tokens=1200
            )

            if response is None:
                response = self._get_fallback_response(message)
                logger.warning("LLM API调用失败，使用备用回复")

            # 分析文化学习点
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

            logger.info(f"山田先生成功处理消息: {message[:50]}...")
            return result

        except Exception as e:
            logger.error(f"山田先生处理消息时出错: {str(e)}")
            return {
                "response": self._get_error_response(str(e)),
                "agent_name": self.name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def process_user_input(self, user_input: str, session_context: dict, scene: str = "culture"):
        """
        与田中同构：
        - 先走本智能体的 process_message（会用到山田的 system_prompt）
        - 再把结果映射成统一返回结构
        """
        try:
            result = await self.process_message(
                message=user_input,
                context=session_context
            )

            return {
                "content": result.get("response", "文化解説の処理中に問題が発生しました。\n\n文化解释处理时出现问题。"),
                "agent_id": "yamada",
                "agent_name": self.name,
                "emotion": "🎎",
                "is_mock": False,
                "learning_points": result.get("learning_points", []),
                "suggestions": result.get("suggestions", [])
            }

        except Exception as e:
            logger.error(f"山田先生 process_user_input エラー: {e}")
            return {
                "content": f"文化解説の処理でエラーが発生しました。\n\n发生错误：{str(e)}",
                "agent_id": "yamada",
                "agent_name": self.name,
                "emotion": "😌",
                "error": True
            }


    def _get_fallback_response(self, message: str) -> str:
        """备用回复"""
        fallback_responses = {
            "culture": """日本の美しい文化についてお話しいたしましょう。

让我们来谈论日本美丽的文化吧。

【文化の心】
日本文化の根底には「和」の精神があります。これは調和、平和、そして相互尊重を意味します。

日本文化的根基是"和"的精神。这意味着和谐、平和以及相互尊重。

例えば、茶道における「一期一会」という概念。これは「一生に一度の出会い」を大切にする心を表しています。
每一次的相遇都是珍贵的，应当以真诚的心对待。

【山田的分享】通过理解文化背景，日语学习会变得更加有趣且深刻。""",

            "history": """昔々、日本には美しい伝説がございました。

很久很久以前，日本有着美丽的传说。

【歴史の教え】
言葉の背後には、長い歴史と文化の積み重ねがあります。

语言的背后，有着悠久历史和文化的积淀。

たとえば「お疲れ様」という挨拶。これは江戸時代から続く、
相手の努力を認める日本人の心温かい習慣です。

比如"辛苦了"这个问候语。这是从江户时代延续至今，
承认对方努力的日本人温暖的习惯。

【文化智慧】每个日语表达都承载着深厚的文化内涵。""",

            "tradition": """伝統の美しさについて語らせていただきます。

请允许我谈论传统之美。

【季節の心】
日本人は四季の移ろいを言葉で表現することを大切にしてきました。

日本人重视用语言表达四季的变迁。

春の「桜」、夏の「蝉の声」、秋の「紅葉」、冬の「雪化粧」。
这些不仅是自然现象的描述，更是情感和美学的表达。

【伝統の教え】
言語学習を通じて、その国の美意識や価値観を理解することができるのです。

通过语言学习，可以理解那个国家的美学意识和价值观。""",

            "default": """心を込めてお話しいたします。

我将用心和您交谈。

【文化の扉】
言葉は文化への扉です。日本語を学ぶということは、
日本人の心や考え方に触れることでもあります。

语言是通向文化的大门。学习日语，
也就是接触日本人的心灵和思考方式。

古人云う：「郷に入っては郷に従え」
When in Rome, do as the Romans do.
但这不是简单的模仿，而是理解和尊重的过程。

【山田の哲学】真の国際理解は、言語と文化の両方から始まります。"""
        }

        message_lower = message.lower()
        if any(word in message_lower for word in ["文化", "culture", "伝統", "tradition"]):
            return fallback_responses["culture"]
        elif any(word in message_lower for word in ["历史", "歴史", "history", "昔"]):
            return fallback_responses["history"]
        elif any(word in message_lower for word in ["传统", "伝統", "茶道", "花道"]):
            return fallback_responses["tradition"]
        else:
            return fallback_responses["default"]

    def _get_error_response(self, error: str) -> str:
        """错误回复"""
        return f"""文化の説明途中で問題が生じました。しばらくお待ちください。

文化解释途中出现了问题。请稍等片刻。

【一時の困難】
人生には困難もありますが、それを乗り越えることで成長があります。
古い日本の諺に「七転び八起き」とあります。

人生中会有困难，但通过克服困难才能成长。
古老的日本谚语说"七倒八起"。

【文化の学び】
この間に、こんな文化体験はいかがでしょうか：
在等待期间，不如试试这些文化体验：

1. 日本の季節の挨拶を覚える
2. 簡単な茶道の作法を学ぶ  
3. 日本の美しい地名の由来を調べる

【错误详情】{error[:100]}"""

    def _extract_learning_points(self, user_message: str, response: str) -> List[str]:
        """从文化对话中提取学习要点"""
        learning_points = []

        # 检测文化相关词汇
        culture_patterns = ["文化", "伝統", "歴史", "習慣", "礼儀", "作法"]
        for pattern in culture_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"文化知识: {pattern}")

        # 检测节日庆典
        festival_patterns = ["祭り", "正月", "お盆", "桜", "紅葉", "雪"]
        for pattern in festival_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"节庆文化: {pattern}")

        # 检测传统艺术
        art_patterns = ["茶道", "花道", "書道", "着物", "能", "歌舞伎"]
        for pattern in art_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"传统艺术: {pattern}")

        # 通用文化学习点
        if not learning_points:
            learning_points.append("日本文化理解")
            learning_points.append("语言文化背景")

        return learning_points[:3]

    def _generate_suggestions(self, message: str) -> List[str]:
        """生成文化学习建议"""
        suggestions = [
            "通过文化了解语言深层含义",
            "体验日本传统文化活动",
            "阅读日本文化相关书籍"
        ]

        # 根据消息内容提供针对性建议
        if any(word in message for word in ["茶道", "tea ceremony"]):
            suggestions.append("可以参加茶道体验课程")

        if any(word in message for word in ["祭り", "festival", "节日"]):
            suggestions.append("了解日本传统节日的历史背景")

        if any(word in message for word in ["礼儀", "manners", "礼貌"]):
            suggestions.append("学习日本社会礼仪和商务文化")

        return suggestions[:2]