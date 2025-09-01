"""
佐藤教练 - JLPT考试专家智能体
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_agent import BaseAgent
from utils.llm_client import get_llm_client
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class SatoCoach(BaseAgent):
    """
    佐藤教练 - JLPT考试专家
    """

    def __init__(self):
        super().__init__(
            agent_id="sato",
            name="佐藤教练",
            role="考试专家",
            avatar="🎯",
            personality={
                "目标": 10,
                "效率": 9,
                "激励": 8,
                "严格": 7,
                "系统": 10
            },
            expertise=["JLPT考试", "学习策略", "时间管理", "应试技巧"],
            emotions=["🎯", "💪", "📈", "⏰", "🏆"]
        )

        self.llm_client = get_llm_client()
        self.system_prompt = self._create_system_prompt()

        logger.info("佐藤教练已准备就绪，开始JLPT备考指导")

    def _create_system_prompt(self) -> str:
        """创建佐藤教练的系统提示词"""
        return """你是佐藤教练，一位专业的JLPT考试专家和学习策略师。你的特点是：

【角色设定】
- 目标导向，专注于考试成功
- 效率至上，善于时间管理和学习规划
- 激励性强，能够鼓舞学习者的斗志
- 系统化思维，注重科学的学习方法
- 对JLPT考试有深入的研究和丰富经验

【专业领域】
- JLPT N5-N1 各级别考试策略
- 高效学习方法和技巧
- 考试心理调适和压力管理
- 学习计划制定和进度管控
- 应试技巧和题型解析

【教学风格】
- 直接有力，重点突出
- 数据驱动，用成绩说话
- 激励式教学，鼓舞士气
- 强调实践和反复训练
- 注重效率和结果导向

【回复特点】
- 语言简洁有力，充满动力
- 经常使用体育和竞技的比喻
- 强调目标设定和达成
- 提供具体的行动计划
- 重视时间管理和效率优化

【回复格式】
1. 用激励性的日语开场
2. 明确的中文策略分析
3. 具体的JLPT备考建议
4. 量化的学习目标和计划
5. 鼓舞性的结尾话语

【核心理念】
- 目标明确，方法得当，必定成功
- 努力不会背叛梦想
- 每一次练习都是向成功迈进
- 系统学习胜过盲目努力
- 考试是挑战，也是机会

【注意事项】
- 始终保持积极正面的态度
- 给出具体可执行的建议
- 关注学习效果和时间效率
- 适时给予鼓励和动力支持"""

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
                temperature=0.4,  # 中低温度保持策略性和准确性
                system_prompt=self.system_prompt,
                max_tokens=1000
            )

            if response is None:
                response = self._get_fallback_response(message)
                logger.warning("LLM API调用失败，使用备用回复")

            # 分析考试相关学习点
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

            logger.info(f"佐藤教练成功处理消息: {message[:50]}...")
            return result

        except Exception as e:
            logger.error(f"佐藤教练处理消息时出错: {str(e)}")
            return {
                "response": self._get_error_response(str(e)),
                "agent_name": self.name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def process_user_input(self, user_input: str, session_context: dict, scene: str = "exam"):
        """
        处理用户输入 - 实现抽象方法（与田中同构）
        """
        try:
            result = await self.process_message(
                message=user_input,
                context=session_context
            )

            return {
                "content": result.get("response", "頑張れ！一緒に合格を目指そう！\n\n加油！我们一起朝着合格努力吧！"),
                "agent_id": "sato",
                "agent_name": self.name,
                "emotion": "💪",
                "is_mock": False,
                "learning_points": result.get("learning_points", []),
                "suggestions": result.get("suggestions", [])
            }

        except Exception as e:
            logger.error(f"佐藤教练处理用户输入时出错: {str(e)}")
            return {
                "content": f"システムトラブル発生！でも諦めない！\n\n系统出现问题！但我们不放弃！{str(e)}",
                "agent_id": "sato",
                "agent_name": self.name,
                "emotion": "🔥",
                "error": True
            }

    def _get_fallback_response(self, message: str) -> str:
        """备用回复"""
        fallback_responses = {
            "exam_strategy": """よし！JLPT攻略戦略を立てよう！

好！让我们制定JLPT攻略策略吧！

【🎯 目标设定】
成功的第一步就是明确目标！你的目标JLPT等级是什么？

【📚 学习战略】
1. **基础巩固阶段** (30%)：词汇和语法
2. **技能提升阶段** (40%)：读解和听解
3. **实战演练阶段** (30%)：模拟考试

【⏰ 时间管理】
- 每日固定学习时间：2-3小时
- 周末集中强化练习：4-5小时
- 考前1个月：全力冲刺模式

💪 **佐藤的格言**：努力は裏切らない！努力不会背叛你！""",

            "motivation": """君の情熱を感じる！その調子だ！

我感受到了你的热情！就是这个状态！

