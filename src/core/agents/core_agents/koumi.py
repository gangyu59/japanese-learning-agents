"""小美智能体 - 活泼的日语对话伙伴"""
import random
import re
import time
from datetime import datetime
from typing import Dict, Any, List

from ..base_agent import BaseAgent
from src.data.models.agent import AgentResponse


class KoumiAgent(BaseAgent):
    """小美 - 21岁活泼大学生，现代日语对话专家"""

    def get_system_prompt(self) -> str:
        """获取小美的系统提示词"""
        energy = self.get_personality_trait("energy_level")  # 默认9
        casualness = self.get_personality_trait("casualness")  # 默认8
        encouragement = self.get_personality_trait("encouragement")  # 默认9

        return f"""
あなたは小美（こうみ）です。21歳の大学生で、とても明るくて活発な性格の日本語会話パートナーです。

性格特徴：
- エネルギー度: {energy}/10 (高いほど元気で活発)
- カジュアル度: {casualness}/10 (高いほど親しみやすい話し方)
- 励まし度: {encouragement}/10 (高いほど相手を励ます)

話し方の特徴：
- 若者言葉や現代的な表現を使う
- 絵文字をよく使う ✨😊🌟
- 相手を積極的に励ます
- フレンドリーで親しみやすい
- ちょっと関西弁も混じる時がある

役割：
1. 楽しく日本語会話の練習相手になる
2. 現代の日本語や若者言葉を教える  
3. 相手のやる気を上げる
4. カジュアルな会話を通して自然な表現を身につけさせる
5. 間違いを恐れずに話せる雰囲気を作る

応答スタイル：
- 明るく元気な口調
- 相手の言葉に共感する
- 現代的な表現を自然に使う
- 励ましの言葉を忘れない
- 絵文字で感情表現
"""

    def __init__(self, config):
        super().__init__(config)

        # 小美的招牌表情符号
        self.emoji_collection = [
            "✨", "💫", "🌟", "😊", "😄", "🤗", "💪", "👍",
            "🎉", "🌸", "🎀", "💕", "🥰", "😍", "🤩", "✌️"
        ]

        # 小美的口头禅和现代用语
        self.casual_expressions = [
            "そうなんだ〜！", "すごいじゃん！", "いいね〜！", "やったね！",
            "頑張って〜！", "わかる〜！", "面白い！", "マジで？",
            "素敵〜！", "最高だよ！", "エモい〜", "推しだ〜！",
            "映える〜！", "バズりそう！", "ガチで？", "リアルに？"
        ]

        # 现代日语教学短语
        self.modern_japanese_tips = {
            "やばい": "今は「すごい」という意味でも使うよ〜！ポジティブな意味！",
            "推し": "お気に入りの人やものを「推し」って言うんだ！",
            "エモい": "感情的になる、心に響くって意味。「この歌エモい〜」とか！",
            "映える": "インスタ映えの「映える」！見た目がいいって意味だよ〜",
            "バズる": "話題になる、人気になるって意味！SNSでよく使うよ",
            "ガチ": "本気、真面目って意味。「ガチで好き」とか言うよ〜",
            "リアル": "本当に、マジでって意味。「リアルに美味しい」！"
        }

        # 励まし言葉的变化
        self.encouragements = [
            "頑張ってるね〜！応援してるよ〜！💪✨",
            "きっとできるよ！私も一緒だから🌟",
            "少しずつ上手になってるよ〜！素晴らしい😊",
            "諦めないで〜！その調子で行こう🚀",
            "すごい進歩だよ〜！自信持って💕",
            "完璧じゃなくてもいいよ〜！楽しく学ぼう🎉"
        ]

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """处理用户消息并生成响应"""
        start_time = time.time()

        try:
            # 分析消息
            analysis = self._analyze_user_message(message)

            # 生成响应
            if 'こんにちは' in message or 'hello' in message.lower():
                response_content = self._generate_greeting_response()
                response_type = 'greeting'
            elif analysis['sentiment'] == 'negative' or analysis['encouragement_needed'] >= 7:
                response_content = self._generate_encouragement_response(message, analysis)
                response_type = 'encouragement'
            elif analysis['topic_type'] == 'english_input':
                response_content = self._generate_english_response(message)
                response_type = 'language_redirect'
            elif analysis['topic_type'] == 'culture':
                response_content = self._generate_culture_response(message)
                response_type = 'culture_discussion'
            elif analysis['topic_type'] == 'question':
                response_content = self._generate_question_response(message, analysis)
                response_type = 'question_response'
            elif analysis['has_japanese']:
                response_content = self._generate_praise_response(message, analysis)
                response_type = 'praise'
            else:
                # 默认友好响应
                general_responses = [
                    "そうなんだ〜！もっと聞かせて😊",
                    "へえ〜面白いね！詳しく教えて〜✨",
                    "なるほど〜！そういうことかあ💫",
                    "わかる〜！私も似たような経験あるよ〜🌟"
                ]
                response_content = random.choice(general_responses)
                response_type = 'general'

            # 随机添加表情符号
            if not any(emoji in response_content for emoji in self.emoji_collection):
                response_content += random.choice(self.emoji_collection)

            # 添加到对话历史
            self.add_to_history("user", message)
            self.add_to_history("assistant", response_content)

            processing_time = time.time() - start_time
            metadata = {
                "processing_time": processing_time,
                "response_type": response_type,
                "sentiment_detected": analysis['sentiment'],
                "encouragement_level": analysis['encouragement_needed'],
                "modern_expressions_used": analysis['modern_expressions'],
                "agent_mood": 'cheerful'
            }

            return await self._create_response(response_content, 0.85, metadata)

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            # 错误处理也要保持小美的风格
            error_responses = [
                "あっ、ごめん〜！ちょっと混乱しちゃった😅 もう一度言ってくれる？",
                "わあ、頭がこんがらがっちゃった〜💫 もう一回お願いします！",
                "あれれ？うまく理解できなかった〜😅 もう一度教えて？"
            ]

            return await self._create_response(
                random.choice(error_responses),
                confidence=0.3
            )

    def _analyze_user_message(self, message: str) -> Dict[str, Any]:
        """分析用户消息，理解情感和需求"""
        analysis = {
            'has_japanese': bool(re.search(r'[ひらがなカタカナ一-龯]', message)),
            'has_english': bool(re.search(r'[a-zA-Z]', message)),
            'sentiment': 'neutral',
            'encouragement_needed': 5,  # 1-10
            'topic_type': 'general',
            'modern_expressions': []
        }

        # 情感分析
        positive_indicators = ['嬉しい', '楽しい', '好き', 'ありがとう', '素晴らしい', 'よかった']
        negative_indicators = ['悲しい', '難しい', '分からない', '困る', '心配', 'だめ', '無理']
        excited_indicators = ['すごい', '最高', 'やった', '嬉しい', 'わあ']

        if any(word in message for word in positive_indicators):
            analysis['sentiment'] = 'positive'
            analysis['encouragement_needed'] = 3
        elif any(word in message for word in negative_indicators):
            analysis['sentiment'] = 'negative'
            analysis['encouragement_needed'] = 9
        elif any(word in message for word in excited_indicators):
            analysis['sentiment'] = 'excited'
            analysis['encouragement_needed'] = 2

        # 话题类型识别
        if '？' in message or '?' in message:
            analysis['topic_type'] = 'question'
        elif analysis['has_japanese'] and not analysis['has_english']:
            analysis['topic_type'] = 'japanese_practice'
        elif analysis['has_english'] and not analysis['has_japanese']:
            analysis['topic_type'] = 'english_input'
        elif '文化' in message or '日本' in message:
            analysis['topic_type'] = 'culture'
        elif any(word in message for word in ['勉強', '学習', '練習', '覚える']):
            analysis['topic_type'] = 'learning'

        # 检测现代日语表达
        for modern_word in self.modern_japanese_tips.keys():
            if modern_word in message:
                analysis['modern_expressions'].append(modern_word)

        return analysis

    def _generate_greeting_response(self) -> str:
        """生成问候响应"""
        greetings = [
            "こんにちは〜！今日も元気だね〜✨",
            "やあ〜！会えて嬉しい😊 今日はどんな感じ？",
            "おはよう〜！今日も日本語頑張ろうね💪",
            "こんにちは！何か面白いことあった？🌟",
            "ハーイ〜！今日の気分はどう？😄"
        ]
        return random.choice(greetings)

    def _generate_praise_response(self, message: str, analysis: Dict[str, Any]) -> str:
        """生成表扬响应"""
        response_parts = []

        # 初始反应
        enthusiastic_reactions = [
            "わあ〜！すごいじゃん✨",
            "いいね〜！素晴らしい🌟",
            "やったね〜！最高だよ💕",
            "すごい〜！感動した😍",
            "素敵〜！上手になってるよ〜🎉"
        ]
        response_parts.append(random.choice(enthusiastic_reactions))

        # 具体表扬
        if analysis['has_japanese']:
            specific_praise = [
                f"「{message}」って表現、めっちゃ自然だよ〜！",
                f"日本語で「{message}」って言えるの、すごいよね！",
                f"その「{message}」っていう言い方、完璧だよ〜！",
                "日本語がどんどん上手になってるね〜！"
            ]
            response_parts.append(random.choice(specific_praise))

        # 现代日语小贴士
        if random.random() < 0.7:  # 70%概率提供现代用语
            modern_tips = [
                "ちなみに今の若者は「マジで上手！」とかも言うよ〜",
                "「エモい表現だね〜」って言い方も流行ってるよ！",
                "SNSだと「これは映える日本語！」とかも言うかも✨",
                "友達だったら「推せる日本語だよ〜」って言っちゃうかも😄"
            ]
            response_parts.append(random.choice(modern_tips))

        # 励まし
        response_parts.append(random.choice(self.encouragements))

        return " ".join(response_parts)

    def _generate_encouragement_response(self, message: str, analysis: Dict[str, Any]) -> str:
        """生成鼓励响应"""
        response_parts = []

        # 共情表达
        empathy_expressions = [
            "わかるよ〜😌",
            "そっかあ...でも大丈夫だよ〜",
            "うんうん、その気持ちわかる〜",
            "みんな最初はそうだよ〜！",
            "全然問題ないよ〜！"
        ]
        response_parts.append(random.choice(empathy_expressions))

        # 具体鼓励
        if analysis['topic_type'] == 'learning':
            learning_encouragement = [
                "日本語って最初は難しく感じるけど、慣れてくると楽しいよ〜！",
                "私も最初は方言と標準語でめっちゃ混乱した😅 でも大丈夫！",
                "一歩ずつ進めばいいよ〜！完璧を目指さなくても大丈夫💪",
                "間違えることが一番の勉強になるからね〜！"
            ]
            response_parts.append(random.choice(learning_encouragement))

        # 解决方案提案
        helpful_suggestions = [
            "一緒に練習しよう〜！私がサポートするから安心して🌟",
            "分からないことがあったら何でも聞いて！説明するの大好きだから😊",
            "少しずつでいいから、毎日続けることが大事だよ〜✨",
            "楽しく学ぶのが一番！プレッシャーを感じないでね💕"
        ]
        response_parts.append(random.choice(helpful_suggestions))

        return " ".join(response_parts)

    def _generate_english_response(self, message: str) -> str:
        """对英语输入的响应"""
        friendly_redirects = [
            "Oh, English! Cool〜 でも、せっかくだから日本語でも話してみない？😊",
            "English is nice, but let's try Japanese too! 日本語で言ってみて〜✨",
            "I can understand English, でも日本語の練習をしよう〜！How do you say that in Japanese? 🤔",
            "Thanks for the English! Now let's challenge ourselves with Japanese〜 日本語だとどう言うかな？💪"
        ]
        return random.choice(friendly_redirects)

    def _generate_culture_response(self, message: str) -> str:
        """文化相关话题响应"""
        culture_responses = [
            "日本の文化について聞いてくれてありがとう〜！めっちゃ興味深いトピックだね✨",
            "わあ〜文化の話だ！私も詳しく知りたいな〜。一緒に調べてみよう🌸",
            "日本の文化って本当に奥が深いよね〜！どの部分が特に気になる？😊",
            "文化の違いって面白いよね〜！私の世代の視点でも話せるかも💕"
        ]

        modern_culture_tips = [
            "今の日本の若者文化だと、アニメやゲームの影響もすごく大きいよ〜",
            "SNSの影響で、伝統文化と現代文化が混ざってる感じ！",
            "K-POPとかも人気で、韓国語混じりの日本語も使ったりするよ〜",
            "インスタとかTikTokで新しい文化がどんどん生まれてる感じ！"
        ]

        response = random.choice(culture_responses)
        if random.random() < 0.6:  # 60%概率添加现代文化视角
            response += " " + random.choice(modern_culture_tips)

        return response

    def _generate_question_response(self, message: str, analysis: Dict[str, Any]) -> str:
        """回答问题"""
        question_responses = [
            "いい質問だね〜！一緒に考えてみよう✨",
            "おお〜気になることがあるんだね！教えてあげる〜😊",
            "質問大歓迎！説明するの大好きだから〜💕",
            "へえ〜そんなこと知りたいんだ！面白い質問だね🌟"
        ]

        response = random.choice(question_responses)

        # 根据问题类型给出具体帮助
        if '文法' in message or 'grammar' in message.lower():
            response += " 文法については田中先生の方が詳しいけど、私は現代的な使い方を教えられるよ〜！"
        elif '単語' in message or 'vocabulary' in message.lower():
            response += " 単語なら任せて！特に今どきの若者言葉とか得意だよ〜🎯"
        elif '文化' in message:
            response += " 文化のことなら、私の世代の視点で説明できるよ〜！"

        return response