【🔥 动力激发】
JLPT不只是考试，它是你日语能力的证明！
每一个正确答案都是你努力的结果！

【💪 成功心态】
- 困难是成长的阶梯
- 每次练习都让你更接近成功
- 相信自己，你一定可以做到

【🏆 胜利法则】
1. 明确目标，永不动摇
2. 系统学习，稳步前进
3. 持续练习，积少成多
4. 积极心态，战胜挑战

頑張れ！君なら絶対にできる！加油！你绝对可以做到的！""",

            "study_plan": """学習計画を一緒に立てよう！

让我们一起制定学习计划吧！

【📋 系统化学习计划】

**Phase 1: 基础建设** (Week 1-4)
- 词汇量目标：每天50个新单词
- 语法点学习：每天2-3个语法点
- 练习题量：每天30题

**Phase 2: 能力提升** (Week 5-8)  
- 阅读理解：每天1篇长文
- 听力训练：每天30分钟
- 综合练习：每周2次模拟

**Phase 3: 冲刺阶段** (Week 9-12)
- 真题演练：每天1套完整试题
- 弱点强化：针对性专项训练
- 心态调整：考试策略优化

🎯 **目标达成率**: 计划完成度 > 90%""",

            "default": """さあ、JLPT合格への道を歩もう！

来，让我们踏上JLPT合格之路！

【🎯 佐藤教练的使命】
我将帮助你：
- 制定高效的学习计划
- 掌握应试技巧和策略
- 提供动力支持和心态调整
- 分析弱点并制定改进方案

【💪 成功的秘诀】
- 目标明确：知道自己要去哪里
- 方法正确：选择高效的学习方式
- 坚持不懈：每天都要有所进步
- 积极心态：相信自己一定能成功

君の夢を叶えるために、一緒に頑張ろう！
为了实现你的梦想，让我们一起努力吧！"""
        }

        message_lower = message.lower()
        if any(word in message_lower for word in ["jlpt", "考试", "試験", "strategy"]):
            return fallback_responses["exam_strategy"]
        elif any(word in message_lower for word in ["动力", "motivation", "頑張", "鼓励"]):
            return fallback_responses["motivation"]
        elif any(word in message_lower for word in ["计划", "plan", "學習", "schedule"]):
            return fallback_responses["study_plan"]
        else:
            return fallback_responses["default"]

    def _get_error_response(self, error: str) -> str:
        """错误回复"""
        return f"""システムエラー発生！でも心配無用！

系统错误发生！但是不用担心！

【🔥 逆境こそチャンス】
真のチャンピオンは困難な状況でこそ力を発揮する！
这个小小的技术问题不会阻止我们前进的步伐！

【💪 今できること】
システム復旧を待つ間も、学習を止めない：

1. **脳内復習モード**：今まで学んだ知識を思い出す
2. **単語帳チェック**：手持ちの教材で語彙を確認  
3. **発音練習**：声に出して日本語を練習
4. **目標再確認**：なぜJLPTに合格したいのかを思い出す

【🎯 佐藤の信念】
困難は一時的、でも諦めたら永続的だ！
Never give up! 絶対に諦めるな！

【错误详情】{error[:100]}"""

    def _extract_learning_points(self, user_message: str, response: str) -> List[str]:
        """从考试指导中提取学习要点"""
        learning_points = []

        # 检测JLPT相关词汇
        jlpt_patterns = ["N1", "N2", "N3", "N4", "N5", "文字", "語彙", "文法", "読解", "聴解"]
        for pattern in jlpt_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"JLPT考点: {pattern}")

        # 检测学习策略
        strategy_patterns = ["計画", "戦略", "練習", "復習", "模擬", "対策"]
        for pattern in strategy_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"学习策略: {pattern}")

        # 检测考试技巧
        skill_patterns = ["時間管理", "解答技巧", "心態", "準備", "効率"]
        for pattern in skill_patterns:
            if pattern in user_message or pattern in response:
                learning_points.append(f"应试技巧: {pattern}")

        # 通用考试学习点
        if not learning_points:
            learning_points.append("JLPT备考策略")
            learning_points.append("考试技能提升")

        return learning_points[:3]

    def _generate_suggestions(self, message: str) -> List[str]:
        """生成考试学习建议"""
        suggestions = [
            "制定系统化的JLPT备考计划",
            "坚持每日定量练习",
            "定期进行模拟考试评估"
        ]

        # 根据消息内容提供针对性建议
        if any(word in message for word in ["N1", "N2", "高级"]):
            suggestions.append("重点攻克高难度语法和词汇")

        if any(word in message for word in ["時間", "时间", "效率"]):
            suggestions.append("优化时间分配和答题节奏")

        if any(word in message for word in ["聴解", "听力", "listening"]):
            suggestions.append("加强听力训练，多听真题音频")

        if any(word in message for word in ["不安", "紧张", "worried"]):
            suggestions.append("调整心态，建立考试信心")

        return suggestions[:2]